from app.models.feedModels import Post, Topic, FeedFollow
from sqlalchemy import desc, func
from app.extensions import db

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
    def get_feed_list(tab, sort, page, size):
        query = None
        item_type = 'post'
        
        if tab == 'follow':
            # 关注页面 - 获取用户关注的话题
            # 注意：这里需要user_id，调用时应该传入
            return {
                "list": [],
                "pageNum": page,
                "pageSize": size,
                "total": 0,
                "pages": 0,
                "isFirstPage": True,
                "isLastPage": True
            }
        elif tab == 'recommend':
            # 推荐页面 - 帖子+话题混合，按热度排序
            return FeedService.get_recommend_feed(sort, page, size)
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
            return FeedService._format_page(pagination, item_type)
        
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
    def get_recommend_feed(sort, page, size):
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
        post = Post(**data, status=1)
        db.session.add(post)
        db.session.commit()
        return post.id
        
    @staticmethod
    def create_topic(data):
        topic = Topic(**data, status=1)
        db.session.add(topic)
        db.session.commit()
        return topic.id