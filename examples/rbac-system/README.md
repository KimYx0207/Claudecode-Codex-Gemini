# 案例2：RBAC权限系统

> 使用Skill方式实现复杂的权限管理系统

## 任务描述

设计并实现一个完整的RBAC（Role-Based Access Control）权限系统，包含：
1. 用户管理（User）
2. 角色管理（Role）
3. 权限管理（Permission）
4. 角色-权限关联（Role-Permission）
5. 用户-角色关联（User-Role）
6. 权限检查中间件

## 技术要求

- **语言**：Python 3.11+
- **框架**：FastAPI
- **数据库**：PostgreSQL（使用SQLAlchemy ORM）
- **缓存**：Redis（权限缓存）
- **API文档**：自动生成OpenAPI文档

## 执行命令

### 使用Skill方式

```bash
./.claude/skills/kim-orchestrator/scripts/orchestrate.sh "设计并实现RBAC权限系统，包含以下需求：

## 核心功能

### 1. 数据模型设计
- User表：id, username, email, password_hash, is_active, created_at
- Role表：id, name, description, is_system（系统角色不可删除）
- Permission表：id, resource, action, description（如：user:create, post:delete）
- user_roles表：user_id, role_id（多对多关系）
- role_permissions表：role_id, permission_id（多对多关系）

### 2. API接口设计

#### 角色管理
- POST /api/roles - 创建角色
- GET /api/roles - 获取角色列表（支持分页）
- GET /api/roles/{id} - 获取角色详情
- PUT /api/roles/{id} - 更新角色
- DELETE /api/roles/{id} - 删除角色（系统角色禁止删除）
- POST /api/roles/{id}/permissions - 分配权限给角色
- DELETE /api/roles/{id}/permissions/{permission_id} - 移除角色权限

#### 权限管理
- POST /api/permissions - 创建权限
- GET /api/permissions - 获取权限列表
- GET /api/permissions/{id} - 获取权限详情
- DELETE /api/permissions/{id} - 删除权限

#### 用户-角色管理
- POST /api/users/{id}/roles - 分配角色给用户
- DELETE /api/users/{id}/roles/{role_id} - 移除用户角色
- GET /api/users/{id}/permissions - 获取用户的所有权限（继承自所有角色）

### 3. 权限检查
- 中间件：@require_permission("resource:action")
- 检查逻辑：用户 → 所有角色 → 所有权限 → 是否包含目标权限
- Redis缓存：缓存用户权限（避免每次查数据库）
- 缓存失效：角色/权限变更时清除缓存

### 4. 预设角色
- admin（管理员）：所有权限
- editor（编辑）：创建、编辑、删除内容
- viewer（查看者）：只读权限

## 技术要求
- FastAPI 0.104+
- SQLAlchemy 2.0（异步）
- Pydantic V2（数据验证）
- Redis（权限缓存，TTL=1小时）
- Alembic（数据库迁移）
- pytest（单元测试+集成测试）

## 非功能需求
- 性能：权限检查<10ms（使用Redis缓存）
- 安全：防止越权访问、SQL注入
- 可扩展：支持自定义权限、动态权限
- 文档：OpenAPI自动文档+中文注释

## 验收标准
1. 所有API接口正常工作
2. 权限检查正确（有权限通过、无权限拒绝）
3. Redis缓存生效（权限变更后缓存更新）
4. 单元测试覆盖率>80%
5. API文档完整清晰"
```

## 预期时间

- **分析阶段**：5分钟（复杂度高，需要仔细设计）
- **代码生成**：18分钟（文件多，逻辑复杂）
- **代码审查**：10分钟（Gemini详细审查）
- **总计**：约33分钟

## 预期输出

### 文件结构

