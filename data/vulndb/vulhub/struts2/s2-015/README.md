# struts2 / s2-015

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-015\README.md
- Vulhub 相对路径: struts2/s2-015/README.md
- 脱敏代码块: 3

---
# S2-015 Remote Code Execution Vulnerablity

[中文版本(Chinese version)](README.zh-cn.md)

Affected Version: 2.0.0 - 2.3.14.2

Details: http://struts.apache.org/docs/s2-015.html

## Setup

```
docker compose build
docker compose up -d
```

## Reference

Struts 2 allows define action mapping base on wildcards, like in example below:

[REDACTED: potential weaponization content removed]

If a request doesn't match any other defined action, it will be matched by * and requested action name will be used to load JSP file base on the name of action. And as value of {1} is threaten as an OGNL expression, thus allow to execute arbitrary Java code on server side. This vulnerability is combination of two problems:

1. requested action name isn't escaped or checked agains whitelist
2. double evaluation of an OGNL expression in TextParseUtil.translateVariables when combination of $ and % open chars is used.

## Exploit

Payload as follows：

[REDACTED: potential weaponization content removed]

Result:

![](01.png)

In addition to the above situation, S2-015 has another case of code execution:

[REDACTED: potential weaponization content removed]

Result:

![](02.png)
