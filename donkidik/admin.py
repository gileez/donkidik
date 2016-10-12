from django.contrib import admin
from donkidik.models import *


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

@admin.register(PostMeta)
class PostMetaAdmin(admin.ModelAdmin):
    pass


@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    pass


@admin.register(ScoreEvent)
class ScoreEventAdmin(admin.ModelAdmin):
    readonly_fields = ['upvote_event', 'downvote_event', 'post_event', 'scored_user', 'score', 'created_ts']


@admin.register(PostUpVote)
class PostUpVoteAdmin(admin.ModelAdmin):
    pass


@admin.register(PostDownVote)
class PostDownVoteAdmin(admin.ModelAdmin):
    pass


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass
