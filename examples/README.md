# 实战案例

> 真实项目中的AI编排应用

## 案例列表

### 1. [登录功能](login-feature/) - 入门案例
**难度**：⭐⭐ 简单
**时间**：7分钟
**方式**：Command

实现JWT登录功能，包含注册、登录、token刷新。

**适合人群**：
- 新手入门
- 快速原型开发
- 学习Command方式

---

### 2. [RBAC权限系统](rbac-system/) - 进阶案例
**难度**：⭐⭐⭐⭐ 复杂
**时间**：33分钟
**方式**：Skill

设计完整的RBAC权限系统，包含角色管理、权限分配、访问控制。

**适合人群**：
- 进阶开发者
- 复杂系统设计
- 学习Skill方式

---

### 3. [模块重构](module-refactor/) - 高级案例
**难度**：⭐⭐⭐⭐⭐ 最复杂
**时间**：整天（持续开发）
**方式**：MCP

重构整个用户模块，拆分Service层，保持上下文一致性。

**适合人群**：
- 高级开发者
- 大型重构项目
- 学习MCP方式

---

## 如何使用案例

### 步骤1：阅读案例README

每个案例都有详细的README文档：
- 任务描述
- 技术要求
- 执行命令
- 预期结果
- 完整代码（参考）

### 步骤2：自己尝试执行

```bash
# 案例1：登录功能（Command方式）
cd examples/login-feature
/kim-team "$(cat task-description.txt)"

# 案例2：RBAC系统（Skill方式）
cd examples/rbac-system
../../.claude/skills/kim-orchestrator/scripts/orchestrate.sh "$(cat task-description.txt)"

# 案例3：模块重构（MCP方式，需要先配置MCP Server）
cd examples/module-refactor
# 参考案例内的README配置MCP
```

### 步骤3：对比结果

将你的输出与案例提供的参考代码对比：
```bash
# 你的输出
cat .kim-orchestrator/phase2_code.md

# 参考代码
cat examples/login-feature/expected-output/phase2_code.md

# 对比差异
diff .kim-orchestrator/phase2_code.md examples/login-feature/expected-output/phase2_code.md
```

---

## 学习路径

**新手**：
1. 先完成案例1（登录功能）- 熟悉Command方式
2. 理解三个阶段的流程（分析→生成→审查）
3. 查看Gemini的审查报告，学习代码质量标准

**进阶**：
1. 完成案例2（RBAC系统）- 学习Skill方式
2. 理解Skill的优势（可复用、保存中间结果）
3. 尝试修改orchestrate.sh，定制自己的工作流

**高级**：
1. 完成案例3（模块重构）- 掌握MCP方式
2. 理解上下文共享的价值（conversationId机制）
3. 编写自己的MCP Server

---

## 贡献案例

欢迎提交你的实战案例！

**要求**：
- 真实项目场景（不要玩具示例）
- 完整的文档（README + task-description.txt）
- 参考代码（expected-output/）
- 经验总结（遇到的问题、解决方案）

**提交方式**：
1. Fork本仓库
2. 在examples/目录下创建你的案例
3. 提交Pull Request

---

**开始实战吧！理论再多不如动手一次。** 💪
