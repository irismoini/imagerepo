from flask import Flask, render_template, make_response, request, redirect, send_file, url_for, request, flash
import os
from werkzeug.utils import secure_filename
from imagerepo import database_ops
import uuid
import hashlib


app = Flask(__name__)

UPLOAD_FOLDER = 'images'
COOKIEID='userId'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
tokens={}

db = database_ops.DB()


#should be run using https for security purposes

def createToken(userId, resp):
    token=uuid.uuid4()
    tokens[token]=userId
    resp.set_cookie(COOKIEID, token.hex)

def getUser(request):
    cookie=request.cookies.get(COOKIEID)
    if cookie is None:
        return None
    token=uuid.UUID(hex=cookie)
    if token not in tokens:
        return None
    userId=tokens[token]
    return userId

@app.route('/')
def root():
    if getUser(request) is None:
        return redirect("/signin")
    else: 
        return redirect("/myimgs")

@app.route('/signin', methods=['GET','POST'])
def signin():
    if request.method == 'POST':
        user=db.getUser(request.form["username"])        
        if user:
            key = hashlib.pbkdf2_hmac(
                'sha256', 
                request.form["password"].encode('utf-8'), 
                user.salt, 
                100000 
            )
            if key==user.passwordHash:
                resp = make_response(redirect(url_for('myImgs')))
                createToken(user.id, resp)
                return resp
        return "Invalid username or password"
    return render_template("signin.html")

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        if not request.form["name"]:
            return "Enter your name"
         #if no field entered for username
        if not request.form["username"]:
            return "Enter your username"
         #if no field entered for password
        if not request.form["password"]:
            return "Enter your password"
        #if username already exists return username already exists
        if db.getUser(request.form["username"]) is not None:
            return "Username already exists, select a different one"
        #save user into database
        salt = os.urandom(32) 
        key = hashlib.pbkdf2_hmac(
            'sha256', 
            request.form["password"].encode('utf-8'), 
            salt, 
            100000 
        )
        db.addUser(request.form["username"], request.form["name"], key, salt)
        user = db.getUser(request.form['username'])
        resp = make_response(redirect(url_for('myImgs')))
        createToken(user.id,resp)
        return resp
    return render_template("signup.html")


@app.route('/images', methods=['GET'])
def sendImage():
    img = db.getImg(request.args.get('imageid')) 
    if img is None:
        return 'image does not exist', 404
    
    if img.public==True:
        resp = send_file(img.path, mimetype='image/gif')
        resp.headers["Cache-Control"] = "no-cache"
        return resp
    else:
        userId=getUser(request)
        if userId is not None:
            if userId==img.user:
                resp = send_file(img.path, mimetype='image/gif')
                resp.headers["Cache-Control"] = "no-cache"
                return resp

    return 'image does not belong to user',403
  
@app.route('/public')
def public():
    publicImgs=db.getImgs(publicSetting=True)
    return render_template('public.html',data=[img.id for img in publicImgs] )

@app.route('/myimgs')
def myImgs():
    userId=getUser(request)
    if userId is None:
        return redirect('/signin')
    userImgs=db.getImgs(userId)
    return render_template('myImgs.html',public=[img.id for img in userImgs if img.public], private=[img.id for img in userImgs if not img.public] )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET','POST'])
def uploadImg():
    userId=getUser(request)
    if userId is None:
        return redirect("\signin")
    if request.method == 'POST':
        if 'image' not in request.files:
            return "Upload in one of the following formats: png, jpg, jpeg, gif'"
        img = request.files['image']
        if img.filename == '':
            return "No file selected"
        if img and allowed_file(img.filename):
            _, ext=os.path.splitext(img.filename)
            filename=uuid.uuid4().hex
            fullPath=os.path.join(app.config['UPLOAD_FOLDER'],filename+ext)
            privacySetting=request.form["privacySetting"]
            if privacySetting=="Private":
                privacySetting=False
            if privacySetting=="Public":
                privacySetting=True
            img.save(fullPath)
            db.insertImg(fullPath, userId, privacySetting)
            return redirect(url_for('myImgs'))
    return render_template('upload.html')
    


@app.route("/logout")
def logout():
    resp=redirect("/signin")
    token=request.cookies.get(COOKIEID)
    if token in tokens:
        tokens.pop(token)
    resp.delete_cookie(COOKIEID)
    return resp
