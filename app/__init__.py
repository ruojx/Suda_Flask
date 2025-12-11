from flask import Flask
from .config import Config
from .extensions import db, cors

def create_app():
    app = Flask(__name__, static_folder='../static', static_url_path='/static')
    app.config.from_object(Config)

    # 初始化插件
    db.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}}) # 允许所有跨域

    # 注册中间件
    from app.services.auth_service import auth_middleware
    app.before_request(auth_middleware)

    # 注册蓝图 (Controllers)
    from app.api.auth import auth_bp
    from app.api.feedController import feed_bp
    from app.api.resource import resource_bp
    from app.api.chat import chat_bp
    from app.api.feedInteractionController import interaction_bp
    from app.api.feedSearchController import feed_search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(resource_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(interaction_bp)
    app.register_blueprint(feed_search_bp)

    return app