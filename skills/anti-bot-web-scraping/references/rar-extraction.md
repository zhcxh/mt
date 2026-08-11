# RAR文件解压参考

## 问题

服务器上没有安装 `unrar` 或 `7z` 工具，无法直接解压RAR文件。

## 解决方案

使用 Python 的 `libarchive-c` 库可以读取RAR文件内容，无需安装unrar。

### 安装

```bash
cd /opt/data && uv venv rar_env && source rar_env/bin/activate
uv pip install libarchive-c
```

### 读取RAR文件列表

```python
import libarchive

rar_path = 'path/to/file.rar'

with libarchive.file_reader(rar_path) as a:
    for entry in a:
        print(f'{entry.name} ({entry.size} bytes)')
```

### 解压RAR文件

```python
import libarchive
import os

rar_path = 'path/to/file.rar'
extract_path = 'output/dir'

os.makedirs(extract_path, exist_ok=True)

with libarchive.file_reader(rar_path) as a:
    for entry in a:
        if entry.name.endswith('/'):
            continue  # 跳过目录
        out_path = os.path.join(extract_path, entry.name)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'wb') as f:
            for block in entry.get_blocks():
                f.write(block)
```

### 注意事项

1. `libarchive-c` 只能读取，不能创建RAR文件
2. 某些压缩的RAR文件可能无法完全解压
3. 目录条目需要特殊处理（跳过或单独创建）
