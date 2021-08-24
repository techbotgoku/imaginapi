# IMAGIN REST API created by Gokul Naidu For Hedgehog Lab

### description : This is an API I created for a task given by hedgehog lab, I took a lot of concepts from instagram to do this API.

### Development hardware and software: Macbook Pro 2015, Python Version = 3.9.1, Coding environment= VS code , Testing application = Postman

#### additional information : This is the first time I created a REST API and I spent less than 24hrs (2 days on a whole) on learning about how to create and use REST API in python (with the help of stackoverflow and youtube) and tested to see if the api runs smoothly

## Setup:

1. Recommended : activate virtual environment (you can activate the same virtual environment for using)
`source .venv/bin/activate`
note: to deactivate virtual environment(to be done at end only) `$ deactivate`

2. Install **requirements.txt** to make sure the file runs
`pip3 install -r requirements.txt ` 

3. Check if **data.db** is present else use onine database url(default using the offline sqllite database) 

use this if data.db is absent and you want to create a local sqllite database
`python3 run.py` else add database url in imaginpost.py `app.config['SQLALCHEMY_DATABASE_URI'] = '<url>'`

4. To start using the API,
`python3 imagin.py`

5. Open Postman to use the api

## How to use:

### To create user:

**POST** Request, url = **<serveraddress>/user**
and in Postman go to Body --> raw mode and enter the following:
```Json
{
    "user_name" : "<user_name>",
    "name" : "<name>",
    "bio" : "<any_bio_the_user_wants>",
    "password" : "<password>" 
}
```
upon successfully creating an account the following will be returned in the body:
```Json
{
    "Successfully added user": "<user_name>"
}
```
Do note: user_name is unique and multiple entries under the same user_name is not possible

If it's a new database make sure to create an **admin** account first as admin can delete any user account and can control the entire api, to do this set user_name as "admin" `"user_name" : "<admin>"`


### To Login :

**GET** Request, url = **<serveraddress>/login**
and in Postman go to Authorization --> Type = Basic Auth and enter the **Username and password**
upon successful login you get the unique token in the body which is needed to do any task in the api,
```Json
{
    "token": "<token_value_displayed>"
}
```
 
Do note: make a note of this token and its valid only for  **60 minutes** after which you need to login

# Important only these above tasks don't require token, while the rest need token authentication to perform any other tasks, so to do that perform the following:

## In postman go to Headers and then add a new key termed:
 `x-access-token`  and value is `<token_value_displayed>`, the token which was displayed on successfull login


### To see all users in the app along with their following,followers and total posts:

**GET** Request, url = **<serveraddress>/user**

output will be in this format for normal user:
```Json
{
    "users": [
        {
            "bio": "<user1_bio>",
            "followers": <user1_followers_count>,
            "following": <user1_following_count>,
            "name": "<user1_name>",
            "posts": <user1_posts_count>,
            "user_name": "<user1_user_name>"
        },
        {
            "bio": "<user2_bio>",
            "followers": <user2_followers_count>,
            "following": <user2_following_count>,
            "name": "<user2_name>",
            "posts": <user2_posts_count>,
            "user_name": "<user2_user_name>"
        }
        .
        .
        .

    ]
}
```

output for admin will also have hashed passwords of users, their public _id and admin security clearance:
```Json
{
    "users": [
        {
            "admin": true,
            "bio": "<admin_bio>",
            "followers": <admin_followers_count>,
            "following": <admin_following_count>,
            "name": "<admin_name>",
            "password": "<admin_hashed_password>",
            "posts": <admin_posts_count>,
            "public_id": "<admin_public_id>",
            "user_name": "admin"
        },
        {
            "admin": false,
            "bio": "<user1_bio>",
            "followers": <user1_followers_count>,
            "following": <user1_following_count>,
            "name": "<user1_name>",
            "password": "<user1_hashed_password>",
            "posts": <user1_posts_count>,
            "public_id": "<user1_public_id>",
            "user_name": "<user1_user_name>"
        }
        .
        .
        .
        .
    ]
}

```


### To view specific user profile in the app along with their following,followers and total posts and posts details(including likes):

**GET** Request, url = **<serveraddress>/user/<username>**

If the current logged in user is trying to open their profile / if admin is trying to access
they can see hashed_password of the user along with public_id and the other details example:
```Json
{
    "user": {
        "admin": false,
        "bio": "Never Settle",
        "followers": 0,
        "following": 0,
        "name": "Gokul",
        "password": "sha256$Gj2wTo9Qq3G9iNdy$bc098e9696e2aff4b28e32317e2e777c277819af35ee95624aabe932b2a6cfe6",
        "posts": [
            {
                "caption": "Car",
                "likes": 0,
                "public_id": "ca9a6ed0-a64c-44dc-9fb8-b6176914b4c9",
                "url": "https://thumbor.forbes.com/thumbor/fit-in/1200x0/filters%3Aformat%28jpg%29/https%3A%2F%2Fspecials-images.forbesimg.com%2Fimageserve%2F5d35eacaf1176b0008974b54%2F0x0.jpg%3FcropX1%3D790%26cropX2%3D5350%26cropY1%3D784%26cropY2%3D3349"
            }
        ],
        "public_id": "6b559667-72fa-427d-accb-3bdab2c270e8",
        "total_posts": 1,
        "user_name": "techbotgoku"
    }
}
```
other wise if a user is normally visiting other user's profle, the output will be like:
```Json
{
    "user": {
        "bio": "Never Settle",
        "followers": 0,
        "following": 0,
        "name": "Gokul",
        "posts": [
            {
                "caption": "Car",
                "likes": 0,
                "public_id": "ca9a6ed0-a64c-44dc-9fb8-b6176914b4c9",
                "url": "https://thumbor.forbes.com/thumbor/fit-in/1200x0/filters%3Aformat%28jpg%29/https%3A%2F%2Fspecials-images.forbesimg.com%2Fimageserve%2F5d35eacaf1176b0008974b54%2F0x0.jpg%3FcropX1%3D790%26cropX2%3D5350%26cropY1%3D784%26cropY2%3D3349"
            }
        ],
        "total_posts": 1,
        "user_name": "techbotgoku"
    }
}
```


