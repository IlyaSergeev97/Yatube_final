from typing import Any
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Follow, Group, Post, User
from .forms import PostForm, CommentForm
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required

COUNT = 10


def paginator(request: Any, query_set: Any):
    paginator = Paginator(query_set, COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(60 * 20)
def index(request):
    '''Функия главной страницы.'''
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all().order_by('-pub_date')
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
    user = request.user
    if (
            user.is_authenticated
            and author != user
            and Follow.objects.filter(user=user, author=author).exists()
    ):
        following = True
    else:
        following = False
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
    group = get_object_or_404(Group, id=post.group_id)
    get_user_object = User.objects.get(pk=post.author_id)
    user = get_user_object.get_full_name
    post_list = Post.objects.filter(author=get_user_object)
    post_count = post_list.count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'user': user,
        'group': group,
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
    user = request.user
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=user, author=author)
    if user != author and not following.exists():
        Follow.objects.create(user=request.user, author=author)
        return redirect("group_posts:profile", username)
    return redirect('group_posts:profile', author)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=user).delete()
    return redirect('group_posts:profile', username=author)
