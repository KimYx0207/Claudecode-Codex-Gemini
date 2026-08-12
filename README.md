# Kim 智能多CLI编排系统

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/KimYx0207/Claudecode-Codex-Gemini?style=social)](https://github.com/KimYx0207/Claudecode-Codex-Gemini)
[![GitHub forks](https://img.shields.io/github/forks/KimYx0207/Claudecode-Codex-Gemini?style=social)](https://github.com/KimYx0207/Claudecode-Codex-Gemini)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/KimYx0207/Claudecode-Codex-Gemini)
[![Language](https://img.shields.io/badge/language-Python-orange.svg)](https://github.com/KimYx0207/Claudecode-Codex-Gemini)

**让 Claude Code 自动协调多个 AI 工具（Sonnet、Codex、Gemini），全流程自动化**

</div>

> 🔗 **GitHub仓库**：[https://github.com/KimYx0207/Claudecode-Codex-Gemini](https://github.com/KimYx0207/Claudecode-Codex-Gemini)

> 老金的开源知识库，实时更新群二维码：https://my.feishu.cn/wiki/OhQ8wqntFihcI1kWVDlcNdpznFf

---

## 📞 联系方式

<div align="center">
  <img src="https://raw.githubusercontent.com/KimYx0207/Claude-Code-x-OpenClaw-Guide-Zh/main/images/二维码基础款.png" alt="联系方式" width="600"/>
  <p><strong>获取更多AI资讯和技术支持</strong></p>
  <p>
    🌐 <a href="https://www.aiking.dev/">aiking.dev</a>
  </p>
</div>

---

<img width="876" height="544" alt="image" src="https://github.com/user-attachments/assets/79f6669a-d0b3-47db-8b3f-0f38cf0b97b2" />

## 📝 更新日志

### 2025-12-08
- **新增命令**：`/kim-ui2code` - 截图转代码（Gemini看图 + Claude规划 + Codex生成 + Gemini审查）
- **三引擎联动**：真正发挥Gemini多模态视觉能力，从设计稿直接生成前端代码
- **命令扩展**：从9个命令扩展到10个命令

### 2025-12-07
- **品牌升级**：所有命令从 `ai-` 改为 `kim-`，作为老金的个人标识
- **命令扩展**：从3个命令扩展到9个命令，按使用逻辑排序
- **新增命令**：
  - `/kim-setup` - 环境配置检测
  - `/kim-help` - 帮助指南和命令推荐
  - `/kim-plan` - 需求拆解为任务列表
  - `/kim-crud` - CRUD代码生成
  - `/kim-api` - API端点生成
  - `/kim-form` - 表单组件生成
- **健康检查**：添加MCP Server健康检查模块
- **智能提示**：核心命令执行后推荐相关命令

### 2025-12-06
- **新增命令**：增加 `/kim-code`（Claude+Codex快速开发）和 `/kim-review`（Claude+Gemini代码审查）两个精简版命令
- **文档整合**：docs目录从12个文件精简到5个核心文档，删除冗余博客文章
- **文档去重**：移除installation.md、claude-code-specs.md、README.md中的重复内容
- **新增规范**：skill增加「完成后规范」，要求每次更新后记录更新日志
- **usage.md增强**：整合多模型协作规范（Codex/Gemini分工指南）

### 2025-12-05
- **项目初始化**：创建智能多CLI编排系统
- **MCP Server**：实现Codex和Gemini的MCP封装
- **5种集成方式**：Command、Skill、MCP、Subagent、Hooks
- **JWT认证模块**：完整的用户认证示例代码

---

# Kim智能多CLI编排系统 (Kim Orchestrator)

> 让Claude Code自动协调多个AI工具（Sonnet、Codex、Gemini）完成需求分析→代码生成→代码审查的完整工作流

## 🎯 项目简介

这个项目解决了**多个AI工具信息不互通**的痛点：
- 以前：Claude分析完需求，手动复制到Codex；Codex写完代码，手动粘贴到Gemini审查；来回切换效率低
- 现在：一个命令启动，Claude自动协调Codex和Gemini，全流程自动化

**效率提升：从20分钟手动操作 → 7分钟自动完成**

## 🌟 核心特性

### 三个AI的最佳组合

| AI模型 | 价格 | 职责 | 核心优势 |
|--------|------|------|----------|
| Claude Sonnet 4.5 | $3/$15/M | 需求分析+编排 | 编排能力强，性价比高 |
| GPT-5.1 Codex Max | $1.25/$10/M | 代码生成 | 最便宜、最稳定、质量高 |
| Gemini 3 Pro | **免费** | 代码审查 | 审查最细致（1000次/天） |

**成本对比**：全用Sonnet $0.105；组合使用只要 $0.056（**省47%**，质量还最高）

### 5种集成方式

1. **Command（Slash命令）** - 最适合新手（⭐ 最简单）
2. **Skill（技能包）** - 最适合进阶用户（⭐⭐⭐ 中等，可复用）
3. **MCP（Model Context Protocol）** - 最适合长期协作（⭐⭐⭐⭐ 较难，上下文共享）
4. **Subagent（子智能体）** - 最适合并行任务（⭐⭐ 简单，但成本高）
5. **Hooks（钩子）** - 最适合自动化（⭐⭐⭐ 中等，自动质检）

## 📦 快速安装

```bash
# 安装三个CLI工具
npm install -g @anthropic-ai/claude-code
npm i -g @openai/codex
npm install -g @google/gemini-cli

# Gemini需要网页授权（1000次/天免费）
gemini auth login
```

> 📖 **详细安装指南**（API配置、环境变量、故障排查）请查看 [installation.md](docs/installation.md)

## 🚀 快速开始

### 10个Kim命令（按使用顺序排列）

| 序号 | 命令 | 引擎组合 | 说明 |
|------|------|----------|------|
| 1 | `/kim-setup` | Claude | 环境配置检测 |
| 2 | `/kim-help` | Claude | 帮助指南，智能推荐命令 |
| 3 | `/kim-plan` | Claude | 需求拆解为任务列表 |
| 4 | `/kim-crud` | Claude + Codex | CRUD代码生成 |
| 5 | `/kim-api` | Claude + Codex | API端点生成 |
| 6 | `/kim-form` | Claude + Codex | 表单组件生成 |
| 7 | `/kim-code` | Claude + Codex | 代码生成（快速开发） |
| 8 | `/kim-review` | Claude + Gemini | 代码审查（深度分析） |
| 9 | `/kim-team` | 三引擎协作 | 完整流程（生产级） |
| 10 | `/kim-ui2code` | 三引擎协作 | 截图转代码（设计稿→前端代码） |

### 使用示例

```bash
# 首次使用，检测环境
/kim-setup

# 不知道用什么命令？
/kim-help "我想生成一个用户表的CRUD"

# 大需求拆解
/kim-plan "实现用户认证系统，包括注册、登录、忘记密码"

# CRUD生成
/kim-crud "User表：id, username, email, password, created_at"

# API生成
/kim-api "发送验证码接口，参数email和type"

# 表单生成
/kim-form "登录表单：用户名、密码、记住我"

# 快速开发（跳过审查）
/kim-code "实现一个简单的计算器类"

# 代码审查
/kim-review "src/auth/utils.py"

# 完整流程（生产级）
/kim-team "实现JWT登录功能，包含注册、登录、token刷新"

# 截图转代码（设计稿→前端代码）
/kim-ui2code "./designs/login-page.png"
```

### 命令选择决策树

```
你的需求是什么？
│
├─ 首次使用/环境问题 ──────────→ /kim-setup
│
├─ 不知道用什么命令 ──────────→ /kim-help
│
├─ 大需求需要规划 ────────────→ /kim-plan
│
├─ 生成代码
│   ├─ CRUD相关 ──────────────→ /kim-crud
│   ├─ API接口 ───────────────→ /kim-api
│   ├─ 表单组件 ──────────────→ /kim-form
│   ├─ 其他代码 ──────────────→ /kim-code
│   └─ 有设计稿/截图 ─────────→ /kim-ui2code ⭐新
│
├─ 审查现有代码 ──────────────→ /kim-review
│
└─ 生产级完整流程 ────────────→ /kim-team

💡 简单问题直接对话即可，无需使用命令
```

## 📁 项目结构

```
.
├── pyproject.toml               # 项目配置（依赖、mypy、ruff、pytest）
├── .mcp.json                    # MCP服务器配置（Claude Code标准）
├── mcp-config.json              # 统一配置文件（代理、权限等）
├── src/                         # 生产级Python代码
│   ├── app.py                   # FastAPI入口
│   ├── auth/                    # JWT认证模块
│   │   ├── models.py            # ORM模型
│   │   ├── schemas.py           # Pydantic验证
│   │   ├── router.py            # API路由
│   │   ├── service.py           # 业务逻辑
│   │   └── utils.py             # 工具函数
│   └── core/
│       ├── config.py            # 配置管理
│       └── database.py          # 数据库连接
├── tests/                       # 测试目录
│   ├── conftest.py              # pytest fixtures
│   └── auth/
│       ├── test_utils.py        # 工具函数测试
│       └── test_schemas.py      # Schema验证测试
├── .claude/
│   ├── commands/                # 10个Kim命令
│   │   ├── kim-setup.md         # 环境配置
│   │   ├── kim-help.md          # 帮助指南
│   │   ├── kim-plan.md          # 需求拆解
│   │   ├── kim-crud.md          # CRUD生成
│   │   ├── kim-api.md           # API生成
│   │   ├── kim-form.md          # 表单生成
│   │   ├── kim-code.md          # 代码生成
│   │   ├── kim-review.md        # 代码审查
│   │   ├── kim-team.md          # 完整流程
│   │   └── kim-ui2code.md       # 截图转代码
│   └── skills/
│       └── kim-orchestrator/
│           ├── skill.yaml       # Skill配置
│           ├── scripts/
│           │   └── orchestrate.sh
│           └── prompts/
│               ├── phase1-analyze.md
│               ├── phase2-code.md
│               ├── phase3-review.md
│               └── health-check.md  # 健康检查模块
├── mcp-servers/
│   ├── codex-server/
│   │   ├── index.js             # Codex MCP Server
│   │   └── README.md
│   ├── gemini-server/
│   │   ├── index.js             # Gemini MCP Server
│   │   └── README.md
│   └── INSTALLATION.md          # MCP配置指南
├── docs/                        # 文档目录
├── examples/                    # 使用案例
│   ├── login-feature/           # 案例1：登录功能
│   ├── rbac-system/             # 案例2：RBAC权限
│   ├── module-refactor/         # 案例3：模块重构
│   └── alternative-auth-impl/   # 备选认证实现（Integer PK + Token Hash）
└── .github/
    └── workflows/
        └── ci.yml               # GitHub Actions CI配置
```

## ⚙️ 配置文件说明

### mcp-config.json（统一配置）

```json
{
  "proxy": {
    "enabled": true,
    "http": "http://127.0.0.1:15236",
    "https": "http://127.0.0.1:15236"
  },
  ...
}
```

> ⚠️ **重要**：`15236` 是你自己的魔法端口，必须根据你本地的代理端口修改！
>
> Gemini网页认证（`gemini auth`）需要通过代理访问Google服务，如果端口配置错误将无法完成认证。
>
> 常见代理端口：Clash(7890)、V2Ray(10808)、自定义端口等，请检查你的代理软件设置。

### .mcp.json（Claude Code标准配置）

```json
{
  "mcpServers": {
    "codex": {
      "type": "stdio",
      "command": "node",
      "args": ["mcp-servers/codex-server/index.js"]
    },
    "gemini": {
      "type": "stdio",
      "command": "node",
      "args": ["mcp-servers/gemini-server/index.js"]
    }
  }
}
```

## 📚 文档

- [详细安装指南](docs/installation.md) - 工具安装、API配置、环境变量
- [使用说明](docs/usage.md) - 5种方式的详细教程（含多模型协作规范）
- [方式对比](docs/comparison.md) - 选择最适合你的方式
- [踩坑记录](docs/troubleshooting.md) - 常见问题解决方案
- [Claude Code规范](docs/claude-code-specs.md) - Command/Skill/MCP/Hooks/Subagent规范

## 🛠️ 开发环境设置

### 安装依赖

```bash
# 克隆项目
git clone <repo-url>
cd 智能多Cli编排系统_Skill

# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖（包含开发工具）
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并显示覆盖率
pytest --cov=src --cov-report=term-missing

# 只运行特定测试
pytest tests/auth/test_utils.py -v
```

### 代码检查

```bash
# 类型检查
mypy src/

# 代码风格检查
ruff check src/ tests/

# 自动格式化
ruff format src/ tests/
```

## 🎯 设计原则（Linus式）

1. **Good Taste** - 简化数据结构，消除特殊情况
2. **Never Break Userspace** - 零破坏性，向后兼容
3. **实用主义** - 解决真实问题，不搞过度设计
4. **简洁癖** - 核心脚本控制在150行内

## 🤝 贡献

欢迎提Issue和PR！

## 📄 开源协议

**CC BY-NC 4.0** (署名-非商业性使用)

本项目仅供学习和个人使用，**禁止商业用途**。如需商业授权请联系作者。

---

**作者**：老金（产品经理，AI工具实践者）
