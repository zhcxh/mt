# Solverr 实测结果 (2026-08-09)

## 部署信息

- **镜像**: `ghcr.io/unseensnick/solverr:latest`
- **版本**: 1.2.2
- **部署位置**: fnOS Docker (192.168.31.118:8191)
- **UserAgent**: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36

## 测试结果

| 站点 | 反爬虫 | 结果 | 说明 |
|------|--------|------|------|
| httpbin.org | 无 | ✅ 成功 | 基础测试 |
| nowsecure.nl | Cloudflare | ✅ 成功 | 179KB HTML，基础 Cloudflare |
| share.acgnx.se | Cloudflare Turnstile | ⚠️ 超时 | 强防护，挑战超时 |
| repack-igruha.net | DDoS-Guard | ⚠️ 超时 | CAPTCHA 太强 |

## 结论

**Solverr 可以绕过基础 Cloudflare**，但对以下情况超时：
- Cloudflare Turnstile (Managed Challenge)
- DDoS-Guard + CAPTCHA

## 替代方案

| 场景 | 推荐方案 |
|------|---------|
| 基础 Cloudflare | Solverr ✅ |
| DDoS-Guard | Playwright + Stealth ✅ |
| Cloudflare Turnstile | RSS Feed (仅列表) ✅ |
| 强防护站点 | 手动验证 |

## API 使用

```bash
# 健康检查
curl -s 'http://192.168.31.118:8191/'
# 返回: {"msg": "FlareSolverr is ready!", "version": "1.2.2", ...}

# 绕过 Cloudflare
curl -s -X POST 'http://192.168.31.118:8191/v1' \
  -H 'Content-Type: application/json' \
  --data '{"cmd":"request.get","url":"https://example.com","maxTimeout":60000}'

# 使用 session 保持
curl -s -X POST 'http://192.168.31.118:8191/v1' \
  -H 'Content-Type: application/json' \
  --data '{"cmd":"request.get","url":"https://example.com","maxTimeout":60000,"session":"mysession"}'
```

## FlareSolverr 替代

如果 Solverr 镜像太大，可以使用 FlareSolverr：
- **镜像**: `flaresolverr/flaresolverr:latest`
- **大小**: ~800MB (比 Solverr 小很多)
- **API**: 相同 (`/v1`)
- **功能**: 单引擎 (仅 Chrome)，无自动故障转移

```bash
docker run -d \
  --name flaresolverr \
  -p 8191:8191 \
  -e LOG_LEVEL=info \
  --restart unless-stopped \
  flaresolverr/flaresolverr:latest
```
