import mysql.connector as mysql

from dataclasses import dataclass


@dataclass(frozen=True)
class ImageResult:
    id: str
    path: str
    public: bool
    user: str

@dataclass(frozen=True)
class UserResult:
    id: str
    username: str
    name: str
    passwordHash: bytes
    salt: bytes

class DB:
    def __init__(self):
        db_connection = mysql.connect(
            host = "localhost",
            user = "root",
            passwd = "imagerepo",
        )
        connection_cursor = db_connection.cursor()

        connection_cursor.execute("CREATE DATABASE if NOT EXISTS imagerepo")
        self.db = mysql.connect(
            host = "localhost",
            user = "root",
            passwd = "imagerepo",
            database="imagerepo",
        )
        self.cursor = self.db.cursor()

        self.cursor.execute("CREATE TABLE IF NOT EXISTS Users (user_id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, user_name VARCHAR(255) NOT NULL UNIQUE, name VARCHAR (255) NOT NULL, password_hash BINARY(32) NOT NULL, salt BINARY(32) NOT NULL)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Images (img_id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, img_path TEXT(3200) NOT NULL, privacy_setting BOOL NOT NULL, user_id INT(11) NOT NULL, FOREIGN KEY(user_id) REFERENCES Users(user_id))")

    def deleteDB(self):
        self.cursor.execute("DROP DATABASE imagerepo")

    #operations for Images table
    def insertImg(self,imgPath, userId, publicSetting):
        query = "INSERT INTO Images (img_path, user_id, privacy_setting) VALUES (%s, %s, %s)"
        values = (imgPath, userId, publicSetting)
        self.cursor.execute(query, values)
        self.db.commit()

    def getImgs(self, userId=None, publicSetting=None):
        if userId is not None and publicSetting is None:
            query = "SELECT * FROM Images WHERE user_id = %s"
            values=(userId,)
        elif userId is not None and publicSetting==True:
            query="Select * FROM Images WHERE user_id= %s AND privacy_setting= TRUE"
            values=(userId,)
        elif userId is not None and publicSetting==False:
            query="Select * FROM Images WHERE user_id= %s AND privacy_setting= FALSE"
            values=(userId,)
        elif userId is None and publicSetting==True:
            query = "SELECT * FROM Images WHERE privacy_setting = TRUE"
            values=None
        else:
            raise Exception("Incorrect parameters to getImgs()")
        self.cursor.execute(query,values)
        imgs = self.cursor.fetchall()
        imgs = [ImageResult(*img) for img in imgs]
        return imgs
    
    def getImg(self,imgId):
        query = "SELECT * FROM Images WHERE img_id = %s"
        values=(imgId,)
        self.cursor.execute(query,values)
        img = self.cursor.fetchall()
        if img:
            return ImageResult(*(img[0]))
        return None

    def modifyPrivacySet(self, imgId, publicSetting):
        if publicSetting==True:
            query = "UPDATE Images SET privacy_setting=TRUE WHERE img_id = %s"
        if publicSetting==False:
            query = "UPDATE Images SET privacy_setting=FALSE WHERE img_id =%s"
        values=(imageId,)
        self.cursor.execute(query,values)
        self.db.commit()

    def deleteImg(self,imgId):
        query = "DELETE FROM Images WHERE img_id = %s"
        values=(imageId,)
        self.cursor.execute(query,values)
        self.db.commit()

    #operations for User Table
    def addUser(self,username, name, passwordHash, salt):
        query = "INSERT INTO Users (user_name, name, password_hash, salt) VALUES (%s, %s, %s, %s)"
        values = (username, name, passwordHash, salt)
        self.cursor.execute(query, values)
        self.db.commit()

    def deleteUser(self,userId):
        query = "DELETE FROM Users WHERE user_id = %s"
        values=(userId,)
        self.cursor.execute(query,values)
        self.db.commit()

    def getUser(self,username):
        query= "SELECT * FROM Users WHERE user_name = %s"
        values=(username,)
        self.cursor.execute(query,values)
        user = self.cursor.fetchall()
        if user:
            return UserResult(*(user[0]))
        return None


if __name__=="__main__":
    import sys
    db=DB()
    if len(sys.argv) >= 2 and sys.argv[1] == 'drop':
        db.deleteDB() 


