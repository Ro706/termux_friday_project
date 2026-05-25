from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask App and SQLAlchemy
app = Flask(__name__)

# Database configuration
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "database.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define ChatLog Model
class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {"role": self.role, "content": self.content}

# Create the database and tables
def InitDB():
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    with app.app_context():
        db.create_all()

# Helper functions for database operations
def AddMessage(role, content):
    with app.app_context():
        new_log = ChatLog(role=role, content=content)
        db.session.add(new_log)
        db.session.commit()

def GetMessages():
    with app.app_context():
        logs = ChatLog.query.order_by(ChatLog.timestamp.asc()).all()
        return [log.to_dict() for log in logs]

def ClearChatLog():
    with app.app_context():
        ChatLog.query.delete()
        db.session.commit()

if __name__ == "__main__":
    InitDB()
    print(f"Database initialized at: {db_path}")
