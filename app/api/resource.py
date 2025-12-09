from flask import Blueprint, request
from app.services.resource_service import ResourceService
from app.utils.result import Result
from app.utils.context import get_current_user_id
from app.schemas.responses import ResourceVOSchema

resource_bp = Blueprint('resource', __name__, url_prefix='/resource')

@resource_bp.route('/list', methods=['POST'])
def list_res():
    data = request.get_json()
    page = data.get('page', 1)
    res = ResourceService.page_query(data.get('q'), page, data.get('pageSize', 10))
    # 手动构造 PageResult
    return Result.success({
        "total": res['total'],
        "rows": ResourceVOSchema(many=True).dump(res['rows'])
    })

@resource_bp.route('/createFile', methods=['POST'])
def create_file():
    user_id = get_current_user_id()
    file = request.files.get('file')
    title = request.form.get('title')
    rid = ResourceService.upload_local(file, user_id, title, request.form.get('desc'), request.form.get('tags'))
    return Result.success({"id": rid})

@resource_bp.route('/like/<int:id>', methods=['POST'])
def like(id):
    user_id = get_current_user_id()
    res = ResourceService.toggle_like(id, user_id)
    return Result.success(res)

@resource_bp.route('/tags', methods=['POST'])
def tags():
    # 返回 mock 数据或从数据库查
    return Result.success({"items": ["Java", "Python", "AI", "前端", "面试"]})

# 【新增】下载/预览接口
@resource_bp.route('/download/<int:id>', methods=['POST'])
def download(id):
    # 简单返回一个 url
    return Result.success({"url": "#", "expiresIn": 3600})

@resource_bp.route('/preview/<int:id>', methods=['POST'])
def preview(id):
    return Result.success({"previewUrl": "#", "expiresIn": 3600})