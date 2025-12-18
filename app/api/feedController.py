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
    
    # 获取当前用户ID（从token中获取）
    from app.utils.context import get_current_user_id
    current_user_id = get_current_user_id()
    
    print(f"DEBUG: 当前用户ID: {current_user_id}, tab: {tab}")  # 调试信息
    
    data = FeedService.get_feed_list(tab, sort, page, size, current_user_id)
    
    # 序列化结果
    serialized_list = FeedSchema(many=True).dump(data['list'])
    data['list'] = serialized_list
    
    # 调试输出，查看是否包含isFollowed字段
    if tab == 'topic' and current_user_id:
        print("=========================================")
        print(f"DEBUG: 话题列表序列化后检查isFollowed字段:")
        for i, item in enumerate(serialized_list):
            if item.get('type') == 'topic':
                print(f"  话题 {item.get('title')} - isFollowed: {item.get('isFollowed')}")
        print("=========================================")
    
    return Result.success(data)
@feed_bp.route('/follow', methods=['GET'])
def get_user_follows():
    """
    获取用户关注的话题
    """
    # 尝试从token获取用户ID
    from app.utils.context import get_current_user_id
    user_id = get_current_user_id()
    
    # 如果提供了userId参数，使用参数（管理员可能查看其他用户）
    request_user_id = request.args.get('userId')
    if request_user_id:
        try:
            user_id = int(request_user_id)
        except ValueError:
            pass
    
    if not user_id:
        return Result.error('请先登录')
    
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    
    # 获取用户关注的话题
    data = FeedService.get_feed_list('follow', 'time', page, size, user_id)
    
    serialized_list = FeedSchema(many=True).dump(data['list'])
    data['list'] = serialized_list
    
    return Result.success(data)
@feed_bp.route('/post', methods=['POST'])
def create_post():
    """
    创建帖子（支持关联话题）
    """
    try:
        data = PostRequestSchema().load(request.get_json())
        
        # 如果有话题ID，验证话题是否存在
        topic_id = data.get('topicId')
        if topic_id:
            from app.models.feedModels import Topic
            topic = Topic.query.filter_by(id=topic_id, status=1).first()
            if not topic:
                return Result.error('关联的话题不存在')
        
        pid = FeedService.create_post(data)
        return Result.success({"id": pid})
        
    except Exception as e:
        return Result.error(f"创建失败: {str(e)}")

@feed_bp.route('/topic', methods=['POST'])
def create_topic():
    data = TopicRequestSchema().load(request.get_json())
    tid = FeedService.create_topic(data)
    return Result.success({"id": tid})

# 在feedController.py中添加以下修改

