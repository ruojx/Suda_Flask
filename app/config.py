import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(PROJECT_ROOT, 'instance', 'project.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 密钥 (用于 JWT)
    SECRET_KEY = 'your-super-secret-key-change-it'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'uploads')
    # 静态文件 URL 前缀 (对应 application.yml 中的 server context path 或 nginx 配置)
    # 本地开发直接用 host
    BASE_URL = "http://localhost:5000"
    
    # JSON 配置
    JSON_AS_ASCII = False