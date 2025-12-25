# app/api/user.py
from flask import Blueprint, request
from app.services.user_service import UserService
from app.utils.result import Result
from app.utils.context import get_current_user_id
from app.schemas.requests import UserUpdateRequestSchema
from app.schemas.requests import UserUpdateRequestSchema, PasswordUpdateSchema

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
    
# 【新增】修改密码接口
# 请求路径: PUT /api/user/password
@user_bp.route('/password', methods=['PUT'])
def update_password():
    user_id = get_current_user_id()
    
    try:
        # 1. 解析参数
        data = PasswordUpdateSchema().load(request.get_json())
        
        # 2. 调用业务逻辑
        # data['old_password'] 是由 Schema 转换后的蛇形命名
        UserService.update_password(user_id, data['old_password'], data['new_password'])
        
        return Result.success("密码修改成功")
    except Exception as e:
        return Result.error(str(e))
    
