
from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.utils.result import Result
from app.schemas.responses import LoginVOSchema
from app.schemas.requests import ResetDTOSchema # 记得导入 Schema

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    res = AuthService.login(data.get('username'), data.get('password'))
    if res:
        return Result.success(LoginVOSchema().dump(res))
    return Result.error("用户名或密码错误")

# 【核心修改】复刻 Java 的 /reset 接口
@auth_bp.route('/reset', methods=['PUT'])
def reset():
    try:
        # 1. 解析参数
        data = ResetDTOSchema().load(request.get_json())
        
        # 2. 调用通用的重置逻辑
        rows = AuthService.reset(data)
        
        if rows > 0:
            return Result.success()
        else:
            return Result.error("更新失败，请检查信息")
            
    except Exception as e:
        return Result.error(str(e))