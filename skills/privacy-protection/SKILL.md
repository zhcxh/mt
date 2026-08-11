---
name: privacy-protection
description: LLM调用时的隐私保护与自动脱敏 - 仅在发送给LLM模型时对敏感信息进行脱敏处理，本地存储保持原样
version: 1.0.0
tags: [privacy, security, sanitize, llm, memory]
---

# LLM调用隐私保护与自动脱敏技能

## 功能概述

在Hermes Agent调用LLM模型时，自动对上下文中的敏感信息进行脱敏处理，保护用户隐私。

**关键特性：**
- ✅ **本地存储保持原样** - 不影响记忆系统
- ✅ **LLM调用时自动脱敏** - 仅在发送给模型前处理
- ✅ **支持多种数据类型** - 文本、字典、列表、消息数组
- ✅ **可配置** - 支持启用/禁用、自定义规则

## 脱敏规则

### 1. 密码脱敏（最高优先级）
- **检测模式**：`密码：xxx`、`password: xxx`、`pwd: xxx`
- **处理方式**：完全替换为 `***`
- **示例**：`密码：Sr@010203` → `密码：***`

### 2. API密钥脱敏
- **检测模式**：
  - `api_key: xxx`、`apikey: xxx`
  - `token: xxx`、`secret: xxx`
  - `xs_live_xxx`（以特定前缀开头）
- **处理方式**：显示前8后4位，中间用`***`替代
- **示例**：`xs_live_GvUszp1YEXXO7_CvqaEq2u6hHtwDgt4CvzRzinei6kw` → `xs_live_***i6kw`

### 3. 姓名脱敏
- **检测模式**：`用户：xxx`、`姓名：xxx`、`xxx的信息`
- **处理方式**：保留姓，名字用`*`替代
- **示例**：`用户：朱正兴` → `用户：朱**`

### 4. 地址脱敏
- **检测模式**：包含省/市的完整地址
- **处理方式**：只保留到市级，详细地址用`***`替代
- **示例**：`缅甸仰光市某某路` → `缅甸仰光市***`

### 5. 邮箱脱敏
- **检测模式**：标准邮箱格式
- **处理方式**：用户名前2位+`***`+域名
- **示例**：`CeliaTemple5706@outlook.com` → `Ce***@outlook.com`

### 6. 手机号脱敏
- **检测模式**：11位手机号
- **处理方式**：显示前3后4位
- **示例**：`13812345678` → `138****5678`

### 7. 身份证号脱敏
- **检测模式**：18位身份证号
- **处理方式**：显示前6后4位
- **示例**：`110101199001011234` → `110101********1234`

### 8. 银行卡号脱敏
- **检测模式**：16-19位银行卡号
- **处理方式**：显示前4后4位
- **示例**：`6222021234567890123` → `6222 **** **** 0123`

## 使用方法

### 1. 命令行测试

```bash
# 测试脱敏功能
python /opt/data/scripts/hermes_llm_sanitize.py

# 脱敏特定文本
python /opt/data/scripts/llm_sanitize.py "密码：abc123，邮箱：test@example.com"
```

### 2. Python代码集成

```python
import sys
sys.path.append('/opt/data/scripts')

from hermes_llm_sanitize import (
    get_sanitizer,
    sanitize_for_llm_call,
    sanitize_context_for_llm_call,
    LLMSanitizer,
    HermesLLMHook
)

# 获取脱敏器实例
sanitizer = get_sanitizer()

# 脱敏文本
text = "密码：Sr@010203，邮箱：test@example.com"
clean_text = sanitize_for_llm_call(text)

# 脱敏上下文
context = {
    "prompt": "用户信息：密码：abc123",
    "memory": ["邮箱：test@example.com"]
}
clean_context = sanitize_context_for_llm_call(context)

# 使用脱敏器
clean = sanitizer.sanitize_prompt("密码：abc123")
```

### 3. 集成到Hermes Agent

在Hermes Agent的LLM调用流程中集成脱敏处理：

