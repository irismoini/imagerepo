# Shopify Developer Intern Summer 2021 Backend Challenge

This project is an image repo created using Flask as the web framework and MySQL as the database. The project
allows for the creation of new users, and associates users with images they have uploaded. 

# Usage and Installation

In order to use this application, MySQL must be installed. All Python requirements are listed in requirements.txt and must be installed. 

From the command line run `flask run` to start the server and follow the link provided.

This will take users to a sign-in page. Anyone (even those without an account) can view public images by clicking the Public Images button in the top left corner. Individuals who are not logged in will not be allowed to upload an image or view their private images and will be redirected to sign-in. 
 
Users who have not created an account will not be allowed to sign-in. Click create new user to create a new account. No two users may have the same username (a message will be displayed if the username already exists when attempting sign-in). Upon creating an account users will be able to view their images, upload an image, and select the image's privacy settings when uploading. They will also be able to view all users' public images. After logging out, users will be redirect to sign-in. The user's private images will no longer be avaliable for viewing and users will be unable to upload an image without signing in again at this point.

# Future development 
The database operations for modifying privacy setting of an image, and for deleting an image have already been implemented.
However, the frontend features, as well as the security to make sure that only owners of the image are attempting to delete and modify it's settings still need to be implemented. Because this was a backend challenge, the frontend could also be significantly improved. 




