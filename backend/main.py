from fastapi import FastAPI,Depends, HTTPException,status,UploadFile,File
from database import Base,engine,SessionLocal
from models import User,UserRole,Message,Like,Comment
from auth import get_password_hash,verify_token,verify_password,create_access_token
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html,get_swagger_ui_oauth2_redirect_html
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from schemas import (UserCreate, UserResponse, UserLogin, UserUpdate,
                      MessageResponse, MessageCreate, CommentResponse,CommentCreate
                      ,AdminUserResponse,AdminUserUpdate)
import uuid
import uvicorn
import json
# 创建所有数据库表
Base.metadata.create_all(bind=engine)

# 创建管理员账号
def create_default_admin():
  # 创建一个数据库会话线程
  db = SessionLocal()
  try:
    # 检测是否已有管理员账号 first()返回第一个查询结果
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    # 如果管理员账号不存在，则创建
    if not admin:
      admin_user = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        nickname="管理员",
        role=UserRole.ADMIN,
        is_active=True
      )
      # 执行插入sql语句完成Create操作
      db.add(admin_user)
      # 提交事务
      db.commit()
      print("管理员账号已创建：admin/admin123")
  finally:
    # 如果管理员用户已经创建则直接关闭数据库线程
    db.close()

# 初始化管理员
create_default_admin()

# 创建文件上传目录
# Path相当于os.path
UPLOAD_DIR = Path("uploads")
# exist_ok 若文件存在则不创建，不存在则创建
UPLOAD_DIR.mkdir(exist_ok=True)

# 创建FastAPI应用实例
app = FastAPI(
  title="留言墙API",
  description="一个简单的留言墙API，支持用户注册、登录、留言、点赞和评论等功能。",
  version="1.0.0",
  docs_url=None,  # 禁用默认的Swagger UI
  redoc_url=None  # 禁用默认的ReDoc UI
)

# 服务器挂载静态文件
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")
# 添加CROS中间件，解决跨域问题
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"], # 允许前端发送请求的源地址
  allow_credentials=True, # 允许携带jwt token
  allow_methods=["*"], # 允许所有http方法
  allow_headers=["*"], # 允许所有请求头
)

# 安全提取token
security = HTTPBearer()

# 数据库会话依赖
def get_db():
  db = SessionLocal() # 从会话工程中创建一会话线程
  try:
    yield db # 返回会话线程，会话结束后执行finally语句
  finally:
    db.close() # 关闭会话线程，释放资源

# 获取当前用户  HTTPAuthorizationCredentials返回的类型  Session相当于一个sql的会话
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db:Session=Depends(get_db)):
  # 获取jwt token
  token = credentials.credentials
  # token解码
  payload = verify_token(token)
  if payload is None:
    raise HTTPException(
      status_code = status.HTTP_401_UNAUTHORIZED,
      detail = "无效的Token",
      headers={"WWW-Authenticate":"Bearer"}
    )
  # 获取用户ID sub里面一般是用户ID  401错误说明用户未登录或token无效
  user_id = payload.get("sub")
  user = db.query(User).filter(User.id == user_id).first()
  if user is None:
    raise HTTPException(
      status_code = status.HTTP_401_UNAUTHORIZED,
      detail = "用户不存在"
    )
  if not user.is_active:
    raise HTTPException(
      status_code = status.HTTP_401_UNAUTHORIZED,
      detail = "该账号已被禁用"
    )
  return user

# 获取管理员用户 403错误认证成功但是无权限
def get_admin_user(current_user:User = Depends(get_current_user)):
  if current_user.role != UserRole.ADMIN:
    raise HTTPException(
      status_code = status.HTTP_403_FORBIDDEN,
      detail = "权限不足，非管理员"
    )
  return current_user

@app.get("/")
async def root():
  return {"message":"欢迎使用留言墙API服务！如需查看接口文档，请访问/docs"}

