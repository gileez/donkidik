from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
import pytz


POST_TYPE_GENERAL = 1
POST_TYPE_REPORT = 2
# POST_TYPE_FORCAST = 3
POST_TYPES = [
    (POST_TYPE_GENERAL, 'General'),
    (POST_TYPE_REPORT, 'Report'),
]
# ---------------------------------------------
SESSION_TYPE_BIGKITES = 1
SESSION_TYPE_REGULAR = 2
SESSION_TYPE_SMALLKITES = 3

SESSION_TYPES = [
    (SESSION_TYPE_BIGKITES, 'BigKites'),
    (SESSION_TYPE_REGULAR, 'Regular'),
    (SESSION_TYPE_SMALLKITES, 'SmallKites'),
]
# --------------------------------------------
# SCORES
EVENT_UPVOTE_SCORE = 2
EVENT_DOWNVOTE_SCORE = -1
EVENT_WINDREPORT_SCORE = 5


@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
    # make sure its not an update
    if kwargs.get('created', False):
        UserProfile.objects.get_or_create(user=kwargs.get('instance'))
    return


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', null=False, primary_key=True)
    pic = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        db_table = 'user_profile'

    def __str__(self):
        return "{} profile".format(self.user.username)

    def get_score(self):
        ret = 0
        for s in self.user.score_events.all():
            ret += s.score
        if ret < 0:  # no negative score...
            ret = 0
        return ret

    def update(self, data):
        # TODO
        pass


class Post(models.Model):
    user = models.ForeignKey(User, related_name='posts')
    post_type = models.IntegerField(choices=POST_TYPES, default=POST_TYPE_GENERAL, blank=False, null=False, db_index=True)
    text = models.TextField()
    upvotes = models.ManyToManyField(User, related_name='upvoted_posts', through='PostUpVote', blank=True)
    downvotes = models.ManyToManyField(User, related_name='downvoted_posts', through='PostDownVote', blank=True)
    created_ts = models.DateTimeField(default=datetime.now)
    last_action_ts = models.DateTimeField(default=datetime.now)
    related_session = models.ForeignKey('Session', models.SET_NULL, related_name='related_posts', blank=True, null=True)

    class Meta:
        db_table = 'post'

    def __str__(self):
        return "{} post".format(self.user.username)

    def get_score(self):
        return self.upvotes.count() - self.downvotes.count()

    def to_json(self, user):
        uv = [u.id for u in self.upvotes.all()]
        dv = [u.id for u in self.downvotes.all()]
        ret = {
            'post_id': self.id,
            'post_type': self.post_type,
            'post_score': self.get_score(),
            'user': {
                'name': self.user.first_name,
                'id': self.user.id,
                'score': self.user.profile.get_score(),
                'pic': self.user.profile.pic
            },
            'text': self.text,
            'created_ts': self.created_ts,
            'last_action_ts': self.last_action_ts,
            'time': '',
            'seconds_passed': 0,
            'comments': [c.to_json() for c in self.comments.all()],
            'upvotes': uv,
            'downvotes': dv,
            'is_owner': user.id == self.user.id,
            'is_upvoted': user.id in uv,
            'is_downvoted': user.id in dv,
        }

        if hasattr(self, 'meta'):
            # there is a meta record for this post
            ret.update({
                'knots': self.meta.knots,
                'gust': self.meta.gust,
                'spot': self.meta.spot.name if hasattr(self.meta, 'spot') and self.meta.spot else None,
                'spot_id': self.meta.spot.pk if hasattr(self.meta, 'spot') and self.meta.spot else None,
            })

        return ret

    @staticmethod
    def create(user, post_type, text=None, meta_data=None):

        if post_type not in [POST_TYPE_GENERAL, POST_TYPE_REPORT]:
            return None

        post = Post(user=user, post_type=post_type)
        if text:
            post.text = text

        if post_type == POST_TYPE_REPORT:
            spot_id = meta_data['spot_id'] if 'spot_id' in meta_data else None
            knots = meta_data['knots'] if 'knots' in meta_data else None
            gust = meta_data['gust'] if 'gust' in meta_data else None

            if not spot_id or not knots:
                return None

            try:
                spot = Spot.objects.get(id=spot_id)
            except:
                return None

            pm = PostMeta(post=post, spot=spot, knots=knots, gust=gust)
            pm.save()

            # store ScoreEvent
            ScoreEvent.create(post)

        post.save()
        return post

    def update(self, user, post_type, text, meta_data=None):
        if post_type not in [POST_TYPE_GENERAL, POST_TYPE_REPORT]:
            return False
        else:
            self.post_type = post_type
        if text:
            self.text = text
        if post_type == POST_TYPE_GENERAL:
            # GAL need some clarification here
            post.meta.delete()
            post.meta = None
        elif post_type == POST_TYPE_REPORT:
            spot_id = meta_data['spot_id'] if 'spot_id' in meta_data else None
            knots = meta_data['knots'] if 'knots' in meta_data else None
            gust = meta_data['gust'] if 'gust' in meta_data else None

            if not spot_id or not knots:
                return None
            if not (hasattr(self, 'meta') and spot_id == post.meta.spot.pk):
                # need to replace the spot instance
                try:
                    spot = Spot.objects.get(id=spot_id)
                except:
                    return None
            if hasattr(self, 'meta'):
                # simply update the meta fiels
                self.meta.spot = spot
                self.meta.knots = knots
                self.meta.save()
            else:
                # need to create a PostMeta
                pm = PostMeta(post=self, spot=spot, knots=knots, gust=gust)
                pm.save()

        self.save()
        return True

    def remove(self, user):
        if not (user.pk == self.user.pk or user.is_admin):
            # user has no permission to delete this post
            return False
        self.delete()
        return True

    def upvote(self, user):
        if self.user.id == user.id:
            return (False, 'own_post')

        if self.upvotes.filter(id=user.id).exists():
            # GAL should i make a cancel_upvote function too?
            return (False, 'already_upvoted')

        # store a new upvote action
        uv = PostUpVote(post=self, user=user)
        uv.save()

        # store ScoreEvent
        ScoreEvent.create(uv)
        return (True, None)

    def downvote(self, user):

        if self.user.id == user.id:
            return (False, 'own_post')

        if self.downvotes.filter(id=user.id).exists():
            return (False, 'already_downvoted')

        # store a new downvote action
        dv = PostDownVote(post=self, user=user)
        dv.save()

        # store ScoreEvent
        ScoreEvent.create(dv)
        return (True, None)

    def remove_comment(self, user, cid):
        if not (user or cid):
            return (False, "Missing Data")
        try:
            c = self.comments.get(pk=cid)
        except:
            return (False, "Comment Not Found")
        return c.remove(user)

    @staticmethod
    def get_by_id(pid):
        try:
            return Post.objects.get(pk=pid)
        except:
            return None


