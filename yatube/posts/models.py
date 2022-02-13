from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post (models.Model):
    '''Созадние модели таблицы постов.'''
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts',
                               db_index=True)
    group = models.ForeignKey('Group', on_delete=models.CASCADE,
                              blank=True, null=True, related_name='posts',
                              verbose_name='Группа',
                              help_text='Выберите группу',
                              db_index=True)
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text


class Group (models.Model):
    '''Созадние модели таблицы групп.'''
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=50, unique=True, db_index=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment (models.Model):
    '''Создание модели коментарии'''
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments',
                             db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments',
                               db_index=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.text


class Follow (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')
