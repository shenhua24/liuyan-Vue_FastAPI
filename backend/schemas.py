from pydantic import BaseModel, Field
from typing import Optional
from models import UserRole
from datetime import datetime

# 用户基本模式
class UserBase(BaseModel):
  username: str = Field(...,min_length=3,max_length=50,description="用户名")

# 用户创建模式继承UserBase
class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")

# 用户登录模式
class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

# 用户界面响应模式
class UserResponse(BaseModel):
   id:int
   username:str
   nickname:str
   avatar:str
   role:UserRole
   is_active:bool

   class Config:
      from_attributes=True
# 用户可更新模式
class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像路径")

# 管理员可更新信息模式
class AdminUserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    role: Optional[UserRole] = Field(None, description="用户角色")
    is_active: Optional[bool] = Field(None, description="账户状态")

# 管理员响应页面模式
class AdminUserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    avatar: str
    role: UserRole
    is_active: bool
    created_at: datetime
    messages_count: int = 0

    class Config:
        from_attributes = True

# 留言模式
class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=500, description="留言内容")

# 留言创建模式
class MessageCreate(MessageBase):
    pass

# 留言可展示模式
class MessageResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserResponse
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False

    class Config:
        from_attributes = True

# 点赞创建模式
class LikeCreate(BaseModel):
    message_id: int = Field(..., description="留言ID")

# 点赞可展示界面模式
class LikeResponse(BaseModel):
    id: int
    user_id: int
    message_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 评论相关模式
class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=200, description="评论内容")
    message_id: int = Field(..., description="留言ID")

# 评论可展示界面模式
class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserResponse
    message_id: int

    class Config:
        from_attributes = True