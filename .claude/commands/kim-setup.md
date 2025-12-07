---
description: Kim环境配置命令 - 一键检测和配置Claude Code + Codex + Gemini开发环境
allowed-tools: Read, Write, Edit, Bash
argument-hint: [可选：check/fix/full]
---

# Kim环境配置命令

> 一键检测Node.js、CLI工具、MCP Server配置，自动修复常见问题

运行模式：$ARGUMENTS（默认：check）
- **check**: 仅检测环境状态，不做修改
- **fix**: 检测并尝试自动修复问题
- **full**: 完整配置向导（适合首次使用）

## 执行流程

### 1️⃣ 基础环境检测

执行以下检测（使用Bash工具）：

```bash
# Node.js版本检测（需要18+）
node --version

# npm版本检测
npm --version

# Python版本检测（可选，用于部分功能）
python --version 2>/dev/null || python3 --version 2>/dev/null
```

**输出格式**：
```
📦 基础环境检测
├─ Node.js: ✅ v20.10.0 (需要 >= 18)
├─ npm: ✅ v10.2.3
└─ Python: ✅ v3.11.5 (可选)
```

### 2️⃣ CLI工具检测

检测三个核心CLI工具：

```bash
# Claude Code CLI
claude --version 2>/dev/null || echo "NOT_INSTALLED"

# Codex CLI
codex --version 2>/dev/null || echo "NOT_INSTALLED"

# Gemini CLI
gemini --version 2>/dev/null || echo "NOT_INSTALLED"
```

**输出格式**：
```
🔧 CLI工具检测
├─ Claude Code: ✅ v1.0.29
├─ Codex CLI: ✅ v0.1.2505011803
└─ Gemini CLI: ✅ v0.1.28
```

**如果缺失，提示安装命令**：
```
❌ 检测到以下工具未安装：

# 安装Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 安装Codex CLI
npm i -g @openai/codex

# 安装Gemini CLI
npm install -g @google/gemini-cli
```

### 3️⃣ MCP Server配置检测

检测本项目的MCP Server配置：

```bash
# 检查.mcp.json是否存在
ls -la .mcp.json 2>/dev/null

# 检查MCP Server文件是否存在
ls -la mcp-servers/codex-server/index.js 2>/dev/null
ls -la mcp-servers/gemini-server/index.js 2>/dev/null
```

**输出格式**：
```
🔌 MCP Server配置
├─ .mcp.json: ✅ 已配置
├─ Codex Server: ✅ 存在
├─ Gemini Server: ✅ 存在
└─ MCP配置状态: ✅ 就绪
```

### 4️⃣ API认证状态检测

```bash
# 检查环境变量（不显示实际值）
echo "ANTHROPIC_API_KEY: $(if [ -n \"$ANTHROPIC_API_KEY\" ]; then echo '已设置'; else echo '未设置'; fi)"
echo "OPENAI_API_KEY: $(if [ -n \"$OPENAI_API_KEY\" ]; then echo '已设置'; else echo '未设置'; fi)"

# 检查Gemini认证状态
gemini auth status 2>/dev/null || echo "未认证"
```

**输出格式**：
```
🔑 API认证状态
├─ ANTHROPIC_API_KEY: ✅ 已设置
├─ OPENAI_API_KEY: ✅ 已设置
└─ Gemini Auth: ✅ 已认证 (1000次/天免费)
```

**如果未设置，提示配置方法**：
```
❌ 检测到以下认证未配置：

# Windows PowerShell (永久设置)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "你的API_KEY", "User")

# macOS/Linux (添加到 ~/.bashrc 或 ~/.zshrc)
export OPENAI_API_KEY="你的API_KEY"

# Gemini认证（网页授权）
gemini auth login
```

### 5️⃣ 代理配置检测（中国用户必需）

```bash
# 检查代理环境变量
echo "HTTP_PROXY: $HTTP_PROXY"
echo "HTTPS_PROXY: $HTTPS_PROXY"

# 检查mcp-config.json中的代理配置
cat mcp-config.json 2>/dev/null | grep -A3 '"proxy"'
```

**输出格式**：
```
🌐 代理配置（中国用户必需）
├─ HTTP_PROXY: ✅ http://127.0.0.1:15236
├─ HTTPS_PROXY: ✅ http://127.0.0.1:15236
└─ mcp-config.json: ✅ 已配置

⚠️ 注意：15236是示例端口，请根据你的代理软件修改！
常见端口：Clash(7890)、V2Ray(10808)
```

---

## 检测结果汇总

根据检测结果，生成汇总报告：

```
╔════════════════════════════════════════════╗
║         Kim环境配置检测报告                 ║
╠════════════════════════════════════════════╣
║ 基础环境    [██████████] 100%  ✅ 通过     ║
║ CLI工具     [████████░░]  80%  ⚠️ 缺1个    ║
║ MCP配置     [██████████] 100%  ✅ 通过     ║
║ API认证     [██████░░░░]  60%  ❌ 缺2个    ║
║ 代理配置    [██████████] 100%  ✅ 通过     ║
╠════════════════════════════════════════════╣
║ 总体状态:  ⚠️ 部分就绪（需要修复2个问题）   ║
╚════════════════════════════════════════════╝
```

---

## 常见问题修复指南

### Q1: Gemini认证失败
```bash
# 1. 确保代理已开启
# 2. 运行认证命令
gemini auth login
# 3. 在浏览器中完成Google账号授权
```

### Q2: MCP工具在Claude Code中不可用
```
1. 确保.mcp.json在项目根目录
2. 重启Claude Code（完全退出后重新打开）
3. 在Claude Code中运行 /mcp 查看已加载的服务器
```

### Q3: Codex返回401错误
```
1. 检查OPENAI_API_KEY是否正确设置
2. 确认API Key有Codex访问权限
3. 检查API Key余额是否充足
```

---

## 使用示例

```bash
# 快速检测环境状态
/kim-setup

# 检测并尝试自动修复
/kim-setup fix

# 首次使用完整配置
/kim-setup full
```

---

## 下一步建议

环境配置完成后：
1. 运行 `/kim-help` 查看所有可用命令
2. 运行 `/kim-code "实现一个简单功能"` 测试代码生成
3. 运行 `/kim-team "实现一个完整功能"` 测试三引擎协作
