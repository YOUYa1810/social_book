from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from itertools import chain
from django.db.models import Q

""" 
user home page 
"""
@login_required(login_url='signin')
def index(request):
    user_profile = Profile.objects.get(user=request.user)
    feed = []
    
    # List following user's posts
    user_following = FollowersCount.objects.filter(follower=request.user)
    for user in user_following:
        feed_lists = Post.objects.filter(user=user.user.username)
        feed.append(feed_lists)   
    feed_list = list(chain(*feed)) 
    # suggest unfollowed users
    user_following = FollowersCount.objects.filter(follower=request.user)
    suggestions_username_list = User.objects.filter(~Q(user__in=user_following))   
    suggestions_username_profile_list = Profile.objects.filter(user__in=suggestions_username_list).filter(~ Q(user=request.user))
    return render(request, 'index.html',  {'user_profile': user_profile, 'posts': feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list})


"""
upload a new post
"""
@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')
        
    else:
        return redirect('/')

"""
follow and unfollow other users
"""
@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':   
        follower = User.objects.get(username=request.POST['follower'])
        user = User.objects.get(username=request.POST['user'])
        if FollowersCount.objects.filter(user=user, follower=follower).first():
            # unfollow           
            delete_follower = FollowersCount.objects.get(user=user, follower=follower)
            delete_follower.delete()
            return redirect('/profile/'+user.username)
        else: 
            # follow
            new_follower = FollowersCount.objects.create(user=user, follower=follower)
            new_follower.save()
            return redirect('/profile/'+user.username)

    else:
        return redirect('/')

"""
search user by username
"""   
@login_required(login_url='signin')
def search(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        # filter user result
        username = request.POST.get('username')
        username_object = User.objects.filter(username__icontains=username)
        username_profile_list = []
        for user in username_object:
            profile_list = Profile.objects.filter(user=user)
            username_profile_list.append(profile_list)
  
    username_profile_list = list(chain(*username_profile_list))     
    return render(request, 'search.html',  {'user_profile': user_profile, 'username_profile_list': username_profile_list})

"""
liske and cancel like function
""" 
@login_required(login_url='signin')
def like_post(request):
    user = request.user
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post=post, user=user).first()
    if like_filter == None:
        # like
        new_like = LikePost.objects.create(post=post, user=user)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        # cancel like
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')

"""
user profile detail
"""
@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=user_object)
    # filter followes info
    button_text = 'Follow'
    if FollowersCount.objects.filter(user=user_object, follower=request.user).first():
        button_text = 'Unfollow'
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': len(user_posts),
        'button_text': button_text, 
        'user_followers': FollowersCount.objects.filter(user=user_object).count(),
        'user_following': FollowersCount.objects.filter(follower=user_object).count(),
        }
    return render(request, 'profile.html', context)
        

"""
edit user's profile
"""    
@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        image = user_profile.profileimg

        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            
        bio = request.POST['bio']
        location = request.POST['location']
        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        return redirect('settings')
    
    # return user profile info to front page
    return render(request, 'setting.html', {'user_profile': user_profile})

"""
new user sign up
"""
def signup(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password != password2:
            messages.info(request, 'Password are not matching')
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email is taken')
            return redirect('signup')
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username is taken')
            return redirect('signup')
                    
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        # log user in and redirect to setting page
        user_login = auth.authenticate(username=username, password=password)
        auth.login(request, user_login)
            
        # create a profile object for the new user
        user_model = User.objects.get(username=username)
        new_profile = Profile.objects.create(user= user_model,id_user=user_model.id)
        new_profile.save()
        return redirect('settings')
            
    
    else:
        return render(request, 'signup.html')
   

"""
user sign in 
"""
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Credentials invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')
    
    
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')