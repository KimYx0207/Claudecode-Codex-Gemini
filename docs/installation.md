# 安装指南

> 完整的工具安装和配置教程

## 目录

1. [前置要求](#前置要求)
2. [安装Claude Code](#安装claude-code)
3. [安装Codex CLI](#安装codex-cli)
4. [安装Gemini CLI](#安装gemini-cli)
5. [配置API密钥](#配置api密钥)
6. [验证安装](#验证安装)
7. [故障排查](#故障排查)

---

## 前置要求

### 系统要求
- **操作系统**: Windows 10+, macOS 10.15+, 或 Linux
- **Node.js**: 版本 18.0.0 或更高
- **npm**: 版本 9.0.0 或更高（随Node.js自动安装）

### 检查Node.js版本
```bash
node --version  # 应该显示 v18.0.0 或更高
npm --version   # 应该显示 9.0.0 或更高
```

如果没有安装Node.js，请访问 https://nodejs.org/ 下载安装。

---

## 安装Claude Code

### 方式1：使用npm安装（推荐）

```bash
npm install -g @anthropic-ai/claude-code
```

### 方式2：使用yarn安装

```bash
yarn global add @anthropic-ai/claude-code
```

### 验证安装

```bash
claude --version
```

应该显示类似 `Claude Code v1.x.x` 的版本信息。

### 配置Claude Code

```bash
# 初始化配置
claude init

# 设置API Key
claude config set anthropic-api-key "your_anthropic_api_key"
```

**获取API Key**：
1. 访问 https://console.anthropic.com/
2. 注册/登录账号
3. 进入API Keys页面生成新的密钥

---

## 安装Codex CLI

Codex CLI是OpenAI官方提供的代码生成工具。

### 方式1：使用npm安装（推荐）

```bash
npm i -g @openai/codex
```

### 方式2：macOS使用Homebrew安装

```bash
brew install --cask codex
```

### 验证安装

```bash
codex --version
```

应该显示版本信息。

### 配置Codex

#### 使用官方API（需要ChatGPT Plus/Pro/Business订阅）

```bash
# 设置API Key
export OPENAI_API_KEY="your_openai_api_key"

# 配置Base URL（官方）
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

#### 使用中转站（如果没有订阅）

```bash
# 中转站API Key
export OPENAI_API_KEY="your_relay_api_key"

# 中转站Base URL（示例）
export OPENAI_BASE_URL="https://your-relay-station.com/v1"
```

**中转站推荐**：
- **公益站**：（关注评论区链接）
- **付费站**：（关注评论区链接）

**持久化配置**（推荐）：

将环境变量写入配置文件：

```bash
# macOS/Linux
echo 'export OPENAI_API_KEY="your_key"' >> ~/.bashrc
echo 'export OPENAI_BASE_URL="https://api.openai.com/v1"' >> ~/.bashrc
source ~/.bashrc

# 或者写入 ~/.zshrc （如果使用zsh）
echo 'export OPENAI_API_KEY="your_key"' >> ~/.zshrc
echo 'export OPENAI_BASE_URL="https://api.openai.com/v1"' >> ~/.zshrc
source ~/.zshrc
```

---

## 安装Gemini CLI

Gemini CLI是Google官方提供的AI工具。

### 安装

```bash
npm install -g @google/gemini-cli
```

### 验证安装

```bash
gemini --version
```

### 配置Gemini（网页授权，推荐）

**重要**：网页授权方式有**1000次/天**的免费配额，比API Key方式（100次/天）多10倍！

#### 步骤1：访问授权页面

```bash
# 方式1：直接访问
open https://geminicli.com/docs/get-started/gemini-3/

# 方式2：命令行打开
gemini-cli auth
```

#### 步骤2：Google账号登录

1. 点击页面上的 "Get Started" 按钮
2. 使用Google账号登录
3. 授权Gemini CLI访问权限
4. 授权完成后会自动跳转

#### 步骤3：完成配置

```bash
# 运行授权命令（如果之前没运行）
gemini-cli auth

# 检查授权状态
gemini -p "Hello, Gemini!"
```

如果返回Gemini的回复，说明配置成功！

### 配置Gemini（API Key方式，不推荐）

**注意**：这种方式只有100次/天，不推荐使用。

```bash
# 1. 访问 https://makersuite.google.com/app/apikey
# 2. 创建API Key
# 3. 配置环境变量
export GEMINI_API_KEY="your_gemini_api_key"
```

---

## 配置API密钥

### 方式1：使用cc switch工具（推荐新手）

`cc switch`是一个傻瓜式配置工具，提供交互界面。

#### 安装cc switch

```bash
npm install -g cc-switch
```

#### 使用cc switch配置

```bash
cc switch
```

按照提示选择：
1. **Claude API**: 填写API Key和Base URL
2. **OpenAI/Codex API**: 填写API Key和Base URL
3. **Gemini**: 选择网页授权（不需要手动配置）

配置会自动保存到环境变量。

### 方式2：手动配置环境变量（进阶用户）

#### macOS/Linux

编辑 `~/.bashrc` 或 `~/.zshrc`：

```bash
# Claude（官方）
export ANTHROPIC_API_KEY="your_anthropic_key"
export ANTHROPIC_BASE_URL="https://api.anthropic.com"

# Codex/OpenAI（官方）
export OPENAI_API_KEY="your_openai_key"
export OPENAI_BASE_URL="https://api.openai.com/v1"

# Gemini（用网页授权，不需要这个）
# export GEMINI_API_KEY="your_gemini_key"
```

保存后执行：

```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

#### Windows

使用PowerShell：

```powershell
# Claude
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "your_key", "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "https://api.anthropic.com", "User")

# Codex/OpenAI
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your_key", "User")
[Environment]::SetEnvironmentVariable("OPENAI_BASE_URL", "https://api.openai.com/v1", "User")
```

或者使用系统设置 → 环境变量 → 新建。

---

## 验证安装

### 1. 验证Claude Code

```bash
claude --version
```

### 2. 验证Codex

```bash
codex exec "print('Hello from Codex')"
```

应该返回一段简单的代码。

### 3. 验证Gemini

```bash
gemini -p "你好，Gemini！请回复'配置成功'。"
```

应该返回Gemini的回复。

### 4. 验证AI编排系统

```bash
# 进入项目目录
cd path/to/ai-orchestrator

# 测试Command方式（在Claude Code里执行）
/ai-team "写一个Hello World程序"

# 测试Skill方式
./.claude/skills/ai-orchestrator/scripts/orchestrate.sh "写一个Hello World程序"
```

如果所有步骤都成功，恭喜你安装完成！🎉

---

## 下一步

安装完成后，继续阅读：
- [使用说明](usage.md) - 学习如何使用5种集成方式
- [方式对比](comparison.md) - 选择最适合你的方式

---

## 遇到问题？

安装过程中的常见问题（如command not found、权限拒绝、配额超限等）都在踩坑记录里有详细解决方案：

👉 **[踩坑记录](troubleshooting.md)** - 12个常见问题的完整解决方案
