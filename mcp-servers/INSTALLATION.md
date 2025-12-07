# MCP Servers 安装配置指南

本指南帮助你将Codex和Gemini两个MCP Server配置到Claude Desktop。

## 前置要求检查

### 1. 检查Codex CLI是否已安装

```bash
codex --version
```

如果未安装：
```bash
npm i -g @openai/codex
```

### 2. 检查Gemini CLI是否已安装

```bash
gemini --version
```

如果未安装：
```bash
npm install -g @google/gemini-cli
gemini-cli auth  # 网页授权，1000次/天
```

### 3. 测试CLI工具是否正常工作

```bash
# 测试Codex
codex exec --skip-git-repo-check "用Python写个Hello World"

# 测试Gemini
gemini -p "Hello, Gemini!"
```

如果以上测试都通过，说明CLI工具配置正确，可以继续下一步。

## 安装步骤

### 步骤1：给MCP Server脚本添加执行权限（仅macOS/Linux需要）

```bash
chmod +x mcp-servers/codex-server/index.js
chmod +x mcp-servers/gemini-server/index.js
```

Windows用户跳过此步骤。

### 步骤2：手动测试MCP Server

#### 测试Codex MCP Server

```bash
echo '{"prompt":"用Python写个Hello World"}' | node mcp-servers/codex-server/index.js
```

期望输出类似：
```json
{
  "result": "```python\nprint('Hello World')\n```",
  "conversationId": "codex_1234567890",
  "metadata": { ... }
}
```

#### 测试Gemini MCP Server

```bash
echo '{"prompt":"Hello, Gemini!","reviewMode":false}' | node mcp-servers/gemini-server/index.js
```

期望输出类似：
```json
{
  "result": "Hello! How can I help you today?",
  "conversationId": "gemini_1234567890",
  "metadata": { ... }
}
```

如果测试失败，查看日志：
```bash
cat ~/.mcp-context/codex/mcp-server.log
cat ~/.mcp-context/gemini/mcp-server.log
```

### 步骤3：配置Claude Desktop

#### Windows用户

1. **关闭Claude Desktop应用**（重要！）

2. **打开配置文件**：
   ```
   C:\Users\你的用户名\AppData\Roaming\Claude\claude_desktop_config.json
   ```

   或者在命令行中：
   ```bash
   notepad "%APPDATA%\Claude\claude_desktop_config.json"
   ```

3. **替换配置内容**（完整替换）：

   ```json
   {
     "mcpServers": {
       "mcp-router": {
         "command": "npx",
         "args": [
           "-y",
           "@mcp_router/cli@latest",
           "connect"
         ],
         "env": {
           "MCPR_TOKEN": "mcpr_hSidxXQ8OqIdbH0Bve74yqliscIz4-IG"
         }
       },
       "codex": {
         "command": "node",
         "args": [
           "C:/Users/admin/Desktop/KimProject/智能多Cli编排系统_Skill/mcp-servers/codex-server/index.js"
         ],
         "env": {}
       },
       "gemini": {
         "command": "node",
         "args": [
           "C:/Users/admin/Desktop/KimProject/智能多Cli编排系统_Skill/mcp-servers/gemini-server/index.js"
         ],
         "env": {}
       }
     }
   }
   ```

   **重要**：把上面路径中的 `C:/Users/admin/Desktop/KimProject/智能多Cli编排系统_Skill` 替换成你的实际项目路径！

   获取实际路径的方法：
   ```bash
   cd 项目目录
   pwd  # macOS/Linux
   echo %cd%  # Windows CMD
   ```

4. **保存文件并重启Claude Desktop**

#### macOS/Linux用户

1. **关闭Claude Desktop应用**

2. **打开配置文件**：
   ```bash
   # macOS
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Linux
   nano ~/.config/claude/claude_desktop_config.json
   ```

3. **替换配置内容**（完整替换）：

   ```json
   {
     "mcpServers": {
       "mcp-router": {
         "command": "npx",
         "args": [
           "-y",
           "@mcp_router/cli@latest",
           "connect"
         ],
         "env": {
           "MCPR_TOKEN": "mcpr_hSidxXQ8OqIdbH0Bve74yqliscIz4-IG"
         }
       },
       "codex": {
         "command": "node",
         "args": [
           "/你的绝对路径/mcp-servers/codex-server/index.js"
         ],
         "env": {}
       },
       "gemini": {
         "command": "node",
         "args": [
           "/你的绝对路径/mcp-servers/gemini-server/index.js"
         ],
         "env": {}
       }
     }
   }
   ```

   **重要**：把 `/你的绝对路径/` 替换成实际项目路径！