# 返回favicon
@app.get("/favicon.ico")
async def favicon():
  return {"file":"static/favicon.ico"}

# 用户注册接口 返回响应类型为UserResponse数据类型
# post表单的json数据直接转换程UserCreate模式
@app.post("/api/register", response_model=UserResponse)
async def register(user:UserCreate,db: Session = Depends(get_db)):
  # 检查用户是否已经注册
  db_user = db.query(User).filter(User.username == user.username).first()
  if db_user:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="用户名已存在"
    )
  # 创建新用户
  # 明文密码加密
  hashed_password = get_password_hash(user.password)
  db_user = User(
    username=user.username,
    hashed_password=hashed_password,
    nickname=user.nickname or user.username,
    avatar=""
  )
  # 执行插入语句
  db.add(db_user)
  try:
    db.commit() # 提交事务
  except:
    db.rollback() # 回滚事务保证数据一致性
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="注册失败，请稍后再试"
    )
  finally:
    db.refresh(db_user) # 获得最新数据
  return UserResponse(
    # 不返回密码和哈希值
    id=db_user.id,
    username=db_user.username,
    nickname=db_user.nickname,
    avatar=db_user.avatar,
    role=db_user.role,
    is_active=db_user.is_active
  )

# 用户登录接口 无需返回类型
@app.get("/api/login")
async def login(user: UserLogin, db:Session = Depends(get_db)):

  # 验证用户是否存在
  db_user = db.query(User).filter(User.username == user.username).first()
  if not db_user or not verify_password(user.password, db_user.hashed_password):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="用户名或密码错误"
    )
  
  # 检测用户状态
  if not db_user.is_active:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="该账号已被禁用，请联系管理员"
    )
  
  # 验证成功，颁发通行证JWT token令牌 sub里面为用户ID
  access_token = create_access_token(data={"sub":str(db_user.id)})

  return{
    "access_token": access_token,
    "token_type":"bearer",
    "user":UserResponse(
      id=db_user.id,
      username=db_user.username,
      nickname=db_user.nickname,
      avatar=db_user.avatar,
      role=db_user.role,
      is_active=db_user.is_active
    )
  }

# 用户信息接口
# 用户信息获取
@app.get("/api/user/profile", response_model=UserResponse)
async def get_user_profile(current_user:User=Depends(get_current_user)):
  # 返回当前用户信息
  return UserResponse(
    id=current_user.id,
    username=current_user.username,
    nickname=current_user.nickname,
    avatar=current_user.avatar,
    role=current_user.role,
    is_active=current_user.is_active
  )

# 用户信息更新
@app.put("/api/user/profile", response_model=UserResponse)
async def update_user_profile(
  user_update: UserUpdate,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  # 更新用户的信息主要是昵称和头像
  if user_update.nickname is not None:
    current_user.nickname = user_update.nickname
  if user_update.avatar is not None:
    current_user.avatar = user_update.avatar

  try:
    db.commit() # 提交事务
  except:
    db.rollback() # 回滚事务保证数据一致性
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="更新失败，请稍后再试"
    )
  finally:
    db.refresh(current_user) # 获得最新数据

  return UserResponse(
    id=current_user.id,
    username=current_user.username,
    nickname=current_user.nickname,
    avatar=current_user.avatar,
    role=current_user.role,
    is_active=current_user.is_active
  )

