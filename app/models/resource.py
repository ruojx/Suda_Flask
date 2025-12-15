from . import BaseModel, db

class Resource(BaseModel):
    __tablename__ = 'resource'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    type = db.Column(db.String(10)) # pdf, zip, link
    size = db.Column(db.Integer, default=0)
    url = db.Column(db.String(500))
    cover = db.Column(db.String(500))
    tags = db.Column(db.String(255))
    status = db.Column(db.Integer, default=1)
    
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    favorite_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)

# 资源点赞表
class ResourceLike(BaseModel):
    __tablename__ = 'resource_like'
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

# 资源收藏表
class ResourceFavorite(BaseModel):
    __tablename__ = 'resource_favorite'
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)