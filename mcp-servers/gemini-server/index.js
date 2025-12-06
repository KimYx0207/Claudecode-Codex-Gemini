#!/usr/bin/env node
/**
 * Gemini MCP Server - 符合MCP标准协议的Gemini CLI封装
 *
 * 参考官方Python实现(geminimcp)的调用方式：
 * - 使用 `gemini --prompt X -o stream-json` 获取JSON流式输出
 * - 支持 `--resume SESSION_ID` 恢复会话
 * - 解析JSON输出提取session_id和agent_messages
 *
 * 作者：老金
 */

const { spawn, execSync } = require("child_process");
const readline = require("readline");
const fs = require("fs");
const path = require("path");

// ========== 配置 ==========

// 加载根目录配置文件
const CONFIG_FILE = path.join(__dirname, "..", "..", "mcp-config.json");
var CONFIG = {
  proxy: { enabled: true, http: "http://127.0.0.1:15236", https: "http://127.0.0.1:15236" },
  gemini: { command: "gemini", defaultArgs: ["-o", "stream-json", "--yolo"], timeout: 300000, environment: { GEMINI_IDE_INTEGRATION: "false" } },
  windows: { forceUserprofileAsHome: true, preferCmdExtension: true },
  logging: { enabled: true, level: "INFO" }
};

if (fs.existsSync(CONFIG_FILE)) {
  try {
    CONFIG = JSON.parse(fs.readFileSync(CONFIG_FILE, "utf8"));
    // Log successful config load after log function is defined
    setTimeout(() => log("配置文件加载成功: " + CONFIG_FILE), 0);
  } catch (e) {
    // Log config parse error - use console.error since log() may not be ready
    console.error("[WARN] 配置文件解析失败: " + CONFIG_FILE + ", 错误: " + e.message + ", 使用默认配置");
  }
} else {
  // Config file not found, using defaults
  console.error("[INFO] 配置文件不存在: " + CONFIG_FILE + ", 使用默认配置");
}

const CONTEXT_DIR = path.join(
  process.env.HOME || process.env.USERPROFILE,
  ".mcp-context",
  "gemini"
);

if (!fs.existsSync(CONTEXT_DIR)) {
  fs.mkdirSync(CONTEXT_DIR, { recursive: true });
}

const LOG_FILE = path.join(CONTEXT_DIR, "mcp-server.log");

// ========== 工具函数 ==========

function log(message, level) {
  level = level || "INFO";
  var timestamp = new Date().toISOString();
  var logMessage = "[" + timestamp + "] [" + level + "] " + message + "\n";
  fs.appendFileSync(LOG_FILE, logMessage);
}

/**
 * Windows下解析CLI命令路径
 * 优先返回.cmd/.bat/.exe文件
 */
function resolveCliCommand(command) {
  if (process.platform === "win32") {
    try {
      var result = execSync("where " + command, { encoding: "utf8" });
      var paths = result.trim().split(/\r?\n/);

      // 优先选择.cmd/.bat/.exe文件
      for (var i = 0; i < paths.length; i++) {
        var p = paths[i].trim();
        if (p.endsWith(".cmd") || p.endsWith(".bat") || p.endsWith(".exe")) {
          return p;
        }
      }

      // 如果没有找到，返回第一个
      if (paths.length > 0) {
        return paths[0].trim();
      }
    } catch (e) {
      log("where命令执行失败: " + e.message, "WARN");
    }
  }
  return command;
}

/**
 * Windows下转义特殊字符
 * 参考官方Python实现的windows_escape函数
 */
