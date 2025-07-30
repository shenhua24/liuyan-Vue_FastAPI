# 数据库字段
from datetime import timezone, timedelta, datetime
import enum
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer,String,Enum,Boolean,DateTime,Text,ForeignKey
# 北京时区
BEIJING_TZ = timezone(timedelta(hours=8))

# 用户权限表 普通用户|管理员用户
class UserRole(enum.Enum):
  USER = "user"
  ADMIN = "admin"

# 用户表
class User(Base):
  # 表名
  __tablename__ = "users"
  # 字段
  id = Column(Integer, primary_key=True, index=True, comment="用户ID")
  username = Column(String(50),unique=True, index=True, nullable=False, comment="用户名")
  hashed_password = Column(String(255), nullable=False, comment="加密后的密码")
  nickname = Column(String(50), nullable=False, comment="昵称")
  avatar = Column(String(255),default="",comment="头像URL")
  role = Column(Enum(UserRole),default=UserRole.USER,nullable=False,comment="用户角色")
  is_active = Column(Boolean,default=True,nullable=False,comment="用户是否激活")
  created_at = Column(DateTime,default=lambda:datetime.now(BEIJING_TZ),comment="创建时间")

  # 关联留言
  messages = relationship("Message",back_populates="author")
  # 关联点赞
  likes = relationship("Like", back_populates="user")
  # 关联评论
  comments = relationship("Comment", back_populates="author")

# 留言表
class Message(Base):
  __tablename__ = "messages"
  id = Column(Integer, primary_key=True, index=True, comment="留言ID")
  content = Column(Text, nullable=False, comment="留言内容")
  author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="作者ID")
  created_at = Column(DateTime, default=lambda:datetime.now(BEIJING_TZ), comment="创建时间")

  # 关联用户
  author = relationship("User", back_populates="messages")
  # 关联点赞
  likes = relationship("Like", back_populates="message")
  # 关联评论
  comments = relationship("Comment", back_populates="message")

# 点赞表
class Like(Base):
  __tablename__ = "likes"

  id = Column(Integer, primary_key=True, index=True, comment="点赞ID")
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
  message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, comment="留言ID")
  created_at = Column(DateTime, default=lambda:datetime.now(BEIJING_TZ), comment="点赞时间")

  # 关联用户和留言
  user = relationship("User", back_populates="likes")
  message = relationship("Message", back_populates="likes")

# 评论表
class Comment(Base):
  __tablename__ = "comments"
  id = Column(Integer, primary_key=True, index=True, comment="评论ID")
  content = Column(Text, nullable=False, comment="评论内容")
  author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="评论者ID")
  message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, comment="留言ID")
  created_at = Column(DateTime, default=lambda:datetime.now(BEIJING_TZ), comment="评论时间")

  # 关联用户和留言
  author = relationship("User", back_populates="comments")
  message = relationship("Message", back_populates="comments")
