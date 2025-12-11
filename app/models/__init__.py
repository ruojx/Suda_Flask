from app.extensions import db
from datetime import datetime

from .user import User
from .feedModels import Post, Topic, FeedLike, FeedCollect, FeedFollow, FeedComment, PostTopicRelation, FeedView
from .resource import Resource, ResourceLike, ResourceFavorite
from .im import Conversation, ConversationMember, Message

class BaseModel(db.Model):
    __abstract__ = True
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)