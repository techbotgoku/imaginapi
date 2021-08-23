from flask import Flask,request,jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import json
import jwt
import datetime
from functools import wraps
from urllib3 import PoolManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db' #linking the database with an url to the Database
app.config['SECRET_KEY'] = 'gokulnaiduvuppalapati'

db = SQLAlchemy(app)

#user table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key= True)
    public_id = db.Column(db.String(50),unique= True) # to send in token, to randomize and imove security
    user_name = db.Column(db.String(50),unique = True, nullable= False) #the user name is stored in string form with max size of 50characters
    password = db.Column(db.String(80))
    name = db.Column(db.String(50),nullable= False)
    bio = db.Column(db.String(200),nullable= True)
    admin = db.Column(db.Boolean)
    images = db.relationship('Images', backref='users',lazy=True)
    likes = db.relationship('Likes', backref='users',lazy=True)
    def __repr__(self):
        return f"{self.name} - {self.bio}"


#image table
class Images(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer,primary_key= True) #the user id is stored in string form with max size of 50characters
    public_id = db.Column(db.String(50),unique= True)
    user = db.Column(db.String(50), db.ForeignKey('users.public_id'))
    url = db.Column(db.String(2000),nullable= False)
    caption = db.Column(db.String(100),nullable= True)
    likes = db.relationship('Likes', backref='images',lazy=True)


#followers table:
class Follow(db.Model):
    __tablename__ = 'followers'
    id = db.Column(db.Integer,primary_key= True)
    user_id = db.Column(db.String(50),db.ForeignKey('users.public_id'))
    followed_id = db.Column(db.String(50),db.ForeignKey('users.public_id'))
    following_user= db.relationship('User',foreign_keys=[user_id],primaryjoin="User.public_id == Follow.user_id")
    followed_user= db.relationship('User',foreign_keys=[followed_id],primaryjoin="User.public_id == Follow.followed_id")

#likes table
class Likes(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer,primary_key= True)
    image_id = db.Column(db.String(50), db.ForeignKey('images.public_id'))
    user_id = db.Column(db.String(50), db.ForeignKey('users.public_id'))

#for token verification
def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'error message': 'Token is missing!'}),401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'error message': 'Token is invalid!'}),401

        return f(current_user,*args,**kwargs)
    
    return decorated

#to see all users registered on the app
@app.route('/user',methods=['GET'])
@token_required
def get_all_users(current_user):
    users = User.query.all()
    output = []
    followers = 0
    following = 0
    # If admin is trying to view he can see all the details of users, including their hashed passwords, admin level access, public_id etc else a normal user will only see the other details
    if current_user.admin:
        for user in users:
            total_posts = Images.query.filter_by(user=user.public_id).count()
            following = Follow.query.filter_by(user_id=user.public_id).count()
            followers = Follow.query.filter_by(followed_id=user.public_id).count()
            user_data= {'public_id':user.public_id,'user_name':user.user_name,'name':user.name,'password':user.password,'bio':user.bio,'admin':user.admin,'followers':followers,'following':following,'posts':total_posts}
            output.append(user_data)
    else:
        for user in users:
            total_posts = Images.query.filter_by(user=user.public_id).count()
            following = Follow.query.filter_by(user_id=user.public_id).count()
            followers = Follow.query.filter_by(followed_id=user.public_id).count()
            user_data= {'user_name':user.user_name,'name':user.name,'bio':user.bio,'followers':followers,'following':following,'posts':total_posts}
            output.append(user_data)       
    return jsonify({'users':output})

