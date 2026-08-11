# 字幕搜索参考

## assrt.net (射手网) API

API文档：https://assrt.net/api/doc

### 配置

- API域名：`api.assrt.net`（不是 assrt.net/api）
- 备用域名：`api.makedie.me`
- 配额：20次/分钟（每token+IP共享）
- 认证：Token参数或Authorization Bearer头

### 搜索字幕

```bash
curl "https://api.assrt.net/v1/sub/search?token=TOKEN&q=Colony+2026&cnt=10"
```

参数：
- `q`：搜索关键词（至少3字符）
- `cnt`：返回结果数量（最多15）
- `pos`：分页起始位置
- `is_file`：值为1时搜索视频文件名
- `filelist`：值为1时返回压缩包内文件列表

### 获取字幕详情

```bash
curl "https://api.assrt.net/v1/sub/detail?token=TOKEN&id=800132"
```

返回 `subs[0].filelist` 包含所有字幕文件的下载URL。

### 字幕文件命名规则

- `chs.srt` / `chs.ass` — 简体中文
- `cht.srt` / `cht.ass` — 繁体中文
- `chs&eng.srt` — 简体+英文双语
- `cht&eng.srt` — 繁体+英文双语
- `eng.srt` — 英文

### 完整流程

1. 搜索：`/v1/sub/search?q=Movie+Name&token=TOKEN`
2. 获取ID：从结果中取 `subs[0].id`
3. 获取详情：`/v1/sub/detail?id=ID&token=TOKEN`
4. 下载：从 `filelist` 中选择合适格式的URL，用curl下载

---

## SubDL (subdl.com)

免费字幕站，无需登录即可下载。

### 搜索

访问 https://subdl.com 搜索影片名，支持多语言筛选。

### 优点
- 免费下载，无需登录
- 支持多语言筛选
- API可用（需注册）

### 缺点
- 中文字幕较少
- 部分影片无中文字幕

---

## 搜索策略

1. **优先 assrt.net** — 中文字幕最全，API免费
2. **次选 SubDL** — 免费但中文少
3. **用英文名搜索** — "Colony 2026" 比 "群体" 更容易找到
4. **验证字幕质量** — 下载后检查前几条是否通顺
