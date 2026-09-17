from django.urls import path

from . import views

app_name = "ai_agent"

urlpatterns = [
    path("chat/", views.chat_view, name="chat"),
path('', views.chat_view, name='agent_chat'),
]