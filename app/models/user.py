from . import BaseModel, db

class User(BaseModel):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    name = db.Column(db.String(50))
    avatar = db.Column(db.String(255))
    introduction = db.Column(db.String(255))
    status = db.Column(db.Integer, default=1)

class Follow(BaseModel):
    __tablename__ = 'follow'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    entity_id = db.Column(db.Integer, nullable=False) # 话题ID
    status = db.Column(db.Integer, default=1) # 1=有效 0=无效