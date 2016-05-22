from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_save # Right before the model is save do something
from django.utils import timezone
from django.utils.text import slugify
from django.utils.safestring import mark_safe

from markdown_deux import markdown
from comments.models import Comment
from .utils import get_read_time

# Create your models here.
class PostManager(models.Manager):
    def active_posts(self, *args, **kwargs):
        return super(PostManager, self).filter(draft = False).filter(publish__lte = timezone.now())

def upload_location(instance, filename):
    return "%s/%s" % (instance.id, filename)

class Post(models.Model):
    title = models.CharField(max_length = 120)
    image = models.ImageField(upload_to = upload_location, blank = True, null = True)
    slug = models.SlugField(unique = True)
    content = models.TextField()
    draft = models.BooleanField(default = False)
    publish = models.DateField(auto_now = False, auto_now_add = False)
    read_time = models.IntegerField(default = 0)
    updated = models.DateTimeField(auto_now = True, auto_now_add = False)
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)
    # Custom model manger
    objects = PostManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:detail", kwargs = {"slug": self.slug})
        #return "/posts/%s/" %(self.id)

    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)

    @property
    def comments(self):
        instance = self
        queryset = Comment.objects.filter_by_instance(instance)
        return queryset

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type

    class Meta:
        ordering = ["-timestamp"]

def create_slug(instance, new_slug = None):
    # converts "first post" => "first-post"
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    queryset = Post.objects.filter(slug = slug).order_by("-id")
    slug_exists = queryset.exists()
    if slug_exists:
        new_slug = "%s-%s" % (slug, queryset.first().id)
        return create_slug(instance, new_slug = new_slug)
    return slug

# any time a post is saved, this function will be called before saving
def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)
    if instance.content:
        html_string = instance.get_markdown()
        # getting read time and storing in read time variable
        read_time_var = get_read_time(html_string)
        # storing the value of read time variable into the model field
        instance.read_time = read_time_var

pre_save.connect(pre_save_post_receiver, sender = Post)