#to see specific user
@app.route('/user/<user_name>',methods=['GET'])
@token_required
def get_one_user(current_user, user_name):
    user = User.query.filter_by(user_name=user_name).first()

    #to verify if the entered user exists
    if not user:
        return jsonify({'error message': 'No such user found'})

    #Getting followers count
    following = Follow.query.filter_by(user_id=user.public_id).count()
    followers = Follow.query.filter_by(followed_id=user.public_id).count()
    
    images = Images.query.filter_by(user=user.public_id)

    posts=[]
    for pic in images:
        user_likes = Likes.query.filter_by(image_id=pic.public_id)
        image_data = {'public_id':pic.public_id,'url':pic.url,'caption':pic.caption,'likes':user_likes.count()}
        posts.append(image_data)
    

    # admin can see any profile's all data but user trying to access can see all details of his profile but can't see all details of other users
    if current_user.admin or current_user.user_name==user_name:
        #getting all the posts of that user
        user_data= {'public_id':user.public_id,'user_name':user.user_name,'name':user.name,'password':user.password,'bio':user.bio,'admin':user.admin,'followers':followers,'following':following,'total_posts':images.count(),'posts':posts}
        return jsonify({'user':user_data})
    
    user_data= {'user_name':user.user_name,'name':user.name,'bio':user.bio,'followers':followers,'following':following,'total_posts':images.count(),'posts':posts}
    return jsonify({'user':user_data})

#to show all posts of current user
@app.route('/user/post', methods=['GET'])
@token_required
def get_images(current_user):
    user = User.query.filter_by(user_name=current_user.user_name).first()
    #to verify if the entered user exists
    if not user:
        return jsonify({'error message': 'No such user found'})
    images = Images.query.filter_by(user=user.public_id)

    if not images:
        return jsonify({'error message': 'No posts'})
    posts=[]
    
    for pic in images:
        user_likes = Likes.query.filter_by(image_id=pic.public_id)
        image_data = {'public_id':pic.public_id,'url':pic.url,'caption':pic.caption,'likes':user_likes.count()}
        posts.append(image_data)
    
    return jsonify({'user':user.user_name,'posts':posts})
        


#to upload a post
@app.route('/user/post', methods=['POST'])
@token_required
def add_images(current_user):
    user = User.query.filter_by(user_name=current_user.user_name).first()
    #to verify if the entered user exists
    if not user:
        return jsonify({'error message': 'No such user found'})
    
    data = request.get_json()
    image_formats = ("image/png", "image/jpeg", "image/gif")
    site = PoolManager().request('GET',data['url'])
    isimage=False
    meta = site.info()  # get header of the http request
    if meta["content-type"] in image_formats:  # check if the content-type is a image
        isimage=True
    
    #if the link is not image an error is returned
    if not isimage:
        return jsonify({"error message":"not of image format"})
        
    image = Images(public_id=str(uuid.uuid4()),user=user.public_id, url=data['url'], caption=data['caption'])
    db.session.add(image)
    db.session.commit()
    return jsonify({user.user_name:"Succussfully posted image" })

#to delete a post
@app.route('/user/post', methods=['DELETE'])
@token_required
def delete_images(current_user):
    user = User.query.filter_by(user_name=current_user.user_name).first()
    #to verify if the entered user exists
    if not user:
        return jsonify({'error message': 'No such user found'})
    
    data = request.get_json()    
    image = Images.query.filter_by(public_id=data['public_id']).first()
    
    #to verify the image exists
    if not image:
        return jsonify({'error message': 'Image not found'})
    if image.user== user.public_id:
        db.session.delete(image)
        db.session.commit()
        return jsonify({user.user_name:"Deleted post" })
    else:
        return jsonify({'error message': 'You have no access to delete this post'})




#to follow
@app.route('/user/<username>/follow', methods=['PUT'])
@token_required
def follow_user(current_user,username):
    
    user = User.query.filter_by(user_name=current_user.user_name).first()
    following = User.query.filter_by(user_name=username).first()
    #to verify if the entered user exists
    if not user or not following:
        return jsonify({'error message': 'No such user found'})
        
    if user.user_name != following.user_name:
        #checking if you are already following user
        if Follow.query.filter_by(user_id=user.public_id,followed_id=following.public_id).count()==0:
            follow_request = Follow(user_id=user.public_id,followed_id=following.public_id)
            db.session.add(follow_request)
            db.session.commit()
            return jsonify({following.user_name:"Now following" })
        else:
            return jsonify({"error message":"Already following"})
    return jsonify({"error message":"can't follow yourself"})

