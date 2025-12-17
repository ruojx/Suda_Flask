from marshmallow import Schema, fields, EXCLUDE # 引入 EXCLUDE

# 1. 修改 TopicRequestSchema
class TopicRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # 【关键修改】忽略前端传来的多余字段(如 content)

    user_id = fields.Int(data_key="userId", required=True)
    author_name = fields.Str(data_key="authorName")
    title = fields.Str(required=True)
    summary = fields.Str()
    # 如果你想把前端传的 content 当作 summary 存，可以解开下面这行
    # content = fields.Str() 

class PostRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE # 建议给 Post 也加上

    user_id = fields.Int(data_key="userId", required=True)
    author_name = fields.Str(data_key="authorName")
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    summary = fields.Str()
    tags = fields.Str()

class InteractionRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    user_id = fields.Int(data_key="userId", required=True)
    entity_id = fields.Int(data_key="entityId", required=True)
    entity_type = fields.Int(data_key="entityType")

class UserUpdateRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    name = fields.Str()
    avatar = fields.Str()
    introduction = fields.Str()
    phone = fields.Str()
    email = fields.Str()