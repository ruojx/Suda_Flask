from flask import Blueprint, request
from app.models.feedModels import FeedComment
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
    """
    获取评论列表
    """
    try:
        comments = InteractionService.get_comments(entity_type, entity_id)
        
        # 这里comments已经是字典列表，不需要再次转换
        # 只需要确保数据结构正确
        return Result.success(comments)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Result.error(f"获取评论失败: {str(e)}")

@interaction_bp.route('/comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """
    删除评论（权限：评论作者或帖子作者）
    """
    try:
        # 从token获取用户ID
        user_id = get_current_user_id()
        
        if not user_id:
            return Result.error('请先登录')
        
        print(f"DEBUG: 删除评论请求 - 用户ID: {user_id}, 评论ID: {comment_id}")
        
        # 获取评论信息
        comment = FeedComment.query.get(comment_id)
        
        if not comment:
            return Result.error('评论不存在')
        
        print(f"DEBUG: 评论信息 - 用户ID: {comment.user_id}, 实体类型: {comment.entity_type}, 实体ID: {comment.entity_id}")
        
        # 获取帖子信息（如果是帖子评论）
        if comment.entity_type == 1:  # 帖子
            from app.models.feedModels import Post
            post = Post.query.get(comment.entity_id)
            
            if post:
                print(f"DEBUG: 帖子信息 - 作者ID: {post.user_id}, 帖子ID: {post.id}")
                
                # 检查权限：评论作者或帖子作者可以删除
                can_delete = False
                
                # 评论作者可以删除
                if comment.user_id == user_id:
                    can_delete = True
                    print(f"DEBUG: 权限检查 - 评论作者匹配")
                
                # 帖子作者可以删除自己帖子下的评论
                elif post.user_id == user_id:
                    can_delete = True
                    print(f"DEBUG: 权限检查 - 帖子作者匹配")
                
                if not can_delete:
                    print(f"DEBUG: 权限检查 - 无权删除")
                    return Result.error('无权删除此评论')
                
                # 执行删除
                result = InteractionService.delete_comment(comment_id, user_id)
                
                if result["success"]:
                    return Result.success(result["message"])
                else:
                    return Result.error(result["message"])
            else:
                return Result.error('关联的帖子不存在')
        else:
            return Result.error('不支持删除非帖子评论')
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Result.error(f"删除失败: {str(e)}")

@interaction_bp.route('/comment/like', methods=['POST'])
def comment_like():
    """
    评论点赞/取消点赞
    """
    try:
        data = request.get_json()
        user_id = data.get('userId')
        comment_id = data.get('commentId')
        
        if not user_id or not comment_id:
            return Result.error('参数不完整')
        
        result = InteractionService.toggle_comment_like(comment_id, user_id)
        
        if result["success"]:
            return Result.success(result["message"])
        else:
            return Result.error(result["message"])
            
    except Exception as e:
        return Result.error(f"操作失败: {str(e)}")