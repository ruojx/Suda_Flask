from flask import request, jsonify, g, current_app
from app.utils.jwt_utils import parse_token
from app.models.user import User
from app.utils.jwt_utils import create_token
from app.extensions import db

# 白名单路径
WHITELIST = ["/login", "/register", "/static", "/api/feed/list"]

def auth_middleware():
    """ 鉴权中间件 """
    path = request.path
    if request.method == 'OPTIONS': return None
    
    # 白名单放行
    for w in WHITELIST:
        if path.startswith(w):
            return None

    token = request.headers.get('token')
    if not token:
        return jsonify({"code": 0, "msg": "未登录"}), 401

    payload = parse_token(token)
    if not payload:
        return jsonify({"code": 0, "msg": "Token失效"}), 401
    
    # 存入 Flask 全局变量
    g.user_id = payload.get('id')

class AuthService:
    @staticmethod
    def login(username, password):
        user = User.query.filter_by(username=username, password=password).first()
        if not user: return None
        token = create_token(user.id)
        return {
            "id": user.id, "username": user.username, "name": user.name,
            "phone": user.phone, "avatar": user.avatar, "token": token
        }