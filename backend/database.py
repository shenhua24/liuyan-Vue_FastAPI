from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
# 加载.env文件
load_dotenv()
# 配置sql数据库路径
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 连接数据库同时允许多线程访问数据库
engine = create_engine(
  SQLALCHEMY_DATABASE_URL,
  connect_args={"check_same_thread": False}
)

# 创建会话工厂，支持同时多线程进行SQL操作
# autocommit 事务自动提交关闭（优化效率）
# autoflush 提交事务后自动刷新关闭,
# 关联数据库bind=engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM的基础类
Base = declarative_base()