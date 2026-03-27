from django.http import JsonResponse
from src.todos.models import Todo


def todo_list(request):
    todos = list(Todo.objects.values("id", "title", "done"))
    return JsonResponse(todos, safe=False)
