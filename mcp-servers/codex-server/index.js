#!/usr/bin/env node
/**
 * Codex MCP Server - 符合MCP标准协议的Codex CLI封装
 *
 * 实现标准MCP协议：
 * 1. JSON-RPC 2.0消息格式
 * 2. tools/list - 列出可用工具
 * 3. tools/call - 执行工具调用
 * 4. 上下文管理 - conversationId机制
 *
 * 作者：老金
 * 遵循原则：KISS、DRY、SOLID
 */

const { spawn } = require('child_process');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

// ========== 配置 ==========

// 加载根目录配置文件
const CONFIG_FILE = path.join(__dirname, '..', '..', 'mcp-config.json');
var CONFIG = {
  proxy: { enabled: true, http: 'http://127.0.0.1:15236', https: 'http://127.0.0.1:15236' },
  codex: {
    command: 'codex',
    defaultArgs: ['exec', '--skip-git-repo-check'],
    sandbox: 'workspace-write',
    approvalPolicy: 'on-failure',
    timeout: 300000
  },
  windows: { forceUserprofileAsHome: true, preferCmdExtension: true },
  logging: { enabled: true, level: 'INFO' }
};

if (fs.existsSync(CONFIG_FILE)) {
  try {
    CONFIG = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    if (!CONFIG.codex) {
      CONFIG.codex = { command: 'codex', defaultArgs: ['exec', '--skip-git-repo-check'], sandbox: 'workspace-write', approvalPolicy: 'on-failure', timeout: 300000 };
    }
    // Log successful config load after log function is defined
    setTimeout(() => log(`配置文件加载成功: ${CONFIG_FILE}`), 0);
  } catch (e) {
    // Log config parse error - use console.error since log() may not be ready
    console.error(`[WARN] 配置文件解析失败: ${CONFIG_FILE}, 错误: ${e.message}, 使用默认配置`);
  }
} else {
  // Config file not found, using defaults
  console.error(`[INFO] 配置文件不存在: ${CONFIG_FILE}, 使用默认配置`);
}

const CONTEXT_DIR = path.join(
  process.env.HOME || process.env.USERPROFILE,
  '.mcp-context',
  'codex'
);

// 确保上下文目录存在
if (!fs.existsSync(CONTEXT_DIR)) {
  fs.mkdirSync(CONTEXT_DIR, { recursive: true });
}

const LOG_FILE = path.join(CONTEXT_DIR, 'mcp-server.log');

// ========== 工具函数 ==========

/**
 * 日志记录
 */
