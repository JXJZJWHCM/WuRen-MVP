# struts2 / s2-007

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-007\README.md
- Vulhub 相对路径: struts2/s2-007/README.md
- 脱敏代码块: 4

---
# S2-007 Remote Code Execution Vulnerablity

[中文版本(Chinese version)](README.zh-cn.md)

Affected Version: 2.0.0 - 2.2.3

Details: http://struts.apache.org/docs/s2-007.html

## Reference

http://rickgray.me/2016/05/06/review-struts2-remote-command-execution-vulnerabilities.html

When `<ActionName> -validation.xml` configured validation rules. If the type validation conversion fails, the server will splice the user-submitted form value strings, then performing an OGNL expression parsing and returning.

For example here is a `UserAction`:

[REDACTED: potential weaponization content removed]

And `UserAction-validation.xml` configuration:

[REDACTED: potential weaponization content removed]

When the user submits `age` as a `str` instead of an `int`, the server splices `"'" + value + "'"` with the code and then use the OGNL expression parse it. To make a successful expliot, we need find a form field configured with similar validation rules to make a conversion error. And then you can inject any OGNL expression code by the way just like SQL single quotes injected.

Payload which bypass the securely configured:

[REDACTED: potential weaponization content removed]

## Setup

```
docker compose build
docker compose up -d
```

## Exploit

Here is the EXP that can execute arbitrary code:

[REDACTED: potential weaponization content removed]

Put EXP into the input box (age), then get the command execution result:

![](1.jpeg)