4. **保存文件并重启Claude Desktop**

### 步骤4：验证MCP Server是否加载成功

1. **重启Claude Desktop后，打开应用**

2. **在Claude Code中检查可用工具**：

   在对话中输入：
   ```
   请列出所有可用的MCP工具
   ```

   你应该能看到类似这样的工具列表：
   ```
   - mcp__mcpServers__codex
   - mcp__mcpServers__gemini
   - mcp__mcp-router__...（其他mcp-router工具）
   ```

3. **测试调用MCP工具**：

   ```
   请使用codex工具生成一个Python的Hello World
   ```

   Claude应该能成功调用 `mcp__mcpServers__codex` 并返回结果。

## 故障排除

### 问题1：MCP Server未出现在工具列表中

**可能原因**：
1. 配置文件格式错误（JSON语法错误）
2. 路径不是绝对路径或路径错误
3. Node.js未安装或不在PATH中

**解决方法**：
```bash
# 1. 验证JSON格式
cat claude_desktop_config.json | jq  # macOS/Linux
type claude_desktop_config.json | jq  # Windows（需安装jq）

# 2. 验证路径
ls mcp-servers/codex-server/index.js  # 文件应该存在

# 3. 验证Node.js
node --version  # 应该输出版本号
```

### 问题2：调用MCP工具时报错

**错误信息**：`spawn node ENOENT` 或 `Command not found`

**解决方法**：确保Node.js在PATH中
```bash
which node  # macOS/Linux
where node  # Windows
```

如果没有输出，需要安装Node.js或添加到PATH。

### 问题3：Codex/Gemini CLI调用失败

**错误信息**：`spawn codex ENOENT` 或 `spawn gemini ENOENT`

**解决方法**：
```bash
# 确保CLI工具在PATH中
which codex  # macOS/Linux
where codex  # Windows

which gemini
where gemini

# 重新安装CLI工具
npm i -g @openai/codex
npm install -g @google/gemini-cli
```

### 问题4：API认证失败

**Codex错误**：`401 Unauthorized`

**解决方法**：配置OpenAI API Key
```bash
export OPENAI_API_KEY="sk-..."
# 或使用中转站
export OPENAI_BASE_URL="https://your-proxy.com/v1"
```

**Gemini错误**：`Authentication required`

**解决方法**：重新授权
```bash
gemini-cli auth
```

### 问题5：查看详细日志

```bash
# Codex日志
tail -f ~/.mcp-context/codex/mcp-server.log

# Gemini日志
tail -f ~/.mcp-context/gemini/mcp-server.log

# 启用调试模式（在配置文件的env中添加）
{
  "codex": {
    "command": "node",
    "args": [...],
    "env": {
      "DEBUG_MCP": "1"
    }
  }
}
```

## 高级配置

### 1. 自定义Codex模型

在env中添加模型参数：
```json
{
  "codex": {
    "command": "node",
    "args": [...],
    "env": {
      "CODEX_DEFAULT_MODEL": "gpt-4-turbo"
    }
  }
}
```

### 2. 自定义Gemini模型

```json
{
  "gemini": {
    "command": "node",
    "args": [...],
    "env": {
      "GEMINI_DEFAULT_MODEL": "gemini-pro"
    }
  }
}
```

### 3. 配置代理

```json
{
  "codex": {
    "command": "node",
    "args": [...],
    "env": {
      "HTTP_PROXY": "http://proxy.example.com:8080",
      "HTTPS_PROXY": "http://proxy.example.com:8080"
    }
  }
}
```

## 下一步

配置成功后，你可以：

1. **创建AI编排Command**：参考 `.claude/commands/kim-team.md`
2. **使用MCP工具**：在Claude Code中直接调用 `mcp__mcpServers__codex` 和 `mcp__mcpServers__gemini`
3. **查看使用文档**：
   - Codex MCP Server: `mcp-servers/codex-server/README.md`
   - Gemini MCP Server: `mcp-servers/gemini-server/README.md`

## 参考资料

- Claude Code MCP文档：https://code.claude.com/docs/en/mcp
- MCP协议规范：https://modelcontextprotocol.io/
- Codex CLI文档：https://developers.openai.com/codex/cli/
- Gemini CLI文档：https://developers.google.com/gemini-code-assist/docs/gemini-cli
