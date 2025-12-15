from . import BaseModel, db

class Conversation(BaseModel):
    __tablename__ = 'conversation'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10)) # group, dm
    name = db.Column(db.String(200))
    owner_id = db.Column(db.Integer)
    dm_key = db.Column(db.String(64), unique=True) # min#max
    is_active = db.Column(db.Integer, default=1)

class ConversationMember(BaseModel):
    __tablename__ = 'conversation_member'
    __table_args__ = (db.PrimaryKeyConstraint('conversation_id', 'user_id'),)
    conversation_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    role = db.Column(db.String(10), default='member')
    last_read_msg_id = db.Column(db.Integer, default=0)
    join_time = db.Column(db.DateTime, default=db.func.now())

class Message(BaseModel):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, index=True)
    sender_id = db.Column(db.Integer)
    kind = db.Column(db.String(10), default='text')
    content = db.Column(db.Text)
    file_url = db.Column(db.String(500))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    reply_to_id = db.Column(db.Integer)