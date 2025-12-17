# app/api/user.py
from flask import Blueprint, request
from app.services.user_service import UserService
from app.utils.result import Result
from app.utils.context import get_current_user_id
from app.schemas.requests import UserUpdateRequestSchema

# 定义路由前缀为 /api/user
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

# 1. 获取个人信息
# 前端请求：GET /api/user/info
@user_bp.route('/info', methods=['GET'])
def get_info():
    user_id = get_current_user_id()
    data = UserService.get_info(user_id)
    return Result.success(data)

# 2. 修改个人资料
# 前端请求：PUT /api/user/update
@user_bp.route('/update', methods=['PUT'])
def update_info():
    user_id = get_current_user_id()
    # 校验参数
    data = UserUpdateRequestSchema().load(request.get_json())
    
    try:
        new_info = UserService.update_info(user_id, data)
        return Result.success(new_info)
    except Exception as e:
        return Result.error(str(e))