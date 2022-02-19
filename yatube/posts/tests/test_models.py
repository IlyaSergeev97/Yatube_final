from django.contrib.auth.models import User
from django.test import TestCase

from yatube.settings import FIFTEEN_CHARACTERS

from ..models import Group, Post


class PostModelTest(TestCase):

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

    def test_verbose_name_post(self):
        """verbose_name в полях таблици posts совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата создания поста',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_verbose_name_group(self):
        """verbose_name в полях таблице group совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Адрес для страницы с задачей',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def post_help_text(self):
        """help_text в полях таблице posts совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
            'image': 'Выберите картинку',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def group_help_text(self):
        """help_text в полях таблице group совпадает с ожидаемым."""
        group = PostModelTest.group
        field_help_texts = {
            'title': 'Введите название группы',
            'description': 'Введите описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)

    def test_posy_models_have_correct__str__(self):
        """Проверяем, что у моделей post корректно работает __str__,
        отображаются первый 15 символов поста."""
        post = PostModelTest.post
        expected_object_name = post.text[:FIFTEEN_CHARACTERS]
        self.assertEqual(expected_object_name, str(post))

    def test_group_models_have_correct__str__(self):
        """Проверяем, что у моделей group корректно работает __str__,
        назване группы."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
