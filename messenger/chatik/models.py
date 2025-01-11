from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.
class User(AbstractUser):
    photo = models.ImageField(upload_to='media/profilePhotos/', null=True, blank=True)
    
class Chat(models.Model):
    title = models.CharField(max_length=20)
    users = models.ManyToManyField(User, related_name='chats')
    
    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    text = models.TextField()
    sendtime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('sendtime',)
        