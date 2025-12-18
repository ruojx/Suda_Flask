from app.models.feedModels import Post, Topic, FeedLike, FeedCollect, FeedFollow, FeedComment, FeedView
from app.extensions import db
from sqlalchemy import desc
from datetime import datetime

class FeedDetailService:
    @staticmethod
    def get_post_detail(post_id, user_id=None):
        """
        获取帖子详情
        """
        try:
            post = Post.query.filter_by(id=post_id, status=1).first()
            if not post:
                return {"success": False, "message": "帖子不存在或已被删除"}
            
            # 增加浏览数
            post.view_count = (post.view_count or 0) + 1
            
            # 创建浏览记录
            from flask import request
            view_record = FeedView(
                user_id=user_id or 0,
                entity_type=1,
                entity_id=post_id,
                ip_address=request.remote_addr if request else '',
                user_agent=request.headers.get('User-Agent', '') if request else '',
                referer=request.headers.get('Referer', '') if request else ''
            )
            
            db.session.add(view_record)
            db.session.commit()
            
            # 获取帖子详情数据
            post_data = {c.name: getattr(post, c.name) for c in post.__table__.columns}
            post_data['type'] = 'post'
            
            # 获取用户的互动状态
            if user_id:
                # 点赞状态
                like_record = FeedLike.query.filter_by(
                    user_id=user_id,
                    entity_type=1,
                    entity_id=post_id,
                    status=1
                ).first()
                post_data['is_liked'] = like_record is not None
                
                # 收藏状态
                collect_record = FeedCollect.query.filter_by(
                    user_id=user_id,
                    entity_id=post_id,
                    status=1
                ).first()
                post_data['is_collected'] = collect_record is not None
            
            return {"success": True, "data": post_data}
            
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"获取帖子详情失败: {str(e)}"}
    
    @staticmethod
    def get_topic_detail(topic_id, user_id=None):
        """
        获取话题详情
        """
        try:
            topic = Topic.query.filter_by(id=topic_id, status=1).first()
            if not topic:
                return {"success": False, "message": "话题不存在或已被删除"}
            
            # 增加浏览数
            topic.view_count = (topic.view_count or 0) + 1
            
            # 创建浏览记录
            from flask import request
            view_record = FeedView(
                user_id=user_id or 0,
                entity_type=2,
                entity_id=topic_id,
                ip_address=request.remote_addr if request else '',
                user_agent=request.headers.get('User-Agent', '') if request else '',
                referer=request.headers.get('Referer', '') if request else ''
            )
            
            db.session.add(view_record)
            db.session.commit()
            
            # 获取话题详情数据
            topic_data = {c.name: getattr(topic, c.name) for c in topic.__table__.columns}
            topic_data['type'] = 'topic'
            
            # 获取用户的互动状态
            if user_id:
                # 点赞状态
                like_record = FeedLike.query.filter_by(
                    user_id=user_id,
                    entity_type=2,
                    entity_id=topic_id,
                    status=1
                ).first()
                topic_data['is_liked'] = like_record is not None
                
                # 关注状态
                follow_record = FeedFollow.query.filter_by(
                    user_id=user_id,
                    entity_id=topic_id,
                    status=1
                ).first()
                topic_data['is_followed'] = follow_record is not None
            
            return {"success": True, "data": topic_data}
            
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"获取话题详情失败: {str(e)}"}
    
    @staticmethod
    def get_topic_posts(topic_id, page=1, size=10, sort='time'):
        """
        获取话题下的帖子列表（返回格式化数据）
        """
        try:
            # 检查话题是否存在
            topic = Topic.query.filter_by(id=topic_id, status=1).first()
            if not topic:
                return {"success": False, "message": "话题不存在"}
            
            # 查询该话题下的帖子
            query = Post.query.filter_by(topic_id=topic_id, status=1)
            
            # 排序
            if sort == 'hot':
                query = query.order_by(desc(Post.like_count))
            else:
                query = query.order_by(desc(Post.create_time))
            
            # 分页
            pagination = query.paginate(page=page, per_page=size, error_out=False)
            
            # 格式化帖子数据
            posts = []
            for post in pagination.items:
                post_data = {
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
                posts.append(post_data)
            
            return {
                "success": True,
                "data": {
                    "list": posts,
                    "pageNum": pagination.page,
                    "pageSize": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "isFirstPage": pagination.page == 1,
                    "isLastPage": pagination.page == pagination.pages
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取话题帖子失败: {str(e)}"}

    @staticmethod
    def get_post_comments(post_id, page=1, size=20):
        """
        获取帖子的评论列表
        """
        try:
            # 检查帖子是否存在
            post = Post.query.filter_by(id=post_id, status=1).first()
            if not post:
                return {"success": False, "message": "帖子不存在"}
            
            # 查询评论
            query = FeedComment.query.filter_by(
                entity_type=1,  # 帖子
                entity_id=post_id,
                status=1
            ).order_by(desc(FeedComment.create_time))
            
            # 分页
            pagination = query.paginate(page=page, per_page=size, error_out=False)
            
            # 格式化评论
            comments = []
            for comment in pagination.items:
                comment_data = {
                    "id": comment.id,
                    "user_id": comment.user_id,
                    "content": comment.content,
                    "like_count": comment.like_count,
                    "create_time": comment.create_time.strftime('%Y-%m-%d %H:%M:%S') if comment.create_time else None
                }
                
                # 获取用户信息（这里需要您已有的用户服务）
                # 可以调用已有的用户服务获取用户名等
                # user_info = UserService.get_user_info(comment.user_id)
                # comment_data['user_name'] = user_info.get('name', '匿名用户')
                
                comments.append(comment_data)
            
            return {
                "success": True,
                "data": {
                    "list": comments,
                    "pageNum": pagination.page,
                    "pageSize": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "isFirstPage": pagination.page == 1,
                    "isLastPage": pagination.page == pagination.pages
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取评论失败: {str(e)}"}
    
    @staticmethod
    def get_user_interaction_status(user_id, entity_type, entity_id):
        """
        获取用户对某个实体的互动状态
        """
        try:
            result = {
                "is_liked": False,
                "is_collected": False,
                "is_followed": False
            }
            
            if not user_id:
                return {"success": True, "data": result}
            
            # 点赞状态
            like_record = FeedLike.query.filter_by(
                user_id=user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                status=1
            ).first()
            result["is_liked"] = like_record is not None
            
            if entity_type == 1:  # 帖子
                # 收藏状态
                collect_record = FeedCollect.query.filter_by(
                    user_id=user_id,
                    entity_id=entity_id,
                    status=1
                ).first()
                result["is_collected"] = collect_record is not None
            elif entity_type == 2:  # 话题
                # 关注状态
                follow_record = FeedFollow.query.filter_by(
                    user_id=user_id,
                    entity_id=entity_id,
                    status=1
                ).first()
                result["is_followed"] = follow_record is not None
            
            return {"success": True, "data": result}
            
        except Exception as e:
            return {"success": False, "message": f"获取互动状态失败: {str(e)}"}
    
    @staticmethod
    def get_related_posts(post_id, limit=5):
        """
        获取相关帖子（基于标签）
        """
        try:
            post = Post.query.filter_by(id=post_id, status=1).first()
            if not post or not post.tags:
                return {"success": True, "data": []}
            
            # 解析标签
            tags = [tag.strip() for tag in post.tags.split(',') if tag.strip()]
            if not tags:
                return {"success": True, "data": []}
            
            # 构建查询条件
            from sqlalchemy import or_
            conditions = []
            for tag in tags[:3]:  # 最多使用3个标签
                conditions.append(Post.tags.like(f'%{tag}%'))
            
            # 查询相关帖子（排除当前帖子）
            related_posts = Post.query.filter(
                Post.id != post_id,
                Post.status == 1,
                or_(*conditions)
            ).order_by(desc(Post.like_count)).limit(limit).all()
            
            # 格式化结果
            posts_data = []
            for related_post in related_posts:
                post_data = {
                    "id": related_post.id,
                    "title": related_post.title,
                    "summary": related_post.summary,
                    "like_count": related_post.like_count,
                    "view_count": related_post.view_count,
                    "comment_count": related_post.comment_count,
                    "create_time": related_post.create_time.strftime('%Y-%m-%d %H:%M:%S') if related_post.create_time else None
                }
                posts_data.append(post_data)
            
            return {"success": True, "data": posts_data}
            
        except Exception as e:
            return {"success": False, "message": f"获取相关帖子失败: {str(e)}"}