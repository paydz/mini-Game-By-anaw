from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Mini Game Lucky Coin đang chạy 🚀"

if __name__ == "__main__":
    app.run()
