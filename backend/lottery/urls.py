from django.urls import path
from . import views

app_name = "lottery"

urlpatterns = [
    path("", views.index, name="index"),  # 前端頁面
    path("draw/", views.draw_fortune, name="draw"),  # API endpoint
]