class PostUpVote(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    created_ts = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'post_upvotes'

    def __str__(self):
        return "[{}] (+v) {} --> {}".format(self.id, self.user.username, self.post)


class PostDownVote(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    created_ts = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'post_downvotes'

    def __str__(self):
        return "[{}] (-v) {} --> {}".format(self.id, self.user.username, self.post)


class PostMeta(models.Model):
    post = models.OneToOneField('Post', related_name='meta', primary_key=True)
    knots = models.IntegerField(blank=True, null=True)
    gust = models.IntegerField(blank=True, null=True)
    spot = models.ForeignKey('Spot', related_name='posts_metas', blank=True, null=True)

    class Meta:
        db_table = 'post_meta'

    def __str__(self):
        return "Post {} meta".format(self.post)


class ScoreEvent(models.Model):
    upvote_event = models.ForeignKey('PostUpVote', blank=True, null=True, db_index=True)
    downvote_event = models.ForeignKey('PostDownVote', blank=True, null=True, db_index=True)
    post_event = models.ForeignKey('Post', blank=True, null=True, db_index=True)
    scored_user = models.ForeignKey(User, related_name='score_events')
    score = models.IntegerField(default=0, blank=False, null=False)
    created_ts = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'score_event'

    def __str__(self):
        return "ScoreEvent {} {}{}".format(self.scored_user, '+' if self.score >= 0 else '-', self.score)

    @staticmethod
    def create(event):
        score_event = None
        if isinstance(event, PostUpVote):
            # remove user downvotes & related score events
            PostDownVote.objects.filter(post=event.post, user=event.user).delete()
            # create ScoreEvent
            score_event = ScoreEvent(upvote_event=event, scored_user=event.post.user, score=EVENT_UPVOTE_SCORE)
        elif isinstance(event, PostDownVote):
            # remove user upvotes & related score events
            PostUpVote.objects.filter(post=event.post, user=event.user).delete()
            # create ScoreEvent
            score_event = ScoreEvent(downvote_event=event, scored_user=event.post.user, score=EVENT_DOWNVOTE_SCORE)
        elif isinstance(event, Post):
            if event.post_type == POST_TYPE_REPORT:
                # create ScoreEvent
                score_event = ScoreEvent(post_event=event, scored_user=event.user, score=EVENT_WINDREPORT_SCORE)

        if score_event:
            score_event.save()
            return score_event
        return None


class Comment(models.Model):
    post = models.ForeignKey('Post', related_name='comments', blank=False, null=False, db_index=True)
    user = models.ForeignKey(User, related_name='comments')
    text = models.TextField()
    created_ts = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'comment'

    def __str__(self):
        return "{} comment".format(self.post)

    def to_json(self):
        return {
            'text': self.text,
            'date': self.created_ts,
            'time': '',
            'user_name': self.user.first_name,
            'user_id': self.user.pk,
            'comment_id': self.pk,
        }

    @staticmethod
    def create(user, text, pid):
        if not (user and text):
            return False, "Missing data"
        try:
            p = Post.objects.get(pk=pid)
        except:
            return False, "Post not found"
        try:
            c = Comment(user=user, text=text, post=p).save()
            p.comments.add(c)
        except:
            return False, "Failed creating the comment"
        return c

    def remove(self, user):
        if not (user):
            return (False, "Missing Data")
        if not (user.pk == self.user.pk or user.is_admin):
            return (False, "Permission Denied")
        self.delete()
        return (True, None)


class Spot(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.CharField(max_length=128)
    longitude = models.CharField(max_length=128)

    class Meta:
        db_table = 'spot'

    def __str__(self):
        return "Spot {}".format(self.name)

    # GAL is this function really necessary? can't we just make an instance from api?
    # @staticmethod
    # def create(name, latitude, longtitude):
    #     spot = Spot(name=name, latitude=latitude, longtitude=longtitude)
    #     spot.save()
    #     return spot


@receiver(post_save, sender=PostMeta)
def sessionManager(sender, **kwargs):
    # make sure its a report
    post = kwargs.get('instance').post
    if post.post_type != POST_TYPE_REPORT:
        return
    # TODO should search for a session from today. don't want to open two sessions
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0)
    today_end = now.replace(hour=23, minute=59, second=59)
    session = Session.objects.filter(spot=post.meta.spot, created_ts__gte=today_start, created_ts__lte=today_end).first()
    if session:
        # theres an ongoing session. lets update it
        session.update(post)
    else:
        # create a session
        Session.create(post)
    return


def get_end_ts():
    # TODO handle timezone properly
    return datetime.now().replace(tzinfo=pytz.UTC, hour=23, minute=59, second=59)


class Session(models.Model):
    spot = models.ForeignKey('Spot', related_name='sessions', blank=False, null=True)
    owner = models.ForeignKey(User, related_name='own_sessions', blank=True, null=True)
    users = models.ManyToManyField(User, related_name='sessions', blank=True)
    intended_users = models.ManyToManyField(User, related_name='intented_sessions', blank=True)
    created_ts = models.DateTimeField(default=datetime.now)
    end_ts = models.DateTimeField(default=get_end_ts)
    closed_by = models.ForeignKey(User, related_name='closed_sessions', blank=True, null=True)
    # TODO future_ts for forecasts
    session_type = models.IntegerField(choices=SESSION_TYPES, default=SESSION_TYPE_REGULAR, blank=False, null=False)
    active = models.BooleanField(default=False)

    class Meta:
        db_table = 'session'

    def __str__(self):
        return "Session {} at {}".format(self.id, self.spot.name)

    @staticmethod
    def create(post):
        if post.meta.knots < 8:
            return None
        if post.meta.knots < 15:
            session_type = SESSION_TYPE_BIGKITES
        elif post.meta.knots > 25:
            session_type = SESSION_TYPE_SMALLKITES
        s = Session(spot=post.meta.spot)
        s.owner = post.user
        s.session_type = session_type
        s.active = True
        s.save()
        # GAL: must save before many to many modifications. anyway to avoid this?
        s.users.add(post.user)
        s.related_posts.add(post)
        s.save()
        return s

    def update(self, post):
        session_type = self.session_type
        self.active = True
        if post.meta.knots < 8:
            # this session should end
            self.end_ts = datetime.now()
            self.active = False
            self.closed_by = post.user
        elif post.meta.knots < 15:
            session_type = SESSION_TYPE_BIGKITES
        elif post.meta.knots > 25:
            session_type = SESSION_TYPE_SMALLKITES
        else:
            session_type = SESSION_TYPE_REGULAR
        self.users.add(post.user)
        self.related_posts.add(post)
        self.session_type = session_type
        self.save()
        return self

    def add_user(self, user):
        # GAL - could this function create a race on the session due to many people trying to add themselves to the session?
        # adds user to this session and removes him from intended users if was there
        if self.intended_users.filter(pk=user.pk):
            # TODO check if this could have been done with the object itself
            self.intended_users.delete(user)
        self.users.add(user)
        self.save()
        return

    def remove_user(self, user):
        # removes user from this session
        self.users.remove(user)
        self.save()
        return

    def add_intended_user(self, user):
        if self.users.filter(pk=user.pk):
            self.users.remove(user)
        self.intended_users.add(user)
        self.save()
        return

    def remove_intended_user(self, user):
        self.intended_users.remove(user)
        self.save()
        return

    def to_json(self, user):
        return {
            'active': self.active,
            'session_id': self.pk,
            'spot': self.spot.name,
            'spot_id': self.spot.pk,
            'owner': self.owner.pk,
            'created_ts': self.created_ts,
            'type': self.session_type,
            # GAL - should these fields do the full jsonify for user \ posts \ at this stage?
            'users': [u.pk for u in self.users],
            'intended_users': [u.pk for u in self.intended_users],
            'related_posts': [p.pk for p in self.related_posts]
        }


class Forecast(models.Model):
    # TODO - PHASE 2
    pass
