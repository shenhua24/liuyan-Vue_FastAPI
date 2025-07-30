# 留言墙项目技术文档

## 📋 项目概述

这是一个基于 Vue3 和 FastAPI 开发的现代化留言墙应用，支持用户注册登录、留言发布、点赞评论、图片上传以及完整的管理员后台功能。

### 🎯 核心功能

- **用户系统**：注册、登录、个人信息管理
- **留言功能**：发布、查看、点赞、评论
- **图片上传**：支持头像和图片上传
- **管理后台**：用户管理、内容管理、统计分析
- **权限控制**：角色权限、账户状态管理

## 🏗️ 技术架构

### 前端技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 现代化构建工具
- **Vue Router 4** - 官方路由管理器
- **Pinia** - 新一代状态管理库
- **Element Plus** - Vue 3 UI 组件库
- **Axios** - HTTP 客户端库

### 后端技术栈

- **FastAPI** - 现代化 Python Web 框架
- **SQLAlchemy** - Python ORM 框架
- **SQLite** - 轻量级数据库
- **JWT** - JSON Web Token 认证
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证库

## 📁 项目结构

```
demo-liuyan/
├── frontend/                 # Vue3前端项目
│   ├── src/
│   │   ├── components/       # 可复用组件
│   │   │   └── ImageUpload.vue
│   │   ├── views/           # 页面组件
│   │   │   ├── Login.vue    # 登录页面
│   │   │   ├── Register.vue # 注册页面
│   │   │   ├── Home.vue     # 主页布局
│   │   │   ├── Messages.vue # 留言墙页面
│   │   │   ├── Profile.vue  # 个人信息页面
│   │   │   └── Admin.vue    # 管理员后台
│   │   ├── stores/          # 状态管理
│   │   │   └── user.js      # 用户状态管理
│   │   ├── router/          # 路由配置
│   │   │   └── index.js     # 路由定义
│   │   └── utils/           # 工具函数
│   │       └── api.js       # API请求封装
│   ├── package.json         # 依赖配置
│   ├── vite.config.js       # Vite配置
│   └── index.html           # HTML模板
├── backend/                 # FastAPI后端项目
│   ├── main.py             # 主应用文件
│   ├── models.py           # 数据模型
│   ├── schemas.py          # 数据验证模式
│   ├── database.py         # 数据库配置
│   ├── auth.py             # 身份验证
│   ├── requirements.txt    # Python依赖
│   ├── uploads/            # 文件上传目录
│   └── liuyan.db          # SQLite数据库文件
├── README.md               # 项目说明
└── 技术文档.md             # 技术文档
```

## 🗄️ 数据库设计

### 用户表 (users)

| 字段            | 类型        | 说明                 |
| --------------- | ----------- | -------------------- |
| id              | Integer     | 主键，自增           |
| username        | String(50)  | 用户名，唯一         |
| hashed_password | String(255) | 加密密码             |
| nickname        | String(50)  | 昵称                 |
| avatar          | String(255) | 头像路径             |
| role            | Enum        | 用户角色(user/admin) |
| is_active       | Boolean     | 账户状态             |
| created_at      | DateTime    | 创建时间             |

### 留言表 (messages)

| 字段       | 类型     | 说明          |
| ---------- | -------- | ------------- |
| id         | Integer  | 主键，自增    |
| content    | Text     | 留言内容      |
| author_id  | Integer  | 作者 ID，外键 |
| created_at | DateTime | 创建时间      |

### 点赞表 (likes)

| 字段       | 类型     | 说明          |
| ---------- | -------- | ------------- |
| id         | Integer  | 主键，自增    |
| user_id    | Integer  | 用户 ID，外键 |
| message_id | Integer  | 留言 ID，外键 |
| created_at | DateTime | 点赞时间      |

### 评论表 (comments)

| 字段       | 类型     | 说明            |
| ---------- | -------- | --------------- |
| id         | Integer  | 主键，自增      |
| content    | Text     | 评论内容        |
| author_id  | Integer  | 评论者 ID，外键 |
| message_id | Integer  | 留言 ID，外键   |
| created_at | DateTime | 评论时间        |

## 🔐 身份验证系统

### JWT Token 认证

- **算法**：HS256
- **过期时间**：30 天
- **存储位置**：localStorage + HTTP Header
- **自动刷新**：支持 token 自动续期

### 权限控制

