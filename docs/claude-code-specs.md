# Claude Code 完整规范指南

基于官方文档和最新实践，以下是Claude Code的五大核心功能的详细规范。

---

## 1. Command（自定义命令）规范

### 目录结构

```
project-root/
├── .claude/
│   └── commands/
│       ├── command-name.md
│       ├── namespace/
│       │   ├── subcommand1.md
│       │   └── subcommand2.md
```

### 配置文件格式（YAML Frontmatter + Markdown）

```markdown
---
description: 简明描述此命令的用途和调用时机（必需，最多255字符）
model: sonnet                           # 可选：sonnet/opus/haiku
allowed-tools: Bash, Read, Write        # 可选：逗号分隔的工具列表
argument-hint: [参数描述]                # 可选：CLI风格的参数提示
---

# 命令内容
$ARGUMENTS  # 获取用户参数
```

### 命名规则

| 文件位置 | 调用方式 |
|---------|---------|
| `.claude/commands/deploy.md` | `/deploy` |
| `.claude/commands/git/commit.md` | `/git:commit` |

---

## 2. Skill（技能）规范

### 目录结构

```
project-root/
├── .claude/
│   └── skills/
│       └── skill-name/
│           ├── SKILL.md           # 必需：技能定义
│           ├── scripts/           # 可选：辅助脚本
│           └── prompts/           # 可选：提示模板
```

### 配置文件格式（SKILL.md）

```yaml
---
name: skill-name-lowercase          # 必需：小写字母/数字/连字符
description: 何时调用此技能          # 必需：最多1024字符
allowed-tools: Read, Grep           # 可选：限制可用工具
---

# 技能内容和指导
```

### 特点
- **自动发现**：Claude根据描述自动判断何时使用
- **无需显式调用**：与Command不同，用户不需要输入`/skill-name`

---

## 3. MCP Server 规范

### 配置位置

| 文件 | 用途 | 版本控制 |
|------|------|---------|
| `.mcp.json` | 项目级配置 | 是 |
| `.claude/settings.local.json` | 本地私有配置 | 否 |

### 配置格式

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",              // stdio/http
      "command": "node",
      "args": ["index.js"],
      "env": {
        "API_KEY": "${ENV_VAR}"     // 支持环境变量
      }
    }
  }
}
```

### 传输类型

| 类型 | 用途 | 配置 |
|------|------|------|
| `stdio` | 本地进程 | `command` + `args` |
| `http` | 远程服务 | `url` |

---

## 4. Hooks（钩子）规范

### 配置位置
`.claude/settings.json` 或 `.claude/settings.local.json`

### 钩子事件

| 事件 | 触发时机 | 可阻止 |
|------|---------|--------|
| `PreToolUse` | 工具执行前 | 是 |
| `PostToolUse` | 工具执行后 | 否 |
| `SubagentStop` | Subagent停止时 | 是 |
| `Stop` | 主线程停止时 | 是 |

### 配置格式

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash validate.sh",
            "timeout": 5000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write '$file_path'",
            "suppressOutput": true
          }
        ]
      }
    ]
  }
}
```

### 钩子脚本输出格式

```json
// 继续执行
{"continue": true}

// 阻止执行
{"continue": false, "stopReason": "原因", "decision": "block"}
```

---

## 5. Subagent（子代理）规范

### 目录结构

```
project-root/
├── .claude/
│   └── agents/
│       └── agent-name.md
```

### 配置格式

```yaml
---
name: agent-name                    # 必需：唯一标识
description: 何时调用此agent        # 必需
model: sonnet                       # 可选：sonnet/opus/haiku/inherit
tools: Read, Write, Bash(git:*)     # 可选：限制工具
permissionMode: default             # 可选：default/manual/acceptEdits/acceptAll
skills: skill1, skill2              # 可选：自动加载的技能
---

# Agent系统提示
```

### 权限模式

| 模式 | 说明 |
|------|------|
| `default` | 按工具定义，需确认 |
| `manual` | 所有操作需手动确认 |
| `acceptEdits` | 自动接受文件编辑 |
| `acceptAll` | 完全自动化 |

---

> 📊 **想了解5种方式的详细对比？** 请查看 [方式对比](comparison.md)
