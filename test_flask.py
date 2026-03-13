# test_flask.py
from flask import Flask
print("Flask import OK")

app = Flask(__name__)
print("Flask app created")

@app.route("/")
def index():
    return "Hello world"

if __name__ == "__main__":
    print("Running Flask")
    app.run(debug=True)