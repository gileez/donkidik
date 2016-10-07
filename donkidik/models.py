from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

POST_TYPE_GENERAL = 1
POST_TYPE_REPORT = 2
# POST_TYPE_FORCAST = 3
POST_TYPES = [
    (POST_TYPE_GENERAL, 'General'),
    (POST_TYPE_REPORT, 'Report'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', null=False, primary_key=True)
    pic = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        db_table = 'user_profile'

    def __str__(self):
        return "{} profile".format(self.user.email)


class Post(models.Model):
    user = models.ForeignKey(User, related_name='posts')
    post_type = models.IntegerField(choices=POST_TYPES, default=POST_TYPE_GENERAL, blank=False, null=False, db_index=True)
    text = models.TextField()
    score = models.IntegerField(default=0)
    upvotes = models.ManyToManyField(User, related_name='upvoted_posts')
    downvotes = models.ManyToManyField(User, related_name='downvoted_posts')
    created_ts = models.DateTimeField(default=datetime.now)
    last_action_ts = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'post'

    def __str__(self):
        return "{} post".format(self.user.email)

    @staticmethod
    def create(user, post_type, text=None, meta_data=None):

        if post_type not in [POST_TYPE_GENERAL, POST_TYPE_REPORT]:
            return None

        post = Post(user=user, post_type=post_type)
        if text:
            post.text = text

        elif post_type == POST_TYPE_REPORT:
            spot_id = meta_data['spot_id'] if 'spot_id' in meta_data else None
            knots = meta_data['knots'] if 'knots' in meta_data else None
            # TODO: gust

            if not spot_id or not knots:
                return None

            try:
                spot = Spot.objects.get(id=spot_id)
            except:
                return None

            pm = PostMeta(post=post, spot=spot, knots=knots)
            pm.save()

        post.save()
        return post


class PostMeta(models.Model):
    post = models.OneToOneField('Post', related_name='meta', primary_key=True)
    knots = models.IntegerField(blank=True, null=True)
    gust = models.IntegerField(blank=True, null=True)
    spot = models.ForeignKey('Spot', related_name='posts_metas', blank=True, null=True)

    class Meta:
        db_table = 'post_meta'

    def __str__(self):
        return "Post {} meta".format(self.post)


class Comment(models.Model):
    post = models.ForeignKey('Post', related_name='comments', blank=False, null=False, db_index=True)
    user = models.ForeignKey(User, related_name='comments')
    text = models.TextField()
    created_ts = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'comment'

    def __str__(self):
        return "{} comment".format(self.post)


class Spot(models.Model):
    name = models.CharField(max_length=256, unique=True)
    latitude = models.CharField(max_length=128)
    longitude = models.CharField(max_length=128)

    class Meta:
        db_table = 'spot'

    def __str__(self):
        return "Spot {}".format(self.name)


class Session(models.Model):
    # TODO
    pass


class Forecast(models.Model):
    # TODO
    pass
