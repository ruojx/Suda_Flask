from flask import Blueprint, request
from app.services.feedService import FeedService
from app.utils.result import Result
from app.utils.context import get_current_user_id
from app.schemas.requests import PostRequestSchema, TopicRequestSchema
from app.schemas.responses import FeedSchema
from datetime import datetime

feed_bp = Blueprint('feed', __name__, url_prefix='/api/feed')

@feed_bp.route('/list', methods=['GET'])
def list_feed():
    tab = request.args.get('tab', 'post')
    sort = request.args.get('sort', 'hot')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    
    data = FeedService.get_feed_list(tab, sort, page, size)
    # data 中已经是 list 字典，并包含 type，直接使用 Schema 序列化 list 部分
    # 但由于 data 结构复杂 (PageInfo)，这里直接返回字典结构，仅对 list 内部元素序列化
    serialized_list = FeedSchema(many=True).dump(data['list'])
    data['list'] = serialized_list # 替换为前端需要的驼峰格式
    
    return Result.success(data)

@feed_bp.route('/post', methods=['POST'])
def create_post():
    data = PostRequestSchema().load(request.get_json())
    pid = FeedService.create_post(data)
    return Result.success({"id": pid})

@feed_bp.route('/topic', methods=['POST'])
def create_topic():
    data = TopicRequestSchema().load(request.get_json())
    tid = FeedService.create_topic(data)
    return Result.success({"id": tid})

@feed_bp.route('/follow', methods=['GET'])
def get_user_follows():
    """
    获取用户关注的话题
    """
    user_id = request.args.get('userId')
    
    if not user_id:
        # 尝试从token获取
        user_id = get_current_user_id()
        
    if not user_id:
        return Result.error('请先登录')
    
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    
    # 获取用户关注的话题
    from app.models.feedModels import FeedFollow, Topic
    from sqlalchemy import desc
    
    # 获取用户关注的话题ID
    follows = FeedFollow.query.filter_by(
        user_id=user_id,
        status=1
    ).all()
    
    topic_ids = [follow.entity_id for follow in follows]
    
    if not topic_ids:
        return Result.success({
            "list": [],
            "pageNum": page,
            "pageSize": size,
            "total": 0,
            "pages": 0,
            "isFirstPage": True,
            "isLastPage": True
        })
    
    # 查询话题
    query = Topic.query.filter(
        Topic.id.in_(topic_ids),
        Topic.status == 1
    ).order_by(desc(Topic.create_time))
    
    pagination = query.paginate(page=page, per_page=size, error_out=False)
    
    # 格式化结果
    items = []
    for item in pagination.items:
        d = {c.name: getattr(item, c.name) for c in item.__table__.columns}
        d['type'] = 'topic'
        items.append(d)
    
    data = {
        "list": items,
        "pageNum": pagination.page,
        "pageSize": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "isFirstPage": pagination.page == 1,
        "isLastPage": pagination.page == pagination.pages
    }
    
    serialized_list = FeedSchema(many=True).dump(data['list'])
    data['list'] = serialized_list
    
    return Result.success(data)

@feed_bp.route('/post/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    from app.models.feedModels import Post
    
    post = Post.query.get(post_id)
    
    if not post or post.status != 1:
        return Result.error('帖子不存在')
    
    # 增加浏览数
    post.view_count = (post.view_count or 0) + 1
    
    # 创建浏览记录
    from app.models.feedModels import FeedView
    from flask import request
    
    view_record = FeedView(
        user_id=get_current_user_id() or 0,
        entity_type=1,
        entity_id=post_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', ''),
        referer=request.headers.get('Referer', '')
    )
    
    from app.extensions import db
    db.session.add(view_record)
    db.session.commit()
    
    # 返回帖子详情
    post_data = {c.name: getattr(post, c.name) for c in post.__table__.columns}
    post_data['type'] = 'post'
    
    serialized_post = FeedSchema().dump(post_data)
    
    return Result.success(serialized_post)

@feed_bp.route('/topic/<int:topic_id>', methods=['GET'])
def get_topic_detail(topic_id):
    from app.models.feedModels import Topic
    
    topic = Topic.query.get(topic_id)
    
    if not topic or topic.status != 1:
        return Result.error('话题不存在')
    
    # 增加浏览数
    topic.view_count = (topic.view_count or 0) + 1
    
    # 创建浏览记录
    from app.models.feedModels import FeedView
    from flask import request
    
    view_record = FeedView(
        user_id=get_current_user_id() or 0,
        entity_type=2,
        entity_id=topic_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', ''),
        referer=request.headers.get('Referer', '')
    )
    
    from app.extensions import db
    db.session.add(view_record)
    db.session.commit()
    
    # 返回话题详情
    topic_data = {c.name: getattr(topic, c.name) for c in topic.__table__.columns}
    topic_data['type'] = 'topic'
    
    serialized_topic = FeedSchema().dump(topic_data)
    
    return Result.success(serialized_topic)

@feed_bp.route('/post/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    from app.models.feedModels import Post
    from app.extensions import db
    
    post = Post.query.get(post_id)
    
    if not post:
        return Result.error('帖子不存在')
    
    # 检查权限
    user_id = get_current_user_id()
    if not user_id or post.user_id != user_id:
        return Result.error('无权修改此帖子')
    
    data = request.get_json()
    
    # 更新字段
    if 'title' in data:
        post.title = data['title']
    if 'content' in data:
        post.content = data['content']
    if 'summary' in data:
        post.summary = data['summary']
    if 'tags' in data:
        post.tags = data['tags']
    
    post.update_time = datetime.now()
    db.session.commit()
    
    return Result.success("更新成功")

@feed_bp.route('/topic/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    from app.models.feedModels import Topic
    from app.extensions import db
    from datetime import datetime
    
    topic = Topic.query.get(topic_id)
    
    if not topic:
        return Result.error('话题不存在')
    
    # 检查权限
    user_id = get_current_user_id()
    if not user_id or topic.user_id != user_id:
        return Result.error('无权修改此话题')
    
    data = request.get_json()
    
    # 更新字段
    if 'title' in data:
        topic.title = data['title']
    if 'summary' in data:
        topic.summary = data['summary']
    
    topic.update_time = datetime.now()
    db.session.commit()
    
    return Result.success("更新成功")

@feed_bp.route('/post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    from app.models.feedModels import Post
    from app.extensions import db
    
    post = Post.query.get(post_id)
    
    if not post:
        return Result.error('帖子不存在')
    
    # 检查权限
    user_id = get_current_user_id()
    if not user_id or post.user_id != user_id:
        return Result.error('无权删除此帖子')
    
    # 软删除
    post.status = 0
    db.session.commit()
    
    return Result.success("删除成功")

@feed_bp.route('/topic/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    from app.models.feedModels import Topic
    from app.extensions import db
    
    topic = Topic.query.get(topic_id)
    
    if not topic:
        return Result.error('话题不存在')
    
    # 检查权限
    user_id = get_current_user_id()
    if not user_id or topic.user_id != user_id:
        return Result.error('无权删除此话题')
    
    # 软删除
    topic.status = 0
    db.session.commit()
    
    return Result.success("删除成功")