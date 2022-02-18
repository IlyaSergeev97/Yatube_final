from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from pytils.translit import slugify

from .settings import FIFTY_CHARACTERS, TWO_HUNDRED_CHARACTERS

User = get_user_model()


class Post(models.Model):
    '''Созадние модели таблицы постов.'''
    text = models.TextField('Текст поста', help_text='Введите текст поста')
    pub_date = models.DateTimeField('Дата создания поста', auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts',
                               db_index=True)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL,
                              blank=True, null=True, related_name='posts',
                              verbose_name='Группа',
                              help_text='Выберите группу',
                              db_index=True)
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Выберите картинку'
    )

    def __str__(self):
        return self.text


class Group(models.Model):
    '''Созадние модели таблицы групп.'''
    title = models.CharField('Название группы',
                             max_length=TWO_HUNDRED_CHARACTERS, db_index=True,
                             help_text='Введите название группы')
    slug = models.SlugField('Адрес для страницы с задачей',
                            max_length=FIFTY_CHARACTERS,
                            unique=True, db_index=True)
    description = models.TextField('Описание группы',
                                   help_text='Введите описание группы')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:FIFTY_CHARACTERS]
        super().save(*args, **kwargs)


class Comment(models.Model):
    '''Создание модели коментарии'''
    text = models.TextField('Текст комментария',
                            help_text='Введите текст комменатрия')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments',
                             db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments',
                               db_index=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')
