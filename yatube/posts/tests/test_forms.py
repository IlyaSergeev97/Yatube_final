
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post
from .settings import COUNT_ONE

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста',
            group=cls.group,)

        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Test comment',
            post=cls.post
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'image': self.uploaded,
        }
        self.authorized_client.post(
            reverse('group_posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + COUNT_ONE)
        self.assertTrue(
            Post.objects.filter(
                text='Текст поста',
                image='posts/small.gif'
            ).exists()
        )

    def test_comment(self):
        '''"""Валидная форма созадет комменатрий."""'''
        cooment_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария'
        }
        self.authorized_client.post(
            reverse('group_posts:add_comment',
                    kwargs={'post_id': self.comment.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(),
                         cooment_count + COUNT_ONE)
        self.assertTrue(
            Comment.objects.filter(
                text=self.comment.text,
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма обновляет выбранный пост."""
        post = PostFormTest.post
        form_data = {
            'text': 'Текст обновленного поста',
            'group': self.post.id,
        }
        response = self.authorized_client.post(
            reverse('group_posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        post.refresh_from_db()
        expected_object_text = post.text
        self.assertRedirects(response, reverse('group_posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        self.assertEqual(expected_object_text, 'Текст обновленного поста')
