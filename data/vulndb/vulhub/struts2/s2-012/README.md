# struts2 / s2-012

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-012\README.md
- Vulhub 相对路径: struts2/s2-012/README.md
- 脱敏代码块: 2

---
# S2-012 Remote Code Execution Vulnerablity

[中文版本(Chinese version)](README.zh-cn.md)

Affected Version: 2.1.0 - 2.3.13

Details: http://struts.apache.org/docs/s2-012.html

## Reference

If the redirect type is used when configuring `result` in the `action`, and ${param_name} is also used as the redirect variable, for example:

[REDACTED: potential weaponization content removed]

During the redirection process, struts2 performs an OGNL expression parsing on the value of the `name` parameter, so that OGNL expression can be inserted to cause the command execution.

## Setup

```
docker compose build
docker compose up -d
```

## Exploit

We can use s2-001's POC directly:

[REDACTED: potential weaponization content removed]

Result：

![](1.png)
