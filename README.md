`telegram_webproxy.js` 是一个单文件 Cloudflare Workers 实现：Telegram 官方 Web Proxy（td web-proxy）后端，来自https://github.com/ToiCF/CF-Workers-TGProxy
<br>绑定变量`SECRET`、`BOOT` ，使用 PowerShell 执行
```text
$bytes = New-Object byte[] 16; [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes); -join ($bytes | ForEach-Object { $_.ToString("x2") })
```
```text
$bytes = New-Object byte[] 24; [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes); -join ($bytes | ForEach-Object { $_.ToString("x2") })
```
