# Hermes插件集成参考

## 插件系统架构

Hermes Agent使用插件系统扩展功能，插件通过中间件（middleware）拦截和修改请求。

### 中间件类型

| 中间件类型 | 用途 | 触发时机 |
|-----------|------|----------|
| `llm_request` | 修改LLM请求payload | LLM调用前 |
| `llm_execution` | 包装LLM执行过程 | LLM执行时 |
| `tool_request` | 修改工具请求参数 | 工具调用前 |
| `tool_execution` | 包装工具执行过程 | 工具执行时 |

### 插件目录结构

```
/opt/data/plugins/<plugin_name>/
├── manifest.json              # 插件清单（必需）
├── <plugin_name>.py           # 插件代码（必需）
├── README.md                  # 使用说明（可选）
└── references/                # 参考文档（可选）
```

### manifest.json 格式

```json
{
  "name": "plugin_name",
  "version": "1.0.0",
  "description": "插件描述",
  "author": "作者",
  "license": "MIT",
  "entry_point": "plugin_code.py",
  "register_function": "register_plugin",
  "dependencies": [],
  "config": {
    "config_key": {
      "type": "boolean|object|string",
      "default": true,
      "description": "配置说明"
    }
  }
}
```

### 插件代码结构

```python
def register_plugin(plugin_manager):
    """
    注册插件
    
    Args:
        plugin_manager: 插件管理器
    """
    # 1. 创建插件
    plugin = plugin_manager.create_plugin(
        name="plugin_name",
        version="1.0.0",
        description="插件描述"
    )
    
    # 2. 注册中间件
    def my_middleware(request, **context):
        """中间件函数"""
        # 修改request
        modified_request = modify(request)
        return {"request": modified_request}
    
    plugin.register_middleware("llm_request", my_middleware)
    
    return plugin
```

## LLM脱敏中间件实现

### 中间件函数签名

```python
def llm_request_middleware(
    request: Dict[str, Any],  # LLM请求payload
    **context: Any            # 上下文信息
) -> Dict[str, Any]:
    """
    LLM请求中间件
    
    Args:
        request: 原始请求payload
        context: 上下文（包含model、provider等）
    
    Returns:
        {"request": modified_request}  # 修改后的请求
    """
    # 脱敏处理
    sanitized = sanitize_payload(request)
    return {"request": sanitized}
```

### 脱敏处理流程

```python
def sanitize_payload(payload):
    """脱敏LLM请求payload"""
    result = payload.copy()
    
    # 1. 脱敏messages数组
    if 'messages' in result:
        result['messages'] = sanitize_messages(result['messages'])
    
    # 2. 脱敏其他字段
    for field in ['prompt', 'query', 'question', 'text', 'content']:
        if field in result and isinstance(result[field], str):
            result[field] = sanitize_text(result[field])
    
    return result

def sanitize_messages(messages):
    """脱敏消息数组"""
    result = []
    for msg in messages:
        if isinstance(msg, dict) and 'content' in msg:
            if isinstance(msg['content'], str):
                msg = msg.copy()
                msg['content'] = sanitize_text(msg['content'])
        result.append(msg)
    return result
```

## 配置管理

### 配置文件位置

```
/opt/data/config/plugins.json
```

### 配置格式

```json
{
  "plugins": {
    "plugin_name": {
      "enabled": true,
      "config": {
        "key1": "value1",
        "key2": "value2"
      }
    }
  }
}
```

### 在插件中读取配置

```python
import json

def load_config():
    """加载插件配置"""
    config_path = "/opt/data/config/plugins.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get("plugins", {}).get("llm_sanitize", {}).get("config", {})
    except Exception:
        return DEFAULT_CONFIG
```

## 测试插件

### 单元测试

```python
from plugins.llm_sanitize.llm_sanitize_plugin import LLMSanitizeMiddleware

def test_basic_sanitization():
    middleware = LLMSanitizeMiddleware()
    
    messages = [
        {"role": "user", "content": "密码：abc123"}
    ]
    
    sanitized = middleware.sanitize_messages(messages)
    assert sanitized[0]['content'] == "密码：***"
```

### 集成测试

```bash
# 测试插件加载
python /opt/data/plugins/llm_sanitize/llm_sanitize_plugin.py

# 测试完整流程
python /opt/data/scripts/test_llm_sanitize_plugin.py
```

## 调试技巧

### 1. 启用日志

```json
{
  "plugins": {
    "llm_sanitize": {
      "config": {
        "log_sanitize": true
      }
    }
  }
}
```

### 2. 查看日志

```bash
tail -f ~/.hermes/logs/gateway.log | grep -i sanitize
```

### 3. 检查插件加载

```bash
hermes plugins list
```

### 4. 测试中间件

```python
from plugins.llm_sanitize.llm_sanitize_plugin import LLMSanitizeMiddleware

middleware = LLMSanitizeMiddleware({"log_sanitize": True})

# 测试payload
payload = {
    "messages": [{"role": "user", "content": "密码：abc123"}]
}

result = middleware.sanitize_payload(payload)
print(result)
```

## 常见问题

### Q: 插件未加载怎么办？

A: 检查以下几点：
1. 插件目录是否存在：`ls -la /opt/data/plugins/llm_sanitize/`
2. manifest.json是否正确：`cat /opt/data/plugins/llm_sanitize/manifest.json`
3. plugins.json配置是否正确：`cat /opt/data/config/plugins.json`
4. 重启Hermes服务：`hermes gateway restart`

### Q: 脱敏未生效怎么办？

A: 检查以下几点：
1. 插件是否启用：`"enabled": true`
2. 脱敏功能是否启用：`"config.enabled": true`
3. 查看日志是否有错误：`tail -f ~/.hermes/logs/gateway.log`
4. 测试插件是否正常：`python /opt/data/plugins/llm_sanitize/llm_sanitize_plugin.py`

### Q: 如何添加新的脱敏规则？

A: 修改`/opt/data/scripts/llm_sanitize.py`中的`SANITIZE_RULES`字典，添加新的规则。

### Q: 如何禁用特定类型的脱敏？

A: 修改`/opt/data/config/plugins.json`中的`rules`配置，将对应规则设为`false`。
