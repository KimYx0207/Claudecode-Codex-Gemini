---
description: Kim代码审查命令 - Claude需求理解 + Gemini深度审查（审查现有代码，无生成）
allowed-tools: Read, Write, Edit, Bash, Task, Glob, Grep
argument-hint: [代码文件路径或审查需求]
---

# Kim代码审查命令（Claude + Gemini）

> 代码审查模式：理解代码 → 深度审查，专注于代码质量和安全

你现在要协调2个AI工具完成代码审查：$ARGUMENTS

**模式说明**：这是专业审查模式，适合审查现有代码、代码质量检查、安全审计。

## ⚠️ 文件写入规则（必须遵守）

Claude Code的Write工具要求：**写入文件前必须先读取它**。对于新文件：

```bash
# 创建新文件的标准流程：
1. 用 Bash 创建目录和空文件：mkdir -p 目录 && echo "" > 文件路径
2. 用 Read 读取该文件
3. 用 Write 写入实际内容
```

## 执行流程

### 阶段0.1：健康检查

**参考 `.claude/skills/kim-orchestrator/prompts/health-check.md` 执行MCP健康检查。**

在开始前检测 `mcp__gemini__gemini` 工具是否可用：
- ✅ 可用 → 继续执行
- ❌ 不可用 → 显示修复指南，询问是否用Claude降级执行

### 阶段0.2：初始化工作目录

```bash
mkdir -p .kim-orchestrator && echo "" > .kim-orchestrator/phase1_analysis.json && echo "" > .kim-orchestrator/phase2_review.md && echo "" > .kim-orchestrator/result.md
```

然后读取这些文件：
- Read .kim-orchestrator/phase1_analysis.json
- Read .kim-orchestrator/phase2_review.md
- Read .kim-orchestrator/result.md

### 阶段1：代码理解与分析（你自己完成）

首先读取用户指定的代码文件，然后分析：

1. **识别审查目标**：用户可能提供文件路径、目录、或描述
2. **读取代码**：使用Read/Glob/Grep工具获取代码内容
3. **初步分析**：理解代码结构、功能、潜在问题点

输出JSON格式的分析报告：

```json
{
  "review_target": "审查目标描述",
  "files_analyzed": [
    {"path": "文件路径", "lines": 行数, "purpose": "用途"}
  ],
  "code_summary": "代码功能概述",
  "initial_concerns": [
    "初步发现的问题1",
    "初步发现的问题2"
  ],
  "review_focus": [
    "重点审查方向1：安全性",
    "重点审查方向2：性能",
    "重点审查方向3：可维护性"
  ]
}
```

保存到 `.kim-orchestrator/phase1_analysis.json`

### 阶段2：深度代码审查（调用Gemini MCP Server）

**检查工具**：确认 `mcp__gemini__gemini` 可用。如果不可用，提示用户配置MCP Server。

调用Gemini进行深度审查：
- prompt: 包含代码内容和phase1_analysis.json的审查要点
- reviewMode: true（启用专业审查模式）
- conversationId: "kim_review_" + 当前时间戳

**审查维度**：
1. **代码质量**：可读性、命名规范、代码复杂度
2. **安全性**：SQL注入、XSS、认证漏洞、敏感信息泄露
3. **性能**：N+1查询、内存泄漏、算法效率
4. **可维护性**：模块化、依赖关系、测试覆盖
5. **最佳实践**：设计模式、SOLID原则、错误处理

将响应保存到 `.kim-orchestrator/phase2_review.md`

### 阶段3：生成审查报告

```markdown
# Kim代码审查报告（Claude + Gemini）

**审查目标**: $ARGUMENTS
**审查时间**: [当前时间]
**模式**: 深度代码审查

---

## 阶段1: 代码分析（Claude Sonnet 4.5）

\`\`\`json
[phase1_analysis.json的内容]
\`\`\`

---

## 阶段2: 深度审查（Gemini 3 Pro）

[phase2_review.md的内容]

---

## 审查总结

### 🔴 严重问题（必须修复）
[列出严重问题]

### 🟡 一般问题（建议修复）
[列出一般问题]

### 🟢 优化建议（可选改进）
[列出优化建议]

---

## 下一步建议

1. 优先修复严重问题
2. 使用 `/kim-code` 生成修复代码
3. 修复后再次运行 `/kim-review` 验证
```

保存到 `.kim-orchestrator/result.md` 并展示给用户。

---

## 使用示例

```bash
# 审查单个文件
/kim-review "src/auth/utils.py"

# 审查整个模块
/kim-review "审查src/auth/目录下的所有认证代码"

# 安全审计
/kim-review "对用户输入处理代码进行安全审计"

# 性能审查
/kim-review "审查数据库查询性能，检查N+1问题"
```

---

## 适用场景

✅ **适合使用 /kim-review**：
- 代码质量检查
- 安全漏洞审计
- 性能问题排查
- Code Review辅助
- 技术债务评估

❌ **建议使用 /kim-team**：
- 需要生成新代码
- 完整的开发流程
- 需要Codex参与的任务

---

## 🔗 相关命令推荐

执行完成后，根据审查结果推荐下一步：

| 场景 | 推荐命令 | 原因 |
|------|----------|------|
| 发现需要修复的问题 | `/kim-code` | 生成修复代码 |
| 需要修复后再审查 | `/kim-review` | 验证修复效果 |
| 需要完整重构 | `/kim-team` | 重构+审查一条龙 |
| 需要拆解修复任务 | `/kim-plan` | 规划修复工作 |