```python
from hermes_llm_sanitize import HermesLLMHook, get_sanitizer

# 创建钩子
hook = HermesLLMHook()

# 在LLM调用前调用
def call_llm_with_sanitization(payload):
    # 1. 脱敏payload
    sanitized_payload = hook.before_llm_call(payload)
    
    # 2. 调用LLM（使用脱敏后的payload）
    response = llm_api.call(sanitized_payload)
    
    # 3. 处理响应（如果需要）
    return hook.after_llm_call(response)

# 或者使用装饰器
sanitizer = get_sanitizer()
@sanitizer.wrap_api_call
def call_llm(payload):
    return llm_api.call(payload)
```

## 测试验证

### 测试1：基本脱敏
```bash
python /opt/data/scripts/llm_sanitize.py "用户：朱正兴，密码：Sr@010203，API密钥：xs_live_GvUszp1YEXXO7_CvqaEq2u6hHtwDgt4CvzRzinei6kw，地址：缅甸仰光市，邮箱：CeliaTemple5706@outlook.com"
```

**预期输出：**
```
朱**，密码：***，API密钥：xs_live_***i6kw，地址：缅甸仰光市，邮箱：Ce***@outlook.com
```

### 测试2：完整上下文脱敏
```python
from hermes_llm_sanitize import sanitize_context_for_llm_call

context = {
    "prompt": "查询用户：朱正兴，密码：Sr@010203",
    "memory": ["邮箱：CeliaTemple5706@outlook.com"],
    "messages": [
        {"role": "user", "content": "密码：abc123"},
        {"role": "assistant", "content": "已处理"}
    ]
}

clean = sanitize_context_for_llm_call(context)
print(clean)
# {
#   "prompt": "查询用户：朱**，密码：***",
#   "memory": ["邮箱：Ce***@outlook.com"],
#   "messages": [
#     {"role": "user", "content": "密码：***"},
#     {"role": "assistant", "content": "已处理"}
#   ]
# }
```

## 配置选项

### 启用/禁用脱敏
```python
sanitizer = get_sanitizer()
sanitizer.enabled = False  # 禁用脱敏
sanitizer.enabled = True   # 启用脱敏
```

### 启用日志
```python
sanitizer = get_sanitizer()
sanitizer.log_sanitize = True  # 启用脱敏日志
```

### 自定义规则
```python
from llm_sanitize import sanitize_text, SANITIZE_RULES

# 添加自定义规则
custom_rules = {
    "custom_pattern": {
        "pattern": r'自定义模式',
        "replacement": lambda m: "替换内容",
        "description": "自定义规则描述"
    }
}

text, rules = sanitize_text("文本内容", custom_rules)
```

## 注意事项

1. **本地存储不脱敏**：记忆系统保持原样，仅在LLM调用时脱敏
2. **性能影响**：脱敏处理会增加少量延迟，但对大多数应用影响不大
3. **准确性**：脱敏基于正则表达式，可能有误判，建议定期测试
4. **恢复机制**：当前不支持自动恢复脱敏内容，如需恢复需额外处理
5. **多语言支持**：主要支持中文和英文，其他语言可能需要自定义规则
6. **测试充分**：在生产环境使用前，建议充分测试各种场景

## Hermes插件集成

### 插件架构

插件已集成到Hermes Agent，通过中间件系统拦截LLM调用：

```
/opt/data/plugins/llm_sanitize/
├── manifest.json              # 插件清单
├── llm_sanitize_plugin.py     # 插件代码
└── README.md                  # 使用说明
```

### 插件配置

配置文件：`/opt/data/config/plugins.json`

```json
{
  "plugins": {
    "llm_sanitize": {
      "enabled": true,
      "config": {
        "enabled": true,
        "log_sanitize": false,
        "rules": {
          "password": true,
          "api_key": true,
          "name": true,
          "address": true,
          "email": true,
          "phone": true,
          "id_card": true,
          "bank_card": true
        }
      }
    }
  }
}
```

### 插件工作原理

