from flask import g

def get_current_user_id():
    # 从 Flask 全局对象 g 中获取 user_id (由中间件注入)
    return getattr(g, 'user_id', None)