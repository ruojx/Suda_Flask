from flask import Blueprint, request
from app.services.feedService import FeedService
from app.utils.result import Result
from app.utils.context import get_current_user_id
from app.schemas.requests import PostRequestSchema, TopicRequestSchema
from app.schemas.responses import FeedSchema


feed_bp = Blueprint('feed', __name__, url_prefix='/api/feed')

@feed_bp.route('/list', methods=['GET'])
def list_feed():
    tab = request.args.get('tab', 'post')
    sort = request.args.get('sort', 'hot')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    
    data = FeedService.get_feed_list(tab, sort, page, size)
    # data 中已经是 list 字典，并包含 type，直接使用 Schema 序列化 list 部分
    # 但由于 data 结构复杂 (PageInfo)，这里直接返回字典结构，仅对 list 内部元素序列化
    serialized_list = FeedSchema(many=True).dump(data['list'])
    data['list'] = serialized_list # 替换为前端需要的驼峰格式
    
    return Result.success(data)

@feed_bp.route('/post', methods=['POST'])
def create_post():
    data = PostRequestSchema().load(request.get_json())
    pid = FeedService.create_post(data)
    return Result.success({"id": pid})

@feed_bp.route('/topic', methods=['POST'])
def create_topic():
    data = TopicRequestSchema().load(request.get_json())
    tid = FeedService.create_topic(data)
    return Result.success({"id": tid})