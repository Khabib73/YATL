from flask import Flask, request, jsonify

app = Flask(__name__)

users = {
    1: {
        "name": "John Doe",
        "age": 30,
    }
}


@app.get("/users/<int:user_id>")
def get_user(user_id):
    if user_id not in users:
        return jsonify({"detail": "User not found"}), 404
    return jsonify(users[user_id])


@app.post("/users")
def create_user():
    data = request.get_json()
    if not data or "name" not in data or "age" not in data:
        return jsonify({"detail": "Invalid input"}), 400

    user_id = len(users) + 1
    users[user_id] = {
        "name": data["name"],
        "age": data["age"],
    }
    return jsonify(users[user_id]), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
