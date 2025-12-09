from app import create_app, db
from app.models.user import User
from app.models.content import Post, Topic
from app.models.resource import Resource
from app.models.community import Question, Answer # 假设你建了这个文件，如果没有可以删掉这两行
from datetime import datetime
import os

app = create_app()

def init_db_data():
    """初始化测试数据"""
    
    # --- 1. 初始化用户 (User) ---
    if not User.query.first():
        print("⚡️ 正在初始化用户数据...")
        users = [
            User(id=1, username='1', password='1', name='管理员', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=1', introduction='我是管理员'),
            User(id=2, username='2', password='2', name='李四', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=2', introduction='热爱前端'),
            User(id=3, username='3', password='3', name='王五', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=3', introduction='后端架构师'),
            User(id=4, username='4', password='4', name='赵六', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=4', introduction='AI 研究员'),
            User(id=5, username='5', password='5', name='孙七', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=5', introduction='全栈开发者'),
        ]
        db.session.add_all(users)
        db.session.commit()
        print(f"✅ 已创建 {len(users)} 个用户")

    # --- 2. 初始化帖子 (Post) ---
    if not Post.query.first():
        print("⚡️ 正在初始化帖子数据...")
        posts = [
            Post(user_id=1, author_name='管理员', title='Vue3和Spring Boot全栈开发体验', content='这是详细内容...', summary='Vue3和Spring Boot全栈开发体验分享', view_count=150, like_count=25, tags='Vue3,Spring Boot,全栈', create_time=datetime.now()),
            Post(user_id=2, author_name='李四', title='如何设计一个高可用的后端系统', content='这是详细内容...', summary='高可用后端系统设计原则和实践', view_count=300, like_count=45, tags='后端,高可用', create_time=datetime.now()),
            Post(user_id=3, author_name='王五', title='前端性能优化实战指南', content='这是详细内容...', summary='前端性能优化的各种技巧', view_count=200, like_count=35, tags='前端,性能优化', create_time=datetime.now()),
            Post(user_id=4, author_name='赵六', title='Docker容器化部署入门', content='这是详细内容...', summary='Docker基础与生产环境实践', view_count=180, like_count=20, tags='Docker,DevOps', create_time=datetime.now()),
            Post(user_id=5, author_name='孙七', title='Python数据分析入门', content='这是详细内容...', summary='Pandas与NumPy基础教程', view_count=220, like_count=35, tags='Python,数据分析', create_time=datetime.now()),
            Post(user_id=1, author_name='管理员', title='Kubernetes集群管理', content='这是详细内容...', summary='K8s架构与运维实践', view_count=300, like_count=42, tags='Kubernetes,云原生', create_time=datetime.now()),
        ]
        db.session.add_all(posts)
        db.session.commit()
        print(f"✅ 已创建 {len(posts)} 篇帖子")

    # --- 3. 初始化话题 (Topic) ---
    if not Topic.query.first():
        print("⚡️ 正在初始化话题数据...")
        topics = [
            Topic(user_id=1, author_name='管理员', title='全栈开发', summary='全栈开发相关讨论', view_count=500, like_count=10, post_count=50),
            Topic(user_id=2, author_name='李四', title='后端架构', summary='后端架构设计与实践', view_count=800, like_count=20, post_count=80),
            Topic(user_id=3, author_name='王五', title='前端框架', summary='前端框架比较和最佳实践', view_count=600, like_count=30, post_count=60),
            Topic(user_id=4, author_name='赵六', title='人工智能', summary='机器学习与深度学习', view_count=950, like_count=80, post_count=120),
            Topic(user_id=5, author_name='孙七', title='云计算', summary='AWS与阿里云实战', view_count=320, like_count=15, post_count=25),
        ]
        db.session.add_all(topics)
        db.session.commit()
        print(f"✅ 已创建 {len(topics)} 个话题")

    # --- 4. 初始化资源 (Resource) ---
    if not Resource.query.first():
        print("⚡️ 正在初始化资源数据...")
        resources = [
            Resource(user_id=1, title='Spring Boot 学习笔记', description='入门文档含代码', type='pdf', url='https://pdfobject.com/pdf/sample.pdf', size=102400, tags='Java,Spring', view_count=100, create_time=datetime.now()),
            Resource(user_id=2, title='深度学习数据集', description='图像分类数据集', type='zip', url='#', size=2048000, tags='AI,Data', view_count=200, create_time=datetime.now()),
            Resource(user_id=3, title='Vue3 前端分享PPT', description='技术分享课件', type='pptx', url='#', size=51200, tags='Vue,前端', view_count=50, create_time=datetime.now()),
            Resource(user_id=4, title='React 官方文档', description='React官方学习资料', type='link', url='https://react.dev/', size=0, tags='React,文档', view_count=500, create_time=datetime.now()),
        ]
        db.session.add_all(resources)
        db.session.commit()
        print(f"✅ 已创建 {len(resources)} 个资源")

if __name__ == '__main__':
    # 确保上传目录存在
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    with app.app_context():
        # 1. 创建表结构
        db.create_all()
        
        # 2. 插入所有初始数据
        try:
            init_db_data()
        except Exception as e:
            print(f"❌ 数据初始化部分失败 (可能是部分表已存在数据): {e}")

    print("🚀 服务已启动: http://0.0.0.0:5000")
    print("👉 测试账号: 1 / 密码: 1")
    app.run(debug=True, host='0.0.0.0', port=5000)