# 留言信息页
# 获取留言信息
# 分页功能未实现（可优化）
@app.get("/api/messages", response_model=list[MessageResponse])
async def get_messages(
  # skip为初始页数, limit为每页数量, 后端分页实现
  # skip: int = 0,
  # limit: int = 10,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  # 获取留言列表 desc()按时间降序排列即最新的排在前面
  messages = db.query(Message).order_by(Message.created_at.desc()).all()

  result = []
  for message in messages:
    # 统计当前留言的点赞量
    likes_count = db.query(Like).filter(Like.message_id == message.id).count()
    # 统计当前留言的评论数量
    comments_count = db.query(Comment).filter(Comment.message_id == message.id).count()
    # 判断当前用户是否已经点赞
    is_liked = db.query(Like).filter(
      # 该点赞数据是否已经存在
      Like.message_id == message.id,
      # 该点赞数据是否属于当前用户
      Like.user_id == current_user.id
    ).first() is not None

  result.append(MessageResponse(
    id=message.id,
    content=message.content,
    created_at=message.created_at,
    author=UserResponse(
      id=message.author.id,
      username=message.author.username,
      nickname=message.author.nickname,
      avatar=message.author.avatar,
      role=message.author.role,
      is_active=message.author.is_active
    ),
    likes_count=likes_count,
    momments_count=comments_count,
    is_liked=is_liked
  ))
  return result

# 创建留言
@app.post("/api/messages",response_model=MessageResponse)
async def create_message(
  message: MessageCreate,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  db_message = Message(
    content=message.content,
    author_id=current_user.id
  )
  db.add(db_message)
  try:
    db.commit() # 提交事务
  except:
    db.rollback() # 回滚事务保证数据一致性
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="创建留言失败，请稍后再试"
    )
  finally:
    db.refresh(db_message) # 获得最新数据
  return MessageResponse(
    id=db_message.id,
    content=db_message.content,
    created_at=db_message.created_at,
    author=UserResponse(
      id=current_user.id,
      username=current_user.username,
      nickname=current_user.nickname,
      avatar=current_user.avatar,
      role=current_user.role,
      is_active=current_user.is_active
    )
  )

# 文件上传
@app.post("/api/upload")
async def upload_file(
  file: UploadFile = File(...),
  current_user: User = Depends(get_current_user)
):
  # 检查文件类型
  if not file.content_type.startswith('image/'):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="只允许上传图片文件"
    )
  
  # 生成唯一文件名 -1表示最后一个
  file_extension = file.filename.split(".")[-1]
  unique_filename = f"{uuid.uuid4()}.{file_extension}"
  file_path = UPLOAD_DIR / unique_filename

  # 保存文件 w表示写 b表示二进制 await异步读取
  with open(file_path, "wb")as buffer:
    content = await file.read()
    buffer.write(content)

  # 返回文件url
  file_url = f"/uploads/{unique_filename}"
  return{"url": file_url}

# 留言点赞
@app.post("/api/messages/{message_id}/like")
async def toggle_like(
  message_id: int,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  # 先判断留言是否存在
  message = db.query(Message).filter(Message.id == message_id).first()
  if not message:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="该留言不存在"
    )
  # 检查是否已经点赞了
  existing_like = db.query(Like).filter(
    Like.message_id == message_id,
    Like.user_id == current_user.id
  ).first()

  if existing_like:
    # 已有点赞，再次点击则取消点赞
    db.delete(existing_like)
    db.commit()
    return {"liked":False,"message":"取消点赞"}
  else:
    # 未点赞则点赞
    new_like = Like(
      message_id = message_id,
      user_id = current_user.id
    )
    db.add(new_like)
    db.commit()
    return {"liked":True, "message":"点赞成功"}
  
# 获取留言评论信息
@app.get("api/messages/{message_id}/comments", response_model=list[CommentResponse])
async def get_comments(
  message_id: int,
  db: Session = Depends(get_db)
):
  # 获取留言的评论列表
  comments = db.query(Comment).filter(
    Comment.message_id == message_id
  ).order_by(Comment.created_at.desc()).all()

  return [CommentResponse(
    id=comment.id,
    content=comment.content,
    created_at=comment.created_at,
    message_id=comment.message_id,
    author=UserResponse(
      id=comment.author.id,
      username=comment.author.username,
      nickname=comment.author.nickname,
      avatar=comment.author.avatar,
      role=comment.author.role,
      is_active=comment.author.is_active
    )
  )for comment in comments
  ]

