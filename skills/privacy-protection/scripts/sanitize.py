#!/usr/bin/env python3
"""
敏感信息自动脱敏处理脚本 v2
用于在存储记忆前对敏感信息进行脱敏
"""

import re
import json
import sys
import os
from typing import Dict, List, Tuple

# 脱敏规则配置
SANITIZE_RULES = {
    # 密码脱敏（最高优先级）
    "password": {
        "patterns": [
            r'密码[：:]\s*([^\s，,。.]+)',
            r'(?i)password[：:]\s*([^\s，,。.]+)',
            r'(?i)pwd[：:]\s*([^\s，,。.]+)'
        ],
        "replacement": lambda m: m.group(0).replace(m.group(1), '***'),
        "description": "密码：完全脱敏"
    },
    # API密钥脱敏
    "api_key": {
        "patterns": [
            r'(?i)(api[_-]?key|apikey)[：:]\s*([a-zA-Z0-9_\-]{20,})',
            r'(?i)(token)[：:]\s*([a-zA-Z0-9_\-]{20,})',
            r'(?i)(secret)[：:]\s*([a-zA-Z0-9_\-]{20,})',
            r'xs_live_[a-zA-Z0-9_]{20,}',
            r'(?i)api密钥[：:]\s*([a-zA-Z0-9_\-]{20,})'
        ],
        "replacement": lambda m: f"{m.group(0)[:8]}***{m.group(0)[-4:]}" if len(m.group(0)) > 20 else m.group(0),
        "description": "API密钥：显示前8后4位"
    },
    # 姓名脱敏（保留姓）
    "name": {
        "patterns": [
            r'用户[：:]\s*([\u4e00-\u9fa5]{2,4})',
            r'姓名[：:]\s*([\u4e00-\u9fa5]{2,4})',
            r'名字[：:]\s*([\u4e00-\u9fa5]{2,4})',
            r'([\u4e00-\u9fa5]{2,4})的(?:信息|资料|数据)'
        ],
        "replacement": lambda m: m.group(1)[0] + '*' * (len(m.group(1)) - 1),
        "description": "姓名：保留姓，名字脱敏"
    },
    # 地址脱敏：只保留到市
    "address": {
        "patterns": [
            r'地址[：:]\s*((?:[\u4e00-\u9fa5]+(?:省|自治区|特别行政区)|[\u4e00-\u9fa5]+市)[\u4e00-\u9fa5]+(?:市|区|县|镇|街|路|号|室|楼|层|单元)[^\s，,。.]*)',
            r'((?:[\u4e00-\u9fa5]+(?:省|自治区|特别行政区)|[\u4e00-\u9fa5]+市)[\u4e00-\u9fa5]+(?:市|区|县|镇|街|路|号|室|楼|层|单元)[^\s，,。.]*)'
        ],
        "replacement": lambda m: m.group(1).split('市')[0] + '市***',
        "description": "地址：只保留到市级"
    },
    # 邮箱脱敏（保留域名）
    "email": {
        "pattern": r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        "replacement": lambda m: f"{m.group(1)[:2]}***@{m.group(2)}",
        "description": "邮箱：用户名前2位+域名"
    },
    # 手机号脱敏
    "phone": {
        "pattern": r'(?<!\d)(1[3-9]\d{9})(?!\d)',
        "replacement": lambda m: f"{m.group(1)[:3]}****{m.group(1)[-4:]}",
        "description": "手机号：显示前3后4位"
    },
    # 身份证号脱敏
    "id_card": {
        "pattern": r'(?<!\d)([1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx])(?!\d)',
        "replacement": lambda m: f"{m.group(1)[:6]}********{m.group(1)[-4:]}",
        "description": "身份证：显示前6后4位"
    },
    # 银行卡号脱敏
    "bank_card": {
        "pattern": r'(?<!\d)([1-9]\d{15,18})(?!\d)',
        "replacement": lambda m: f"{m.group(1)[:4]} **** **** {m.group(1)[-4:]}",
        "description": "银行卡：显示前4后4位"
    }
}


def sanitize_text(text: str, custom_rules: Dict = None) -> Tuple[str, List[str]]:
    """
    对文本进行脱敏处理
    
    Args:
        text: 原始文本
        custom_rules: 自定义规则（可选）
    
    Returns:
        (脱敏后的文本, 应用的规则列表)
    """
    if not text:
        return text, []
    
    rules = SANITIZE_RULES.copy()
    if custom_rules:
        rules.update(custom_rules)
    
    applied_rules = []
    result = text
    
    # 按优先级处理：密码 > API密钥 > 其他
    priority_order = ["password", "api_key"]
    
    for rule_name in priority_order:
        if rule_name not in rules:
            continue
            
        rule_config = rules[rule_name]
        patterns = rule_config.get("patterns", [rule_config.get("pattern")])
        
        for pattern in patterns:
            if pattern and re.search(pattern, result, re.IGNORECASE):
                result = re.sub(pattern, rule_config["replacement"], result, flags=re.IGNORECASE)
                if rule_name not in applied_rules:
                    applied_rules.append(rule_name)
    
    # 处理其他规则
    for rule_name, rule_config in rules.items():
        if rule_name in priority_order:  # 已处理
            continue
        
        patterns = rule_config.get("patterns", [rule_config.get("pattern")])
        
        for pattern in patterns:
            if pattern and re.search(pattern, result):
                result = re.sub(pattern, rule_config["replacement"], result)
                if rule_name not in applied_rules:
                    applied_rules.append(rule_name)
    
    return result, applied_rules


def sanitize_memory_entry(entry: str) -> str:
    """
    对记忆条目进行脱敏处理
    
    Args:
        entry: 原始记忆条目
    
    Returns:
        脱敏后的记忆条目
    """
    sanitized, applied = sanitize_text(entry)
    
    if applied:
        # 添加脱敏标记
        rules_str = ", ".join(applied)
        sanitized = f"[已脱敏: {rules_str}] {sanitized}"
    
    return sanitized


def sanitize_for_llm(text: str) -> str:
    """
    为LLM调用进行脱敏处理
    
    Args:
        text: 原始文本
    
    Returns:
        脱敏后的文本（不含脱敏标记）
    """
    sanitized, _ = sanitize_text(text)
    return sanitized


def sanitize_batch(entries: List[str]) -> List[str]:
    """
    批量脱敏处理
    
    Args:
        entries: 记忆条目列表
    
    Returns:
        脱敏后的记忆条目列表
    """
    return [sanitize_memory_entry(entry) for entry in entries]


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("用法: python sanitize.py <text_or_file>")
        print("示例: python sanitize.py '密码：abc123'")
        print("示例: python sanitize.py memory.txt")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    
    # 判断是文件还是文本
    if os.path.isfile(input_arg):
        with open(input_arg, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = input_arg
    
    sanitized, applied = sanitize_text(text)
    
    print("脱敏结果：")
    print("-" * 50)
    print(sanitized)
    print("-" * 50)
    
    if applied:
        print(f"\n应用的规则：{', '.join(applied)}")
    else:
        print("\n未检测到需要脱敏的信息")


if __name__ == "__main__":
    main()
