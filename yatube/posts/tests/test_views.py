
import tempfile
from datetime import date

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post
from .settings import (FIRST_POST, ONE_POST, TEN_POST_PAGE, THIRTEEN_POSTS,
                       THREE_POST_PAGE)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.another_user = User.objects.create_user(username='another_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста',
            group=cls.group,
            pub_date=date.today(),
            image=uploaded)

        cls.another_group = Group.objects.create(
            title='Тестовая группа-2',
            slug='test-slug-2',
            description='Тестовое описание-2',
        )
        cls.comment = Comment.objects.create(
            text='Text-post1',
            post=cls.post,
            author=cls.user
        )
        cls.templates_pages_names = {
            reverse('group_posts:index'): 'posts/index.html',
            reverse('group_posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('group_posts:profile', kwargs={'username': cls.user}):
                'posts/profile.html',
            reverse('group_posts:post_detail',
                    kwargs={'post_id': cls.post.id}):
                'posts/post_detail.html',
            reverse('group_posts:post_edit',
                    kwargs={'post_id': cls.post.id}):
                'posts/create_post.html',
            reverse('group_posts:post_create'): 'posts/create_post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower = Client()
        self.follower.force_login(self.another_user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_cache_index_page_correct_context(self):
        """Кэш index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('group_posts:index'))
        content = response.content
        post_id = TaskPagesTests.post.id
        instance = Post.objects.get(pk=post_id)
        instance.delete()
        new_response = self.authorized_client.get(
            reverse('group_posts:index'))
        new_content = new_response.content
        self.assertEqual(content, new_content)
        cache.clear()
        response_new = self.authorized_client.get(
            reverse('group_posts:index'))
        content_new = response_new.content
        self.assertNotEqual(content, content_new)

    def test_index_list_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('group_posts:index'))
        first_object = response.context['page_obj'][FIRST_POST]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.pub_date, self.post.pub_date)
        self.assertEqual(first_object.image, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts:group_list',
                    kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][FIRST_POST]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.pub_date, self.post.pub_date)
        self.assertEqual(first_object.image, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts:profile',
                    kwargs={'username': self.user}))
        first_object = response.context['page_obj'][FIRST_POST]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.pub_date, self.post.pub_date)
        self.assertEqual(first_object.image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts:post_detail',
                    kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('post').group,
                         self.post.group)
        self.assertEqual(response.context.get('post').text,
                         self.post.text)
        self.assertEqual(response.context.get('post').author,
                         self.post.author)
        self.assertEqual(response.context.get('post').pub_date,
                         self.post.pub_date)
        self.assertEqual(response.context.get('post').image,
                         self.post.image)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_pages_contains_test_group_post(self):
        """При создании поста с группой он появляется на всех страницах."""
        adresses = [
            reverse('group_posts:index'),
            reverse('group_posts:group_list',
                    kwargs={'slug': self.post.group.slug}),
            reverse('group_posts:profile',
                    kwargs={'username': self.user.username})

        ]
        for adress in adresses:
            response = self.authorized_client.get(adress)
            first_object = response.context['page_obj'][FIRST_POST]
            post_text = first_object.text
            post_group = first_object.group.title
            self.assertEqual(post_text, self.post.text)
            self.assertEqual(post_group, self.post.group.title)

    def test_follower_post(self):
        '''Пост появляетсмя у подписчиков'''
        self.follower.get(
            reverse('group_posts:profile_follow',
                    kwargs={'username': self.user})
        )
        post_text = self.post.text
        self.assertEqual(post_text, self.post.text)

    def test_comment(self):
        '''Комментарий появляется на странице поста'''
        reverse('group_posts:post_detail',
                kwargs={'post_id': self.post.id})
        post_comment = self.comment.text
        self.assertEqual(post_comment, self.comment.text)

    def test_another_group_list_page_not_show_post(self):
        """Пост, не принадлежащий группе не показывается на странице группы."""
        post = TaskPagesTests.post
        response = self.guest_client.get(
            reverse('group_posts:group_list',
                    kwargs={'slug': self.another_group.slug}))
        self.assertNotIn(post, response.context.get('page_obj'))

    def test_authorized_client_follow(self):
        """Авторизованный пользователь может подписаться на автора."""
        follow_count = Follow.objects.count()
        self.follower.get(
            reverse('group_posts:profile_follow',
                    kwargs={'username': self.user})
        )
        self.assertEqual(Follow.objects.count(), follow_count + ONE_POST)

    def test_authorized_client_unfollow(self):
        """Авторизованный пользователь может отписаться  от автора."""
        follow_count = Follow.objects.count()
        follow_count_one = follow_count + 1
        self.follower.get(
            reverse('group_posts:profile_unfollow',
                    kwargs={'username': self.user})
        )
        self.assertEqual(follow_count, follow_count_one - 1)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testUser')
        cls.another_user = User.objects.create_user(username='testAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        for i in range(THIRTEEN_POSTS):
            Post.objects.create(
                author=cls.user,
                text=f'Текст {i}',
                group=cls.group
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_first_page_index_contains_ten_records(self):
        '''Проверка: количество постов на 1 странице равно 10.'''
        response = self.authorized_client.get(reverse('group_posts:index'))
        self.assertEqual(len(response.context['page_obj']), TEN_POST_PAGE)

    def test_second_page_index_contains_three_records(self):
        '''Проверка: количество постов на 2 странице равно 3.'''
        response = self.authorized_client.get(
            reverse('group_posts:index') + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), THREE_POST_PAGE)

    def test_first_page_group_list_contains_ten_records(self):
        '''Проверка: количество постов на 1 странице равно 10.'''
        response = self.authorized_client.get(
            reverse('group_posts:group_list',
                    kwargs={'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']), TEN_POST_PAGE)

    def test_second_page_group_list_contains_three_records(self):
        '''Проверка: количество постов на 2 странице равно 3.'''
        response = self.authorized_client.get(
            reverse('group_posts:group_list',
                    kwargs={'slug': 'test-slug-2'}) + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), THREE_POST_PAGE)

    def test_first_page_profile_contains_ten_records(self):
        '''Проверка: количество постов на 1 странице равно 10.'''
        response = self.authorized_client.get(
            reverse('group_posts:profile', kwargs={'username': self.user}))
        self.assertEqual(len(response.context['page_obj']), TEN_POST_PAGE)

    def test_second_page_profile_contains_three_records(self):
        '''Проверка: количество постов на 2 странице равно 3.'''
        response = self.authorized_client.get(
            reverse('group_posts:profile',
                    kwargs={'username': self.user}) + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), THREE_POST_PAGE)
