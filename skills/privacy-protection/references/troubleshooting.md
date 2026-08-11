# 故障排除参考

## 常见问题及解决方案

### 1. 插件未加载

**症状：**
- 脱敏功能不生效
- 日志中没有sanitize相关记录

**检查步骤：**

```bash
# 1. 检查插件目录
ls -la /opt/data/plugins/llm_sanitize/

# 2. 检查manifest.json
cat /opt/data/plugins/llm_sanitize/manifest.json

# 3. 检查配置文件
cat /opt/data/config/plugins.json

# 4. 检查日志
tail -f ~/.hermes/logs/gateway.log | grep -i plugin

# 5. 重启服务
hermes gateway restart
```

**常见原因：**
- 插件目录不存在
- manifest.json格式错误
- plugins.json配置错误
- 插件代码有语法错误

**解决方案：**

```bash
# 重建插件目录
mkdir -p /opt/data/plugins/llm_sanitize

# 验证manifest.json
python -c "import json; json.load(open('/opt/data/plugins/llm_sanitize/manifest.json'))"

# 验证plugins.json
python -c "import json; json.load(open('/opt/data/config/plugins.json'))"

# 重启服务
hermes gateway restart
```

### 2. 脱敏未生效

**症状：**
- 消息中的敏感信息未被脱敏
- LLM调用时仍然包含原始敏感信息

**检查步骤：**

```bash
# 1. 测试插件是否正常
python /opt/data/plugins/llm_sanitize/llm_sanitize_plugin.py

# 2. 测试脱敏脚本
python /opt/data/scripts/llm_sanitize.py "密码：abc123"

# 3. 启用日志
# 修改 /opt/data/config/plugins.json
# 设置 "log_sanitize": true

# 4. 查看日志
tail -f ~/.hermes/logs/gateway.log | grep -i sanitize
```

**常见原因：**
- 插件未启用
- 脱敏功能未启用
- 正则表达式不匹配
- 消息格式不正确

**解决方案：**

```json
// 确保配置正确
{
  "plugins": {
    "llm_sanitize": {
      "enabled": true,
      "config": {
        "enabled": true,
        "log_sanitize": true
      }
    }
  }
}
```

### 3. 正则表达式误匹配

**症状：**
- 正常文本被错误脱敏
- 脱敏结果不符合预期

**检查步骤：**

```python
from llm_sanitize import sanitize_text

# 测试文本
text = "你的密码是什么？"
sanitized, rules = sanitize_text(text)
print(f"原始：{text}")
print(f"脱敏：{sanitized}")
print(f"规则：{rules}")
```

**常见原因：**
- 正则表达式过于宽松
- 文本格式不符合预期
- 多个规则冲突

**解决方案：**

```python
# 1. 调试正则表达式
import re

pattern = r'密码[：:]\s*([^\s，,。.]+)'
test_cases = [
    "密码：abc123",  # 应该匹配
    "密码是什么？",  # 不应该匹配
    "password: abc",  # 应该匹配
]

for test in test_cases:
    match = re.search(pattern, test, re.IGNORECASE)
    print(f"{test}: {'✓' if match else '✗'}")

# 2. 修改正则表达式
# 如果"密码是什么？"被误匹配，可以修改pattern
# 例如：r'密码[：:]\s*([^\s，,。.]+)' → r'密码[：:]\s+([^\s，,。.]+)'
# 添加\s+确保冒号后有空格
```

### 4. 性能问题

**症状：**
- LLM调用延迟增加
- 脱敏处理耗时过长

**检查步骤：**

```python
import time
from llm_sanitize import sanitize_text

# 测试性能
texts = ["密码：abc123"] * 1000

start = time.time()
for text in texts:
    sanitize_text(text)
end = time.time()

print(f"1000次脱敏耗时：{end - start:.3f}秒")
print(f"平均每次：{(end - start) * 1000:.3f}毫秒")
```

**常见原因：**
- 正则表达式过于复杂
- 文本过长
- 批量处理未优化

**解决方案：**

```python
# 1. 优化正则表达式
# 使用更简单的模式
# 避免使用回溯（backtracking）

# 2. 批量处理
from llm_sanitize import sanitize_batch

texts = ["密码：abc123", "邮箱：test@example.com"]
sanitized = sanitize_batch(texts)  # 批量处理更高效

# 3. 缓存结果
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_sanitize(text):
    return sanitize_text(text)
```

### 5. 插件加载失败

**症状：**
- Hermes启动时报错
- 插件未被识别

