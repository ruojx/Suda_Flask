from app.models.feedModels import Post, Topic
from app.extensions import db
from sqlalchemy import or_, desc
from datetime import datetime

class FeedSearchService:
    @staticmethod
    def search_content(keyword, filters, page=1, size=10):
        """
        搜索帖子/话题内容
        :param keyword: 搜索关键词
        :param filters: 筛选条件列表，如 ['post', 'title', 'content']
        :param page: 页码
        :param size: 每页大小
        :return: 分页结果
        """
        
        # 确定搜索的实体类型
        search_posts = False
        search_topics = False
        
        # 解析filters，确定搜索范围
        if 'post' in filters or 'topic' in filters:
            search_posts = 'post' in filters
            search_topics = 'topic' in filters
        else:
            # 默认搜索帖子和话题
            search_posts = True
            search_topics = True
        
        # 构建查询条件
        conditions = []
        
        # 构建字段搜索条件
        field_conditions = []
        
        # 解析字段筛选
        search_fields = {
            'title': 'title' in filters,
            'content': 'content' in filters,
            'author_name': 'author_name' in filters,
            'summary': 'summary' in filters,
            'tags': 'tags' in filters
        }
        
        # 如果没有指定字段，默认搜索所有字段
        if not any(search_fields.values()):
            search_fields = {k: True for k in search_fields.keys()}
        
        # 构建搜索表达式
        if search_fields['title']:
            field_conditions.append(Post.title.ilike(f'%{keyword}%'))
        if search_fields['content']:
            field_conditions.append(Post.content.ilike(f'%{keyword}%'))
        if search_fields['author_name']:
            field_conditions.append(Post.author_name.ilike(f'%{keyword}%'))
        if search_fields['summary']:
            field_conditions.append(Post.summary.ilike(f'%{keyword}%'))
        if search_fields['tags']:
            field_conditions.append(Post.tags.ilike(f'%{keyword}%'))
        
        # 执行搜索
        results = []
        
        if search_posts:
            # 搜索帖子
            post_query = Post.query.filter(
                Post.status == 1,
                or_(*field_conditions) if field_conditions else True
            ).order_by(desc(Post.create_time))
            
            post_pagination = post_query.paginate(page=page, per_page=size, error_out=False)
            
            for post in post_pagination.items:
                results.append({
                    'id': post.id,
                    'type': 'post',
                    'title': post.title,
                    'summary': post.summary,
                    'author_name': post.author_name,
                    'view_count': post.view_count,
                    'like_count': post.like_count,
                    'comment_count': post.comment_count,
                    'collect_count': post.collect_count,
                    'tags': post.tags,
                    'create_time': post.create_time
                })
            
            if search_topics:
                # 如果也搜索话题，调整每页数量
                topic_page = page
                topic_size = size - len(results)
            else:
                topic_page = 1
                topic_size = 0
        
        if search_topics and topic_size > 0:
            # 构建话题搜索条件（话题没有content和tags字段）
            topic_conditions = []
            
            if search_fields['title']:
                topic_conditions.append(Topic.title.ilike(f'%{keyword}%'))
            if search_fields['author_name']:
                topic_conditions.append(Topic.author_name.ilike(f'%{keyword}%'))
            if search_fields['summary']:
                topic_conditions.append(Topic.summary.ilike(f'%{keyword}%'))
            
            # 搜索话题
            topic_query = Topic.query.filter(
                Topic.status == 1,
                or_(*topic_conditions) if topic_conditions else True
            ).order_by(desc(Topic.create_time))
            
            topic_pagination = topic_query.paginate(page=topic_page, per_page=topic_size, error_out=False)
            
            for topic in topic_pagination.items:
                results.append({
                    'id': topic.id,
                    'type': 'topic',
                    'title': topic.title,
                    'summary': topic.summary,
                    'author_name': topic.author_name,
                    'view_count': topic.view_count,
                    'like_count': topic.like_count,
                    'follow_count': topic.follow_count,
                    'post_count': topic.post_count,
                    'create_time': topic.create_time
                })
        
        # 计算总页数
        total = len(results)
        pages = max(1, (total + size - 1) // size)
        
        return {
            "list": results,
            "pageNum": page,
            "pageSize": size,
            "total": total,
            "pages": pages,
            "isFirstPage": page == 1,
            "isLastPage": page >= pages
        }
    
    @staticmethod
    def get_hot_tags(limit=10):
        """
        获取热门标签
        :param limit: 返回的标签数量
        :return: 标签列表
        """
        # 从帖子中提取标签并统计
        from sqlalchemy import func
        
        posts = Post.query.filter(
            Post.status == 1,
            Post.tags.isnot(None),
            Post.tags != ''
        ).all()
        
        tag_counts = {}
        
        for post in posts:
            if post.tags:
                tags = [tag.strip() for tag in post.tags.split(',')]
                for tag in tags:
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 按出现次数排序
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        # 返回热门标签
        hot_tags = [tag for tag, count in sorted_tags[:limit]]
        
        # 如果标签不足，添加默认标签
        if len(hot_tags) < limit:
            default_tags = ['Vue3', 'Spring Boot', '前端', '后端', 'Docker', 
                          'Python', 'JavaScript', 'Java', '数据库', '算法']
            for tag in default_tags:
                if tag not in hot_tags:
                    hot_tags.append(tag)
                if len(hot_tags) >= limit:
                    break
        
        return hot_tags