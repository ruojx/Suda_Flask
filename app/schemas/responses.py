from marshmallow import Schema, fields

class BaseResponseSchema(Schema):
    create_time = fields.DateTime(format='%Y-%m-%d %H:%M:%S', data_key="createTime")
    update_time = fields.DateTime(format='%Y-%m-%d %H:%M:%S', data_key="updateTime")

class LoginVOSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    name = fields.Str()
    phone = fields.Str()
    avatar = fields.Str()
    token = fields.Str()

class FeedSchema(BaseResponseSchema):
    id = fields.Int()
    type = fields.Str() # '1为post' or '2为topic'
    title = fields.Str()
    summary = fields.Str()
    author_name = fields.Str(data_key="authorName")
    view_count = fields.Int(data_key="viewCount")
    like_count = fields.Int(data_key="likeCount")
    # Post fields
    comment_count = fields.Int(data_key="commentCount", dump_default=0)
    collect_count = fields.Int(data_key="collectCount", dump_default=0)
    tags = fields.Str()
    # Topic fields
    follow_count = fields.Int(data_key="followCount", dump_default=0)
    post_count = fields.Int(data_key="postCount", dump_default=0)
    # 添加用户是否关注该话题的字段
    is_followed = fields.Bool(data_key="isFollowed", dump_default=False)

class ResourceVOSchema(BaseResponseSchema):
    id = fields.Int()
    user_id = fields.Int(data_key="userId")
    title = fields.Str()
    description = fields.Str()
    type = fields.Str()
    size = fields.Int()
    url = fields.Str()
    cover = fields.Str()
    tags = fields.Str()
    view_count = fields.Int(data_key="viewCount")
    like_count = fields.Int(data_key="likeCount")
    favorite_count = fields.Int(data_key="favoriteCount")
    download_count = fields.Int(data_key="downloadCount")

class ConversationSchema(BaseResponseSchema):
    id = fields.Int()
    type = fields.Str()
    name = fields.Str()
    owner_id = fields.Int(data_key="ownerId")
    is_active = fields.Int(data_key="isActive")
    # 额外字段
    members = fields.Int(dump_default=0)
    unread = fields.Int(dump_default=0)

class MessageSchema(BaseResponseSchema):
    id = fields.Int()
    conversation_id = fields.Int(data_key="conversationId")
    sender_id = fields.Int(data_key="senderId")
    kind = fields.Str()
    content = fields.Str()
    file_url = fields.Str(data_key="fileUrl")