from flask import Flask, render_template, request, redirect, session, jsonify
import random
import json
import os

app = Flask(__name__)
app.secret_key = "luckycoin_secret_key_123" # Khóa bảo mật cho session

# Hàm đọc dữ liệu từ file JSON
def load_users():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open("users.json", "r") as f:
            content = f.read()
            return json.loads(content) if content else {}
    except:
        return {}

# Hàm lưu dữ liệu vào file JSON
def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

@app.route("/")
def home():
    if "username" not in session:
        return redirect("/login")
    users = load_users()
    user = users.get(session["username"], {"money": 0})
    return render_template("home.html", username=session["username"], money=user["money"])

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return "Vui lòng nhập đủ thông tin! <a href='/register'>Làm lại</a>"
        if username in users:
            return "Tài khoản đã tồn tại! <a href='/register'>Thử tên khác</a>"

        users[username] = {"password": password, "money": 50000} # Tặng 50k khởi nghiệp
        save_users(users)
        return "Đăng ký thành công! <a href='/login'>Đăng nhập ngay</a>"
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect("/")
        return "Sai tài khoản hoặc mật khẩu! <a href='/login'>Thử lại</a>"
    return render_template("login.html")

@app.route("/dice", methods=["GET", "POST"])
def dice():
    if "username" not in session: return redirect("/login")
    users = load_users()
    user = users[session["username"]]
    result_msg = ""
    dice_roll = None

    if request.method == "POST":
        try:
            bet = int(request.form.get("bet", 0))
            choice = request.form.get("choice")
            if bet <= 0 or bet > user["money"]:
                result_msg = "Tiền cược không hợp lệ!"
            else:
                dice_roll = random.randint(1, 6) # Logic xúc xắc
                is_tai = dice_roll >= 4
                if (is_tai and choice == "tai") or (not is_tai and choice == "xiu"):
                    user["money"] += bet
                    result_msg = f"Kết quả {dice_roll}: BẠN THẮNG!"
                else:
                    user["money"] -= bet
                    result_msg = f"Kết quả {dice_roll}: BẠN THUA!"
                save_users(users)
        except:
            result_msg = "Lỗi nhập liệu!"
    return render_template("dice.html", money=user["money"], result=result_msg, dice=dice_roll)

@app.route("/coin", methods=["GET", "POST"])
def coin():
    if "username" not in session: return redirect("/login")
    users = load_users()
    user = users[session["username"]]
    result_msg = ""
    flip = None

    if request.method == "POST":
        try:
            bet = int(request.form.get("bet", 0))
            choice = request.form.get("choice")
            if bet <= 0 or bet > user["money"]:
                result_msg = "Tiền cược không hợp lệ!"
            else:
                flip = random.choice(["ngua", "sap"]) # Logic đồng xu
                if flip == choice:
                    user["money"] += bet
                    result_msg = f"Kết quả {flip.upper()}: BẠN THẮNG!"
                else:
                    user["money"] -= bet
                    result_msg = f"Kết quả {flip.upper()}: BẠN THUA!"
                save_users(users)
        except:
            result_msg = "Lỗi nhập liệu!"
    return render_template("coin.html", money=user["money"], result=result_msg, flip=flip)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