function windowsEscape(prompt) {
  if (process.platform !== "win32") {
    return prompt;
  }

  var result = prompt;
  result = result.replace(/\\/g, "\\\\");
  result = result.replace(/"/g, '\\"');
  result = result.replace(/\n/g, "\\n");
  result = result.replace(/\r/g, "\\r");
  result = result.replace(/\t/g, "\\t");
  result = result.replace(/'/g, "\\'");

  return result;
}

/**
 * 调用Gemini CLI
 *
 * Gemini CLI v0.19+ 用法：
 * gemini "prompt" -o stream-json
 * gemini "prompt" -o stream-json --resume <session>
 *
 * 注意：--prompt 参数已废弃，使用位置参数
 */
function callGemini(prompt, options) {
  options = options || {};

  return new Promise(function(resolve, reject) {
    log("调用Gemini CLI, 提示词长度: " + prompt.length);

    var geminiPath = resolveCliCommand("gemini");
    log("Gemini CLI路径: " + geminiPath);

    // 构建命令参数（使用位置参数，--prompt已废弃）
    // Windows shell: true 时需要用引号包裹含空格/中文的参数
    var escapedPrompt = windowsEscape(prompt);
    var quotedPrompt = process.platform === "win32" ? '"' + escapedPrompt + '"' : escapedPrompt;
    var defaultArgs = CONFIG.gemini.defaultArgs || ["-o", "stream-json", "--yolo"];
    var args = [quotedPrompt].concat(defaultArgs);

    if (options.sandbox) {
      args.push("--sandbox");
    }

    if (options.model) {
      args.push("--model", options.model);
    }

    if (options.sessionId) {
      args.push("--resume", options.sessionId);
    }

    log("执行命令: gemini " + args.slice(0, 3).join(" ") + "...");

    // 构建环境变量，确保Windows路径正确
    var spawnEnv = Object.assign({}, process.env);

    // Windows下强制使用USERPROFILE作为HOME，解决Git Bash路径问题
    if (process.platform === "win32" && process.env.USERPROFILE && CONFIG.windows.forceUserprofileAsHome) {
      spawnEnv.HOME = process.env.USERPROFILE;
      log("强制HOME=" + spawnEnv.HOME);
    }

    // 应用gemini特定的环境变量
    var geminiEnv = CONFIG.gemini.environment || {};
    for (var key in geminiEnv) {
      spawnEnv[key] = geminiEnv[key];
    }

    // 代理配置（从配置文件或环境变量）
    if (CONFIG.proxy.enabled) {
      var proxy = process.env.HTTPS_PROXY || process.env.HTTP_PROXY || CONFIG.proxy.https;
      spawnEnv.HTTPS_PROXY = proxy;
      spawnEnv.HTTP_PROXY = process.env.HTTP_PROXY || CONFIG.proxy.http;
      log("代理配置: " + proxy);
    }

    // 如果有API Key，确保传递（支持无浏览器认证）
    if (process.env.GEMINI_API_KEY) {
      log("使用GEMINI_API_KEY认证");
    }

    // Windows下.cmd文件需要shell: true
    var gemini = spawn(geminiPath, args, {
      env: spawnEnv,
      shell: true,
      stdio: ["pipe", "pipe", "pipe"]
    });

    var allMessages = [];
    var agentMessages = "";
    var sessionId = null;
    var errorOutput = "";

    gemini.stdout.on("data", function(data) {
      var lines = data.toString().split("\n");

      for (var i = 0; i < lines.length; i++) {
        var line = lines[i].trim();
        if (!line) continue;

        try {
          var lineDict = JSON.parse(line);
          allMessages.push(lineDict);

          // 提取session_id
          if (lineDict.session_id) {
            sessionId = lineDict.session_id;
          }

          // 提取agent消息
          var itemType = lineDict.type || "";
          var itemRole = lineDict.role || "";

          if (itemType === "message" && itemRole === "assistant") {
            var content = lineDict.content || "";
            // 过滤掉deprecation警告
            if (content.indexOf("--prompt (-p) flag has been deprecated") === -1) {
              agentMessages += content;
            }
          }
        } catch (e) {
          // 非JSON行，可能是普通输出
          if (line && line.indexOf("ERROR") === -1) {
            agentMessages += line + "\n";
          }
        }
      }
    });

    gemini.stderr.on("data", function(data) {
      errorOutput += data.toString();
    });

    gemini.on("close", function(code) {
      log("Gemini CLI退出, 退出码: " + code);

      if (code !== 0 && !agentMessages) {
        log("Gemini CLI执行失败: " + errorOutput, "ERROR");
        reject(new Error("Gemini执行失败: " + (errorOutput || "未知错误")));
        return;
      }

      resolve({
        success: true,
        sessionId: sessionId,
        agentMessages: agentMessages,
        allMessages: allMessages
      });
    });

    gemini.on("error", function(error) {
      log("Gemini CLI启动失败: " + error.message, "ERROR");
      reject(new Error("无法启动Gemini CLI: " + error.message));
    });
  });
}

// ========== MCP协议处理 ==========

var TOOLS = [{
  name: "gemini",
  description: "调用Google Gemini进行代码审查、UI设计、技术问答。支持SESSION_ID保持多轮对话上下文。Gemini擅长前端设计和UI/UX，但上下文长度有限(32k)。",
  inputSchema: {
    type: "object",
    properties: {
      prompt: {
        type: "string",
        description: "给Gemini的提示词"
      },
      SESSION_ID: {
        type: "string",
        description: "可选的会话ID，用于恢复之前的对话上下文"
      },
      model: {
        type: "string",
        description: "可选的模型名称"
      },
      sandbox: {
        type: "boolean",
        description: "是否启用沙箱模式"
      },
      return_all_messages: {
        type: "boolean",
        description: "是否返回所有消息（包括推理过程）"
      }
    },
    required: ["prompt"]
  }
}];

function handleToolsList(id) {
  log("处理tools/list请求");
  return {
    jsonrpc: "2.0",
    id: id,
    result: { tools: TOOLS }
  };
}

async function handleToolsCall(id, params) {
  var name = params.name;
  var args = params.arguments || {};

  log("处理tools/call请求: " + name);

  if (name !== "gemini") {
    return {
      jsonrpc: "2.0",
      id: id,
      error: { code: -32601, message: "Unknown tool: " + name }
    };
  }

  if (!args.prompt) {
    return {
      jsonrpc: "2.0",
      id: id,
      error: { code: -32602, message: "Invalid params: prompt is required" }
    };
  }

  try {
    var result = await callGemini(args.prompt, {
      sessionId: args.SESSION_ID,
      model: args.model,
      sandbox: args.sandbox
    });

    var response = {
      jsonrpc: "2.0",
      id: id,
      result: {
        content: [{ type: "text", text: result.agentMessages }],
        success: true,
        SESSION_ID: result.sessionId
      }
    };

    if (args.return_all_messages) {
      response.result.all_messages = result.allMessages;
    }

    return response;

  } catch (error) {
    log("工具调用失败: " + error.message, "ERROR");
    return {
      jsonrpc: "2.0",
      id: id,
      error: { code: -32603, message: error.message }
    };
  }
}

/**
 * 处理MCP initialize握手请求
 * MCP 2025-06-18协议要求Server响应initialize请求
 */
function handleInitialize(id, params) {
  log("处理initialize请求, 协议版本: " + (params.protocolVersion || "unknown"));
  return {
    jsonrpc: "2.0",
    id: id,
    result: {
      protocolVersion: "2025-06-18",
      capabilities: {
        tools: {}
      },
      serverInfo: {
        name: "gemini-mcp-server",
        version: "1.0.0"
      }
    }
  };
}

async function handleRequest(request) {
  // 处理通知（无需响应）
  if (request.method === "notifications/initialized") {
    log("收到initialized通知");
    return null; // 通知不需要响应
  }

  if (request.jsonrpc !== "2.0") {
    return {
      jsonrpc: "2.0",
      id: request.id,
      error: { code: -32600, message: "Invalid Request" }
    };
  }

  switch (request.method) {
    case "initialize":
      return handleInitialize(request.id, request.params || {});
    case "tools/list":
      return handleToolsList(request.id);
    case "tools/call":
      return await handleToolsCall(request.id, request.params);
    default:
      log("未知方法: " + request.method, "WARN");
      return {
        jsonrpc: "2.0",
        id: request.id,
        error: { code: -32601, message: "Method not found: " + request.method }
      };
  }
}

// ========== 主程序 ==========

log("Gemini MCP Server 启动");

var rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.on("line", async function(line) {
  try {
    log("收到请求: " + line.substring(0, 100) + "...");
    var request = JSON.parse(line);
    var response = await handleRequest(request);
    // 通知类请求不需要响应
    if (response !== null) {
      console.log(JSON.stringify(response));
      log("响应已发送");
    } else {
      log("通知已处理（无需响应）");
    }
  } catch (error) {
    log("处理请求失败: " + error.message, "ERROR");
    console.log(JSON.stringify({
      jsonrpc: "2.0",
      id: null,
      error: { code: -32700, message: "Parse error: " + error.message }
    }));
  }
});

process.on("SIGINT", function() {
  log("收到SIGINT信号，正在关闭...");
  rl.close();
  process.exit(0);
});

process.on("SIGTERM", function() {
  log("收到SIGTERM信号，正在关闭...");
  rl.close();
  process.exit(0);
});

log("Gemini MCP Server 已就绪，等待请求...");
