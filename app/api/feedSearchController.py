from flask import Blueprint, request
from app.services.feedSearchService import FeedSearchService
from app.utils.result import Result
from app.schemas.responses import FeedSchema

feed_search_bp = Blueprint('feed_search', __name__, url_prefix='/api/feed')

@feed_search_bp.route('/search', methods=['GET'])
def search():
    """
    搜索内容
    """
    keyword = request.args.get('keyword', '')
    filters = request.args.getlist('filters')  # 支持多个filters参数
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    
    if not keyword:
        return Result.error('请输入搜索关键词')
    
    # 获取当前用户ID
    from app.utils.context import get_current_user_id
    current_user_id = get_current_user_id()
    
    print(f"DEBUG: 搜索 - 当前用户ID: {current_user_id}, 关键词: {keyword}")  # 调试信息
    
    # 执行搜索
    data = FeedSearchService.search_content(keyword, filters, page, size, current_user_id)
    
    # 序列化结果
    serialized_list = FeedSchema(many=True).dump(data['list'])
    data['list'] = serialized_list
    
    return Result.success(data)

@feed_search_bp.route('/tags/hot', methods=['GET'])
def get_hot_tags():
    """
    获取热门标签
    """
    limit = int(request.args.get('limit', 10))
    
    hot_tags = FeedSearchService.get_hot_tags(limit)
    
    return Result.success(hot_tags)