from app.models.feedModels import FeedLike, FeedCollect, FeedFollow, FeedComment, Post, Topic
from app.extensions import db

class InteractionService:
    @staticmethod
    def toggle_like(entity_type, entity_id, user_id):
        record = FeedLike.query.filter_by(
            user_id=user_id, 
            entity_type=entity_type, 
            entity_id=entity_id
        ).first()
        
        delta = 0
        if record:
            # 切换点赞状态
            record.status = 1 if record.status == 0 else 0
            delta = 1 if record.status == 1 else -1
        else:
            # 创建新的点赞记录
            db.session.add(FeedLike(
                user_id=user_id, 
                entity_type=entity_type, 
                entity_id=entity_id, 
                status=1
            ))
            delta = 1
        
        # 更新计数
        if delta != 0:
            if entity_type == 1:  # 帖子
                obj = Post.query.get(entity_id)
                if obj: 
                    obj.like_count = max(0, obj.like_count + delta)
            elif entity_type == 2:  # 话题
                obj = Topic.query.get(entity_id)
                if obj: 
                    obj.like_count = max(0, obj.like_count + delta)
        
        db.session.commit()
        return {"success": True, "message": "操作成功"}
    
    @staticmethod
    def toggle_collect(entity_id, user_id):
        record = FeedCollect.query.filter_by(
            user_id=user_id, 
            entity_id=entity_id
        ).first()
        
        delta = 0
        if record:
            # 切换收藏状态
            record.status = 1 if record.status == 0 else 0
            delta = 1 if record.status == 1 else -1
        else:
            # 创建新的收藏记录
            db.session.add(FeedCollect(
                user_id=user_id, 
                entity_id=entity_id, 
                status=1
            ))
            delta = 1
        
        # 更新帖子收藏计数
        if delta != 0:
            post = Post.query.get(entity_id)
            if post: 
                post.collect_count = max(0, post.collect_count + delta)
        
        db.session.commit()
        return {"success": True, "message": "操作成功"}
    
    @staticmethod
    def toggle_follow(entity_id, user_id):
        record = FeedFollow.query.filter_by(
            user_id=user_id, 
            entity_id=entity_id
        ).first()
        
        delta = 0
        if record:
            # 切换关注状态
            record.status = 1 if record.status == 0 else 0
            delta = 1 if record.status == 1 else -1
        else:
            # 创建新的关注记录
            db.session.add(FeedFollow(
                user_id=user_id, 
                entity_id=entity_id, 
                status=1
            ))
            delta = 1
        
        # 更新话题关注计数
        if delta != 0:
            topic = Topic.query.get(entity_id)
            if topic: 
                topic.follow_count = max(0, topic.follow_count + delta)
        
        db.session.commit()
        return {"success": True, "message": "操作成功"}
    
    @staticmethod
    def add_comment(entity_type, entity_id, user_id, content):
        # 创建评论
        comment = FeedComment(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            content=content,
            status=1
        )
        db.session.add(comment)
        
        # 更新评论计数
        if entity_type == 1:  # 帖子
            post = Post.query.get(entity_id)
            if post:
                post.comment_count = (post.comment_count or 0) + 1
        
        db.session.commit()
        return comment
    
    @staticmethod
    def get_comments(entity_type, entity_id):
        comments = FeedComment.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id,
            status=1
        ).order_by(FeedComment.create_time.desc()).all()
        
        return comments
    
    @staticmethod
    def delete_comment(comment_id, user_id):
        comment = FeedComment.query.get(comment_id)
        
        if not comment:
            return {"success": False, "message": "评论不存在"}
        
        # 检查权限
        if comment.user_id != user_id:
            return {"success": False, "message": "无权删除此评论"}
        
        # 软删除
        comment.status = 0
        
        # 更新评论计数
        if comment.entity_type == 1:  # 帖子
            post = Post.query.get(comment.entity_id)
            if post:
                post.comment_count = max(0, (post.comment_count or 0) - 1)
        
        db.session.commit()
        return {"success": True, "message": "删除成功"}