### To upload a post:
Note: The post will be uploaded to the current loggedin user only, and not even admin can upload images to others profile

**POST** Request, url = **<serveraddress>/user/post**

and in Postman go to Body --> raw mode and enter the following:
```Json
{
    "url" : "<image_url>",
    "caption" : "<caption>"
}
```
Note: if the url is not image an error will be thrown
Note: if you face an issue with posting image it might be due to the certifiates not being installed do the following if issue arrises :
```python
cd /Applications/Python\3.9/
./Install\ Certificates.command
```
or refer to https://stackoverflow.com/questions/40684543/how-to-make-python-use-ca-certificates-from-mac-os-truststore

### To delete a post:
Note: The post will be deleted from the current loggedin user only, and the public_id of the image should match with the user

**DELETE** Request, url = **<serveraddress>/user/post**

and in Postman go to Body --> raw mode and enter the following:
```Json
{
    "public_id" : "<image_public_id>",
}
```
Note: if the public_id is invalid or if the public_id doesn't belong to the user an error will be thrown

### To see all the posts of the current user:

**GET** Request, url = **<serveraddress>/user/post**

### To follow a user:

**PUT** Request, url = **<serveraddress>/user/<username_to_follow>/follow**
output will be 
```Json
{
    "<username_to_follow>": "Now following"
}
```
if already following :
```Json
{
    "error message": "Already following"
}
```
Note: You can only follow a user who you didn't follow yet if you try to follow a allready following user an error will be thrown


### to Unfollow user:

**DELETE** Request, url = **<serveraddress>/user/<username_to_follow>/follow**
output will be 
```Json
{
    "username_to_follow": " Now Unfollowed"
}
```
if already following :
```Json
{
    "error message": "Not a follower to unfollow"
}
```
Note: You can only unfollow a user who you followed, if you try to unfollow a allready not following user an error will be thrown **Also not all the likes the user did on the followers posts will be removed as well**


### To like post:
Note:User can like his post and his followings posts only and once liked they can't like again until unliked 
**POST** Request, url = **<serveraddress>/user/post/like**
and in Postman go to Body --> raw mode and enter the following:

```Json
{
    "public_id" : "<public_id_of_image_to_like>",
}
```

### to unlike post:
Note:User can unlike his posts and his followings posts only and once unliked they can't unlike again until liked 

**DELETE** Request, url = **<serveraddress>/user/post/like** 
and in Postman go to Body --> raw mode and enter the following:

```Json
{
    "public_id" : "<public_id_of_image_to_like>",
}
```


### to show the recent posts of the user's following list including his posts sorted by latest first(just like instagram's feed)
**GET** Request, url = **<serveraddress>/user/feed**

will give output in following format:
```Json
{
    "Feed": [
        {
            "caption": "Tesla",
            "likes": 0,
            "public_id": "4afdb79a-5822-428e-b02f-3b8217aa6d0f",
            "url": "https://i.insider.com/60f860760729770012b91c62?width=700",
            "user_name": "techbotgoku"
        },
        {
            "caption": "Car",
            "likes": 0,
            "public_id": "ca9a6ed0-a64c-44dc-9fb8-b6176914b4c9",
            "url": "https://thumbor.forbes.com/thumbor/fit-in/1200x0/filters%3Aformat%28jpg%29/https%3A%2F%2Fspecials-images.forbesimg.com%2Fimageserve%2F5d35eacaf1176b0008974b54%2F0x0.jpg%3FcropX1%3D790%26cropX2%3D5350%26cropY1%3D784%26cropY2%3D3349",
            "user_name": "admin"
        }
    ]
}
```

### to show all top posts from all users sorted by likes if no like it'll show the most recent posts after that

**GET** Request, url = **<serveraddress>/user/trending**


### to show the loggedin user's followers list

**GET** Request, url = **<serveraddress>/user/followers**


### to show the loggedin user's following list

**GET** Request, url = **<serveraddress>/user/following**

### to show people who liked the post(based on image_public id)
**GET** Request, url = **<serveraddress>/user/post/like**
and in Postman go to Body --> raw mode and enter the following:

```Json
{
    "public_id" : "<public_id_of_image>",
}
```

Note: Only the user's followers and the user can see the people who liked the post


### To delete user:

Note: admin can delete any profile and in password he/she needs to enter admin's password in the password field

An user can delete his profile with entering his password in the password field
first,
**DELETE** Request, url = **<serveraddress>/user/<user_to_be_deleted>**
and in Postman go to Body --> raw mode and enter the following:

for normal user:
```Json
{
    "password" : "<password_of_user>",
}
```

for admin:
```Json
{
    "password" : "<password_of_admin>",
}
```

### to give admin level access to any user
Note: Only current users with admin level access can give new users admin level access
**PUT** Request, url = **<serveraddress>/user/<user_to_given_access>**
