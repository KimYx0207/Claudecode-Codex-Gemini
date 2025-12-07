# MCP Server健康检查模块

> 此模块被kim-code、kim-review、kim-team引用，用于检测MCP Server可用性

## 检测逻辑

### Codex MCP Server检测

在调用 `mcp__codex__codex` 之前，先检测工具是否可用。

**检测方式**：尝试调用工具列表，确认 `mcp__codex__codex` 存在。

**如果不可用，显示以下提示**：

```
╔══════════════════════════════════════════════════════════════════╗
║  ⚠️ Codex MCP Server 未就绪                                      ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  可能原因：                                                       ║
║  1. .mcp.json 配置文件不存在或配置错误                            ║
║  2. Claude Code 需要重启以加载MCP配置                             ║
║  3. mcp-servers/codex-server/index.js 文件缺失                   ║
║  4. Node.js 未安装或版本过低                                      ║
║                                                                  ║
║  修复步骤：                                                       ║
║  1. 确认 .mcp.json 存在且配置正确                                 ║
║  2. 完全退出并重启 Claude Code                                    ║
║  3. 运行 /kim-setup 检查完整环境                                  ║
║                                                                  ║
║  📖 详细文档：mcp-servers/INSTALLATION.md                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

**降级方案**：
```
💡 Codex不可用，是否使用Claude直接生成代码？
（质量可能略低，但可以继续工作）

输入 Y 继续 / N 中止
```

### Gemini MCP Server检测

在调用 `mcp__gemini__gemini` 之前，先检测工具是否可用。

**检测方式**：尝试调用工具列表，确认 `mcp__gemini__gemini` 存在。

**如果不可用，显示以下提示**：

```
╔══════════════════════════════════════════════════════════════════╗
║  ⚠️ Gemini MCP Server 未就绪                                     ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  可能原因：                                                       ║
║  1. Gemini CLI 未安装（npm i -g @google/gemini-cli）              ║
║  2. 未完成Gemini认证（运行 gemini auth login）                    ║
║  3. 代理配置问题（中国用户需要配置代理）                           ║
║  4. .mcp.json 配置文件问题                                        ║
║                                                                  ║
║  修复步骤：                                                       ║
║  1. 确认代理已开启（检查 mcp-config.json 中的端口）               ║
║  2. 运行 gemini auth login 完成Google账号授权                     ║
║  3. 完全退出并重启 Claude Code                                    ║
║  4. 运行 /kim-setup 检查完整环境                                  ║
║                                                                  ║
║  📖 详细文档：mcp-servers/gemini-server/README.md                 ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

**降级方案**：
```
💡 Gemini不可用，是否跳过代码审查？
（可以后续使用 /kim-review 单独审查）

输入 Y 继续 / N 中止
```

---

## 检测结果状态

健康检查返回以下状态之一：

| 状态 | 含义 | 建议行动 |
|------|------|----------|
| ✅ READY | 所有服务就绪 | 直接执行 |
| ⚠️ PARTIAL | 部分服务可用 | 询问是否降级执行 |
| ❌ UNAVAILABLE | 关键服务不可用 | 显示修复指南 |

---

## 引用方式

在kim-code、kim-review、kim-team命令中引用此模块：

```markdown
## 阶段0：健康检查

在执行任何MCP调用前，按照 `.claude/skills/kim-orchestrator/prompts/health-check.md`
的规范检测对应MCP Server的可用性。

根据检测结果决定：
- ✅ READY → 继续执行
- ⚠️ PARTIAL → 询问用户是否降级执行
- ❌ UNAVAILABLE → 显示修复指南并中止
```

---

## 快速修复命令

```bash
# 检查完整环境
/kim-setup

# 检查MCP配置
cat .mcp.json

# 测试Codex连接
codex --version

# 测试Gemini认证
gemini auth status

# 重启Claude Code（完全退出后重新打开项目）
```
