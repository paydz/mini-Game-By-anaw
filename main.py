from flask import Flask, render_template_string, request, redirect, session
import random
import json
import os

app = Flask(__name__)
app.secret_key = "luckycoin_secret_key"

DATA_FILE = "users.json"

# Tạo file nếu chưa có
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)


def load_users():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def format_money(amount):
    if amount >= 1_000_000_000:
        return f"{amount/1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"{amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"{amount/1_000:.1f}K"
    return str(amount)


# Trang chủ
@app.route("/")
def home():
    if "username" not in session:
        return redirect("/login")

    users = load_users()
    money = users[session["username"]]["money"]

    return render_template_string("""
    <h1>🎮 Lucky Coin</h1>
    <h3>👤 {{username}}</h3>
    <h3>💰 {{money}} LC</h3>
    <a href="/dice">🎲 Chơi Tung Xúc Xắc</a><br><br>
    <a href="/logout">🚪 Đăng xuất</a>
    """, username=session["username"], money=format_money(money))


# Đăng ký
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users:
            return "Tài khoản đã tồn tại!"

        users[username] = {
            "password": password,
            "money": 50000
        }

        save_users(users)
        return redirect("/login")

    return """
    <h2>Đăng ký</h2>
    <form method="POST">
        <input name="username" placeholder="Tên tài khoản"><br>
        <input name="password" type="password" placeholder="Mật khẩu"><br>
        <button>Đăng ký</button>
    </form>
    <a href="/login">Đăng nhập</a>
    """


# Đăng nhập
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect("/")

        return "Sai tài khoản hoặc mật khẩu!"

    return """
    <h2>Đăng nhập</h2>
    <form method="POST">
        <input name="username" placeholder="Tên tài khoản"><br>
        <input name="password" type="password" placeholder="Mật khẩu"><br>
        <button>Đăng nhập</button>
    </form>
    <a href="/register">Đăng ký</a>
    """


# Đăng xuất
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# Game xúc xắc
@app.route("/dice", methods=["GET", "POST"])
def dice():
    if "username" not in session:
        return redirect("/login")

    users = load_users()
    user = users[session["username"]]
    result = ""
    dice_roll = None

    if request.method == "POST":
        bet = int(request.form["bet"])

        if bet > user["money"]:
            result = "❌ Không đủ tiền!"
        else:
            dice_roll = random.randint(1, 6)

            if dice_roll >= 4:
                user["money"] += bet
                result = "🎉 Bạn thắng!"
            else:
                user["money"] -= bet
                result = "💀 Bạn thua!"

            save_users(users)

    return render_template_string("""
    <h1>🎲 Tung Xúc Xắc</h1>
    <h3>💰 {{money}} LC</h3>

    <form method="POST">
        <input name="bet" type="number" placeholder="Nhập tiền cược">
        <button>Chơi</button>
    </form>

    <h2>{{result}}</h2>
    <h2>Kết quả: {{dice}}</h2>

    <a href="/">⬅ Về trang chủ</a>
    """,
    money=format_money(user["money"]),
    result=result,
    dice=dice_roll)


if __name__ == "__main__":
    app.run()
