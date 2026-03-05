from flask import Flask, render_template_string, request, redirect, session
import random
import json
import os

app = Flask(__name__)
app.secret_key = "luckycoin_secret"

# =====================
# USER DATA
# =====================

def load_users():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def format_money(amount):
    if amount >= 1_000_000_000:
        return f"{amount/1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"{amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"{amount/1_000:.1f}K"
    return str(amount)

# =====================
# REGISTER
# =====================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            return "❌ Tài khoản đã tồn tại!"

        users[username] = {
            "password": password,
            "money": 50000  # tặng 50K
        }

        save_users(users)
        return redirect("/login")

    return """
    <h1>Đăng ký Lucky Coin</h1>
    <form method="POST">
        <input name="username" placeholder="Username"><br><br>
        <input name="password" type="password" placeholder="Password"><br><br>
        <button>Đăng ký</button>
    </form>
    <a href="/login">Đã có tài khoản?</a>
    """

# =====================
# LOGIN
# =====================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect("/")

        return "❌ Sai tài khoản hoặc mật khẩu!"

    return """
    <h1>Login Lucky Coin</h1>
    <form method="POST">
        <input name="username" placeholder="Username"><br><br>
        <input name="password" type="password" placeholder="Password"><br><br>
        <button>Login</button>
    </form>
    <a href="/register">Tạo tài khoản</a>
    """

# =====================
# HOME
# =====================

@app.route("/")
def home():
    if "username" not in session:
        return redirect("/login")

    users = load_users()
    user = users[session["username"]]

    return render_template_string("""
    <h1>🎮 Lucky Coin Casino</h1>
    <h3>👤 {{username}}</h3>
    <h3>💰 {{money}} LC</h3>

    <a href="/dice">🎲 Tài / Xỉu</a><br><br>
    <a href="/coin">🪙 Tung Đồng Xu</a><br><br>

    <a href="/logout">🚪 Đăng xuất</a>
    """,
    username=session["username"],
    money=format_money(user["money"]))

# =====================
# TÀI / XỈU
# =====================

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
        choice = request.form["choice"]

        if bet > user["money"]:
            result = "❌ Không đủ tiền!"
        else:
            dice_roll = random.randint(1, 6)
            tai = dice_roll >= 4

            if (tai and choice == "tai") or (not tai and choice == "xiu"):
                user["money"] += bet
                result = "🎉 Bạn thắng!"
            else:
                user["money"] -= bet
                result = "💀 Bạn thua!"

            save_users(users)

    return render_template_string("""
    <h1>🎲 Tài / Xỉu</h1>
    <h3>💰 {{money}} LC</h3>

    <form method="POST">
        <input name="bet" type="number" placeholder="Nhập tiền cược"><br><br>

        <button name="choice" value="tai">🔥 TÀI (4-6)</button>
        <button name="choice" value="xiu">❄️ XỈU (1-3)</button>
    </form>

    <h2>{{result}}</h2>
    <h2>Kết quả: {{dice}}</h2>

    <a href="/">⬅ Về trang chủ</a>
    """,
    money=format_money(user["money"]),
    result=result,
    dice=dice_roll)

# =====================
# TUNG ĐỒNG XU
# =====================

@app.route("/coin", methods=["GET", "POST"])
def coin():
    if "username" not in session:
        return redirect("/login")

    users = load_users()
    user = users[session["username"]]
    result = ""
    flip = None

    if request.method == "POST":
        bet = int(request.form["bet"])
        choice = request.form["choice"]

        if bet > user["money"]:
            result = "❌ Không đủ tiền!"
        else:
            flip = random.choice(["ngua", "sap"])

            if flip == choice:
                user["money"] += bet
                result = "🎉 Bạn thắng!"
            else:
                user["money"] -= bet
                result = "💀 Bạn thua!"

            save_users(users)

    return render_template_string("""
    <h1>🪙 Tung Đồng Xu</h1>
    <h3>💰 {{money}} LC</h3>

    <form method="POST">
        <input name="bet" type="number" placeholder="Nhập tiền cược"><br><br>

        <button name="choice" value="ngua">🟡 Ngửa</button>
        <button name="choice" value="sap">⚫ Sấp</button>
    </form>

    <h2>{{result}}</h2>
    <h2>Kết quả: {{flip}}</h2>

    <a href="/">⬅ Về trang chủ</a>
    """,
    money=format_money(user["money"]),
    result=result,
    flip=flip)

# =====================
# LOGOUT
# =====================

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

# =====================
# RUN
# =====================

if __name__ == "__main__":
    app.run(debug=True)
