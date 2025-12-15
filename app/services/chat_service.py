from app.models.im import Conversation, ConversationMember, Message
from app.extensions import db
from datetime import datetime

class ChatService:
    @staticmethod
    def get_dm_id(u1, u2):
        key = f"{min(u1, u2)}#{max(u1, u2)}"
        conv = Conversation.query.filter_by(dm_key=key).first()
        if not conv:
            conv = Conversation(type='dm', dm_key=key, is_active=1)
            db.session.add(conv)
            db.session.flush()
            db.session.add(ConversationMember(conversation_id=conv.id, user_id=u1))
            db.session.add(ConversationMember(conversation_id=conv.id, user_id=u2))
            db.session.commit()
        return conv.id

    @staticmethod
    def list_groups(user_id):
        return db.session.query(Conversation).join(
            ConversationMember, Conversation.id == ConversationMember.conversation_id
        ).filter(
            ConversationMember.user_id == user_id,
            Conversation.type == 'group',
            Conversation.is_active == 1
        ).all()

    @staticmethod
    def send_msg(sender_id, type, group_id, to_user_id, content, kind='text'):
        conv_id = group_id if type == 'group' else ChatService.get_dm_id(sender_id, to_user_id)
        msg = Message(
            conversation_id=conv_id, sender_id=sender_id, 
            kind=kind, content=content, create_time=datetime.now()
        )
        db.session.add(msg)
        db.session.commit()
        return msg