#to unfollow
@app.route('/user/<username>/follow', methods=['DELETE'])
@token_required
def unfollow_user(current_user,username):
    
    user = User.query.filter_by(user_name=current_user.user_name).first()
    following = User.query.filter_by(user_name=username).first()
    #to verify if the entered user exists
    if not user or not following:
        return jsonify({'error message': 'No such user found'})
    
    if user.user_name != following.user_name:
        unfollow_request=Follow.query.filter_by(user_id=user.public_id,followed_id=following.public_id).first()
        #checking if you are already following user
        if not unfollow_request:
            return jsonify({"error message":"Not a follower to unfollow"})
        else:
            db.session.delete(unfollow_request)
            #to remove all likes from the unfollowing user if unfollwed
            images = Images.query.filter_by(user= following.public_id)
            for pic in images:
                unlike = Likes.query.filter_by(image_id=pic.public_id,user_id=user.public_id).first()
                if unlike:
                    db.session.delete(unlike)
            db.session.commit()
            return jsonify({following.user_name:" Now Unfollowed"})
    return jsonify({"error message":"can't unfollow yourself"})


#to like image with public id of image
@app.route('/user/post/like', methods=['POST'])
@token_required
def send_like(current_user):
    user = User.query.filter_by(user_name=current_user.user_name).first()
    #to verify if the entered user exists
    if not user:
        return jsonify({'error message': 'No such user found'})
    data = request.get_json()    
    
    image = Images.query.filter_by(public_id=data['public_id']).first()
    #to verify the image exists
    if not image:
        return jsonify({'error message': 'Image not found'})
    
    #to check if the current user is following the post owner to like the post
    if Follow.query.filter_by(user_id=user.public_id,followed_id=image.user).count()==0 and user.public_id!=image.user:
        return jsonify({"error message":"Not Following user"})

    #to like an image
    if Likes.query.filter_by(image_id=image.public_id,user_id=user.public_id).count()==0:
        like_request = Likes(image_id=image.public_id,user_id=user.public_id)
        db.session.add(like_request)
        db.session.commit()
        return jsonify({image.caption:"Image Liked" })
    else:
        return jsonify({"error message":"Already Liked"})


#to unlike image with public id of image
@app.route('/user/post/like', methods=['DELETE'])
@token_required
def do_unlike(current_user):
    user = User.query.filter_by(user_name=current_user.user_name).first()
    #to verify if the entered user exists
    if not user:
        return jsonify({'error message': 'No such user found'})
    data = request.get_json()    
    image = Images.query.filter_by(public_id=data['public_id']).first()
    #to verify the image exists
    if not image:
        return jsonify({'error message': 'Image not found'})
    
    #to check if the current user is following the post owner to like the post
    if Follow.query.filter_by(user_id=user.public_id,followed_id=image.user).count()==0 and user.public_id!=image.user:
        return jsonify({"error message":"Not Following user"})

    unlike_request = Likes.query.filter_by(image_id=image.public_id,user_id=user.public_id).first()
    #to unlike an image
    if not unlike_request:
        return jsonify({"error message":"Not Liked post to unlike"})
    else:
        db.session.delete(unlike_request)
        db.session.commit()
        return jsonify({image.caption:"Image Unliked" })
        
    
#to show recent feed i.e get most recent posts by the followers
@app.route('/user/feed', methods=['GET'])
@token_required
def get_feed(current_user):
    user = User.query.filter_by(user_name=current_user.user_name).first()
    #to verify if the entered user exists
    if not user:
        return jsonify({'error message': 'No such user found'})
    
    #to get the list of users the current user is following
    following = Follow.query.filter_by(user_id=user.public_id)
    follow=[]
    for x in following:
        follow.append(x.followed_id)
    
    #sorting the images in desecnding order to get the most recent posts
    images=Images.query.order_by(Images.id.desc()).all()
    feed_data=[]
    for pic in images:
        #to check if the current user is following the post owner to show the post in the feed
        if Follow.query.filter_by(user_id=user.public_id,followed_id=pic.user).count()!=0 or user.public_id == pic.user:
            user_likes = Likes.query.filter_by(image_id=pic.public_id)
            user_name= User.query.filter_by(public_id=pic.user).first()
            image_data = {'public_id':pic.public_id,'url':pic.url,'caption':pic.caption,'likes':user_likes.count(),'user_name':user_name.user_name}
            feed_data.append(image_data)
    
    if len(feed_data)==0:
        return jsonify({'error message': 'Follow users / upload images to see posts'})

    return jsonify({"Feed":feed_data})



