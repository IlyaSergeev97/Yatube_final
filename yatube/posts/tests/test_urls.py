
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import Client, TestCase

from yatube.settings import (ERROR_FOUR_HUNDRED_AND_FOUR,
                             THE_ANSWER_IS_TWO_HUNDRED)

from ..models import Group, Post


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.urls = [
            '/',
            '/group/test-slug/',
            '/profile/test/',
            f'/posts/{cls.post.id}/',
            '/create/',
            f'/posts/{cls.post.id}/edit/',
        ]
        cls.templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/test/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTest.user)
        cache.clear()

    def test_urls_uses_correct_template(self):
        for url in self.urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code,
                                 THE_ANSWER_IS_TWO_HUNDRED)

    def test_unexisting_page(self):
        """Запрос к страница unixisting_page вернет ошибку 404"""
        response = self.guest_client.get('/unixisting_page/')
        self.assertEqual(
            response.status_code, ERROR_FOUR_HUNDRED_AND_FOUR)

    def test_urls_uses_correct(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
