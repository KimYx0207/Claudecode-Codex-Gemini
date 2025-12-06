# 使用说明

> 5种集成方式的详细使用教程

## 目录

1. [方式1：Command（最简单）](#方式1command最简单)
2. [方式2：Skill（最实用）](#方式2skill最实用)
3. [方式3：MCP（最强大）](#方式3mcp最强大)
4. [方式4：Subagent（最灵活）](#方式4subagent最灵活)
5. [方式5：Hooks（最自动）](#方式5hooks最自动)
6. [选择建议](#选择建议)

---

## 方式1：Command（最简单）

### 适用场景
- ✅ 新手入门
- ✅ 简单任务（如快速原型）
- ✅ 流程固定的任务
- ❌ 复杂工作流
- ❌ 需要保存中间结果

### 使用方法

#### 步骤1：确认配置文件存在

```bash
ls .claude/commands/ai-team.md
```

如果不存在，请先完成项目安装。

#### 步骤2：在Claude Code中使用

```bash
# 启动Claude Code
claude

# 使用Slash命令
/ai-team "实现用户登录功能"
```

#### 步骤3：等待执行

Claude会自动：
1. 分析需求（Claude自己完成）
2. 调用Codex生成代码
3. 调用Gemini审查代码
4. 返回完整报告

### 示例

#### 示例1：简单功能

```bash
/ai-team "实现一个计算器类，支持加减乘除"
```

**预计时间**：3-5分钟

#### 示例2：完整模块

```bash
/ai-team "实现JWT登录功能，包含注册、登录、token刷新、密码重置"
```

**预计时间**：5-10分钟

#### 示例3：系统设计

```bash
/ai-team "设计RESTful API接口，包含用户管理、文章管理、评论管理"
```

**预计时间**：7-15分钟

### 查看结果

所有中间文件保存在 `.ai-orchestrator/` 目录：

```bash
cat .ai-orchestrator/result.md  # 查看最终报告
cat .ai-orchestrator/phase2_code.md  # 查看生成的代码
cat .ai-orchestrator/phase3_review.md  # 查看审查报告
```

---

## 方式2：Skill（最实用）

### 适用场景
- ✅ 复杂多步骤任务
- ✅ 需要保存中间结果
- ✅ 需要错误重试
- ✅ 工作流复用
- ❌ 一次性简单任务
- ❌ 不熟悉bash脚本

### 使用方法

#### 步骤1：确认Skill配置

```bash
ls .claude/skills/ai-orchestrator/skill.yaml
ls .claude/skills/ai-orchestrator/scripts/orchestrate.sh
```

#### 步骤2：直接执行脚本

```bash
# 给脚本添加执行权限（首次使用）
chmod +x .claude/skills/ai-orchestrator/scripts/orchestrate.sh

# 执行任务
./.claude/skills/ai-orchestrator/scripts/orchestrate.sh "RBAC权限系统"
```

#### 步骤3：查看执行日志

脚本会实时输出日志：

```bash
[2025-12-04 12:00:00] 🚀 AI多引擎编排开始
[2025-12-04 12:00:00] 任务: RBAC权限系统
[2025-12-04 12:00:01] 🔍 检查工具安装情况...
[2025-12-04 12:00:01] ✅ codex 工具已安装
[2025-12-04 12:00:01] ✅ gemini 工具已安装
[2025-12-04 12:00:02] 📋 阶段1: 需求分析（Claude）
...
```

### 生成的文件

```bash
.ai-orchestrator/
├── phase1_requirements.json  # Claude的需求分析（JSON格式）
├── phase2_code.md            # Codex生成的代码（Markdown）
├── phase3_review.md          # Gemini的审查报告（Markdown）
├── result.md                 # 最终整合报告
└── orchestration.log         # 详细执行日志
```

### 示例

#### 示例1：复杂功能开发

```bash
./orchestrate.sh "实现完整的用户认证模块，包含：
1. JWT token生成和验证
2. 用户注册（邮箱验证）
3. 用户登录（支持记住密码）
4. 密码重置（邮件链接）
5. 用户权限管理
6. 单元测试覆盖"
```

**预计时间**：20-30分钟

#### 示例2：系统架构设计

```bash
./orchestrate.sh "设计一个微服务架构的电商系统，包含：
- 用户服务（User Service）
- 商品服务（Product Service）
- 订单服务（Order Service）
- 支付服务（Payment Service）
- 消息队列（RabbitMQ）
- API网关（Kong）
- 数据库设计（MySQL + Redis）"
```

**预计时间**：30-45分钟

#### 示例3：模块重构

```bash
./orchestrate.sh "重构现有的用户模块：
1. 分离Service层和Controller层
2. 添加Repository模式
3. 实现依赖注入
4. 添加单元测试
5. 优化数据库查询性能"
```

**预计时间**：40-60分钟

### 查看详细报告

```bash
# 打开最终报告
cat .ai-orchestrator/result.md

# 或用VS Code打开
code .ai-orchestrator/result.md

# 查看执行日志
cat .ai-orchestrator/orchestration.log
```

---

## 方式3：MCP（最强大）

### 适用场景
- ✅ 长期协作项目
- ✅ 需要保持上下文（会话管理）
- ✅ 持续开发（如整天重构）
- ❌ 一次性任务
- ❌ 不懂MCP Server开发
- ❌ 简单任务

### 核心概念

MCP（Model Context Protocol）通过**自定义MCP Server包装本地CLI**实现上下文共享：

```
Claude Code (主)
    ↓ (通过MCP调用)
Codex MCP Server → Codex CLI
    ↓ (上下文共享)
Gemini MCP Server → Gemini CLI
```

**关键特性**：`conversationId`机制让多个AI共享同一个上下文文件。

### 实现步骤

#### 步骤1：创建Codex MCP Server

创建文件 `codex-mcp-server.js`：

```javascript
#!/usr/bin/env node
// MCP Server - 包装Codex CLI，支持conversationId上下文传递

const { spawn } = require('child_process');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

// 会话上下文存储
const CONTEXT_DIR = path.join(process.env.HOME, '.mcp-context');
if (!fs.existsSync(CONTEXT_DIR)) {
  fs.mkdirSync(CONTEXT_DIR, { recursive: true });
}

// 监听stdin
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.on('line', (line) => {
  const request = JSON.parse(line);
  const { prompt, conversationId } = request;

  // 读取历史上下文
  let context = '';
  if (conversationId) {
    const contextFile = path.join(CONTEXT_DIR, `${conversationId}.json`);
    if (fs.existsSync(contextFile)) {
      const history = JSON.parse(fs.readFileSync(contextFile, 'utf-8'));
      context = history.map(item => `${item.role}: ${item.content}`).join('\\n\\n');
    }
  }

  // 构建完整提示词（包含历史上下文）
  const fullPrompt = context ? `${context}\\n\\n${prompt}` : prompt;

  // 调用Codex CLI
  const codex = spawn('codex', ['exec', fullPrompt]);

  let output = '';
  codex.stdout.on('data', (data) => {
    output += data.toString();
  });

  codex.on('close', () => {
    // 保存本次对话到上下文
    if (conversationId) {
      const contextFile = path.join(CONTEXT_DIR, `${conversationId}.json`);
      let history = [];
      if (fs.existsSync(contextFile)) {
        history = JSON.parse(fs.readFileSync(contextFile, 'utf-8'));
      }
      history.push({ role: 'user', content: prompt });
      history.push({ role: 'assistant', content: output });
      fs.writeFileSync(contextFile, JSON.stringify(history, null, 2));
    }

    // 返回结果
    console.log(JSON.stringify({
      result: output,
      conversationId: conversationId || `conv_${Date.now()}`
    }));
  });
});
```

同样方式创建 `gemini-mcp-server.js`（把`codex exec`改成`gemini -p`）。

#### 步骤2：连接MCP Server

```bash
# 连接Codex MCP Server
claude mcp add-json --scope user codex '{
  "type": "stdio",
  "command": "node",
  "args": ["/path/to/codex-mcp-server.js"]
}'

# 连接Gemini MCP Server
claude mcp add-json --scope user gemini '{
  "type": "stdio",
  "command": "node",
  "args": ["/path/to/gemini-mcp-server.js"]
}'
```

#### 步骤3：使用（整天持续开发）

在Claude Code中启动Plan Mode：

```
用户：重构用户模块，拆分Service层

Claude：好的，我先分析... [生成conversationId: conv_123]
       方案：拆分为UserService、AuthService、ProfileService

       现在让Codex生成UserService...
       [通过MCP调用Codex，传入conversationId: conv_123]

Codex：[读取conv_123上下文，知道要拆分Service层]
       生成UserService代码... [保存到conv_123]

Claude：代码生成完毕，让Gemini审查...
       [通过MCP调用Gemini，传入conversationId: conv_123]

Gemini：[读取conv_123，看到Claude的规划和Codex的代码]
        审查发现：UserService的依赖注入有问题... [保存到conv_123]

Claude：Codex改一下依赖注入...
       [通过MCP调用Codex，传入conversationId: conv_123]

Codex：[读取conv_123，看到Gemini的审查意见]
       已修正依赖注入问题... [保存到conv_123]
```

**核心价值**：`conversationId`让三个AI共享同一个上下文文件（`~/.mcp-context/conv_123.json`），实现真正的协作！

### 高级配置：多模型协作规范

如果你想让Claude Code自动按照最佳实践调用Codex和Gemini，可以在 `~/.claude/CLAUDE.md` 中添加协作规范：

```markdown
## 多模型协作规范

### 核心原则
Claude作为主架构师，根据以下分工调度Codex和Gemini：

1. **需求分析阶段**：将用户需求同时告知codex/gemini，进行迭代争辩、互为补充
2. **编码阶段**：向codex/gemini索要代码原型（unified diff patch），以此为参考重写生产级代码
3. **审查阶段**：完成编码后，必须使用codex review代码改动

### 模型分工

| 模型 | 擅长领域 | 限制 |
|------|----------|------|
| **Codex** | 后端逻辑、Bug定位、代码审查 | sandbox需设为read-only |
| **Gemini** | 前端设计、需求清晰化、任务规划 | 上下文仅32k，禁止后端代码 |

### 调用规范

**Codex调用**：
- 每次调用保存返回的SESSION_ID
- 使用sandbox="read-only"避免意外修改
- 擅长：后端逻辑、精准定位、Debug分析、代码审查

**Gemini调用**：
- 捕获返回的SESSION_ID用于多轮对话
- 严禁让Gemini编写复杂后端逻辑
- 擅长：需求清晰化、任务规划、前端原型（CSS/HTML/UI组件）

### 协作流程示例

1. 用户提出需求 → Claude分析
2. Claude将需求转发给Codex/Gemini讨论
3. 获取代码原型 → Claude重写为生产级代码
4. 实施修改 → Codex审查 → 迭代完善
```

---

## 方式4：Subagent（最灵活）

### 适用场景
- ✅ 独立模块并行开发
- ✅ 预算充足
- ✅ 追求速度
- ❌ 强依赖任务
- ❌ 预算紧张
- ❌ 简单任务

### 使用方法

在Claude Code中使用Task工具启动子智能体：

```javascript
// 启动后端子智能体
Task({
  subagent_type: "general-purpose",
  prompt: `开发后端API接口，用Codex CLI生成代码

  步骤：
  1. 分析API需求
  2. 调用本地codex生成代码：bash -c "codex exec '[需求描述]'"
  3. 保存到backend/目录
  `,
  model: "sonnet"
})

// 启动前端子智能体（同时进行）
Task({
  subagent_type: "general-purpose",
  prompt: `开发前端UI组件，用Codex CLI生成代码

  步骤：
  1. 分析UI需求
  2. 调用本地codex生成代码：bash -c "codex exec '[需求描述]'"
  3. 保存到frontend/目录
  `,
  model: "haiku"  // 用便宜的模型
})

// 主Claude等待两边完成后整合
```

**优点**：并行开发，时间减半
**缺点**：token消耗翻倍

---

## 方式5：Hooks（最自动）

### 适用场景
- ✅ 特定时机自动触发（如git commit前审查）
- ✅ 强制质检
- ✅ 不想手动执行
- ❌ 触发条件不固定
- ❌ 需要人工判断
- ❌ 调试期间

### 配置方法

编辑 `.claude/settings.json`：

```json
{
  "hooks": {
    "preToolUse": {
      "Bash(git commit)": [{
        "command": "bash",
        "args": [
          "-c",
          "gemini -p \\\"请审查以下代码改动：$(git diff --cached)\\\" > .review.md && cat .review.md"
        ]
      }]
    }
  }
}
```

### 使用效果

```bash
用户：git commit -m "feat: 添加用户登录"

[Hook自动触发]
正在调用Gemini审查代码改动...

Gemini报告：
代码质量：良好
发现1个安全问题：密码传输未加密
建议：使用HTTPS或加密传输

Claude：发现了安全问题，是否继续提交？
```

---

## 选择建议

### 新手路径
1. **从Command开始** - 熟悉流程（1-2天）
2. **进阶到Skill** - 处理复杂任务（3-5天）
3. **按需扩展** - 根据项目需要选择MCP/Subagent/Hooks

### 日常开发推荐组合
- **简单任务** → Command（快速）
- **复杂任务** → Skill（可复用）
- **质检流程** → Hooks（自动化）
- **大型重构** → MCP（上下文打通）

---

**下一步**：
- [方式对比](comparison.md) - 详细对比5种方式
- [实战案例](../examples/) - 查看真实项目案例
- [踩坑记录](troubleshooting.md) - 常见问题解决
