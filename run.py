from app import create_app, db
from app.models.user import User
from app.models.feedModels import Post, Topic, FeedLike, FeedCollect, FeedFollow, FeedComment, PostTopicRelation, FeedView
from app.models.resource import Resource, ResourceLike, ResourceFavorite
from app.models.im import Conversation, ConversationMember, Message
from datetime import datetime, timedelta
import os
import random

app = create_app()

def init_db_data():
    """初始化测试数据"""
    
    # --- 1. 初始化用户 (User) ---
    if not User.query.first():
        print("⚡️ 正在初始化用户数据...")
        users = [
            User(id=11, username='11', password='11', name='用户11', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=11', introduction='用户11的介绍'),
            User(id=22, username='22', password='22', name='用户22', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=22', introduction='用户22的介绍'),
            User(id=33, username='33', password='33', name='用户33', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=33', introduction='用户33的介绍'),
            User(id=44, username='44', password='44', name='用户44', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=44', introduction='用户44的介绍'),
            User(id=55, username='55', password='55', name='用户55', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=55', introduction='用户55的介绍'),
            User(id=66, username='66', password='66', name='用户66', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=66', introduction='用户66的介绍'),
            User(id=77, username='77', password='77', name='用户77', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=77', introduction='用户77的介绍'),
            User(id=88, username='88', password='88', name='用户88', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=88', introduction='用户88的介绍'),
            User(id=99, username='99', password='99', name='用户99', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=99', introduction='用户99的介绍'),
            User(id=111, username='111', password='111', name='用户111', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=111', introduction='用户111的介绍'),
            User(id=222, username='222', password='222', name='用户222', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=222', introduction='用户222的介绍'),
            User(id=333, username='333', password='333', name='用户333', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=333', introduction='用户333的介绍'),
            User(id=444, username='444', password='444', name='用户444', avatar='https://api.dicebear.com/7.x/miniavs/svg?seed=444', introduction='用户444的介绍'),
        ]
        db.session.add_all(users)
        db.session.commit()
        print(f"✅ 已创建 {len(users)} 个用户")

    # --- 2. 初始化话题 (Topic) ---
    if not Topic.query.first():
        print("⚡️ 正在初始化话题数据...")
        topics = [
            Topic(id=1, user_id=11, author_name='用户11', title='全栈开发', summary='全栈开发相关讨论', view_count=500, like_count=10, follow_count=120, post_count=50, create_time=datetime.now()),
            Topic(id=2, user_id=22, author_name='用户22', title='后端架构', summary='后端架构设计与实践', view_count=800, like_count=20, follow_count=200, post_count=80, create_time=datetime.now()),
            Topic(id=3, user_id=33, author_name='用户33', title='前端框架', summary='前端框架比较和最佳实践', view_count=600, like_count=30, follow_count=150, post_count=60, create_time=datetime.now()),
            Topic(id=4, user_id=44, author_name='用户44', title='云计算入门', summary='云计算基础概念与应用场景', view_count=320, like_count=15, follow_count=80, post_count=25, create_time=datetime.now()),
            Topic(id=5, user_id=55, author_name='用户55', title='机器学习实战', summary='机器学习算法与实际案例解析', view_count=950, like_count=80, follow_count=300, post_count=120, create_time=datetime.now()),
            Topic(id=6, user_id=66, author_name='用户66', title='网络安全基础', summary='常见网络攻击与防御措施', view_count=420, like_count=25, follow_count=90, post_count=40, create_time=datetime.now()),
            Topic(id=7, user_id=77, author_name='用户77', title='DevOps实践', summary='自动化部署与持续集成', view_count=680, like_count=45, follow_count=180, post_count=75, create_time=datetime.now()),
            Topic(id=8, user_id=88, author_name='用户88', title='区块链技术', summary='去中心化应用与智能合约', view_count=550, like_count=30, follow_count=120, post_count=50, create_time=datetime.now()),
            Topic(id=9, user_id=99, author_name='用户99', title='大数据分析', summary='Hadoop与Spark实战指南', view_count=870, like_count=60, follow_count=220, post_count=95, create_time=datetime.now()),
            Topic(id=10, user_id=111, author_name='用户111', title='移动端开发', summary='iOS与Android开发对比', view_count=610, like_count=35, follow_count=150, post_count=60, create_time=datetime.now()),
            Topic(id=11, user_id=222, author_name='用户222', title='微服务架构', summary='分布式系统设计模式', view_count=780, like_count=50, follow_count=200, post_count=85, create_time=datetime.now()),
            Topic(id=12, user_id=333, author_name='用户333', title='人工智能伦理', summary='AI发展中的道德问题探讨', view_count=290, like_count=12, follow_count=70, post_count=30, create_time=datetime.now()),
            Topic(id=13, user_id=444, author_name='用户444', title='物联网应用', summary='智能家居与工业物联网案例', view_count=500, like_count=28, follow_count=110, post_count=45, create_time=datetime.now()),
        ]
        db.session.add_all(topics)
        db.session.commit()
        print(f"✅ 已创建 {len(topics)} 个话题")

    # --- 3. 初始化帖子 (Post) ---
    if not Post.query.first():
        print("⚡️ 正在初始化帖子数据...")
        posts = [
            Post(id=1, user_id=11, author_name='用户11', title='Vue3和Spring Boot全栈开发体验', content='详细内容...', summary='Vue3和Spring Boot全栈开发体验分享', view_count=150, like_count=25, comment_count=10, collect_count=5, tags='Vue3,Spring Boot,全栈', topic_id=1, create_time=datetime.now()),
            Post(id=2, user_id=22, author_name='用户22', title='如何设计一个高可用的后端系统', content='详细内容...', summary='高可用后端系统设计原则和实践', view_count=300, like_count=45, comment_count=20, collect_count=15, tags='后端,高可用,设计原则', topic_id=2, create_time=datetime.now()),
            Post(id=3, user_id=33, author_name='用户33', title='前端性能优化实战指南', content='详细内容...', summary='前端性能优化的各种技巧和方法', view_count=200, like_count=35, comment_count=15, collect_count=8, tags='前端,性能优化,技巧', topic_id=3, create_time=datetime.now()),
            Post(id=4, user_id=44, author_name='用户44', title='Docker容器化部署', content='详细内容...', summary='Docker基础与生产环境实践', view_count=180, like_count=20, comment_count=8, collect_count=6, tags='Docker,容器,DevOps', topic_id=4, create_time=datetime.now()),
            Post(id=5, user_id=55, author_name='用户55', title='Python数据分析入门', content='详细内容...', summary='Pandas与NumPy基础教程', view_count=220, like_count=35, comment_count=12, collect_count=10, tags='Python,数据分析,教程', topic_id=5, create_time=datetime.now()),
            Post(id=6, user_id=66, author_name='用户66', title='密码学基础', content='详细内容...', summary='加密算法与安全协议', view_count=150, like_count=18, comment_count=5, collect_count=4, tags='密码学,安全,加密', topic_id=6, create_time=datetime.now()),
            Post(id=7, user_id=77, author_name='用户77', title='Kubernetes集群管理', content='详细内容...', summary='K8s架构与运维实践', view_count=300, like_count=42, comment_count=15, collect_count=12, tags='Kubernetes,运维,云原生', topic_id=7, create_time=datetime.now()),
            Post(id=8, user_id=88, author_name='用户88', title='智能合约开发', content='详细内容...', summary='Solidity与以太坊实战', view_count=250, like_count=30, comment_count=10, collect_count=8, tags='区块链,智能合约,Solidity', topic_id=8, create_time=datetime.now()),
            Post(id=9, user_id=99, author_name='用户99', title='Hive数据仓库', content='详细内容...', summary='HQL查询与优化技巧', view_count=190, like_count=22, comment_count=7, collect_count=5, tags='Hadoop,Hive,大数据', topic_id=9, create_time=datetime.now()),
            Post(id=10, user_id=111, author_name='用户111', title='React Native跨端开发', content='详细内容...', summary='React Native核心原理', view_count=210, like_count=28, comment_count=9, collect_count=7, tags='React Native,跨端,移动开发', topic_id=10, create_time=datetime.now()),
            Post(id=11, user_id=222, author_name='用户222', title='服务网格Istio', content='详细内容...', summary='Istio流量管理实战', view_count=270, like_count=38, comment_count=14, collect_count=11, tags='Istio,微服务,云原生', topic_id=11, create_time=datetime.now()),
            Post(id=12, user_id=333, author_name='用户333', title='AI与隐私保护', content='详细内容...', summary='联邦学习与差分隐私', view_count=130, like_count=15, comment_count=4, collect_count=3, tags='人工智能,隐私,伦理', topic_id=12, create_time=datetime.now()),
            Post(id=13, user_id=444, author_name='用户444', title='5G与物联网', content='详细内容...', summary='5G在物联网中的应用', view_count=230, like_count=25, comment_count=8, collect_count=6, tags='5G,物联网,通信', topic_id=13, create_time=datetime.now()),
        ]
        db.session.add_all(posts)
        db.session.commit()
        print(f"✅ 已创建 {len(posts)} 篇帖子")

    # --- 4. 初始化帖子-话题关联 (PostTopicRelation) ---
    if not PostTopicRelation.query.first():
        print("⚡️ 正在初始化帖子-话题关联数据...")
        relations = [
            PostTopicRelation(post_id=1, topic_id=1),  # 帖子1属于话题1
            PostTopicRelation(post_id=1, topic_id=2),  # 帖子1也属于话题2
            PostTopicRelation(post_id=2, topic_id=2),  # 帖子2属于话题2
            PostTopicRelation(post_id=3, topic_id=3),  # 帖子3属于话题3
            # 为其他帖子添加关联（每个帖子一个话题）
            PostTopicRelation(post_id=4, topic_id=4),
            PostTopicRelation(post_id=5, topic_id=5),
            PostTopicRelation(post_id=6, topic_id=6),
            PostTopicRelation(post_id=7, topic_id=7),
            PostTopicRelation(post_id=8, topic_id=8),
            PostTopicRelation(post_id=9, topic_id=9),
            PostTopicRelation(post_id=10, topic_id=10),
            PostTopicRelation(post_id=11, topic_id=11),
            PostTopicRelation(post_id=12, topic_id=12),
            PostTopicRelation(post_id=13, topic_id=13),
        ]
        db.session.add_all(relations)
        db.session.commit()
        print(f"✅ 已创建 {len(relations)} 条帖子-话题关联")

    # --- 5. 初始化点赞数据 (FeedLike) ---
    if not FeedLike.query.first():
        print("⚡️ 正在初始化点赞数据...")
        likes = [
            FeedLike(user_id=11, entity_type=1, entity_id=1, status=1),  # 用户11点赞帖子1
            FeedLike(user_id=22, entity_type=1, entity_id=1, status=1),  # 用户22点赞帖子1
            FeedLike(user_id=33, entity_type=1, entity_id=1, status=1),  # 用户33点赞帖子1
            FeedLike(user_id=11, entity_type=1, entity_id=2, status=1),  # 用户11点赞帖子2
            FeedLike(user_id=22, entity_type=1, entity_id=3, status=1),  # 用户22点赞帖子3
            # 话题点赞
            FeedLike(user_id=11, entity_type=2, entity_id=1, status=1),  # 用户11点赞话题1
            FeedLike(user_id=22, entity_type=2, entity_id=2, status=1),  # 用户22点赞话题2
            FeedLike(user_id=33, entity_type=2, entity_id=3, status=1),  # 用户33点赞话题3
        ]
        db.session.add_all(likes)
        db.session.commit()
        print(f"✅ 已创建 {len(likes)} 条点赞记录")

    # --- 6. 初始化收藏数据 (FeedCollect) ---
    if not FeedCollect.query.first():
        print("⚡️ 正在初始化收藏数据...")
        collects = [
            FeedCollect(user_id=11, entity_id=1, status=1),  # 用户11收藏帖子1
            FeedCollect(user_id=22, entity_id=2, status=1),  # 用户22收藏帖子2
            FeedCollect(user_id=33, entity_id=3, status=1),  # 用户33收藏帖子3
        ]
        db.session.add_all(collects)
        db.session.commit()
        print(f"✅ 已创建 {len(collects)} 条收藏记录")

    # --- 7. 初始化关注数据 (FeedFollow) ---
    if not FeedFollow.query.first():
        print("⚡️ 正在初始化关注数据...")
        follows = [
            FeedFollow(user_id=11, entity_id=1, status=1),  # 用户11关注话题1
            FeedFollow(user_id=22, entity_id=2, status=1),  # 用户22关注话题2
            FeedFollow(user_id=33, entity_id=3, status=1),  # 用户33关注话题3
        ]
        db.session.add_all(follows)
        db.session.commit()
        print(f"✅ 已创建 {len(follows)} 条关注记录")

    # --- 8. 初始化评论数据 (FeedComment) ---
    if not FeedComment.query.first():
        print("⚡️ 正在初始化评论数据...")
        comments = [
            FeedComment(user_id=22, entity_type=1, entity_id=1, content='这篇文章很有帮助，谢谢分享！', like_count=5, create_time=datetime.now()),
            FeedComment(user_id=33, entity_type=1, entity_id=1, content='学到了很多新知识', like_count=3, create_time=datetime.now()),
            FeedComment(user_id=11, entity_type=1, entity_id=2, content='很实用的设计原则', like_count=8, create_time=datetime.now()),
        ]
        db.session.add_all(comments)
        db.session.commit()
        print(f"✅ 已创建 {len(comments)} 条评论记录")

    # --- 9. 初始化访问记录数据 (FeedView) ---
    if not FeedView.query.first():
        print("⚡️ 正在初始化访问记录数据...")
        # 为部分帖子和话题添加初始访问记录
        
        view_records = []
        
        # 为每个帖子添加一些访问记录
        posts = Post.query.all()
        for post in posts:
            # 每个帖子有 10-50 次访问记录
            for _ in range(random.randint(10, 50)):
                # 随机选择一个用户（可能包括未登录用户 user_id=0）
                user_id = random.choice([0, 11, 22, 33, 44, 55])
                
                # 随机生成访问时间（过去30天内）
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                access_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                
                view_records.append(
                    FeedView(
                        user_id=user_id,
                        entity_type=1,  # 帖子
                        entity_id=post.id,
                        ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                        user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(500, 600)}.36",
                        referer=f"https://example.com/page{random.randint(1, 10)}",
                        create_time=access_time
                    )
                )
        
        # 为每个话题添加一些访问记录
        topics = Topic.query.all()
        for topic in topics:
            # 每个话题有 20-100 次访问记录
            for _ in range(random.randint(20, 100)):
                # 随机选择一个用户
                user_id = random.choice([0, 11, 22, 33, 44, 55])
                
                # 随机生成访问时间
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                access_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                
                view_records.append(
                    FeedView(
                        user_id=user_id,
                        entity_type=2,  # 话题
                        entity_id=topic.id,
                        ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                        user_agent=f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/{random.randint(500, 600)}.36",
                        referer=f"https://example.com/topic{random.randint(1, 10)}",
                        create_time=access_time
                    )
                )
        
        # 批量插入访问记录
        batch_size = 100
        for i in range(0, len(view_records), batch_size):
            batch = view_records[i:i+batch_size]
            db.session.add_all(batch)
            db.session.flush()  # 分批提交，避免内存占用过高
        
        db.session.commit()
        print(f"✅ 已创建 {len(view_records)} 条访问记录")
        
        # 更新帖子和话题的 view_count（与实际访问记录保持一致）
        print("⚡️ 正在更新帖子和话题的访问量统计...")
        
        # 更新帖子的 view_count
        posts = Post.query.all()
        for post in posts:
            view_count = FeedView.query.filter_by(entity_type=1, entity_id=post.id).count()
            post.view_count = view_count
        
        # 更新话题的 view_count
        topics = Topic.query.all()
        for topic in topics:
            view_count = FeedView.query.filter_by(entity_type=2, entity_id=topic.id).count()
            topic.view_count = view_count
        
        db.session.commit()
        print("✅ 已更新帖子和话题的访问量统计")

    # --- 10. 初始化资源 (Resource) ---
    if not Resource.query.first():
        print("⚡️ 正在初始化资源数据...")
        resources = [
            Resource(user_id=11, title='Spring Boot 学习笔记', description='入门文档含代码', type='pdf', url='https://pdfobject.com/pdf/sample.pdf', size=102400, tags='Java,Spring', view_count=100, create_time=datetime.now()),
            Resource(user_id=22, title='深度学习数据集', description='图像分类数据集', type='zip', url='#', size=2048000, tags='AI,Data', view_count=200, create_time=datetime.now()),
            Resource(user_id=33, title='Vue3 前端分享PPT', description='技术分享课件', type='pptx', url='#', size=51200, tags='Vue,前端', view_count=50, create_time=datetime.now()),
            Resource(user_id=44, title='React 官方文档', description='React官方学习资料', type='link', url='https://react.dev/', size=0, tags='React,文档', view_count=500, create_time=datetime.now()),
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
    print("👉 测试账号: 11 / 密码: 11")
    app.run(debug=True, host='0.0.0.0', port=5000)