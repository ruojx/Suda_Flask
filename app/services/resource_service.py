import os
from flask import current_app
from app.models.resource import Resource, ResourceLike, ResourceFavorite
from app.extensions import db
from datetime import datetime

class ResourceService:
    @staticmethod
    def upload_local(file, user_id, title, desc, tags):
        filename = file.filename
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        
        # 生成访问 URL
        url = f"{current_app.config['BASE_URL']}/static/uploads/{filename}"
        
        res = Resource(
            user_id=user_id, title=title, description=desc,
            type='file', size=os.path.getsize(save_path),
            url=url, tags=tags, status=1
        )
        db.session.add(res)
        db.session.commit()
        return res.id

    @staticmethod
    def page_query(q, page, size):
        query = Resource.query.filter_by(status=1)
        if q:
            query = query.filter(Resource.title.like(f"%{q}%"))
        
        pagination = query.paginate(page=page, per_page=size)
        return {
            "total": pagination.total,
            "rows": pagination.items # Controller 层会序列化
        }

    @staticmethod
    def toggle_like(rid, uid):
        # 简单实现点赞
        exists = ResourceLike.query.filter_by(resource_id=rid, user_id=uid).first()
        res = Resource.query.get(rid)
        if exists:
            db.session.delete(exists)
            res.like_count = max(0, res.like_count - 1)
            is_like = False
        else:
            db.session.add(ResourceLike(resource_id=rid, user_id=uid))
            res.like_count += 1
            is_like = True
        db.session.commit()
        return {"likeCount": res.like_count, "like": is_like}