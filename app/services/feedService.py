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
        """
        # 分别获取帖子和话题
        post_query = Post.query.filter_by(status=1)
        topic_query = Topic.query.filter_by(status=1)
        
        # 按不同方式排序
        if sort == 'hot':
            post_query = post_query.order_by(desc(Post.like_count))
            topic_query = topic_query.order_by(desc(Topic.view_count))
        else:
            post_query = post_query.order_by(desc(Post.create_time))
            topic_query = topic_query.order_by(desc(Topic.create_time))
        
        # 分页获取
        post_pagination = post_query.paginate(page=page, per_page=size//2, error_out=False)
        topic_pagination = topic_query.paginate(page=page, per_page=size//2, error_out=False)
        
        # 合并结果
        items = []
        
        # 添加帖子
        for post in post_pagination.items:
            d = {c.name: getattr(post, c.name) for c in post.__table__.columns}
            d['type'] = 'post'
            items.append(d)
        
        # 添加话题
        for topic in topic_pagination.items:
            d = {c.name: getattr(topic, c.name) for c in topic.__table__.columns}
            d['type'] = 'topic'
            items.append(d)
        
        # 计算总页数（简化处理）
        total = post_pagination.total + topic_pagination.total
        pages = max(1, (total + size - 1) // size)
        
        return {
            "list": items,
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