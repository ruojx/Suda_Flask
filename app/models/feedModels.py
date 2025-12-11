from . import BaseModel, db
from datetime import datetime

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
    # 新增：帖子所属话题ID（一个帖子只能有一个话题）
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))

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

class FeedLike(BaseModel):
    __tablename__ = 'feed_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    entity_type = db.Column(db.Integer)  # 1-帖子 2-话题
    entity_id = db.Column(db.Integer)
    status = db.Column(db.Integer, default=1)

class FeedCollect(BaseModel):
    __tablename__ = 'feed_collect'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    entity_id = db.Column(db.Integer)  # 帖子ID
    status = db.Column(db.Integer, default=1)

class FeedFollow(BaseModel):
    __tablename__ = 'feed_follow'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    entity_id = db.Column(db.Integer)  # 话题ID
    status = db.Column(db.Integer, default=1)

class FeedComment(BaseModel):
    __tablename__ = 'feed_comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    entity_type = db.Column(db.Integer)  # 1-帖子 2-话题
    entity_id = db.Column(db.Integer)
    content = db.Column(db.Text)
    like_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)

class PostTopicRelation(BaseModel):
    __tablename__ = 'post_topic_relation'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    
    # 建立关系
    post = db.relationship('Post', backref=db.backref('topic_relations', lazy=True))
    topic = db.relationship('Topic', backref=db.backref('post_relations', lazy=True))

class FeedView(BaseModel):
    __tablename__ = 'feed_view'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)  # 访问者ID（0表示未登录用户）
    entity_type = db.Column(db.Integer, nullable=False)  # 实体类型：1-帖子，2-话题
    entity_id = db.Column(db.Integer, nullable=False)  # 实体ID
    ip_address = db.Column(db.String(45))  # 访问者IP地址（支持IPv6）
    user_agent = db.Column(db.String(500))  # 用户代理信息
    referer = db.Column(db.String(500))  # 来源页面
    create_time = db.Column(db.DateTime, default=datetime.now)  # 访问时间
    
    # 复合索引，提高查询性能
    __table_args__ = (
        db.Index('idx_entity_user', 'entity_type', 'entity_id', 'user_id'),
        db.Index('idx_entity_time', 'entity_type', 'entity_id', 'create_time'),
    )