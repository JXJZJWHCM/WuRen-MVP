# Cross-Site Scripting (XSS)

## 描述
跨站脚本（XSS）是将恶意脚本注入到页面上下文中的漏洞类型，可导致会话劫持、数据窃取、钓鱼与横向利用等风险。

## Types
1. **Stored XSS**: The malicious script is permanently stored on the target server.
2. **Reflected XSS**: The malicious script is reflected off the web server, such as in an error message or search result.
3. **DOM-based XSS**: The vulnerability exists in client-side code rather than server-side code.

## 快速验证要点（授权环境）
1. 确认注入点是否进入 HTML/属性/JS/URL 等不同上下文
2. 优先使用无害 PoC 验证（如触发可观测事件，不进行破坏性操作）
3. 若存在 CSP/过滤，先判断“被过滤的字符/关键字”再选 payload

## 相关工具
- `xsser`
- `dalfox`
