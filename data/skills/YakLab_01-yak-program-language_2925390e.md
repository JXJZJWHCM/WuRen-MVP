# 01.会话固定漏洞案例 | Yak Program Language

- 来源: https://www.yaklang.com/Yaklab/vulinbox/mall/01unsafe-sessionid/
- 抓取时间: 2026-02-06T07:03:09Z

---
会话固定漏洞是指网站或应用程序在用户登录时分配的会话标识符（Session ID）是固定不变的，而不是在每次会话中都重新生成。攻击者可以利用这个固定的会话标识符，轻松地接管用户的会话，执行未经授权的操作，甚至冒充合法用户。

```
// 登陆功能
{
    // 省略部分信息
    Handler: func(writer http.ResponseWriter, request *http.Request) {
        // 省略部分逻辑
        // 假设验证通过，返回登录成功消息
        response := struct {
            Id      uint   `json:"id"`
            Success bool   `json:"success"`
            Message string `json:"message"`
        }{
            Id:      user.ID,
            Success: true,
            Message: "Login successful",
        }
        var sessionID = "fixedSessionID"
        // 设置固定的会话标识符
        http.SetCookie(writer, &http.Cookie{
            Name:    "sessionID",
            Value:   sessionID,
            Path:    "/",
            Expires: time.Now().Add(15 * time.Minute),
        })
        // 返回登录成功信息
        writer.Header().Set("Content-Type", "application/json")
        err = json.NewEncoder(writer).Encode(response)
        if err != nil {
            writer.WriteHeader(http.StatusInternalServerError)
            return
        }
        writer.WriteHeader(http.StatusOK)
        return
    },
    RiskDetected: true,
},
```

攻击者可以利用固定的会话标识符，在不知晓用户密码的情况下直接将固定的会话ID注入到请求中，绕过登录验证，获取用户的登录状态和权限。攻击者可以在不登录的情况下访问用户的个人信息、执行关键操作，或者冒充用户进行各种恶意操作。

- 随机生成会话标识符： 在用户登录成功后，应该使用随机生成的会话标识符，并在每次会话中更新会话标识符，而不是使用固定的会话标识符。
- 设置安全的 Cookie 属性： 在设置 Cookie 时，应该使用 HttpOnly 和 Secure 属性，使得 Cookie 只能通过 HTTP 请求访问，以及仅在使用 HTTPS 连接时才能传输。
- 定期更新会话标识符： 应该定期更新会话标识符，例如在用户登录后、密码修改后、用户权限变更后等关键操作之后更新会话标识符，以降低攻击者获取固定会话标识符的机会。
- 加强会话管理： 对于敏感操作，应该实施额外的会话管理措施，如双因素认证、会话超时机制等，以提高系统的安全性。

通过以上防御措施，可以有效地防止会话固定漏洞的利用，保护用户的信息安全和系统的稳定性。

会话固定漏洞在靶场的" 商城登陆" 位置，演示如下:
