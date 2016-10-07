from donkidik.models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from donkidik.decorators import api_login_required

# HOME VIEW


@csrf_exempt
def get_feed(request):
    ret = {'status': 'FAIL'}
    if request.method == 'GET':
        posts = []
        for post in Post.objects.all().order_by('-last_action_ts')[:50]:
            posts.append(post.to_json(request.user))

        ret['status'] = 'OK'
        ret['posts'] = posts

    return JsonResponse(ret)

# USER


@csrf_exempt
def user_create(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not first_name or not last_name or not email or not password:
            ret['error'] = 'missing_params'
            return JsonResponse(ret)

        try:
            User.objects.get(email=email)
            ret['error'] = 'user_exists'
            return JsonResponse(ret)
        except:
            pass

        user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
        if user:
            login(request, user)
            ret['status'] = 'OK'
        else:
            ret['error'] = 'internal_error'

    return JsonResponse(ret)


@csrf_exempt
def authenticate_user(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            ret['error'] = 'invalid_creds'

        user = authenticate(username=email, password=password)
        if user:
            ret['status'] == 'OK'
        else:
            ret['error'] = 'invalid_creds'

    return JsonResponse(ret)


@csrf_exempt
@api_login_required
def user_update(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        new_first_name = request.POST.get('first_name')
        new_last_name = request.POST.get('last_name')
        new_email = request.POST.get('email')
        new_password = request.POST.get('password')

        to_save = False
        if new_first_name:
            request.user.first_name = new_first_name
            to_save = True

        if new_last_name:
            request.user.last_name = new_last_name
            to_save = True

        if new_email:
            request.user.email = new_email
            request.user.username = new_email
            to_save = True

        if new_password:
            request.user.set_password(new_password)

        if to_save:
            request.user.save()

        ret['status'] = 'OK'

    return JsonResponse(ret)


@csrf_exempt
@api_login_required
def user_delete(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        try:
            User.objects.get(id=request.user.id).delete()
            ret['status'] = 'OK'
        except Exception, e:
            ret['error'] = e.message

    return JsonResponse(ret)


# POST

@csrf_exempt
@api_login_required
def post_create(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        post_type = request.POST.get('post_type')
        text = request.POST.get('text')
        spot_id = request.POST.get('spot_id')
        knots = request.POST.get('knots')

        if not post_type:
            ret['error'] = 'missing_args'
            return JsonResponse(ret)

        meta_data = {
            "spot_id": spot_id,
            "knots": knots
        }
        post = Post.create(user, post_type, text=text, meta_data=meta_data)
        if post:
            ret['status'] = 'OK'
            ret['post_id'] = post.id
        else:
            ret['error'] = 'invalid_args'

    return JsonResponse(ret)


@csrf_exempt
@api_login_required
def post_comment_add(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        text = request.POST.get('text')

        try:
            post = Post.objects.get(id=post_id)
        except:
            ret['error'] = 'invalid_post'
            return JsonResponse(ret)

        if not text:
            ret['error'] = 'missing_args'
            return JsonResponse(ret)

        c = Comment(post=post, user=request.user, text=text)
        c.save()
        ret['status'] = 'OK'

    return JsonResponse(ret)


@csrf_exempt
@api_login_required
def post_update(request):
    # TODO
    pass


@csrf_exempt
@api_login_required
def post_delete(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        post_id = request.POST.get('post_id')

        try:
            post = Post.objects.get(id=post_id)
        except:
            ret['error'] = 'invalid_post'
            return JsonResponse(ret)

        if post.user.id != request.user.id:
            ret['error'] = 'permission_denied'
            return JsonResponse(ret)

        post.delete()
        ret['status'] = 'OK'

    return JsonResponse(ret)


@csrf_exempt
@api_login_required
def post_upvote(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        post_id = request.POST.get('post_id')

        try:
            post = Post.objects.get(id=post_id)
        except:
            ret['error'] = 'invalid_post'
            return JsonResponse(ret)

        if post.user.id == request.user.id:
            # can't vote to yourself
            ret['error'] = 'own_post'
            return JsonResponse(ret)

        if post.upvotes.filter(id=request.user.id).exists():
            ret['error'] = 'already_upvoted'
            return JsonResponse(ret)

        if post.downvotes.filter(id=request.user.id).exists():
            post.downvotes.remove(request.user)

        post.upvotes.add(request.user)
        ret['status'] = 'OK'

    return JsonResponse(ret)


@csrf_exempt
@api_login_required
def post_downvote(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        post_id = request.POST.get('post_id')

        try:
            post = Post.objects.get(id=post_id)
        except:
            ret['error'] = 'invalid_post'
            return JsonResponse(ret)

        if post.user.id == request.user.id:
            # can't vote to yourself
            ret['error'] = 'own_post'
            return JsonResponse(ret)

        if post.downvotes.filter(id=request.user.id).exists():
            ret['error'] = 'already_downvoted'
            return JsonResponse(ret)

        if post.upvotes.filter(id=request.user.id).exists():
            post.upvotes.remove(request.user)

        post.downvotes.add(request.user)
        ret['status'] = 'OK'

    return JsonResponse(ret)
