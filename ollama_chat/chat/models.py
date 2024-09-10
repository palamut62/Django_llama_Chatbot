from django.db import models

# Create your models here.
from django.db import models

class Chat(models.Model):
    chat_id = models.CharField(max_length=14, unique=True)
    summary = models.CharField(max_length=255, blank=True, default="No summary")  # Varsayılan değer eklendi
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