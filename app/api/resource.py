from flask import Blueprint, request
from app.services.resource_service import ResourceService
from app.utils.result import Result
from app.utils.context import get_current_user_id
from app.schemas.responses import ResourceVOSchema

resource_bp = Blueprint('resource', __name__, url_prefix='/resource')

# ========================= 列表（分页 + 筛选） =========================

@resource_bp.route('/list', methods=['POST'])
def list_res():
    data = request.get_json() or {}
    query_params = {
        'q': data.get('q'),
        'types': data.get('types', []),
        'tags': data.get('tags', []),
        'sort_by': data.get('sortBy'),
        'page': data.get('page', 1),
        'page_size': data.get('pageSize', 10)
    }
    res = ResourceService.page_query(query_params)
    return Result.success({
        "total": res['total'],
        "rows": ResourceVOSchema(many=True).dump(res['rows'])
    })

# ========================= 上传 =========================

@resource_bp.route('/createFile', methods=['POST'])
def create_file():
    user_id = get_current_user_id()
    file = request.files.get('file')
    dto = {
        "title": request.form.get('title'),
        "type": request.form.get('type'),
        "desc": request.form.get('desc'),
        "tags": request.form.getlist('tags'),
        "cover": request.form.get('cover')
    }
    # 注意：create_file 确实需要 user_id 参数
    rid = ResourceService.create_file(file, user_id, **dto)
    return Result.success({"id": rid})

@resource_bp.route('/createLink', methods=['POST'])
def create_link():
    data = request.get_json()
    rid = ResourceService.create_link(data)
    return Result.success({"id": rid})

# ========================= 预览 / 下载 =========================

@resource_bp.route('/preview/<int:id>', methods=['POST'])
def preview(id):
    return Result.success(ResourceService.preview(id))

@resource_bp.route('/download/<int:id>', methods=['POST'])
def download(id):
    return Result.success(ResourceService.download_url(id))

# ========================= 点赞 / 收藏（已修正参数） =========================

@resource_bp.route('/like/<int:id>', methods=['POST'])
def like(id):
    # 修正：只传 id，Service 内部会自动获取当前用户
    return Result.success(ResourceService.like(id))

@resource_bp.route('/unlike/<int:id>', methods=['POST'])
def unlike(id):
    # 修正：只传 id
    return Result.success(ResourceService.unlike(id))

@resource_bp.route('/favorite/<int:id>', methods=['POST'])
def favorite(id):
    # 修正：只传 id
    return Result.success(ResourceService.favorite(id))

@resource_bp.route('/unfavorite/<int:id>', methods=['POST'])
def unfavorite(id):
    # 修正：只传 id
    return Result.success(ResourceService.unfavorite(id))

# ========================= AI 能力 =========================

@resource_bp.route('/ai/summary', methods=['POST'])
def ai_summary():
    resource_id = request.get_json() 
    return Result.success(ResourceService.ai_summary(resource_id))

@resource_bp.route('/ai/plan', methods=['POST'])
def ai_plan():
    resource_id = request.get_json()
    return Result.success(ResourceService.ai_plan(resource_id))

# ========================= 标签 =========================

@resource_bp.route('/tags', methods=['POST'])
def tags():
    return Result.success({"items": ResourceService.tag_list()}) 