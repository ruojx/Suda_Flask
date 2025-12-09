from . import BaseModel, db

class Question(BaseModel):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    tags = db.Column(db.String(255))
    view_count = db.Column(db.Integer, default=0)
    answer_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)

class Answer(BaseModel):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer)
    content = db.Column(db.Text)
    upvote_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)