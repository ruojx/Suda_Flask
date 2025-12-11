from app.models.feed import FeedView, Post, Topic, FeedLike, FeedFollow, FeedCollect, FeedComment, PostTopicRelation
from app.extensions import db

class InteractionService:
    @staticmethod
    def toggle_like(entity_type, entity_id, user_id):
        record = FeedLike.query.filter_by(user_id=user_id, entity_type=entity_type, entity_id=entity_id).first()
        delta = 0
        if record:
            record.status = 1 if record.status == 0 else 0
            delta = 1 if record.status == 1 else -1
        else:
            db.session.add(FeedLike(user_id=user_id, entity_type=entity_type, entity_id=entity_id, status=1))
            delta = 1
        
        # 更新计数
        if delta != 0:
            Model = Post if entity_type == 1 else Topic
            obj = Model.query.get(entity_id)
            if obj: obj.like_count += delta
            
        db.session.commit()
        return "操作成功"
    
    # toggle_collect 和 toggle_follow 逻辑类似，略，参照 toggle_like