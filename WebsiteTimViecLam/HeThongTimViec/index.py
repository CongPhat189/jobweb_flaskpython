from flask import Flask, render_template
from WebsiteTimViecLam.HeThongTimViec import models


app = Flask(__name__)


@app.route("/")
def index():
    return  render_template("index.html")


if __name__=="__main__":
    with app.app_context():
        app.run(debug=True, port=5000)