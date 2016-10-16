from donkidik.models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from donkidik.decorators import api_login_required


# ==============================GET======================================
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


@csrf_exempt
def get_sessions(request):
    ret = {'status': 'FAIL'}
    if request.method == 'GET':
        sessions = []
        for session in Session.objects.all().order_by('end_ts'):
            sessions.append(session.to_json(request.user))

        ret['status'] = 'OK'
        ret['sessions'] = sessions

    return JsonResponse(ret)


@csrf_exempt
@api_login_required
def get_one_post(request, post_id):
    ret = {'status': 'FAIL'}
    if not request.user.is_authenticated():
        ret['error'] = "User is not logged in"
        return JsonResponse(ret)
    else:
        ret['post'] = []
        p = Post.get_by_id(post_id)
        if p:
            ret['post'].append(p.to_json(user=request.user))
            ret['status'] = 'OK'
    return JsonResponse(ret)


@csrf_exempt
@api_login_required
def get_spots(request):
    ret = {'status': 'FAIL', 'spots': []}
    spots = Spot.objects.all()
    for s in spots:
        ret['spots'].append({
            'id': int(s.id),
            'name': s.name,
            'long': s.longtitude,
            'lat': s.latitude
        })
    ret['status'] = 'OK'
    return JsonResponse(ret)


# ================================USER===========================================
@csrf_exempt
def login_req(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            ret['error'] = 'invalid_creds'

        user = authenticate(username=email, password=password)
        if user:
            ret['status'] == 'OK'
            # GAL - i think this next line was missing here
            login(request, user)
        else:
            ret['error'] = 'invalid_creds'

    return JsonResponse(ret)


@csrf_exempt
def logout_req(request):
    logout(request)
    return HttpResponseRedirect('/')


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

        if request.FILES and 'pic' in request.FILES:
            p = request.user.profile
            pic_file = request.FILES['pic']
            filename = p.unique_image_path()
            print "saving image to {}".format(filename)

            destination = open(filename, 'wb+')
            for chunk in avatar_file.chunks():
                destination.write(chunk)
            destination.close()
            print "saved"

            p.pic = 'static/avatars/{}/{}'.format(p.user.id, filename[filename.rfind('/') + 1:])
            p.save()

        if to_save:
            request.user.save()

        ret['status'] = 'OK'
        ret['user'] = p.to_json(request.user)
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


# ====================================POST====================================================

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
def post_update(request):
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
        post = Post.get_by_id(post_id)
        if not post:
            ret['error'] = 'invalid_post'
            return JsonResponse(ret)

        (success, err) = post.update(user, post_type, text=text, meta_data=meta_data)
        if sucess:
            ret['ststus'] = 'OK'
            ret['post_id'] = post_id
        else:
            ret['error'] = err

        return JsonResponse(ret)


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

        (success, err) = post.upvote(request.user)
        if success:
            ret['status'] = 'OK'
        else:
            ret['error'] = err

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

        (success, err) = post.downvote(request.user)
        if success:
            ret['status'] = 'OK'
        else:
            ret['error'] = err

    return JsonResponse(ret)


# =====================================COMMENT=======================================
@csrf_exempt
@api_login_required
def add_comment(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        comment_type = request.POST.get('comment_on')
        object_id = request.POST.get('obj_id')
        text = request.POST.get('text')

        if comment_type == 'post':
            comment_type = COMMENT_ON_POST
        elif comment_type == 'comment':
            comment_type = COMMENT_ON_COMMENT
        else:
            ret['error'] = 'invalid_comment_type'
            return JsonResponse(ret)

        (comment, err) = Comment.create(request.user, text, comment_type, object_id)
        if err is None:
            ret['status'] = 'OK'
            ret['comment_id'] = c.pk
        else:
            ret['error'] = err

    return JsonResponse(ret)


@csrf_exempt
@api_login_required
def remove_comment(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        comment = Comment.get_by_id(comment_id)
        if comment:
            (success, err) = comment.remove(request.user)
            if success:
                ret['status'] = 'OK'
            else:
                ret['error'] = err

    return JsonResponse(ret)


@csrf_exempt
@api_login_required
def update_comment(request):
    ret = {'status': 'FAIL'}
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        text = request.POST.get('text')
        comment = Comment.get_by_id(comment_id)
        if comment:
            (success, err) = comment.update(request.user, text)
            if success:
                ret['status'] = 'OK'
            else:
                ret['error'] = err

    return JsonResponse(ret)

# ====================================FOLLOW========================================
# TODO
# ====================================SESSION=======================================
