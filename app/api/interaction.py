from flask import Blueprint, request
from app.services.interaction_service import InteractionService
from app.utils.result import Result
from app.schemas.requests import InteractionRequestSchema


interaction_bp = Blueprint('interaction', __name__, url_prefix='/api/interaction')

@interaction_bp.route('/like', methods=['POST'])
def like():
    data = InteractionRequestSchema().load(request.get_json())
    msg = InteractionService.toggle_like(data['entity_type'], data['entity_id'], data['user_id'])
    return Result.success(msg)