- **用户角色**：普通用户(user) / 管理员(admin)
- **路由守卫**：基于角色的页面访问控制
- **API 权限**：接口级别的权限验证
- **状态检查**：实时账户状态监控

### 账户状态管理

- **多层拦截**：登录、路由、API、定期检查
- **即时生效**：账户禁用立即拦截访问
- **友好提示**：明确的错误信息提示
- **自动清理**：禁用后自动清除登录状态

## 📡 API 接口文档

### 用户认证接口

```
POST /api/register     # 用户注册
POST /api/login        # 用户登录
GET  /api/user/profile # 获取用户信息
PUT  /api/user/profile # 更新用户信息
```

### 留言相关接口

```
GET  /api/messages              # 获取留言列表
POST /api/messages              # 发布留言
POST /api/messages/{id}/like    # 点赞/取消点赞
GET  /api/messages/{id}/comments # 获取评论列表
POST /api/comments              # 发表评论
```

### 文件上传接口

```
POST /api/upload       # 上传文件
```

### 管理员接口

```
GET    /api/admin/users        # 获取用户列表
PUT    /api/admin/users/{id}   # 更新用户信息
DELETE /api/admin/messages/{id} # 删除留言
GET    /api/admin/stats        # 获取统计信息
```

## 🎨 前端架构设计

### 组件化设计

- **页面组件**：负责页面级别的业务逻辑
- **通用组件**：可复用的功能组件
- **布局组件**：页面布局和导航

### 状态管理

- **用户状态**：登录信息、个人资料
- **响应式数据**：自动更新 UI
- **持久化存储**：localStorage 同步

### 路由设计

- **嵌套路由**：主页下的子页面
- **路由守卫**：权限控制和状态检查
- **动态导入**：按需加载页面组件

## 🔧 开发环境配置

### 环境要求

- **Node.js**: >= 16.0.0
- **Python**: >= 3.8
- **npm**: >= 8.0.0

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd demo-liuyan
```

#### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 启动项目

#### 启动后端服务

```bash
cd backend
python main.py
# 服务运行在 http://localhost:8001
```

#### 启动前端服务

```bash
cd frontend
npm run dev
# 服务运行在 http://localhost:5173
```

## 🚀 部署指南

### 生产环境配置

#### 后端部署

1. **环境变量配置**

```bash
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="your-production-database-url"
```

2. **使用 Gunicorn 部署**

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### 前端部署

1. **构建生产版本**

```bash
npm run build
```

2. **使用 Nginx 部署**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔍 功能特性详解

### 图片上传系统

- **支持格式**：JPG、PNG、GIF
- **大小限制**：2MB
- **存储方式**：本地文件系统
- **URL 生成**：自动生成访问链接
- **拖拽上传**：支持拖拽和点击上传

### 实时交互功能

- **点赞系统**：实时点赞状态更新
- **评论系统**：嵌套评论显示
- **状态同步**：前后端数据实时同步
- **用户体验**：流畅的交互动画

### 管理员后台

- **用户管理**：查看、编辑、禁用用户
- **内容管理**：删除不当留言
- **统计分析**：用户数、留言数等统计
- **权限控制**：管理员专属功能

## 🛡️ 安全机制

### 数据验证

- **前端验证**：表单输入验证
- **后端验证**：Pydantic 数据模型验证
- **SQL 注入防护**：ORM 自动防护
- **XSS 防护**：输入内容转义

### 权限安全

- **JWT 安全**：密钥加密和过期控制
- **角色权限**：基于角色的访问控制
- **API 权限**：接口级别权限验证
- **状态监控**：实时账户状态检查

## 📊 性能优化

### 前端优化

- **代码分割**：路由级别的懒加载
- **组件缓存**：合理使用 keep-alive
- **图片优化**：图片压缩和格式优化
- **请求优化**：防抖和节流处理

### 后端优化

- **数据库优化**：索引和查询优化
- **缓存策略**：合理使用缓存
- **异步处理**：FastAPI 异步特性
- **文件处理**：高效的文件上传处理

## 🐛 常见问题解决

### 开发环境问题

1. **端口冲突**：修改配置文件中的端口号
2. **依赖安装失败**：检查 Node.js 和 Python 版本
3. **数据库连接失败**：检查数据库文件权限

### 功能问题

1. **图片上传失败**：检查文件大小和格式
2. **登录失败**：检查用户名密码和账户状态
3. **权限不足**：检查用户角色和权限配置

## 📈 扩展建议

### 功能扩展

- **消息通知**：实时消息推送
- **社交功能**：关注、私信等
- **内容审核**：自动内容审核
- **数据分析**：更详细的统计分析

### 技术升级

- **数据库升级**：迁移到 PostgreSQL 或 MySQL
- **缓存系统**：引入 Redis 缓存
- **消息队列**：使用 Celery 处理异步任务
- **容器化部署**：Docker 容器化部署

## 📞 技术支持

如有技术问题，请参考：

1. **项目 README**：基础使用说明
2. **API 文档**：http://localhost:8001/docs
3. **源码注释**：详细的中文注释
4. **测试用例**：参考测试脚本

## 🧪 测试指南

### 功能测试流程

#### 1. 用户注册登录测试

```bash
# 测试步骤
1. 访问 http://localhost:5173
2. 点击"立即注册"创建新账户
3. 使用新账户登录系统
4. 验证登录状态和用户信息显示
```

#### 2. 留言功能测试

```bash
# 测试步骤
1. 登录后进入留言墙页面
2. 发布新留言，验证内容显示
3. 点赞留言，验证点赞数变化
4. 发表评论，验证评论显示
5. 测试加载更多功能
```

#### 3. 管理员功能测试

```bash
# 默认管理员账户
用户名: admin
密码: admin123

