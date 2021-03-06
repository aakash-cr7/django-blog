from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# from posts.models import Post, cant do dual imports as comments is imported in models of Post

# Create your models here.

class CommentManager(models.Manager):
    def filter_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__) # instead of writing Post, use this
        obj_id = instance.id
        # super(CommentManager, self) = Comments.objects
        queryset = super(CommentManager, self).filter(content_type = content_type, object_id = obj_id)
        return queryset

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default = 1)
    #post = models.ForeignKey(Post)

    content_type = models.ForeignKey(ContentType, on_delete = models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add = True)
    objects = CommentManager()

    def __str__(self):
        return str(self.user.username)
