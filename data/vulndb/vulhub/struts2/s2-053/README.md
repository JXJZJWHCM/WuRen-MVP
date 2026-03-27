# struts2 / s2-053

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-053\README.md
- Vulhub 相对路径: struts2/s2-053/README.md
- 脱敏代码块: 1

---
# S2-053 Remote Code Execution Vulnerablity

[中文版本(Chinese version)](README.zh-cn.md)

Affected Version: Struts 2.0.1 - Struts 2.3.33, Struts 2.5 - Struts 2.5.10

Details:

 - http://struts.apache.org/docs/s2-053.html
 - https://mp.weixin.qq.com/s?__biz=MzU0NTI4MDQwMQ==&mid=2247483663&idx=1&sn=6304e1469f23c33728ab5c73692b675e

## Setup

```
docker compose up -d
```

After the environment run, you can see a submission page by visiting `http://your-ip:8080/hello.action`.

## Exploit

Struts2 allows parsing OGNL expressions when using the Freemarker template engine. The data is not parsed by OGNL itself, but after being parsed once by Freemarker. It becomes an expression and is parsed by OGNL second time.And remote code execution vulnerablity.

Payload:

[REDACTED: potential weaponization content removed]

![](01.png)

PS: Someone said that they could not reproduce the vulnerability. After my test, I found that the **line break** at the end of the above Payload could not be dropped (that is, the payload must be followed by a newline).
