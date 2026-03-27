from flask import Flask, jsonify, request

app = Flask(__name__)

todos: list[dict[str, object]] = []


@app.get("/todos")
def list_todos():
    return jsonify(todos)


@app.post("/todos")
def create_todo():
    data = request.get_json()
    todos.append(data)
    return jsonify(data), 201
