# 安居客 (Anjuke) 数据提取方法
## 适用于中国房产租赁/销售数据采集

### 页面结构分析

**安居客租赁列表页 URL 模式:**
```
https://{city}.zu.anjuke.com/community/search/?kw={小区名}
```
示例: `https://gz.zu.anjuke.com/community/search/?kw=中海麓府`

**页面结构:**
```
顶部: 社区均价统计（本月整租均价：一室 X元/月 二室 X元/月 三室 X元/月）
筛选: 房型 | 类型 | 更多
列表: 每项包含标题 | 户型 | 面积 | 楼层 | 小区名 | 朝向 | 地铁 | 价格
```

### 数据提取方法

#### 方法1: Strong标签价格提取（推荐）

安居客的价格元素使用 `<strong>` 标签，是页面中最可靠的选择器。

```javascript
// 提取所有价格和关联的房源信息
const strongs = document.querySelectorAll('strong');
const listings = [];
strongs.forEach(s => {
  const priceText = s.textContent.trim();
  // 匹配4-6位数字价格
  if (priceText.match(/^\d{4,6}$/)) {
    let parent = s.closest('[class]');
    let attempts = 0;
    // 向上遍历DOM找到包含完整房源信息的父元素
    while (parent && attempts < 10) {
      const t = parent.textContent.replace(/\s+/g, ' ').trim();
      // 包含面积和房型信息，且长度合理
      if (t.includes('平米') && t.includes('室') && t.length < 600) {
        listings.push({
          price: parseInt(priceText),
          context: t.substring(0, 400)
        });
        break;
      }
      parent = parent.parentElement;
      attempts++;
    }
  }
});
```

#### 方法2: 社区均价提取

社区均价显示在页面顶部，格式为"本月整租均价：三室 14,546元/月"。

```javascript
// 提取社区均价
const avgRentText = document.body.innerText;
const avgMatch = avgRentText.match(/三室\s*(\d+)元\/月/);
if (avgMatch) {
  console.log('三室均价:', avgMatch[1], '元/月');
}
```

### 数据解析模式

**房源信息文本格式:**
```
{标题} {户型}|{面积}平米|{楼层}(共{总楼层}层) {小区名} {区域}-{板块} -{地址} 整租 {朝向} 有电梯 {地铁线} {经纪人} {价格} 元/月
```

**正则解析示例:**
```javascript
const pattern = /(\d)室(\d)厅(\d)?卫?\|(\d+(?:\.\d+)?)平米\|(低|中|高)层\(共(\d+)层\)/;
const match = context.match(pattern);
if (match) {
  const listing = {
    rooms: match[1] + '室' + match[2] + '厅',
    size: parseFloat(match[4]),
    floor: match[5],
    totalFloors: parseInt(match[6]),
    rentPerSqm: Math.round(price / parseFloat(match[4]))
  };
}
```

### 常见陷阱

1. **动态class名**: 安居客使用Webpack打包，class名是哈希值（如 `css-1a2b3c`），不要用class选择器
2. **价格格式**: 价格在 `<strong>` 标签中，不带"元/月"后缀
3. **分页**: 列表页有分页，需要滚动或翻页获取更多数据
4. **验证码**: 频繁访问会触发CAPTCHA，建议控制请求频率
5. **IP限制**: 从云端IP访问可能被限制，建议使用中国境内IP

### 与其他平台对比

| 平台 | 价格选择器 | 数据完整性 | 反爬难度 |
|------|-----------|-----------|---------|
| **安居客** | `<strong>` 标签 | ⭐⭐⭐⭐⭐ | 中（CAPTCHA） |
| 房天下 | 动态class名 | ⭐⭐⭐⭐ | 低 |
| 链家 | 禁止访问 | ⭐⭐⭐⭐⭐ | 高（403） |
| 贝壳 | 禁止访问 | ⭐⭐⭐⭐⭐ | 高（403） |

### 参考案例

- 中海麓府（望庐花园）租赁数据: `property-analysis` 技能中的 `references/zhonghai-lufu-rental-data.md`
