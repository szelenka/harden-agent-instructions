from django.urls import path
from src.todos import views

urlpatterns = [
    path("todos/", views.todo_list),
]
