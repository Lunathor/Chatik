from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    # Поле для хранения фотографии профиля пользователя
    photo = models.ImageField(upload_to='media/profilePhotos/', null=True, blank=True)


class Chat(models.Model):
    # Поле для хранения заголовка чата
    title = models.CharField(max_length=20)
    
    # Связь многие-ко-многим с пользователями (участниками чата)
    users = models.ManyToManyField(User, related_name='chats')
    
    def __str__(self):
        # Возвращаем строковое представление объекта чата (заголовок)
        return self.title  # Исправлено с name на title


class Message(models.Model):
    # Связь с пользователем, отправившим сообщение
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Связь с чатом, в котором было отправлено сообщение
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    
    # Поле для хранения текста сообщения
    text = models.TextField()
    
    # Поле для хранения времени отправки сообщения (автоматически устанавливается при создании)
    sendtime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Указываем порядок сортировки сообщений по времени отправки
        ordering = ('sendtime',)
        