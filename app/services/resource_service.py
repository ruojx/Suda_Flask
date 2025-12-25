import datetime
from sqlalchemy import func, or_
from app.models.resource import Resource, ResourceLike, ResourceFavorite
from app.extensions import db
from app.utils.context import get_current_user_id  # 对应 CurrentHolder
import oss2
import os
import uuid


class ResourceService:

    @staticmethod
    def page_query(params):
        """
        分页查询 (对应 PageHelper + resourceMapper.pageSelect)
        """
        page = params.get('page', 1)
        page_size = params.get('pageSize', 10)
        
        query = Resource.query.filter(Resource.status == 1)
        
        # 筛选逻辑 (MyBatis XML 里的 if 标签逻辑)
        if params.get('q'):
            q = f"%{params.get('q')}%"
            query = query.filter(or_(Resource.title.like(q), Resource.description.like(q)))
        
        if params.get('types'):
            query = query.filter(Resource.type.in_(params.get('types')))

        if params.get('tags'):
            for tag in params['tags']:
                query = query.filter(Resource.tags.like(f"%{tag}%"))
        
        # 排序
        query = query.order_by(Resource.id.desc())
        
        # 执行分页
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        return {
            "total": pagination.total,
            "rows": pagination.items
        }

    @staticmethod
    def preview(resource_id):
        """预览逻辑"""
        res = Resource.query.get(resource_id)
        if not res:
            return {"error": "not_found"}
        
        # 增加浏览量 (对应 mapper.incViewCount)
        res.view_count += 1
        db.session.commit()

        if res.type.lower() == 'link':
            return {"mode": "link", "url": res.url}
        if res.type.lower() == 'zip':
            return {"error": "preview_not_supported"}
            
        return {"previewUrl": res.url, "expiresIn": 3600}

    @staticmethod
    def create_file(file, user_id, **dto):
        # file 是 Flask 的 FileStorage 对象
        file_data = file.read() # 获取 byte[]
        original_filename = file.filename
        
        
        # 调用工具类
        # url = AliyunOSSOperator.upload(file_data, original_filename)

        # 3. 构造数据库记录并保存 (对应 Java 的 BeanUtils.copyProperties)
        new_res = Resource(
            user_id=user_id,
            title=dto.get('title'),
            description=dto.get('desc'),
            type=dto.get('type'),
            cover=dto.get('cover'),
            tags=",".join(dto.get('tags', [])) if isinstance(dto.get('tags'), list) else dto.get('tags'),
            # url=url,
            url="",
            size=len(file_data),
            status=1,
            view_count=0,
            like_count=0,
            favorite_count=0,
            download_count=0,
            comment_count=0
            # create_time 和 update_time 如果你在 BaseModel 里设置了 default=datetime.now 则不需要手动设
        )
        
        db.session.add(new_res)
        db.session.commit()
        return new_res.id

    @staticmethod
    def create_link(dto):
        """外链上传 (对应 createLink)"""
        user_id = get_current_user_id()
        new_res = Resource(
            user_id=user_id,
            title=dto.get('title'),
            description=dto.get('desc'),
            type='link',
            url=dto.get('url'),
            cover=dto.get('cover'),
            tags=",".join(dto.get('tags', [])) if isinstance(dto.get('tags'), list) else dto.get('tags'),
            size=0,
            status=1
        )
        db.session.add(new_res)
        db.session.commit()
        return new_res.id

    @staticmethod
    def download_url(resource_id):
        """下载地址并自增下载数"""
        res = Resource.query.get(resource_id)
        if not res:
            return {"error": "not_found"}
        
        # 自增下载数 (对应 mapper.incDownloadCount)
        res.download_count += 1
        db.session.commit()
        
        return {"url": res.url, "expiresIn": 3600}

    @staticmethod
    def like(resource_id):
        """点赞 (对应 like)"""
        user_id = get_current_user_id()
        # 1. 主表计数加 1
        res = Resource.query.get(resource_id)
        res.like_count += 1
        
        # 2. 插入点赞记录 (likeMapper.insert)
        new_like = ResourceLike(resource_id=resource_id, user_id=user_id)
        db.session.add(new_like)
        
        db.session.commit()
        return {"likeCount": res.like_count, "like": True}

    @staticmethod
    def unlike(resource_id):
        """取消点赞 (对应 unlike)"""
        user_id = get_current_user_id()
        res = Resource.query.get(resource_id)
        
        # 计数减 1 (确保不小于 0)
        if res.like_count > 0:
            res.like_count -= 1
            
        # 删除点赞记录 (Java 代码里写的是 insert，但在逻辑上取消点赞应该是 delete)
        ResourceLike.query.filter_by(resource_id=resource_id, user_id=user_id).delete()
        
        db.session.commit()
        return {"likeCount": res.like_count, "like": False}

    @staticmethod
    def favorite(resource_id):
        """收藏"""
        user_id = get_current_user_id()
        res = Resource.query.get(resource_id)
        res.favorite_count += 1
        
        new_fav = ResourceFavorite(resource_id=resource_id, user_id=user_id)
        db.session.add(new_fav)
        
        db.session.commit()
        return {"favoriteCount": res.favorite_count, "favorite": True}

    @staticmethod
    def unfavorite(resource_id):
        """取消收藏"""
        user_id = get_current_user_id()
        res = Resource.query.get(resource_id)
        
        if res.favorite_count > 0:
            res.favorite_count -= 1
            
        ResourceFavorite.query.filter_by(resource_id=resource_id, user_id=user_id).delete()
        
        db.session.commit()
        return {"favoriteCount": res.favorite_count, "favorite": False}

    @staticmethod
    def ai_plan(resource_id):
        return {"html": "<h3>7 日学习计划</h3><ul><li>Day1：快速通读与目录建立</li><li>Day2-3：重点章节精读</li><li>Day4：动手实践</li><li>Day5：错题/难点回顾</li><li>Day6：输出总结</li><li>Day7：答疑与扩展</li></ul>"}

    @staticmethod
    def ai_summary(resource_id):
        res = Resource.query.get(resource_id)
        title = res.title if res else f"资源#{resource_id}"
        return {"html": f"<p><strong>要点：</strong></p><ol><li>主题：{title}</li><li>核心内容：自动摘要占位</li><li>适合人群：入门/进阶</li></ol>"}

    @staticmethod
    def tag_list():
        """标签聚合 (对应 mapper.allTags)"""
        # 获取所有非空的 tags 字段
        raw_tags = db.session.query(Resource.tags).filter(Resource.tags != None).all()
        
        tag_set = set()
        for (tag_str,) in raw_tags:
            if tag_str:
                # 拆分逗号并去重
                parts = [t.strip() for t in tag_str.split(',') if t.strip()]
                tag_set.update(parts)
                
        return {"items": list(tag_set)}