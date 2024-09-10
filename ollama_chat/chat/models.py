from django.db import models
import uuid

# Create your models here.
from django.db import models

class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    chat_id = models.CharField(max_length=36, unique=True, default=uuid.uuid4, editable=False)
    summary = models.CharField(max_length=255, blank=True, default="Yeni Sohbet")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.chat_id}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', null=True)  # null=True eklendi
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'User' if self.is_user else 'AI'}: {self.content[:50]}..."