# 创建评论
@app.post("/api/comments",response_model=CommentResponse)
async def create_comment(
  comment: CommentCreate,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  # 检查留言是否存在
  message = db.query(Message).filter(Message.id == comment.message_id).first()
  if not message:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="留言不存在"
    )
  
  # 创建评论
  db_comment = Comment(
    content=comment.content,
    message_id=comment.message_id,
    author_id=current_user.id
  )

  db.add(db_comment)
  db.commit()
  db.refresh(db_comment)

  return CommentResponse(
    id=db_comment.id,
    content=db_comment.content,
    created_at=db_comment.created_at,
    message_id=db_comment.message_id,
    author=UserResponse(
      id=current_user.id,
      username=current_user.username,
      nickname=current_user.nickname,
      avatar=current_user.avatar,
      role=current_user.role,
      is_active=current_user.is_active
    )
  )

# 管理员页面

# 获取用户留言总信息(用户管理)
@app.get("/api/admin/users", response_model=list[AdminUserResponse])
async def admin_get_users(
  # 分页管理(未实现)
  admin_user: User = Depends(get_admin_user),
  db: Session = Depends(get_db)
):
  # 获取用户列表
  users = db.query(User).all()
  result = []
  for user in users:
    # 统计用户留言数量
    messages_count = db.query(Message).filter(Message.author_id == user.id).count()
    result.append(
      AdminUserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        avatar=user.avatar,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        messages_count=messages_count
      )
    )
  return result

# 管理员更新用户信息
@app.put("/api/admin/users/{user_id}", response_model=AdminUserResponse)
async def admin_update_user(
  user_id: int,
  user_update: AdminUserUpdate,
  admin_user: User = Depends(get_admin_user),
  db: Session = Depends(get_db)
):
  user = db.query(User).filter(User.id == user_id).first()
  if not user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="用户不存在"
    )
  # 禁止管理员禁用自己
  if user.id == admin_user.id and user_update.is_active is False:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="不可禁用自己的账号"
    )
  # 更新用户信息
  if user_update.nickname is not None:
    user.nickname = user_update.nickname
  if user_update.role is not None:
    user.role = user_update.role
  if user_update.is_active is not None:
    user.is_active = user_update.is_active

  db.commit()
  db.refresh(user)

  # 统计用户留言数
  messages_count = db.query(Message).filter(Message.author_id == user.id).count()
  
  return AdminUserResponse(
    id=user.id,
    username=user.username,
    nickname=user.nickname,
    avatar=user.avatar,
    role=user.role,
    is_active=user.is_active,
    created_at=user.created_at,
    messages_count=messages_count
  )

# 删除留言
@app.delete("/api/admin/messages/{message_id}")
async def admin_delete_message(
  message_id: int,
  admin_user: User = Depends(get_admin_user),
  db: Session =Depends(get_db)
):
  message = db.query(Message).filter(Message.id == message_id).first()
  if not message:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="留言不存在"
    )
  # 删除相关的点赞和评论
  db.query(Like).filter(Like.message_id == message_id).delete()
  db.query(Comment).filter(Comment.message_id == message_id).delete()

  db.delete(message)
  db.commit()

  return {"detail":"留言删除成功"}

# 获取统计信息
@app.get("/api/admin/status")
async def admin_get_status(
  admin_user: User = Depends(get_admin_user),
  db: Session = Depends(get_db)
):
  # 统计信息
  total_users = db.query(User).count()
  active_users = db.query(User).filter(User.is_active == True).count()
  total_messages = db.query(Message).count()
  total_likes = db.query(Like).count()
  total_comments = db.query(Comment).count()

  return{
    "total_users": total_users,
    "active_users": active_users,
    "total_messages": total_messages,
    "total_likes": total_likes,
    "total_comments": total_comments
  }

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

# 启动FastAPI应用
if __name__ == "__main__":
  # 后端端口8001
  uvicorn.run(app, host="localhost", port=8001,  )