# 脱敏规则参考

## 规则优先级

脱敏规则按优先级处理，高优先级规则先执行：

1. **密码**（最高优先级）- 完全替换
2. **API密钥** - 部分替换
3. **其他规则** - 按顺序处理

## 规则详情

### 1. 密码脱敏

**检测模式：**
```python
patterns = [
    r'密码[：:]\s*([^\s，,。.]+)',
    r'(?i)password[：:]\s*([^\s，,。.]+)',
    r'(?i)pwd[：:]\s*([^\s，,。.]+)'
]
```

**处理方式：** 完全替换为 `***`

**示例：**
- `密码：Sr@010203` → `密码：***`
- `password: abc123` → `password: ***`
- `pwd: secret` → `pwd: ***`

**注意事项：**
- 匹配中文冒号（：）和英文冒号（:）
- 不区分大小写（password/PASSWORD/Password）
- 只匹配冒号后的内容

### 2. API密钥脱敏

**检测模式：**
```python
patterns = [
    r'(?i)(api[_-]?key|apikey)[：:]\s*([a-zA-Z0-9_\-]{20,})',
    r'(?i)(token)[：:]\s*([a-zA-Z0-9_\-]{20,})',
    r'(?i)(secret)[：:]\s*([a-zA-Z0-9_\-]{20,})',
    r'xs_live_[a-zA-Z0-9_]{20,}',
    r'(?i)api密钥[：:]\s*([a-zA-Z0-9_\-]{20,})'
]
```

**处理方式：** 显示前8后4位，中间用 `***` 替代

**示例：**
- `xs_live_GvUszp1YEXXO7_CvqaEq2u6hHtwDgt4CvzRzinei6kw` → `xs_live_***i6kw`
- `api_key: abcdefghijklmnopqrstuvwxyz` → `api_key: abcdef***wxyz`

**注意事项：**
- 最小长度20个字符
- 支持下划线、连字符
- 支持xs_live_前缀模式

### 3. 姓名脱敏

**检测模式：**
```python
patterns = [
    r'用户[：:]\s*([\u4e00-\u9fa5]{2,4})',
    r'姓名[：:]\s*([\u4e00-\u9fa5]{2,4})',
    r'名字[：:]\s*([\u4e00-\u9fa5]{2,4})',
    r'([\u4e00-\u9fa5]{2,4})的(?:信息|资料|数据)'
]
```

**处理方式：** 保留姓，名字用 `*` 替代

**示例：**
- `用户：朱正兴` → `用户：朱**`
- `姓名：张三` → `姓名：张*`
- `名字：李四` → `名字：李*`

**注意事项：**
- 只匹配2-4个汉字
- 保留第一个字（姓）
- 支持多种关键词（用户/姓名/名字）

### 4. 地址脱敏

**检测模式：**
```python
patterns = [
    r'地址[：:]\s*((?:[\u4e00-\u9fa5]+(?:省|自治区|特别行政区)|[\u4e00-\u9fa5]+市)[\u4e00-\u9fa5]+(?:市|区|县|镇|街|路|号|室|楼|层|单元)[^\s，,。.]*)',
    r'((?:[\u4e00-\u9fa5]+(?:省|自治区|特别行政区)|[\u4e00-\u9fa5]+市)[\u4e00-\u9fa5]+(?:市|区|县|镇|街|路|号|室|楼|层|单元)[^\s，,。.]*)'
]
```

**处理方式：** 只保留到市级

**示例：**
- `缅甸仰光市某某路` → `缅甸仰光市***`
- `北京市朝阳区xxx路` → `北京市***`

**注意事项：**
- 匹配省/市/自治区前缀
- 保留到第一个"市"字
- 详细地址用 `***` 替代

### 5. 邮箱脱敏

**检测模式：**
```python
pattern = r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
```

**处理方式：** 用户名前2位+`***`+域名

**示例：**
- `CeliaTemple5706@outlook.com` → `Ce***@outlook.com`
- `test@example.com` → `te***@example.com`

**注意事项：**
- 保留域名不变
- 用户名只保留前2位
- 支持所有标准邮箱格式

