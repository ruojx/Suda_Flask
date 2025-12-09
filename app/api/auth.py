from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.utils.result import Result
from app.schemas.responses import LoginVOSchema

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    res = AuthService.login(data.get('username'), data.get('password'))
    if res:
        return Result.success(LoginVOSchema().dump(res))
    return Result.error("用户名或密码错误")