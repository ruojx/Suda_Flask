# app/services/user_service.py
from app.models.user import User
from app.extensions import db

class UserService:
    @staticmethod
    def get_info(user_id):
        """获取当前用户信息"""
        user = User.query.get(user_id)
        if not user:
            return None
        # 返回字典，对应 LoginVO 或者是 UserSimple 的结构
        return {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "phone": user.phone,
            "email": user.email,
            "avatar": user.avatar,
            "introduction": user.introduction
        }

    @staticmethod
    def update_info(user_id, data):
        """更新用户信息"""
        user = User.query.get(user_id)
        if not user:
            raise Exception("用户不存在")
        
        # 逐个字段更新，如果有传值的话
        if 'name' in data: user.name = data['name']
        if 'avatar' in data: user.avatar = data['avatar']
        if 'introduction' in data: user.introduction = data['introduction']
        if 'phone' in data: user.phone = data['phone']
        if 'email' in data: user.email = data['email']
        
        db.session.commit()
        return UserService.get_info(user_id) # 返回更新后的最新信息