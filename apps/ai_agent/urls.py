from django.urls import path

from . import views

app_name = "ai_agent"

urlpatterns = [
    # مسار واحد بس للشات
    path("chat/", views.chat_view, name="chat"),
]