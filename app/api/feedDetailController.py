from flask import Blueprint, request
from app.services.feedDetailService import FeedDetailService
from app.utils.result import Result
from app.utils.context import get_current_user_id

detail_bp = Blueprint('detail', __name__, url_prefix='/api/detail')

@detail_bp.route('/post/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    """
    获取帖子详情
    """
    try:
        # 获取当前用户ID
        user_id = get_current_user_id()
        
        # 获取帖子详情
        result = FeedDetailService.get_post_detail(post_id, user_id)
        
        if result["success"]:
            return Result.success(result["data"])
        else:
            return Result.error(result["message"])
            
    except Exception as e:
        return Result.error(f"获取帖子详情失败: {str(e)}")

@detail_bp.route('/topic/<int:topic_id>', methods=['GET'])
def get_topic_detail(topic_id):
    """
    获取话题详情
    """
    try:
        # 获取当前用户ID
        user_id = get_current_user_id()
        
        # 获取话题详情
        result = FeedDetailService.get_topic_detail(topic_id, user_id)
        
        if result["success"]:
            return Result.success(result["data"])
        else:
            return Result.error(result["message"])
            
    except Exception as e:
        return Result.error(f"获取话题详情失败: {str(e)}")

@detail_bp.route('/topic/<int:topic_id>/posts', methods=['GET'])
def get_topic_posts(topic_id):
    """
    获取话题下的帖子列表
    """
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        sort = request.args.get('sort', 'time')  # time 或 hot
        
        # 获取帖子列表
        result = FeedDetailService.get_topic_posts(topic_id, page, size, sort)
        
        if result["success"]:
            return Result.success(result["data"])
        else:
            return Result.error(result["message"])
            
    except Exception as e:
        return Result.error(f"获取话题帖子失败: {str(e)}")

@detail_bp.route('/post/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    """
    获取帖子的评论列表
    """
    try:
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

@detail_bp.route('/interaction/status', methods=['GET'])
def get_interaction_status():
    """
    获取用户的互动状态
    """
    try:
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

@detail_bp.route('/post/<int:post_id>/related', methods=['GET'])
def get_related_posts(post_id):
    """
    获取相关帖子
    """
    try:
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