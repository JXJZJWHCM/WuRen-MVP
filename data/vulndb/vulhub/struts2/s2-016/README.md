# struts2 / s2-016

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-016\README.md
- Vulhub 相对路径: struts2/s2-016/README.md
- 脱敏代码块: 3

---
# S2-016 Remote Code Execution Vulnerablity

[中文版本(Chinese version)](README.zh-cn.md)

Affected Version: 2.0.0 - 2.3.15

Details:

 - http://struts.apache.org/docs/s2-016.html
 - http://www.freebuf.com/articles/web/25337.html

## Setup

```
docker compose build
docker compose up -d
```

## Exploit

Visit `http://your-ip:8080/index.action?redirect:OGNL expression` to execute an OGNL expression.

Execute `uname -a`:

[REDACTED: potential weaponization content removed]

Get web directory:

[REDACTED: potential weaponization content removed]

Get webshell：

[REDACTED: potential weaponization content removed]

Result:

![](01.png)
