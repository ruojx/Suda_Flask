from flask import request, jsonify, g, current_app
from app.utils.jwt_utils import parse_token
from app.models.user import User
from app.utils.jwt_utils import create_token
from app.extensions import db
# app/services/auth_service.py
from app.models.user import User
from app.extensions import db
from app.utils.jwt_utils import create_token

# 白名单路径
WHITELIST = [
    "/login", "/register", "/static", 
    "/api/feed/search", 
    "/api/feed/tags/hot", "/api/feed/post/<int:post_id>",
    "/api/feed/topic/<int:topic_id>"
]

# auth_service.py 中的 auth_middleware
def auth_middleware():
    """ 鉴权中间件 """
    path = request.path
    if request.method == 'OPTIONS': return None
    
    # 白名单放行
    for w in WHITELIST:
        if path.startswith(w):
            return None

    token = request.headers.get('token')
    print(f"DEBUG: 请求路径 {path} - token: {token[:20] if token else 'None'}")  # 调试
    
    if not token:
        return jsonify({"code": 0, "msg": "未登录"}), 401

    payload = parse_token(token)
    print(f"DEBUG: token解析结果: {payload}")  # 调试
    
    if not payload:
        return jsonify({"code": 0, "msg": "Token失效"}), 401
    
    # 存入 Flask 全局变量
    g.user_id = payload.get('id')
    print(f"DEBUG: 设置 g.user_id = {g.user_id}")  # 调试

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
    
    @staticmethod
    def reset(data):
        """
        对应 Java PublicServiceImpl.reset
        逻辑：如果没传手机号，就认为是“修改密码”（验证旧密码）；
              如果传了手机号，就认为是“重置密码”（验证身份）。
        """
        new_pwd = data.get('new_password')
        phone = data.get('phone')
        
        user = None
        
        # 1. 模式一：通过手机号找回 (Forgot Password)
        if phone:
            # 对应 updatePasswordByIdentifier
            identifier = data.get('identifier') # 用户名
            user = User.query.filter_by(username=identifier, phone=phone).first()
            if not user:
                return 0 # 用户不存在或手机号不匹配
                
            user.password = new_pwd
            db.session.commit()
            return 1
            
        # 2. 模式二：通过旧密码修改 (Change Password)
        else:
            # 对应 updatePassword
            # 必须校验 old_password 和 id
            uid = data.get('id')
            old_pwd = data.get('old_password')
            
            if not uid or not old_pwd:
                raise Exception("参数缺失：ID或旧密码为空")
                
            user = User.query.get(uid)
            if not user:
                return 0
            
            if user.password != old_pwd:
                raise Exception("旧密码错误")
                
            user.password = new_pwd
            db.session.commit()
            return 1