#to show all top posts sorted by likes if no like it'll show the most recent after that
@app.route('/user/trending', methods=['GET'])
@token_required
def get_top_posts(current_user):
    user = User.query.filter_by(user_name=current_user.user_name).first()
    #to verify if the entered user exists
    if not user:
        return jsonify({'error message': 'No such user found'})
    
    #to show the top posts sorted posts
    likequery= db.session.query(Likes.image_id,func.count('*').label('like_count')).group_by(Likes.image_id).subquery()
    images= db.session.query(Images,likequery.c.like_count).join((likequery, Images.public_id==likequery.c.image_id)).order_by(likequery.c.like_count.desc())
    like_data=[]
    for pic,likes in images:
        user_name= User.query.filter_by(public_id=pic.user).first()
        image_data = {'public_id':pic.public_id,'url':pic.url,'caption':pic.caption,'likes':likes,'user_name':user_name.user_name}
        like_data.append(image_data)
    #to show the most recent posts when 0 likes:
    images=Images.query.order_by(Images.id.desc()).all()
    for pic in images:
        if Likes.query.filter_by(image_id= pic.public_id).count() ==0:
            user_name= User.query.filter_by(public_id=pic.user).first()
            image_data = {'public_id':pic.public_id,'url':pic.url,'caption':pic.caption,'likes':0,'user_name':user_name.user_name}
            like_data.append(image_data) 

    if len(like_data)==0:
        return jsonify({'error message': 'Follow users / upload images to see posts'})

    return jsonify({"Feed":like_data})  

# to show the users followers
@app.route('/user/followers', methods=['GET'])
@token_required
def get_followers(current_user):
    user = User.query.filter_by(user_name=current_user.user_name).first()
    #to verify if the entered user exists
    if not user:
        return jsonify({'error message': 'No such user found'})
    followers = Follow.query.filter_by(followed_id= user.public_id)
    foll=[]
    for f in followers:
        follower = User.query.filter_by(public_id=f.user_id).first()
        foll.append({'user_name':follower.user_name,'name':follower.name})
    if len(foll)==0:
        return jsonify({'followers':'No followers'})
    return jsonify({'followers':foll})

# to show the users followers
@app.route('/user/following', methods=['GET'])
@token_required
def get_following(current_user):
    user = User.query.filter_by(user_name=current_user.user_name).first()
    #to verify if the entered user exists
    if not user:
        return jsonify({'error message': 'No such user found'})
    following = Follow.query.filter_by(user_id= user.public_id)
    foll=[]
    for f in following:
        follower = User.query.filter_by(public_id=f.followed_id).first()
        foll.append({'user_name:':follower.user_name,'name':follower.name})
    if len(foll)==0:
        return jsonify({'following':'No following'})
    return jsonify({'following':foll})   
    
#to show list of users who liked current post
@app.route('/user/post/like', methods=['GET'])
@token_required
def get_liked_info(current_user):
    user = User.query.filter_by(user_name=current_user.user_name).first()
    #to verify if the entered user exists
    if not user:
        return jsonify({'error message': 'No such user found'})
    data = request.get_json()    
    image = Images.query.filter_by(public_id=data['public_id']).first()
    #to verify the image exists
    if not image:
        return jsonify({'error message': 'Image not found'})
    
    #to check if the current user is following the post owner to like the post
    if Follow.query.filter_by(user_id=user.public_id,followed_id=image.user).count()==0 and image.user!=user.public_id:
        return jsonify({"error message":"Not Following user"})
    
    likes = Likes.query.filter_by(image_id= image.public_id)
    lik=[]
    for l in likes:
        follower = User.query.filter_by(public_id=l.user_id).first()
        lik.append({'user_name:':follower.user_name,'name':follower.name})
    if len(lik)==0:
        return jsonify({'liked_by':'None'})
    return jsonify({'liked_by':lik})   