```
rbac-system/
├── app/
│   ├── models/
│   │   ├── user.py           # User模型
│   │   ├── role.py           # Role模型
│   │   └── permission.py     # Permission模型
│   ├── schemas/
│   │   ├── user.py           # User Pydantic模型
│   │   ├── role.py           # Role Pydantic模型
│   │   └── permission.py     # Permission Pydantic模型
│   ├── api/
│   │   ├── v1/
│   │   │   ├── roles.py      # 角色API
│   │   │   ├── permissions.py # 权限API
│   │   │   └── users.py      # 用户API
│   │   └── deps.py           # 依赖注入
│   ├── services/
│   │   ├── rbac_service.py   # RBAC核心服务
│   │   └── cache_service.py  # Redis缓存服务
│   ├── middleware/
│   │   └── permission.py     # 权限检查中间件
│   ├── core/
│   │   ├── config.py         # 配置
│   │   ├── database.py       # 数据库连接
│   │   └── security.py       # 安全工具
│   └── main.py               # FastAPI应用
├── alembic/
│   └── versions/             # 数据库迁移脚本
├── tests/
│   ├── test_roles.py
│   ├── test_permissions.py
│   └── test_rbac.py
├── requirements.txt
└── README.md
```

### 关键代码片段

**permission.py**（中间件示例）：
```python
from functools import wraps
from fastapi import HTTPException, Depends
from app.services.rbac_service import check_user_permission

def require_permission(resource: str, action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user, **kwargs):
            has_permission = await check_user_permission(
                current_user.id,
                f"{resource}:{action}"
            )
            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail="权限不足"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# 使用示例
@router.post("/posts")
@require_permission("post", "create")
async def create_post(current_user: User = Depends(get_current_user)):
    pass
```

**rbac_service.py**（核心逻辑示例）：
```python
from app.services.cache_service import CacheService

cache = CacheService()

async def check_user_permission(user_id: int, permission: str) -> bool:
    # 1. 从缓存读取用户权限
    cache_key = f"user_permissions:{user_id}"
    cached_permissions = await cache.get(cache_key)

    if cached_permissions:
        return permission in cached_permissions

    # 2. 从数据库查询用户的所有权限（通过角色）
    user_permissions = await get_user_all_permissions(user_id)

    # 3. 缓存权限（1小时）
    await cache.set(cache_key, user_permissions, ttl=3600)

    return permission in user_permissions
```

## 审查要点

Gemini会重点审查：

1. **数据模型设计**
   - ✅ 多对多关系是否正确？
   - ✅ 索引是否合理？
   - ✅ 是否有冗余字段？

2. **权限检查逻辑**
   - ✅ 是否会有越权漏洞？
   - ✅ 缓存逻辑是否正确？
   - ✅ 缓存失效机制是否完善？

3. **API设计**
   - ✅ RESTful规范
   - ✅ 错误处理
   - ✅ 输入验证

4. **性能优化**
   - ✅ Redis缓存是否生效？
   - ✅ 数据库查询是否优化？
   - ✅ 是否有N+1问题？

## 学习要点

1. **Skill方式的优势**
   - 保存所有中间结果（phase1/2/3）
   - 详细的执行日志
   - 可追溯的开发过程

2. **复杂系统设计**
   - 数据模型设计先行
   - API接口设计清晰
   - 缓存策略合理

3. **代码质量提升**
   - Gemini的审查报告非常详细
   - 学习最佳实践
   - 了解常见安全漏洞

## 扩展练习

完成基础功能后，尝试添加：

1. **分级权限**
   ```bash
   ./orchestrate.sh "为RBAC添加分级权限：权限可以有父子关系，拥有父权限自动拥有所有子权限"
   ```

2. **动态权限**
   ```bash
   ./orchestrate.sh "添加动态权限：支持基于资源所有者的权限判断（如：只能编辑自己的文章）"
   ```

3. **权限审计**
   ```bash
   ./orchestrate.sh "添加权限审计日志：记录所有权限变更、权限检查失败的操作"
   ```

---

**提示**：这是中等难度案例，适合进阶用户学习复杂系统设计。完成后可以尝试案例3（模块重构）。
