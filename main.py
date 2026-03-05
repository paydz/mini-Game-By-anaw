from flask import Flask, render_template, request, redirect, session
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
            "money": 50000
        }

        save_users(users)
        return redirect("/login")

    return render_template("register.html")

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

    return render_template("login.html")

# =====================
# HOME
# =====================

@app.route("/")
def home():
    if "username" not in session:
        return redirect("/login")

    users = load_users()
    user = users[session["username"]]

    return render_template(
        "home.html",
        username=session["username"],
        money=format_money(user["money"])
    )

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

        if bet <= 0:
            result = "❌ Tiền cược không hợp lệ!"
        elif bet > user["money"]:
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

    return render_template(
        "dice.html",
        money=format_money(user["money"]),
        result=result,
        dice=dice_roll
    )

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

        if bet <= 0:
            result = "❌ Tiền cược không hợp lệ!"
        elif bet > user["money"]:
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

    return render_template(
        "coin.html",
        money=format_money(user["money"]),
        result=result,
        flip=flip
    )

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
