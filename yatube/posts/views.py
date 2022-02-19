
from typing import Any

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from yatube.settings import TEN_POST_PAGE, ONE_SECOND, TWENTY_SECOND


def paginator(request: Any, query_set: Any):
    paginator = Paginator(query_set, TEN_POST_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(TWENTY_SECOND * ONE_SECOND)
def index(request):
    '''Функия главной страницы.'''
    title = 'Последние обновления на сайте'
    post_list = Post.objects.order_by('-pub_date')
    page_obj = paginator(request, post_list)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    '''Фунция вызова страницы с постами групп.'''
    title = 'Записи сообщества:'
    group = get_object_or_404(Group, slug=slug)
    group_list = group.posts.order_by('-pub_date')
    page_obj = paginator(request, group_list)
    context = {
        'page_obj': page_obj,
        'title': title,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    '''Профайл пользователя.'''
    author = get_object_or_404(User, username=username)
    posts = author.posts.order_by('-pub_date')
    count_posts = posts.count()
    title = 'Все посты пользователя:'
    following = (request.user.is_authenticated
                 and request.user != author
                 and Follow.objects.filter(user=request.user,
                                           author=author).exists())
    page_obj = paginator(request, posts)
    context = {
        'author': author,
        'count_posts': count_posts,
        'posts': posts,
        'title': title,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    title = 'Пост'
    post = get_object_or_404(Post, pk=post_id)
    post_count = post.author.posts.count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'post_count': post_count,
        'title': title,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("group_posts:profile", username=post.author)
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('group_posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("group_posts:post_detail", post_id=post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('group_posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    authors = user.follower.all().values('author')
    posts_list = Post.objects.filter(author__in=authors)
    page_obj = paginator(request, posts_list)
    context = {'page_obj': page_obj}
    return render(
        request,
        'posts/follow.html',
        context
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=request.user,
                                      author=author).exists()
    if request.user != author and not following:
        Follow.objects.create(user=request.user, author=author)
    return redirect('group_posts:profile', author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(author=author, user=request.user).exists():
        Follow.objects.get(author=author, user=request.user).delete()
    return redirect('group_posts:profile', author)
