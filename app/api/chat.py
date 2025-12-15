from flask import Blueprint, request
from app.services.chat_service import ChatService
from app.utils.result import Result
from app.utils.context import get_current_user_id
from app.schemas.responses import ConversationSchema, MessageSchema

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/groups', methods=['GET'])
def list_groups():
    uid = get_current_user_id()
    data = ChatService.list_groups(uid)
    return Result.success(ConversationSchema(many=True).dump(data))

@chat_bp.route('/send', methods=['POST'])
def send():
    d = request.get_json()
    uid = get_current_user_id()
    msg = ChatService.send_msg(uid, d.get('type'), d.get('groupId'), d.get('toUserId'), d.get('content'))
    return Result.success("发送成功")