# 测试步骤
1. 使用管理员账户登录
2. 进入管理后台页面
3. 测试用户管理功能
4. 测试留言删除功能
5. 查看统计信息
```

#### 4. 图片上传测试

```bash
# 测试步骤
1. 进入个人信息页面
2. 上传头像图片（支持拖拽）
3. 验证图片预览和保存
4. 检查头像在各页面的显示
```

### 自动化测试

#### 后端 API 测试

```python
# 运行测试脚本
cd backend
python test_login.py      # 测试登录功能
python test_user_ban.py   # 测试用户禁用功能
```

#### 前端单元测试

```bash
# 安装测试依赖
npm install --save-dev @vue/test-utils vitest

# 运行测试
npm run test
```

## 📝 开发规范

### 代码规范

#### 前端代码规范

```javascript
// 1. 组件命名使用PascalCase
export default {
  name: "UserProfile",
};

// 2. 变量命名使用camelCase
const userName = ref("");
const isLoading = ref(false);

// 3. 常量使用UPPER_SNAKE_CASE
const API_BASE_URL = "http://localhost:8001";

// 4. 函数命名使用动词开头
const handleSubmit = () => {};
const getUserInfo = () => {};
```

#### 后端代码规范

```python
# 1. 类名使用PascalCase
class UserModel(Base):
    pass

# 2. 函数名使用snake_case
def get_user_by_id(user_id: int):
    pass

# 3. 常量使用UPPER_SNAKE_CASE
SECRET_KEY = "your-secret-key"

# 4. 类型注解
def create_user(user_data: UserCreate) -> UserResponse:
    pass
```

### Git 提交规范

```bash
# 提交信息格式
<type>(<scope>): <description>

# 类型说明
feat:     新功能
fix:      修复bug
docs:     文档更新
style:    代码格式调整
refactor: 代码重构
test:     测试相关
chore:    构建过程或辅助工具的变动

# 示例
feat(auth): 添加用户登录功能
fix(upload): 修复图片上传失败问题
docs(api): 更新API文档
```

## 🔧 配置文件说明

### 前端配置文件

#### vite.config.js

```javascript
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  css: {
    postcss: {},
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      "/api": {
        target: "http://localhost:8001",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
```

#### package.json 关键配置

```json
{
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "element-plus": "^2.4.4"
  }
}
```

### 后端配置文件

#### main.py 关键配置

```python
# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

#### auth.py 配置

```python
# JWT配置
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天
```

## 📊 监控和日志

### 应用监控

```python
# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
    return response
```

### 错误日志

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 性能监控

```javascript
// 前端性能监控
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log(`${entry.name}: ${entry.duration}ms`);
  }
});
observer.observe({ entryTypes: ["navigation", "resource"] });
```

## 🔒 安全最佳实践

### 密码安全

```python
# 使用bcrypt加密密码
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### 输入验证

```python
# 使用Pydantic进行数据验证
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)
    nickname: Optional[str] = Field(None, max_length=50)
```

**项目版本**: 1.0.0
**最后更新**: 2025 年 7 月
**维护状态**: 积极维护
**技术支持**: 详见项目 README 和源码注释
