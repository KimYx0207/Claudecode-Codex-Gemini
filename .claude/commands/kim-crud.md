---
description: Kim CRUD生成命令 - 根据表名和字段生成完整增删改查代码
allowed-tools: Read, Write, Edit, Bash, Task
argument-hint: [表名和字段描述]
---

# Kim CRUD生成命令

> 输入表名和字段，生成完整的增删改查代码（Model + Schema + Router + Service）

你现在要生成CRUD代码：$ARGUMENTS

**模式说明**：这是模板化生成模式，专门处理数据库CRUD操作。

## 执行流程

### 阶段1：信息收集

首先分析用户输入，提取：
- **表名**：如 `User`、`Product`、`Order`
- **字段列表**：字段名、类型、约束
- **技术栈**：FastAPI/Express/Spring（检测项目现有框架）

如果信息不完整，询问用户：
```
📝 请补充以下信息：

1. 表名：User（已识别）
2. 字段（格式：字段名:类型:约束）：
   - id: int: 主键,自增
   - username: str: 唯一,必填
   - email: str: 唯一,必填
   - password: str: 必填
   - created_at: datetime: 默认当前时间

请确认或补充字段：
```

### 阶段2：检测项目技术栈

使用Glob和Read检测项目使用的框架：

```bash
# 检测FastAPI
ls pyproject.toml requirements.txt 2>/dev/null | xargs grep -l "fastapi"

# 检测Express
ls package.json 2>/dev/null | xargs grep -l "express"

# 检测Spring
ls pom.xml build.gradle 2>/dev/null
```

### 阶段3：调用Codex生成代码

使用MCP工具调用Codex，根据检测到的框架生成代码。

**FastAPI模板**（Python）：
```
生成以下文件：
1. models/{table_name}.py - SQLAlchemy ORM模型
2. schemas/{table_name}.py - Pydantic验证模型
3. routers/{table_name}.py - FastAPI路由（5个端点）
4. services/{table_name}.py - 业务逻辑层
```

**Express模板**（Node.js）：
```
生成以下文件：
1. models/{table_name}.js - Sequelize/Prisma模型
2. validators/{table_name}.js - Joi/Zod验证
3. routes/{table_name}.js - Express路由
4. services/{table_name}.js - 业务逻辑
```

### 阶段4：生成并保存代码

初始化工作目录并保存生成的代码：

```bash
mkdir -p .kim-orchestrator && echo "" > .kim-orchestrator/crud_result.md
```

将生成的代码保存到 `.kim-orchestrator/crud_result.md`，同时在项目中创建实际文件。

---

## 生成的API端点

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | /api/{table}s | 创建记录 |
| GET | /api/{table}s | 获取列表（分页） |
| GET | /api/{table}s/{id} | 获取单条记录 |
| PUT | /api/{table}s/{id} | 更新记录 |
| DELETE | /api/{table}s/{id} | 删除记录 |

---

## 使用示例

```bash
# 基础用法
/kim-crud "User表：id, username, email, password, created_at"

# 详细描述
/kim-crud "创建Product表，字段：id主键、name名称、price价格decimal、stock库存int、category分类"

# 指定框架
/kim-crud "用FastAPI生成Order表的CRUD，字段：订单号、用户ID、金额、状态"
```

---

## 生成代码示例（FastAPI）

### models/user.py
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

### schemas/user.py
```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
```

---

## 适用场景

✅ **适合使用 /kim-crud**：
- 需要快速生成标准CRUD
- 新建数据表
- 后台管理功能
- MVP快速开发

❌ **不适合**：
- 复杂业务逻辑 → `/kim-code`
- 非标准接口 → `/kim-api`
- 需要审查 → `/kim-review`
