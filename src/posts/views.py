from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from urllib.parse import quote

from .models import Post
from .forms import PostForm

# Create your views here.

# List all the posts
def list_post(request):
    today = timezone.now().date()
    queryset_list =  Post.objects.active_posts()
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()
    paginator = Paginator(queryset_list, 5) # Show 25 contacts per page

    # Varaiable for reauesting pages
    # /posts/?{page_request_variable}=1
    # /posts/?page=1
    page_request_variable = 'page'
    page = request.GET.get(page_request_variable)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)
    context = {
        # ordering done in models
        #'posts_list': Post.objects.all().order_by("-timestamp"),
        'posts_list':queryset,
        'page_request_variable': page_request_variable,
        'today': today,
    }
    return render(request, 'posts/list_post.html', context)

def detail_post(request, slug = None):
    instance = get_object_or_404(Post, slug = slug)
    if instance.draft or instance.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    # create url encoded strings
    # "I am superman" => "I%20am%20superman"
    share_string = quote(instance.content)
    context = {
        'post': instance,
        'share_string': share_string,
    }
    return render(request, 'posts/detail_post.html', context)

def create_post(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    f = PostForm()
    if request.method == "POST":
        f = PostForm(request.POST, request.FILES or None)
        if f.is_valid():
            instance = f.save(commit = False)
            instance.save()
            messages.success(request, "Succesfully created post")
            return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "form": f,
        "title": "Create post",
    }
    return render(request, 'posts/create_post.html', context)

def update_post(request, slug = None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug = slug)
    f = PostForm(request.POST or None, request.FILES or None, instance = instance)
    if f.is_valid():
        instance = f.save(commit = False)
        instance.save()
        messages.success(request, "Succesfully updated post", extra_tags="some-class")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "form": f,
        "title": "Edit post",
        "instance": instance,
    }
    return render(request, 'posts/edit_post.html', context)

def delete_post(request, slug = None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug = slug)
    instance.delete()
    messages.success(request, "Succesfully deleted post")
    return redirect('posts:list_post')