1. 插件注册LLM请求中间件（`llm_request`）
2. 每次Hermes调用LLM时，中间件自动拦截
3. 对`messages`数组中的每条消息进行脱敏
4. 对`prompt`、`query`等字段进行脱敏
5. 脱敏后的payload发送给LLM API
6. 本地存储（记忆系统）保持原样

### 测试插件

```bash
# 直接运行插件测试
python /opt/data/plugins/llm_sanitize/llm_sanitize_plugin.py

# 运行完整测试套件
python /opt/data/scripts/test_llm_sanitize_plugin.py
```

## 陷阱与注意事项

### ⚠️ 关键陷阱

1. **不要在存储时脱敏**
   - ❌ 错误：存储记忆前调用脱敏函数
   - ✅ 正确：仅在LLM调用时脱敏
   - 原因：本地存储需要完整信息用于调试和恢复

2. **不要修改Hermes核心代码**
   - ❌ 错误：直接修改`/opt/hermes/agent/conversation_loop.py`
   - ✅ 正确：使用插件系统注册中间件
   - 原因：Hermes升级会覆盖核心代码

3. **不要硬编码敏感信息**
   - ❌ 错误：在脚本中直接写密码
   - ✅ 正确：从JSON文件读取
   - 原因：防止泄露到版本控制

### ⚠️ 常见错误

1. **插件未加载**
   - 检查`/opt/data/config/plugins.json`是否正确
   - 检查插件目录是否存在
   - 重启Hermes服务：`hermes gateway restart`

2. **脱敏未生效**
   - 检查插件是否启用：`"enabled": true`
   - 检查脱敏功能是否启用：`"config.enabled": true`
   - 查看日志：`tail -f ~/.hermes/logs/gateway.log | grep sanitize`

3. **正则表达式误匹配**
   - 测试脱敏规则：`python /opt/data/scripts/llm_sanitize.py "测试文本"`
   - 检查应用的规则：输出会显示`应用的规则：password, email`

### ⚠️ 性能考虑

1. **脱敏延迟**：约1-5ms/消息，对大多数应用影响不大
2. **正则编译**：首次调用会编译正则表达式，后续调用复用
3. **内存占用**：脱敏器实例占用约10KB内存

## 文件位置

### 核心脚本
- **脱敏脚本**：`/opt/data/scripts/llm_sanitize.py`
- **Hermes集成**：`/opt/data/scripts/hermes_llm_sanitize.py`
- **使用说明**：`/opt/data/docs/llm_sanitize_usage.md`

### 插件
- **插件目录**：`/opt/data/plugins/llm_sanitize/`
- **插件清单**：`/opt/data/plugins/llm_sanitize/manifest.json`
- **插件代码**：`/opt/data/plugins/llm_sanitize/llm_sanitize_plugin.py`
- **插件说明**：`/opt/data/plugins/llm_sanitize/README.md`

### 配置
- **插件配置**：`/opt/data/config/plugins.json`
- **脱敏规则配置**：`/opt/data/config/llm_sanitize_config.json`

### 测试
- **插件测试**：`/opt/data/scripts/test_llm_sanitize_plugin.py`
- **集成示例**：`/opt/data/scripts/example_hermes_integration.py`

## 参考文档

- **Hermes插件集成**：`references/hermes-plugin-integration.md` - 插件架构、中间件实现、配置管理
- **脱敏规则参考**：`references/sanitization-rules.md` - 规则详情、自定义规则、性能优化
- **故障排除**：`references/troubleshooting.md` - 常见问题、调试工具、错误代码

## 更新日志

- **v1.0** (2026-08-07)：初始版本
  - 支持密码、API密钥、姓名、地址、邮箱、手机号、身份证、银行卡脱敏
  - 支持文本、字典、列表、消息数组脱敏
  - 提供命令行和Python API两种使用方式
  - 专注于LLM调用时的脱敏处理，本地存储保持原样
  - 集成Hermes插件系统，通过中间件拦截LLM调用
  - 提供完整测试套件和配置选项
