# 踩坑记录

> 常见问题和解决方案

## 目录

1. [安装问题](#安装问题)
2. [配置问题](#配置问题)
3. [执行问题](#执行问题)
4. [性能问题](#性能问题)
5. [其他问题](#其他问题)

---

## 安装问题

### 问题1：Codex CLI提示"需要ChatGPT Plus订阅"

**现象**：
```bash
$ codex exec "print('hello')"
Error: ChatGPT Plus subscription required
```

**原因**：Codex CLI需要付费订阅才能使用

**解决方案**：

**方案1：订阅ChatGPT Plus（官方）**
- 访问 https://chat.openai.com/
- 订阅ChatGPT Plus（$20/月）

**方案2：使用中转站（推荐）**
```bash
# 配置中转站API Key和Base URL
export OPENAI_API_KEY="your_relay_api_key"
export OPENAI_BASE_URL="https://your-relay-station.com/v1"

# 测试
codex exec "print('hello')"
```

**中转站推荐**：
- 公益站：（关注评论区链接）
- 付费站：（关注评论区链接，按量付费更划算）

---

### 问题2：Gemini CLI提示"超过免费配额"

**现象**：
```bash
$ gemini -p "hello"
Error: Quota exceeded (100 requests/day limit reached)
```

**原因**：使用API Key方式只有**100次/天**配额

**解决方案**：改用网页授权方式（**1000次/天**）

```bash
# 步骤1：删除旧配置
rm ~/.gemini/config.json  # 或对应的配置文件

# 步骤2：使用网页授权
gemini-cli auth

# 步骤3：按提示在浏览器完成授权

# 步骤4：测试
gemini -p "你好，请回复'配置成功'"
```

**详细教程**：https://geminicli.com/docs/get-started/gemini-3/

---

### 问题3：command not found: claude/codex/gemini

**现象**：
```bash
$ claude --version
-bash: claude: command not found
```

**原因**：npm全局安装路径不在PATH中

**解决方案**：

```bash
# 查看npm全局路径
npm config get prefix

# 输出示例：/usr/local

# 将路径添加到PATH
export PATH="$(npm config get prefix)/bin:$PATH"

# 持久化配置（macOS/Linux）
echo 'export PATH="$(npm config get prefix)/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 或者 zsh 用户
echo 'export PATH="$(npm config get prefix)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 验证
claude --version
```

**Windows用户**：
1. 打开"系统属性" → "环境变量"
2. 编辑PATH变量
3. 添加 `%APPDATA%\npm`

---

## 配置问题

### 问题4：环境变量不生效

**现象**：
```bash
$ echo $OPENAI_API_KEY
[空输出]
```

**原因**：
1. 环境变量没有正确配置
2. 配置文件没有重新加载
3. 使用了错误的shell配置文件

**解决方案**：

**步骤1：确认使用的shell**
```bash
echo $SHELL
# 输出：/bin/bash 或 /bin/zsh
```

**步骤2：编辑对应的配置文件**
```bash
# bash 用户
nano ~/.bashrc

# zsh 用户
nano ~/.zshrc

# 添加以下内容
export OPENAI_API_KEY="your_key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

**步骤3：重新加载配置**
```bash
# bash
source ~/.bashrc

# zsh
source ~/.zshrc
```

**步骤4：验证**
```bash
echo $OPENAI_API_KEY  # 应该输出你的API Key
```

---

### 问题5：Claude Code无法连接API

**现象**：
```bash
$ claude
Error: Failed to connect to Anthropic API
```

**原因**：
1. API Key未配置或错误
2. Base URL配置错误
3. 网络问题

**解决方案**：

**步骤1：检查API Key**
```bash
# 查看当前配置
echo $ANTHROPIC_API_KEY

# 重新配置
claude config set anthropic-api-key "your_key"
```

**步骤2：检查Base URL**
```bash
# 官方API
export ANTHROPIC_BASE_URL="https://api.anthropic.com"

# 中转站（如果使用）
export ANTHROPIC_BASE_URL="https://your-relay-station.com"
```

**步骤3：测试连接**
```bash
# 简单测试
claude -p "Hello Claude, 请回复'连接成功'"

# 如果成功，说明配置正确
```

---

## 执行问题

### 问题6：orchestrate.sh权限被拒绝

**现象**：
```bash
$ ./.claude/skills/kim-orchestrator/scripts/orchestrate.sh "test"
-bash: ./.claude/skills/kim-orchestrator/scripts/orchestrate.sh: Permission denied
```

**原因**：脚本没有执行权限

**解决方案**：
```bash
# 添加执行权限
chmod +x .claude/skills/kim-orchestrator/scripts/orchestrate.sh

# 验证权限
ls -l .claude/skills/kim-orchestrator/scripts/orchestrate.sh
# 应该显示 -rwxr-xr-x

# 重新执行
./.claude/skills/kim-orchestrator/scripts/orchestrate.sh "test"
```

---

### 问题7：Codex生成代码失败

**现象**：
```bash
[2025-12-04 12:00:00] 💻 阶段2: 代码生成（Codex）
[2025-12-04 12:00:01] ❌ 错误: Codex代码生成失败
```

**原因**：
1. Codex CLI未安装
2. API Key配置错误
3. 网络问题
4. 提示词太长或格式错误

**解决方案**：

**步骤1：检查Codex是否安装**
```bash
command -v codex
# 如果没有输出，说明未安装

# 安装
npm i -g @openai/codex
```

**步骤2：检查API配置**
```bash
echo $OPENAI_API_KEY  # 应该输出API Key
echo $OPENAI_BASE_URL  # 应该输出Base URL

# 测试Codex
codex exec "print('hello')"
```

**步骤3：查看详细错误日志**
```bash
cat .kim-orchestrator/orchestration.log
```

**步骤4：简化提示词测试**
```bash
# 用简单任务测试
./orchestrate.sh "写一个Hello World程序"

# 如果成功，说明是提示词太复杂
```

---

### 问题8：Gemini审查报告为空

**现象**：
```bash
$ cat .kim-orchestrator/phase3_review.md
⚠️ Gemini CLI未安装，无法进行代码审查
```

**原因**：Gemini CLI未安装或未授权

**解决方案**：

**步骤1：安装Gemini CLI**
```bash
npm install -g @google/gemini-cli
```

**步骤2：网页授权**
```bash
gemini-cli auth
# 按提示在浏览器完成授权
```

**步骤3：测试Gemini**
```bash
gemini -p "你好，请回复'授权成功'"
```

**步骤4：重新执行任务**
```bash
./orchestrate.sh "你的任务"
# 这次应该有完整的审查报告
```

---

## 性能问题

### 问题9：Subagent token消耗太高

**现象**：使用Subagent并行开发，token消耗翻了3倍

**原因**：每个Subagent都是独立的Claude实例，会消耗独立的token

**解决方案**：

**策略1：只在真正需要并行时使用**
```javascript
// ❌ 不好：串行任务用Subagent
Task(分析需求) → 等待完成 → Task(生成代码)

// ✅ 好：并行任务用Subagent
Task(前端开发) + Task(后端开发) // 同时进行
```

**策略2：使用便宜的模型**
```javascript
// ❌ 不好：所有Subagent都用Sonnet
Task({ model: "sonnet", ... })
Task({ model: "sonnet", ... })

// ✅ 好：简单任务用Haiku
Task({ model: "haiku", ... })  // 便宜10倍
Task({ model: "sonnet", ... }) // 复杂任务用Sonnet
```

**策略3：控制Subagent数量**
```javascript
// ❌ 不好：启动太多Subagent
Task(任务1) + Task(任务2) + Task(任务3) + Task(任务4) + Task(任务5)

// ✅ 好：最多2-3个
Task(主要任务1) + Task(主要任务2)
```

---

### 问题10：Hooks触发太频繁

**现象**：每次写文件都触发Gemini审查，太慢了

**原因**：Hooks配置没有条件限制

**解决方案**：添加条件判断

```json
{
  "hooks": {
    "preToolUse": {
      "Bash(git commit)": [{
        "command": "bash",
        "args": [
          "-c",
          "lines_changed=$(git diff --cached | grep -c '^[+-]'); [ $lines_changed -gt 50 ] && gemini -p \\\"请审查：$(git diff --cached)\\\" || echo '改动较小，跳过审查'"
        ]
      }]
    }
  }
}
```

**说明**：只有改动超过50行才触发审查

---

## 其他问题

### 问题11：MCP Server无法启动

**现象**：
```bash
$ claude
Error: Failed to start MCP server "codex"
```

**原因**：
1. MCP Server脚本路径错误
2. Node.js版本不兼容
3. 脚本有语法错误

**解决方案**：

**步骤1：检查脚本路径**
```bash
# 查看MCP配置
claude mcp list

# 确认脚本文件存在
ls /path/to/codex-mcp-server.js
```

**步骤2：测试脚本**
```bash
# 直接运行脚本
node /path/to/codex-mcp-server.js

# 查看错误信息
```

**步骤3：检查Node.js版本**
```bash
node --version
# 应该是 v18.0.0 或更高

# 如果版本过低，升级Node.js
```

---

### 问题12：生成的代码有语法错误

**现象**：Codex生成的代码无法运行，有明显语法错误

**原因**：
1. 提示词不够明确
2. Codex理解错误
3. 代码被截断

**解决方案**：

**策略1：优化提示词**
```bash
# ❌ 不好：提示词模糊
./orchestrate.sh "写个登录功能"

# ✅ 好：提示词详细
./orchestrate.sh "实现JWT登录功能，要求：
1. 使用Express框架
2. 密码用bcrypt加密
3. token有效期24小时
4. 包含单元测试
5. 使用TypeScript"
```

**策略2：让Gemini审查后再用**
```bash
# 查看审查报告
cat .kim-orchestrator/phase3_review.md

# 根据Gemini的建议修复代码
```

**策略3：分阶段生成**
```bash
# 不要一次生成所有代码
# 第1次：生成基础结构
./orchestrate.sh "生成登录功能的基础结构"

# 第2次：添加具体实现
./orchestrate.sh "为登录功能添加JWT实现"

# 第3次：添加测试
./orchestrate.sh "为登录功能添加单元测试"
```

---

## 获取帮助

如果以上方案都无法解决你的问题：

1. **查看详细日志**
   ```bash
   cat .kim-orchestrator/orchestration.log
   ```

2. **提Issue**
   - 仓库地址：https://github.com/your-repo/issues
   - 包含：操作系统、Node.js版本、完整错误信息、日志文件

3. **加入讨论群**
   - （关注评论区群组链接）
   - 社区有很多热心用户可以帮忙

4. **查看官方文档**
   - Claude Code：https://code.claude.com/docs
   - Codex CLI：https://developers.openai.com/codex/cli/
   - Gemini CLI：https://developers.google.com/gemini-code-assist/docs/gemini-cli

---

**常见问题已覆盖90%+的场景，如果遇到新问题，欢迎提Issue帮助完善文档！**
