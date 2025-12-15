from flask import Blueprint, request
from app.services.feedInteractionService import InteractionService
from app.utils.result import Result
from app.schemas.requests import InteractionRequestSchema
from app.utils.context import get_current_user_id

interaction_bp = Blueprint('interaction', __name__, url_prefix='/api/interaction')

@interaction_bp.route('/like', methods=['POST'])
def like():
    data = InteractionRequestSchema().load(request.get_json())
    result = InteractionService.toggle_like(
        data['entity_type'], 
        data['entity_id'], 
        data['user_id']
    )
    return Result.success(result)

@interaction_bp.route('/collect', methods=['POST'])
def collect():
    data = request.get_json()
    user_id = data.get('userId')
    entity_id = data.get('entityId')
    
    if not user_id or not entity_id:
        return Result.error('参数不完整')
    
    result = InteractionService.toggle_collect(entity_id, user_id)
    return Result.success(result)

@interaction_bp.route('/follow', methods=['POST'])
def follow():
    data = request.get_json()
    user_id = data.get('userId')
    entity_id = data.get('entityId')
    
    if not user_id or not entity_id:
        return Result.error('参数不完整')
    
    result = InteractionService.toggle_follow(entity_id, user_id)
    
    if result["success"]:
        return Result.success({
            "isFollowing": result["isFollowing"],
            "newFollowCount": result["newFollowCount"],
            "message": result["message"]
        })
    else:
        return Result.error(result["message"])

@interaction_bp.route('/comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    user_id = data.get('userId')
    entity_type = data.get('entityType', 1)  # 默认帖子
    entity_id = data.get('entityId')
    content = data.get('content')
    
    if not all([user_id, entity_id, content]):
        return Result.error('参数不完整')
    
    comment = InteractionService.add_comment(entity_type, entity_id, user_id, content)
    
    return Result.success({
        "id": comment.id,
        "message": "评论成功"
    })

@interaction_bp.route('/comment/<int:entity_type>/<int:entity_id>', methods=['GET'])
def get_comments(entity_type, entity_id):
    comments = InteractionService.get_comments(entity_type, entity_id)
    
    # 格式化评论数据
    comment_list = []
    for comment in comments:
        comment_list.append({
            "id": comment.id,
            "userId": comment.user_id,
            "content": comment.content,
            "likeCount": comment.like_count,
            "createTime": comment.create_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return Result.success(comment_list)

@interaction_bp.route('/comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    # 从token获取用户ID
    user_id = get_current_user_id()
    
    if not user_id:
        return Result.error('请先登录')
    
    # 获取评论信息
    from app.models.feedModels import FeedComment, Post
    comment = FeedComment.query.get(comment_id)
    
    if not comment:
        return Result.error('评论不存在')
    
    # 获取帖子信息
    post = None
    if comment.entity_type == 1:  # 帖子
        post = Post.query.get(comment.entity_id)
    
    # 检查权限：评论作者或帖子作者可以删除
    if comment.user_id != user_id and (post and post.user_id != user_id):
        return Result.error('无权删除此评论')
    
    result = InteractionService.delete_comment(comment_id, user_id)
    
    if result["success"]:
        return Result.success(result["message"])
    else:
        return Result.error(result["message"])
    # 从token获取用户ID
    user_id = get_current_user_id()
    
    if not user_id:
        return Result.error('请先登录')
    
    result = InteractionService.delete_comment(comment_id, user_id)
    
    if result["success"]:
        return Result.success(result["message"])
    else:
        return Result.error(result["message"])