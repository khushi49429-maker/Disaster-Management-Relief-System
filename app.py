
from flask import Flask
from backend.auth import auth
from backend.emergencies import emergency
from backend.rescue import rescue
from backend.donations import donation
from backend.admin import admin

app = Flask(__name__)
app.secret_key= "resqnow_secret_key_Change_later"
app.register_blueprint(auth)
app.register_blueprint(emergency)
app.register_blueprint(rescue)
app.register_blueprint(donation)
app.register_blueprint(admin)

@app.route("/")
def home():
    return "Welcome to ResQNow - Disaster Management System!"

if __name__ == "__main__":
    app.run(debug=True)
