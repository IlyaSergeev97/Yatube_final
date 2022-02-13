from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Group, Post


class PostModelTest(TestCase):

    FIFTEEN_CHARACTERS = 15

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_verbose_name(self):
        """verbose_name в поле group совпадает с ожидаемым."""
        post = PostModelTest.post
        verbose = post._meta.get_field('group').verbose_name
        self.assertEqual(verbose, 'Группа')

    def test_title_help_text(self):
        """help_text поля group совпадает с ожидаемым."""
        post = PostModelTest.post
        help_text = post._meta.get_field('group').help_text
        self.assertEqual(help_text, 'Выберите группу')

    def test_models_have_correct__str__(self):
        """Проверяем, что у моделей post корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:self.FIFTEEN_CHARACTERS]
        self.assertEqual(expected_object_name, str(post))

    def test_models_have_correct__str__(self):
        """Проверяем, что у моделей group корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
