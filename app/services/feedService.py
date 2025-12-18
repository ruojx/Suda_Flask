from app.models.feedModels import Post, Topic, FeedFollow
from sqlalchemy import desc, func
from app.extensions import db

# 在 feedService.py 或 feedDetailService.py 中添加
def format_post_data(post):
    """
    格式化帖子数据，确保字段名与前端一致
    """
    return {
        "id": post.id,
        "type": "post",
        "title": post.title,
        "summary": post.summary,
        "authorName": post.author_name,
        "userId": post.user_id,
        "viewCount": post.view_count or 0,
        "likeCount": post.like_count or 0,
        "commentCount": post.comment_count or 0,
        "collectCount": post.collect_count or 0,
        "tags": post.tags,
        "createTime": post.create_time.strftime('%Y-%m-%d %H:%M:%S') if post.create_time else None,
        "updateTime": post.update_time.strftime('%Y-%m-%d %H:%M:%S') if post.update_time else None,
        "topicId": post.topic_id
    }

def format_topic_data(topic):
    """
    格式化话题数据，确保字段名与前端一致
    """
    return {
        "id": topic.id,
        "type": "topic",
        "title": topic.title,
        "summary": topic.summary,
        "authorName": topic.author_name,
        "userId": topic.user_id,
        "viewCount": topic.view_count or 0,
        "likeCount": topic.like_count or 0,
        "followCount": topic.follow_count or 0,
        "postCount": topic.post_count or 0,
        "createTime": topic.create_time.strftime('%Y-%m-%d %H:%M:%S') if topic.create_time else None,
        "updateTime": topic.update_time.strftime('%Y-%m-%d %H:%M:%S') if topic.update_time else None
    }

