from app.models.feedModels import Post, Topic
from sqlalchemy import desc, or_
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
        
        if tab == 'topic':
            query = Topic.query.filter_by(status=1)
            item_type = 'topic'
            if sort == 'hot':
                query = query.order_by(desc(Topic.view_count))
            else:
                query = query.order_by(desc(Topic.create_time))
        else:
            # tab=post or recommend
            query = Post.query.filter_by(status=1)
            if sort == 'hot':
                query = query.order_by(desc(Post.like_count))
            else:
                query = query.order_by(desc(Post.create_time))
                
        pagination = query.paginate(page=page, per_page=size, error_out=False)
        return FeedService._format_page(pagination, item_type)

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