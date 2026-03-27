# 16.Cookie 中的 XSS（Base64） | Yak Program Language

- 来源: https://www.yaklang.com/Yaklab/vulinbox/XSS/16unsafe-cookie-b64
- 抓取时间: 2026-02-06T07:02:10Z

---
该示例从 cookis 中读取数据并经过 base64 解码，将数据插入模版中从而渲染到前端

### 示例代码： #

```
<div>
Here are photo for U! <br>
<img style='width: 100px' src="/static/logo.png" onclick='OrdinaryUser'/>
<script>const name = "Admin";
console.info("Hello" + `OrdinaryUser: ${name}`);</script>
</div>
```

### 攻击示例： #

通过在 Cookie 中构造特定的参数，攻击者可以注入恶意脚本代码

```
Cookie: xCnameB64=YWxlcnQoInhzcyIp
#修改cookie后
<div>
Here are photo for U! <br>
<img style='width: 100px' src="/static/logo.png" onclick='alert("xss")'/>
<script>const name = "Admin";
console.info("Hello" + `alert("xss"): ${name}`);</script>
</div>
```

### 防御措施： #

- 输入验证和过滤：在将数据存储到 Cookie 中之前，对用户输入进行严格验证和过滤。仅允许预期的输入内容，并且对输入内容进行适当的编码，以防止注入恶意数据。
- 限制 Cookie 的范围：将 Cookie 的作用范围限制在必要的路径或域名下，避免将敏感信息暴露在不必要的地方。
- 解析和验证 Cookie 数据：在使用 Cookie 数据之前，先解析和验证其内容。确保数据的格式正确且没有被篡改。

### 靶场演示： 视频 #

- 示例代码：
- 攻击示例：
- 防御措施：
- 靶场演示： 视频
