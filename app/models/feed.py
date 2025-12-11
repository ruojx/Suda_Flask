from . import BaseModel, db

class Post(BaseModel):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    author_name = db.Column(db.String(50))
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    summary = db.Column(db.String(500))
    tags = db.Column(db.String(500))
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    collect_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)

class Topic(BaseModel):
    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    author_name = db.Column(db.String(50))
    title = db.Column(db.String(200))
    summary = db.Column(db.Text)
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    follow_count = db.Column(db.Integer, default=0)
    post_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)

class LikeTable(BaseModel):
    __tablename__ = 'like_table'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    entity_type = db.Column(db.Integer) # 1-帖子 2-话题
    entity_id = db.Column(db.Integer)
    status = db.Column(db.Integer, default=1)

class Collect(BaseModel):
    __tablename__ = 'collect'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    entity_id = db.Column(db.Integer) # 帖子ID
    status = db.Column(db.Integer, default=1)