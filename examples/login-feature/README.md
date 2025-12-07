# 案例1：JWT登录功能

> 使用Command方式快速实现登录功能

## 任务描述

实现一个完整的JWT登录功能，包含：
1. 用户注册（邮箱+密码）
2. 用户登录（返回JWT token）
3. Token刷新（延长有效期）
4. 密码加密（bcrypt）
5. 输入验证

## 技术要求

- **语言**：Node.js + TypeScript
- **框架**：Express.js
- **数据库**：PostgreSQL（使用Prisma ORM）
- **认证**：JWT（jsonwebtoken库）
- **加密**：bcrypt
- **验证**：express-validator

## 执行命令

### 使用Command方式

```bash
/kim-team "实现JWT登录功能，包含以下需求：

1. 用户注册接口（POST /api/auth/register）
   - 输入：email, password, username
   - 验证：email格式、密码强度（最少8位）
   - 密码用bcrypt加密存储
   - 返回：用户信息（不含密码）

2. 用户登录接口（POST /api/auth/login）
   - 输入：email, password
   - 验证：用户存在、密码正确
   - 返回：JWT token（有效期24小时）

3. Token刷新接口（POST /api/auth/refresh）
   - 输入：refresh_token
   - 验证：token有效性
   - 返回：新的access_token

技术栈：
- Node.js 18+ + TypeScript
- Express.js 4.x
- Prisma ORM + PostgreSQL
- jsonwebtoken
- bcrypt
- express-validator

要求：
- 包含完整的错误处理
- 添加单元测试（Jest）
- 提供README说明如何运行
- 遵循RESTful API规范"
```

## 预期时间

- **分析阶段**：1分钟
- **代码生成**：4分钟
- **代码审查**：2分钟
- **总计**：约7分钟

## 预期输出

### 文件结构

```
login-feature/
├── src/
│   ├── controllers/
│   │   └── authController.ts     # 认证控制器
│   ├── services/
│   │   └── authService.ts        # 认证服务
│   ├── middleware/
│   │   ├── authMiddleware.ts     # JWT验证中间件
│   │   └── validation.ts         # 输入验证
│   ├── utils/
│   │   ├── jwt.ts                # JWT工具函数
│   │   └── password.ts           # 密码加密工具
│   ├── types/
│   │   └── auth.types.ts         # 类型定义
│   └── app.ts                    # Express应用
├── tests/
│   └── auth.test.ts              # 单元测试
├── prisma/
│   └── schema.prisma             # 数据库Schema
├── package.json
├── tsconfig.json
└── README.md
```

### 关键代码片段

**authController.ts**（示例）：
```typescript
import { Request, Response } from 'express';
import * as authService from '../services/authService';

export const register = async (req: Request, res: Response) => {
  try {
    const { email, password, username } = req.body;
    const user = await authService.register({ email, password, username });
    res.status(201).json({ user });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};
```

**jwt.ts**（示例）：
```typescript
import jwt from 'jsonwebtoken';

const SECRET = process.env.JWT_SECRET || 'your-secret-key';

export const generateToken = (userId: string): string => {
  return jwt.sign({ userId }, SECRET, { expiresIn: '24h' });
};

export const verifyToken = (token: string): any => {
  return jwt.verify(token, SECRET);
};
```

## 审查要点

Gemini会审查以下内容：

1. **安全性**
   - ✅ 密码是否加密？
   - ✅ JWT secret是否从环境变量读取？
   - ✅ 是否防止SQL注入？

2. **输入验证**
   - ✅ 邮箱格式验证
   - ✅ 密码强度验证
   - ✅ 必填字段检查

3. **错误处理**
   - ✅ 用户不存在
   - ✅ 密码错误
   - ✅ Token过期

4. **代码质量**
   - ✅ 函数单一职责
   - ✅ 类型定义完整
   - ✅ 注释清晰

## 学习要点

1. **Command方式的优势**
   - 快速启动（一条命令）
   - 适合原型开发
   - 无需配置

2. **三个阶段的分工**
   - Claude分析需求 → 确定技术方案
   - Codex生成代码 → 完整可运行
   - Gemini审查质量 → 发现问题

3. **改进建议**
   - 如果审查发现问题，重新执行命令时加上Gemini的建议
   - 可以分阶段生成（先基础功能，再添加测试）

## 扩展练习

完成基础功能后，尝试添加：

1. **邮箱验证**
   ```bash
   /kim-team "为登录功能添加邮箱验证：注册后发送验证邮件，用户点击链接后激活账号"
   ```

2. **密码重置**
   ```bash
   /kim-team "添加密码重置功能：用户忘记密码时，发送重置链接到邮箱"
   ```

3. **双因素认证**
   ```bash
   /kim-team "添加双因素认证（2FA）：使用TOTP算法生成验证码"
   ```

---

**提示**：这是最简单的案例，适合新手熟悉AI编排流程。完成后可以尝试案例2（RBAC权限系统）。