function log(message, level = 'INFO') {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level}] ${message}\n`;

  fs.appendFileSync(LOG_FILE, logMessage);

  if (process.env.DEBUG_MCP) {
    console.error(logMessage.trim());
  }
}

/**
 * 读取历史上下文
 */
function loadContext(conversationId) {
  if (!conversationId) return null;

  const contextFile = path.join(CONTEXT_DIR, `${conversationId}.json`);
  if (!fs.existsSync(contextFile)) return null;

  try {
    const history = JSON.parse(fs.readFileSync(contextFile, 'utf-8'));
    log(`加载上下文: ${conversationId}, 历史消息数: ${history.length}`);
    return history;
  } catch (error) {
    log(`加载上下文失败: ${error.message}`, 'ERROR');
    return null;
  }
}

/**
 * 保存上下文
 */
function saveContext(conversationId, history) {
  if (!conversationId) return;

  const contextFile = path.join(CONTEXT_DIR, `${conversationId}.json`);
  try {
    fs.writeFileSync(contextFile, JSON.stringify(history, null, 2));
    log(`保存上下文: ${conversationId}, 历史消息数: ${history.length}`);
  } catch (error) {
    log(`保存上下文失败: ${error.message}`, 'ERROR');
  }
}

/**
 * 构建包含上下文的完整提示词
 */
function buildPromptWithContext(prompt, history) {
  if (!history || history.length === 0) return prompt;

  const contextStr = history
    .map((item) => {
      return `${item.role === 'user' ? 'User' : 'Assistant'}: ${item.content}`;
    })
    .join('\n\n---\n\n');

  return `之前的对话历史：\n\n${contextStr}\n\n---\n\n当前请求：\n${prompt}`;
}

/**
 * 调用Codex CLI
 */
function callCodex(prompt, options = {}) {
  return new Promise((resolve, reject) => {
    log(`调用Codex CLI, 提示词长度: ${prompt.length}`);

    // 添加sandbox参数（关键：workspace-write允许写入）
    const sandbox = CONFIG.codex.sandbox || 'workspace-write';

    // Windows下需要特殊处理引号
    const escapedPrompt = prompt.replace(/"/g, '\\"');
    const quotedPrompt = `"${escapedPrompt}"`;

    // 构建命令参数：codex exec --skip-git-repo-check --sandbox <mode> "<prompt>"
    const args = ['exec', '--skip-git-repo-check', '--sandbox', sandbox, quotedPrompt];

    if (options.model) {
      args.push('--model', options.model);
    }

    log(`Codex命令参数: codex exec --skip-git-repo-check --sandbox ${sandbox} "..."`);

    // 构建环境变量
    var spawnEnv = { ...process.env };

    // Windows下强制使用USERPROFILE作为HOME
    if (process.platform === 'win32' && process.env.USERPROFILE && CONFIG.windows.forceUserprofileAsHome) {
      spawnEnv.HOME = process.env.USERPROFILE;
    }

    // 代理配置
    if (CONFIG.proxy && CONFIG.proxy.enabled) {
      spawnEnv.HTTPS_PROXY = process.env.HTTPS_PROXY || CONFIG.proxy.https;
      spawnEnv.HTTP_PROXY = process.env.HTTP_PROXY || CONFIG.proxy.http;
    }

    const codex = spawn('codex', args, {
      env: spawnEnv,
      cwd: process.cwd(),
      shell: true,
    });

    let output = '';
    let errorOutput = '';

    codex.stdout.on('data', (data) => {
      output += data.toString();
    });

    codex.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    codex.on('close', (code) => {
      if (code !== 0) {
        log(`Codex CLI执行失败: 退出码${code}, 错误: ${errorOutput}`, 'ERROR');
        reject(new Error(`Codex执行失败: ${errorOutput || '未知错误'}`));
      } else {
        log(`Codex CLI执行成功, 输出长度: ${output.length}`);
        resolve(output);
      }
    });

    codex.on('error', (error) => {
      log(`Codex CLI启动失败: ${error.message}`, 'ERROR');
      reject(new Error(`无法启动Codex CLI: ${error.message}`));
    });
  });
}

// ========== MCP协议处理 ==========

/**
 * 工具定义
 */
const TOOLS = [
  {
    name: 'codex',
    description:
      '调用GPT-5.1 Codex Max生成代码或技术文档。支持上下文传递，可通过conversationId保持多轮对话。',
    inputSchema: {
      type: 'object',
      properties: {
        prompt: {
          type: 'string',
          description: '给Codex的提示词，描述你要生成的代码或文档',
        },
        conversationId: {
          type: 'string',
          description:
            '可选的会话ID，用于保持上下文。多次调用使用相同ID可以共享历史对话',
        },
        model: {
          type: 'string',
          description: '可选的模型名称，默认为gpt-5.1-codex-max',
        },
      },
      required: ['prompt'],
    },
  },
];

/**
 * 处理tools/list请求
 */
function handleToolsList(id) {
  log('处理tools/list请求');

  return {
    jsonrpc: '2.0',
    id: id,
    result: {
      tools: TOOLS,
    },
  };
}

/**
 * 处理tools/call请求
 */
async function handleToolsCall(id, params) {
  const { name, arguments: args } = params;

  log(`处理tools/call请求: ${name}`);

  if (name !== 'codex') {
    return {
      jsonrpc: '2.0',
      id: id,
      error: {
        code: -32601,
        message: `Unknown tool: ${name}`,
      },
    };
  }

  if (!args || !args.prompt) {
    return {
      jsonrpc: '2.0',
      id: id,
      error: {
        code: -32602,
        message: 'Invalid params: prompt is required',
      },
    };
  }

  try {
    // 读取历史上下文
    let history = loadContext(args.conversationId) || [];

    // 构建包含上下文的提示词
    const fullPrompt = buildPromptWithContext(args.prompt, history);

    // 调用Codex CLI
    const output = await callCodex(fullPrompt, { model: args.model });

    // 保存本次对话到上下文
    history.push({ role: 'user', content: args.prompt });
    history.push({ role: 'assistant', content: output });

    const finalConversationId = args.conversationId || `codex_${Date.now()}`;
    saveContext(finalConversationId, history);

    // 返回成功响应
    return {
      jsonrpc: '2.0',
      id: id,
      result: {
        content: [
          {
            type: 'text',
            text: output,
          },
        ],
        conversationId: finalConversationId,
        metadata: {
          model: args.model || 'gpt-5.1-codex-max',
          timestamp: new Date().toISOString(),
          historyLength: history.length,
        },
      },
    };
  } catch (error) {
    log(`工具调用失败: ${error.message}`, 'ERROR');

    return {
      jsonrpc: '2.0',
      id: id,
      error: {
        code: -32603,
        message: error.message,
      },
    };
  }
}

/**
 * 处理MCP initialize握手请求
 * MCP 2025-06-18协议要求Server响应initialize请求
 */
function handleInitialize(id, params) {
  log('处理initialize请求, 协议版本: ' + (params.protocolVersion || 'unknown'));
  return {
    jsonrpc: '2.0',
    id: id,
    result: {
      protocolVersion: '2025-06-18',
      capabilities: {
        tools: {}
      },
      serverInfo: {
        name: 'codex-mcp-server',
        version: '1.0.0'
      }
    }
  };
}

/**
 * 处理JSON-RPC请求
 */
async function handleRequest(request) {
  const { jsonrpc, id, method, params } = request;

  // 处理通知（无需响应）
  if (method === 'notifications/initialized') {
    log('收到initialized通知');
    return null; // 通知不需要响应
  }

  // 验证JSON-RPC版本
  if (jsonrpc !== '2.0') {
    return {
      jsonrpc: '2.0',
      id: id,
      error: {
        code: -32600,
        message: 'Invalid Request: jsonrpc must be "2.0"',
      },
    };
  }

  // 路由到对应的处理函数
  switch (method) {
    case 'initialize':
      return handleInitialize(id, params || {});

    case 'tools/list':
      return handleToolsList(id);

    case 'tools/call':
      return await handleToolsCall(id, params);

    default:
      log('未知方法: ' + method, 'WARN');
      return {
        jsonrpc: '2.0',
        id: id,
        error: {
          code: -32601,
          message: `Method not found: ${method}`,
        },
      };
  }
}

// ========== 主程序 ==========

log('Codex MCP Server 启动');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

rl.on('line', async (line) => {
  try {
    log(`收到请求: ${line.substring(0, 100)}...`);

    const request = JSON.parse(line);
    const response = await handleRequest(request);

    // 通知类请求不需要响应
    if (response !== null) {
      console.log(JSON.stringify(response));
      log('响应已发送');
    } else {
      log('通知已处理（无需响应）');
    }
  } catch (error) {
    log(`处理请求失败: ${error.message}`, 'ERROR');

    const errorResponse = {
      jsonrpc: '2.0',
      id: null,
      error: {
        code: -32700,
        message: `Parse error: ${error.message}`,
      },
    };

    console.log(JSON.stringify(errorResponse));
  }
});

// 优雅退出
process.on('SIGINT', () => {
  log('收到SIGINT信号，正在关闭...');
  rl.close();
  process.exit(0);
});

process.on('SIGTERM', () => {
  log('收到SIGTERM信号，正在关闭...');
  rl.close();
  process.exit(0);
});

log('Codex MCP Server 已就绪，等待请求...');
