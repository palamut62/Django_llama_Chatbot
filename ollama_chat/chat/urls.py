from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('/chat_page', views.chat_page, name='chat_page'),
    path('chat/<int:chat_id>/', views.chat_page, name='chat_page'),
    path('chat/', views.chat_view, name='chat'),
    path('delete/<int:chat_id>/', views.delete_chat, name='delete_chat'),
    path('load_chat/', views.load_chat, name='load_chat'),
]