@feed_bp.route('/post/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    from app.models.feedModels import Post, FeedView, FeedLike, FeedCollect
    from app.extensions import db
    from flask import request
    
    post = Post.query.get(post_id)
    
    if not post or post.status != 1:
        return Result.error('帖子不存在')
    
    # 增加浏览数
    post.view_count = (post.view_count or 0) + 1
    
    # 创建浏览记录
    view_record = FeedView(
        user_id=get_current_user_id() or 0,
        entity_type=1,
        entity_id=post_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', ''),
        referer=request.headers.get('Referer', '')
    )
    
    db.session.add(view_record)
    db.session.commit()
    
    # 获取帖子详情数据
    post_data = {c.name: getattr(post, c.name) for c in post.__table__.columns}
    post_data['type'] = 'post'
    
    # 获取用户的互动状态
    user_id = get_current_user_id()
    
    # 使用 camelCase 字段名，这是前端期待的格式
    if user_id:
        # 点赞状态
        like_record = FeedLike.query.filter_by(
            user_id=user_id,
            entity_type=1,
            entity_id=post_id,
            status=1
        ).first()
        post_data['isLiked'] = like_record is not None
        
        # 收藏状态
        collect_record = FeedCollect.query.filter_by(
            user_id=user_id,
            entity_id=post_id,
            status=1
        ).first()
        post_data['isCollected'] = collect_record is not None
    else:
        # 未登录用户
        post_data['isLiked'] = False
        post_data['isCollected'] = False
    
    # 转换字段名格式（确保字段名符合前端期望）
    # 将数据库的snake_case转换为camelCase
    field_mapping = {
        'user_id': 'userId',
        'author_name': 'authorName',
        'view_count': 'viewCount',
        'like_count': 'likeCount',
        'comment_count': 'commentCount',
        'collect_count': 'collectCount',
        'create_time': 'createTime',
        'update_time': 'updateTime'
    }
    
    formatted_data = {}
    for key, value in post_data.items():
        if key in field_mapping:
            formatted_data[field_mapping[key]] = value
        else:
            formatted_data[key] = value
    
    print(f"DEBUG: 帖子详情返回数据: {formatted_data}")
    
    return Result.success(formatted_data)

@feed_bp.route('/topic/<int:topic_id>', methods=['GET'])
def get_topic_detail(topic_id):
    from app.models.feedModels import Topic, FeedView, FeedLike, FeedFollow
    from app.extensions import db
    from flask import request
    
    topic = Topic.query.get(topic_id)
    
    if not topic or topic.status != 1:
        return Result.error('话题不存在')
    
    # 增加浏览数
    topic.view_count = (topic.view_count or 0) + 1
    
    # 创建浏览记录
    view_record = FeedView(
        user_id=get_current_user_id() or 0,
        entity_type=2,
        entity_id=topic_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', ''),
        referer=request.headers.get('Referer', '')
    )
    
    db.session.add(view_record)
    db.session.commit()
    
    # 获取话题详情数据
    topic_data = {c.name: getattr(topic, c.name) for c in topic.__table__.columns}
    topic_data['type'] = 'topic'
    
    # 获取用户的互动状态
    user_id = get_current_user_id()
    
    # 使用 camelCase 字段名
    if user_id:
        # 点赞状态
        like_record = FeedLike.query.filter_by(
            user_id=user_id,
            entity_type=2,
            entity_id=topic_id,
            status=1
        ).first()
        topic_data['isLiked'] = like_record is not None
        
        # 关注状态
        follow_record = FeedFollow.query.filter_by(
            user_id=user_id,
            entity_id=topic_id,
            status=1
        ).first()
        topic_data['isFollowed'] = follow_record is not None
    else:
        # 未登录用户
        topic_data['isLiked'] = False
        topic_data['isFollowed'] = False
    
    # 转换字段名格式
    field_mapping = {
        'user_id': 'userId',
        'author_name': 'authorName',
        'view_count': 'viewCount',
        'like_count': 'likeCount',
        'follow_count': 'followCount',
        'post_count': 'postCount',
        'create_time': 'createTime',
        'update_time': 'updateTime'
    }
    
    formatted_data = {}
    for key, value in topic_data.items():
        if key in field_mapping:
            formatted_data[field_mapping[key]] = value
        else:
            formatted_data[key] = value
    
    print(f"DEBUG: 话题详情返回数据: {formatted_data}")
    
    return Result.success(formatted_data)

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

# 添加在feedController.py中的合适位置
@feed_bp.route('/topic/<int:topic_id>/posts', methods=['GET'])
def get_topic_posts(topic_id):
    """
    获取话题下的帖子列表
    """
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        sort = request.args.get('sort', 'time')
        
        # 调用服务获取数据
        result = FeedService.get_topic_posts(topic_id, page, size, sort)
        
        if result["success"]:
            return Result.success(result["data"])
        else:
            return Result.error(result["message"])
            
    except Exception as e:
        return Result.error(f"获取话题帖子失败: {str(e)}")

@feed_bp.route('/post/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    """
    获取帖子的评论列表（分页版本）
    """
    try:
        from app.services.feedDetailService import FeedDetailService
        
        # 获取分页参数
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        
        # 获取评论列表
        result = FeedDetailService.get_post_comments(post_id, page, size)
        
        if result["success"]:
            return Result.success(result["data"])
        else:
            return Result.error(result["message"])
            
    except Exception as e:
        return Result.error(f"获取评论失败: {str(e)}")

@feed_bp.route('/interaction/status', methods=['GET'])
def get_interaction_status():
    """
    获取用户的互动状态
    """
    try:
        from app.services.feedDetailService import FeedDetailService
        
        # 获取参数
        entity_type = int(request.args.get('entity_type', 0))
        entity_id = int(request.args.get('entity_id', 0))
        
        if not entity_type or not entity_id:
            return Result.error('参数不完整')
        
        # 获取当前用户ID
        user_id = get_current_user_id()
        
        # 获取互动状态
        result = FeedDetailService.get_user_interaction_status(user_id, entity_type, entity_id)
        
        if result["success"]:
            return Result.success(result["data"])
        else:
            return Result.error(result["message"])
            
    except Exception as e:
        return Result.error(f"获取互动状态失败: {str(e)}")

@feed_bp.route('/post/<int:post_id>/related', methods=['GET'])
def get_related_posts(post_id):
    """
    获取相关帖子
    """
    try:
        from app.services.feedDetailService import FeedDetailService
        
        # 获取数量参数
        limit = int(request.args.get('limit', 5))
        
        # 获取相关帖子
        result = FeedDetailService.get_related_posts(post_id, limit)
        
        if result["success"]:
            return Result.success(result["data"])
        else:
            return Result.error(result["message"])
            
    except Exception as e:
        return Result.error(f"获取相关帖子失败: {str(e)}")

@feed_bp.route('/interaction/state', methods=['GET'])
def get_interaction_state():
    """
    获取用户对某个实体的互动状态（简化版）
    """
    try:
        # 获取参数
        entity_type = int(request.args.get('entity_type', 0))
        entity_id = int(request.args.get('entity_id', 0))
        
        if not entity_type or not entity_id:
            return Result.error('参数不完整')
        
        # 获取当前用户ID
        user_id = get_current_user_id()
        
        # 查询互动状态
        from app.models.feedModels import FeedLike, FeedCollect, FeedFollow
        
        result = {
            "is_liked": False,
            "is_collected": False,
            "is_followed": False
        }
        
        if not user_id:
            return Result.success(result)
        
        # 点赞状态
        like_record = FeedLike.query.filter_by(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            status=1
        ).first()
        result["is_liked"] = like_record is not None
        
        if entity_type == 1:  # 帖子
            # 收藏状态
            collect_record = FeedCollect.query.filter_by(
                user_id=user_id,
                entity_id=entity_id,
                status=1
            ).first()
            result["is_collected"] = collect_record is not None
        elif entity_type == 2:  # 话题
            # 关注状态
            follow_record = FeedFollow.query.filter_by(
                user_id=user_id,
                entity_id=entity_id,
                status=1
            ).first()
            result["is_followed"] = follow_record is not None
        
        return Result.success(result)
        
    except Exception as e:
        return Result.error(f"获取互动状态失败: {str(e)}")