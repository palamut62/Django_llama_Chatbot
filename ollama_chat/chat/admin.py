from django.contrib import admin
from .models import Chat, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('content', 'is_user', 'timestamp')

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'summary', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('chat_id', 'summary')
    readonly_fields = ('chat_id', 'timestamp')
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'is_user', 'content_preview', 'timestamp')
    list_filter = ('is_user', 'timestamp')
    search_fields = ('content',)
    readonly_fields = ('timestamp',)

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'İçerik Önizlemesi'