#create user
@app.route('/user',methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    if data['user_name'] == 'admin':
        new_user = User(public_id=str(uuid.uuid4()),user_name=data['user_name'],name=data['name'],password=hashed_password,bio=data['bio'],admin=True)
    else:
        new_user = User(public_id=str(uuid.uuid4()),user_name=data['user_name'],name=data['name'],password=hashed_password,bio=data['bio'],admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'Successfully added user':new_user.user_name})


#give admin level access
@app.route('/user/<username>',methods=['PUT'])
@token_required
def promote_user(current_user, username):
    if not current_user.admin:
        return jsonify({'error message': 'Admin level access required, entry denied'}),401
    user = User.query.filter_by(user_name=username).first()
    if not user:
        return jsonify({'error message': 'No such user found'})
    user.admin=True
    db.session.commit()
    return jsonify({user.user_name:"Given admin level access"})


#delete user
@app.route('/user/<username>',methods=['DELETE'])
@token_required
def delete_user(current_user, username):
    #only if the user enters the password he can delete profile, 
    #but admin can delete all profile without password but will require admin password
    user = User.query.filter_by(user_name=current_user.user_name).first()
    if not user :
        return jsonify({'error message': 'Inavid user'})
    
    if not user.admin:
        if username != user.user_name:
            return jsonify({'error message': 'Invalid username or dont have admin level access to delete profile'})
        
        data = request.get_json()
        if check_password_hash(user.password,data['password']):
            db.session.delete(user)
            #to remove all following and followers list
            Follow.query.filter_by(user_id=user.public_id).delete()
            Follow.query.filter_by(followed_id=user.public_id).delete()


            #to delete all posts and remove other likes from posts
            images = Images.query.filter_by(user=user.public_id)
            for pic in images:
                Likes.query.filter_by(image_id=pic.public_id).delete()
            images.delete()

            #to remove all the users likes from the table
            Likes.query.filter_by(user_id=user.public_id).delete()
            db.session.delete(user)
            db.session.commit()
            return jsonify({user.user_name:"Profile Deleted"})
        else:
            return jsonify({user.user_name:"Incorrect password"})
    

    #when admin is tryng to delete an user
    else:
        enduser = User.query.filter_by(user_name=username).first()
        if not enduser:
            return jsonify({'error message': 'Inavid user'})
        
        data = request.get_json()
        #checking if admin passsword is correct
        if check_password_hash(user.password,data['password']):
            
            #to remove all following and followers list
            Follow.query.filter_by(user_id=enduser.public_id).delete()
            Follow.query.filter_by(followed_id=enduser.public_id).delete()


            #to delete all posts and remove other likes from posts
            images = Images.query.filter_by(user=enduser.public_id)
            
            for pic in images:
                Likes.query.filter_by(image_id=pic.public_id).delete()
            
            images.delete()

            #to remove all the users likes from the table
            Likes.query.filter_by(user_id=enduser.public_id).delete()
            db.session.delete(enduser)
            db.session.commit()
            return jsonify({enduser.user_name:"Profile Deleted"})
        else:
            return jsonify({user.user_name:"Incorrect password"})

#to login
@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Invalid Login credentials',401,{'WWW-Authenticate':'Basic realm="Login Required!"'})
    user = User.query.filter_by(user_name=auth.username).first()
    if not user:
        return make_response('Invalid Login credentials',401,{'WWW-Authenticate':'Basic realm="No user found"'})
    if check_password_hash(user.password,auth.password):
        token = jwt.encode({'public_id':user.public_id,'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=60)},app.config['SECRET_KEY'],algorithm='HS256')
        return jsonify({'token':token})
    return make_response('Invalid Login credentials',401,{'WWW-Authenticate':'Basic realm="Wrong Password"'})

if __name__ == '__main__':
    app.run(debug=True)