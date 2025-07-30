import os
from jose import jwt,JWTError
from passlib.context import CryptContext
from typing import Optional
from datetime import timedelta,datetime,timezone
from dotenv import load_dotenv
# 加载.env文件
load_dotenv()
# JWT token配置
SECRET_KEY = os.getenv("JWT_SECRET") # 钥匙
ALGORITHM = "HS256" # 加密算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60 # 有效期30天24小时60分钟

# 用户密码加密
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

# 输入明文密码vs数据库加密密码|验证
def verify_password(plain_password:str, hashed_password:str)-> bool:
  return pwd_context.verify(plain_password,hashed_password)

# 获取密码哈希值
def get_password_hash(password: str)->str:
  return pwd_context.hash(password)

# 创建JWT token令牌附加给json数据，且令牌有时间限制
def create_access_token(data:dict, expires_delta:Optional[timedelta]=None):
  to_encode = data.copy() # 不更改原数据，copy一份
  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp":expire})# 更新过期时间
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

# 验证jwt令牌
def verify_token(token:str)->Optional[dict]:
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
  except JWTError:
    return None

