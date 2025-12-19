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
    
    @staticmethod
    def update_password(user_id, old_pwd, new_pwd):
        """修改密码逻辑"""
        user = User.query.get(user_id)
        if not user:
            raise Exception("用户不存在")
            
        # 1. 校验旧密码 (注意：这里目前是明文比对，和你数据库现状一致)
        if user.password != old_pwd:
            raise Exception("原密码错误，请检查")
            
        # 2. 校验新密码不能和旧密码一样 (可选)
        if old_pwd == new_pwd:
            raise Exception("新密码不能与原密码相同")
            
        # 3. 更新密码
        user.password = new_pwd
        db.session.commit()
        
        return True