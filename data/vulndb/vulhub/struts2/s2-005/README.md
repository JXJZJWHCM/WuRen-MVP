# struts2 / s2-005

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-005\README.md
- Vulhub 相对路径: struts2/s2-005/README.md
- 脱敏代码块: 3

---
# S2-005 Remote Code Execution Vulnerability

[中文版本(Chinese version)](README.zh-cn.md)

Affected Version: 2.0.0 - 2.1.8.1

Details: http://struts.apache.org/docs/s2-005.html

## Reference

Refer 《White hat speaking Web Security》 by Wu Hanqing (Author)

> s2-005 is a vulnerability which originating from S2-003(version: < 2.0.12), This behavior has been filtered in S2-003, but it turned out that the resulting fix based on whitelisting acceptable parameter names closed the vulnerability only partially.

XWork will parse the keys and values of the GET parameter into Java statements using OGNL expressions, such as:

[REDACTED: potential weaponization content removed]

Process follows:

- In S2-003 Use `\u0023` to bypass struts2's filter `#`
- After S2-003 struts2 added security mode (sandbox)
- In S2-005 Use the OGNL expression to close the security mode and bypass again

## Setup

Run the following commands to start the environment

```
docker compose build
docker compose up -d
```

## POC && EXP

### Remote code execution POC (don't have display echo, use `@` instead space)

[REDACTED: potential weaponization content removed]

Some others POC will return 400 in tomcat8.Because the characters `\`, `"` can't be placed directly in the path, we need urlencode it before send.

This POC don't have display, used OGNL's Expression Evaluation:

![](1.jpeg)

`(aaa)(bbb)`, `aaa` is used as the OGNL expression string, and `bbb` is the root object of the expression. Therefore, if we needs to execute code like `aaa`, it needs to be wrapped in quotation marks, and the `bbb` position can directly place the Java statement. `(aaa)(bbb)=true` is actually `aaa=true`.

However, how to understand exactly, it needs further research and to be optimized. Hope someone can write a POC that can display echo.

### Remote code execution POC (have display echo, command need urlencode)

[REDACTED: potential weaponization content removed]

![](s2-005-3.png)

![](s2-005-4.png)