### 6. 手机号脱敏

**检测模式：**
```python
pattern = r'(?<!\d)(1[3-9]\d{9})(?!\d)'
```

**处理方式：** 显示前3后4位

**示例：**
- `13812345678` → `138****5678`
- `15912345678` → `159****5678`

**注意事项：**
- 只匹配11位手机号
- 以1开头，第二位3-9
- 使用负向断言防止匹配更长数字

### 7. 身份证号脱敏

**检测模式：**
```python
pattern = r'(?<!\d)([1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx])(?!\d)'
```

**处理方式：** 显示前6后4位

**示例：**
- `110101199001011234` → `110101********1234`

**注意事项：**
- 只匹配18位身份证号
- 支持X结尾
- 使用负向断言防止匹配更长数字

### 8. 银行卡号脱敏

**检测模式：**
```python
pattern = r'(?<!\d)([1-9]\d{15,18})(?!\d)'
```

**处理方式：** 显示前4后4位

**示例：**
- `6222021234567890123` → `6222 **** **** 0123`

**注意事项：**
- 匹配16-19位银行卡号
- 以1-9开头
- 使用负向断言防止匹配更长数字

## 自定义规则

### 添加新规则

```python
# 在 /opt/data/scripts/llm_sanitize.py 中添加
SANITIZE_RULES = {
    # 现有规则...
    
    # 新规则示例：工号脱敏
    "employee_id": {
        "patterns": [
            r'工号[：:]\s*(E\d{6})',
            r'(?i)employee[_-]?id[：:]\s*([A-Z]{2}\d{4})'
        ],
        "replacement": lambda m: f"工号：{m.group(1)[:2]}***",
        "description": "工号：显示前2位"
    }
}
```

### 测试新规则

```bash
python /opt/data/scripts/llm_sanitize.py "工号：E123456"
# 预期输出：工号：E12***
```

## 规则组合

### 多规则匹配

当文本包含多种敏感信息时，所有匹配的规则都会应用：

```python
text = "用户：朱正兴，密码：abc123，邮箱：test@example.com"
sanitized, rules = sanitize_text(text)
# 输出：朱**，密码：***，邮箱：te***@example.com
# 应用的规则：['password', 'email', 'name']
```

### 规则冲突处理

高优先级规则先执行，低优先级规则后执行：

```python
text = "密码：abc123，API密钥：xs_live_xxxx"
sanitized, rules = sanitize_text(text)
# 密码先处理，然后处理API密钥
```

## 性能优化

### 正则表达式编译

正则表达式在首次使用时编译，后续调用复用：

```python
# 首次调用：编译正则（约1ms）
sanitized, rules = sanitize_text("密码：abc123")

# 后续调用：复用编译后的正则（约0.1ms）
sanitized, rules = sanitize_text("密码：def456")
```

### 批量处理

使用`sanitize_batch`处理多个文本：

```python
from llm_sanitize import sanitize_batch

texts = ["密码：abc123", "邮箱：test@example.com"]
sanitized = sanitize_batch(texts)
# 返回脱敏后的文本列表
```

## 调试技巧

### 1. 查看应用的规则

```python
from llm_sanitize import sanitize_text

text = "用户：朱正兴，密码：abc123"
sanitized, rules = sanitize_text(text)
print(f"应用的规则：{rules}")
# 输出：应用的规则：['password', 'name']
```

### 2. 测试单个规则

```python
import re

# 测试密码规则
pattern = r'密码[：:]\s*([^\s，,。.]+)'
text = "密码：abc123"
match = re.search(pattern, text)
if match:
    print(f"匹配到：{match.group(1)}")
    # 输出：匹配到：abc123
```

### 3. 检查正则表达式

```python
import re

# 测试正则表达式
pattern = r'密码[：:]\s*([^\s，,。.]+)'
test_cases = [
    "密码：abc123",
    "密码: abc123",
    "password：abc123",
    "PASSWORD: abc123",
]

for test in test_cases:
    match = re.search(pattern, test, re.IGNORECASE)
    print(f"{test}: {'✓' if match else '✗'}")
```