class FeedService:
    @staticmethod
    def _format_page(pagination, item_type):
        """ 将 Flask 分页转换为 Java PageInfo 格式 """
        items = []
        for item in pagination.items:
            # 转换 Model 为字典并注入 type
            d = {c.name: getattr(item, c.name) for c in item.__table__.columns}
            d['type'] = item_type
            items.append(d)
            
        return {
            "list": items,
            "pageNum": pagination.page,
            "pageSize": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "isFirstPage": pagination.page == 1,
            "isLastPage": pagination.page == pagination.pages
        }
    
    @staticmethod
    def get_feed_list(tab, sort, page, size, current_user_id=None):
        query = None
        item_type = 'post'
        
        if tab == 'follow':
            # 关注页面 - 需要当前用户ID
            if not current_user_id:
                return {
                    "list": [],
                    "pageNum": page,
                    "pageSize": size,
                    "total": 0,
                    "pages": 0,
                    "isFirstPage": True,
                    "isLastPage": True
                }
            
            # 获取用户关注的话题ID
            follows = FeedFollow.query.filter_by(
                user_id=current_user_id,
                status=1
            ).all()
            
            topic_ids = [follow.entity_id for follow in follows]
            
            if not topic_ids:
                return {
                    "list": [],
                    "pageNum": page,
                    "pageSize": size,
                    "total": 0,
                    "pages": 0,
                    "isFirstPage": True,
                    "isLastPage": True
                }
            
            # 查询关注的话题
            query = Topic.query.filter(
                Topic.id.in_(topic_ids),
                Topic.status == 1
            )
            item_type = 'topic'
            if sort == 'hot':
                query = query.order_by(desc(Topic.view_count))
            else:
                query = query.order_by(desc(Topic.create_time))
        elif tab == 'recommend':
            # 推荐页面 - 帖子+话题混合，按热度排序
            return FeedService.get_recommend_feed(sort, page, size, current_user_id)
        elif tab == 'topic':
            # 话题页面 - 只显示话题
            query = Topic.query.filter_by(status=1)
            item_type = 'topic'
            if sort == 'hot':
                query = query.order_by(desc(Topic.view_count))
            else:
                query = query.order_by(desc(Topic.create_time))
        else:
            # 帖子页面 - 只显示帖子
            query = Post.query.filter_by(status=1)
            if sort == 'hot':
                query = query.order_by(desc(Post.like_count))
            else:
                query = query.order_by(desc(Post.create_time))
                
        if query:
            pagination = query.paginate(page=page, per_page=size, error_out=False)
            result = FeedService._format_page(pagination, item_type)
            
            # 为话题添加关注状态
            if current_user_id and item_type == 'topic':
                result['list'] = FeedService._add_follow_status(result['list'], current_user_id)
                print(f"DEBUG: 已为 {len(result['list'])} 个话题添加关注状态")  # 调试信息
            
            return result
        
        return {
            "list": [],
            "pageNum": page,
            "pageSize": size,
            "total": 0,
            "pages": 0,
            "isFirstPage": True,
            "isLastPage": True
        }
    
    @staticmethod
    def _add_follow_status(items, user_id):
        """
        为话题列表添加用户关注状态
        """
        if not user_id or not items:
            return items
        
        # 提取话题ID
        topic_ids = []
        for item in items:
            if item.get('type') == 'topic':
                topic_ids.append(item['id'])
        
        if not topic_ids:
            return items
        
        print(f"DEBUG: 检查用户 {user_id} 对话题 {topic_ids} 的关注状态")  # 调试信息
        
        # 查询用户关注的话题
        follows = FeedFollow.query.filter_by(
            user_id=user_id,
            status=1
        ).filter(FeedFollow.entity_id.in_(topic_ids)).all()
        
        # 创建关注ID集合
        followed_ids = {follow.entity_id for follow in follows}
        print(f"DEBUG: 用户已关注的话题ID: {followed_ids}")  # 调试信息
        
        # 为话题添加关注状态
        for item in items:
            if item.get('type') == 'topic':
                item['is_followed'] = item['id'] in followed_ids
                print(f"DEBUG: 话题 {item['id']} - {item['title']}: is_followed = {item['id'] in followed_ids}")  # 调试信息
        
        return items
    @staticmethod
    def get_recommend_feed(sort, page, size, current_user_id=None):
        """
        获取推荐内容（帖子+话题混合）
        使用综合排序算法
        """
        from datetime import datetime, timedelta
        
        # 分别获取帖子和话题
        posts = Post.query.filter_by(status=1).all()
        topics = Topic.query.filter_by(status=1).all()
        
        all_items = []
        
        # 计算每个帖子的推荐分数
        for post in posts:
            # 基础分数
            like_score = (post.like_count or 0) * 10
            comment_score = (post.comment_count or 0) * 8
            collect_score = (post.collect_count or 0) * 5
            view_score = (post.view_count or 0) * 0.1  # 浏览权重较低
            
            # 时间衰减因子 (新内容加分)
            time_factor = 1.0
            if post.create_time:
                hours_since_creation = (datetime.now() - post.create_time).total_seconds() / 3600
                if hours_since_creation < 24:  # 24小时内
                    time_factor = 1.5
                elif hours_since_creation < 168:  # 一周内
                    time_factor = 1.2
            
            # 总分数
            total_score = (like_score + comment_score + collect_score + view_score) * time_factor
            
            d = {c.name: getattr(post, c.name) for c in post.__table__.columns}
            d['type'] = 'post'
            d['recommend_score'] = total_score
            all_items.append(d)
        
        # 计算每个话题的推荐分数
        for topic in topics:
            # 基础分数
            like_score = (topic.like_count or 0) * 10
            follow_score = (topic.follow_count or 0) * 8
            post_score = (topic.post_count or 0) * 6
            view_score = (topic.view_count or 0) * 0.1
            
            # 时间衰减因子
            time_factor = 1.0
            if topic.create_time:
                hours_since_creation = (datetime.now() - topic.create_time).total_seconds() / 3600
                if hours_since_creation < 24:
                    time_factor = 1.5
                elif hours_since_creation < 168:
                    time_factor = 1.2
            
            # 总分数
            total_score = (like_score + follow_score + post_score + view_score) * time_factor
            
            d = {c.name: getattr(topic, c.name) for c in topic.__table__.columns}
            d['type'] = 'topic'
            d['recommend_score'] = total_score
            all_items.append(d)
        
        # 按推荐分数降序排序
        all_items.sort(key=lambda x: x['recommend_score'], reverse=True)
        
        # 为话题添加关注状态
        if current_user_id:
            all_items = FeedService._add_follow_status(all_items, current_user_id)
        
        # 移除推荐分数字段（前端不需要）
        for item in all_items:
            item.pop('recommend_score', None)
        
        # 手动分页
        total = len(all_items)
        pages = max(1, (total + size - 1) // size)
        start = (page - 1) * size
        end = start + size
        page_items = all_items[start:end]
        
        return {
            "list": page_items,
            "pageNum": page,
            "pageSize": size,
            "total": total,
            "pages": pages,
            "isFirstPage": page == 1,
            "isLastPage": page >= pages
        }

    @staticmethod
    def create_post(data):
        """
        创建帖子
        """
        try:
            # 提取话题ID
            topic_id = data.get('topicId')
            
            # 创建帖子
            post = Post(**data, status=1, topic_id=topic_id)
            db.session.add(post)
            db.session.commit()
            
            # 如果有关联的话题，更新话题的帖子计数
            if topic_id:
                topic = Topic.query.get(topic_id)
                if topic:
                    topic.post_count = (topic.post_count or 0) + 1
                    db.session.commit()
            
            return post.id
            
        except Exception as e:
            db.session.rollback()
            raise e
        
    @staticmethod
    def create_topic(data):
        topic = Topic(**data, status=1)
        db.session.add(topic)
        db.session.commit()
        return topic.id