**检查步骤：**

```bash
# 1. 检查Python语法
python -m py_compile /opt/data/plugins/llm_sanitize/llm_sanitize_plugin.py

# 2. 检查导入
cd /opt/data/plugins/llm_sanitize
python -c "import llm_sanitize_plugin"

# 3. 检查日志
grep -i "error\|exception" ~/.hermes/logs/gateway.log | tail -20
```

**常见原因：**
- Python语法错误
- 导入错误
- 依赖缺失
- 权限问题

**解决方案：**

```bash
# 1. 修复语法错误
python -m py_compile /opt/data/plugins/llm_sanitize/llm_sanitize_plugin.py

# 2. 安装依赖
pip install -r requirements.txt

# 3. 修复权限
chmod 644 /opt/data/plugins/llm_sanitize/llm_sanitize_plugin.py
chmod 644 /opt/data/plugins/llm_sanitize/manifest.json
```

## 调试工具

### 1. 脱敏测试脚本

```bash
# 测试基本脱敏
python /opt/data/scripts/llm_sanitize.py "密码：abc123，邮箱：test@example.com"

# 测试插件
python /opt/data/plugins/llm_sanitize/llm_sanitize_plugin.py

# 运行完整测试
python /opt/data/scripts/test_llm_sanitize_plugin.py
```

### 2. 日志查看

```bash
# 查看实时日志
tail -f ~/.hermes/logs/gateway.log

# 查看sanitize相关日志
tail -f ~/.hermes/logs/gateway.log | grep -i sanitize

# 查看错误日志
grep -i "error\|exception" ~/.hermes/logs/gateway.log | tail -20
```

### 3. 配置验证

```bash
# 验证JSON格式
python -c "import json; json.load(open('/opt/data/config/plugins.json'))"

# 查看当前配置
cat /opt/data/config/plugins.json | python -m json.tool
```

### 4. 插件状态检查

```bash
# 检查插件列表
hermes plugins list

# 检查插件状态
hermes status

# 检查服务状态
hermes gateway status
```

## 性能监控

### 1. 延迟监控

```python
import time
from llm_sanitize import sanitize_text

def monitor_sanitize(text, iterations=100):
    """监控脱敏性能"""
    times = []
    for _ in range(iterations):
        start = time.time()
        sanitize_text(text)
        end = time.time()
        times.append(end - start)
    
    avg = sum(times) / len(times)
    print(f"平均延迟：{avg * 1000:.3f}毫秒")
    print(f"最大延迟：{max(times) * 1000:.3f}毫秒")
    print(f"最小延迟：{min(times) * 1000:.3f}毫秒")

monitor_sanitize("密码：abc123")
```

### 2. 内存监控

```python
import psutil
import os

def monitor_memory():
    """监控内存使用"""
    process = psutil.Process(os.getpid())
    memory = process.memory_info()
    print(f"内存使用：{memory.rss / 1024 / 1024:.2f} MB")

monitor_memory()
```

## 常见错误代码

### 1. ImportError

```python
ImportError: cannot import name 'sanitize_text' from 'llm_sanitize'
```

**原因：** 模块路径不正确或函数名错误

**解决：**
```python
import sys
sys.path.append('/opt/data/scripts')
from llm_sanitize import sanitize_text
```

### 2. KeyError

```python
KeyError: 'messages'
```

**原因：** payload中没有messages字段

**解决：**
```python
if 'messages' in payload:
    payload['messages'] = sanitize_messages(payload['messages'])
```

### 3. TypeError

```python
TypeError: expected string or bytes-like object
```

**原因：** 传入的参数不是字符串

**解决：**
```python
if isinstance(text, str):
    sanitized, rules = sanitize_text(text)
else:
    sanitized = text
    rules = []
```

### 4. RegexError

```python
re.error: nothing to repeat at position 1
```

**原因：** 正则表达式语法错误

**解决：**
```python
# 检查正则表达式
import re
try:
    re.compile(pattern)
except re.error as e:
    print(f"正则表达式错误：{e}")
```

## 联系支持

如果以上方法都无法解决问题，请提供以下信息：

1. **错误信息**：完整的错误堆栈
2. **配置文件**：`/opt/data/config/plugins.json`的内容
3. **日志文件**：`~/.hermes/logs/gateway.log`的相关日志
4. **测试结果**：运行测试脚本的输出
5. **环境信息**：Python版本、Hermes版本、操作系统

将这些信息提供给技术支持，以便快速定位和解决问题。
