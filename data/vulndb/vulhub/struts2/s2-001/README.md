# struts2 / s2-001

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-001\README.md
- Vulhub 相对路径: struts2/s2-001/README.md
- 脱敏代码块: 3

---
# S2-001 Remote Code Execution Vulnerability

[中文版本(Chinese version)](README.zh-cn.md)

## Reference link

[http://rickgray.me/2016/05/06/review-struts2-remote-command-execution-vulnerabilities.html](http://rickgray.me/2016/05/06/review-struts2-remote-command-execution-vulnerabilities.html)

> The vulnerability is that when the user submits the form data and the validation fails, the server parses the parameter values previously submitted by the user with the OGNL expression `%{value}` and repopulates the corresponding form data.For example, in the registration or login page. When submit fail, server will generally return the previously submitted data by default. Since the server uses `%{value}` to execute an OGNL expression parsing on the submitted data, it can send payload directly to execute command.

## Environment setup

Run the following commands to setup

```
docker compose build
docker compose up -d
```

## POC && EXP

Get the tomcat path:

[REDACTED: potential weaponization content removed]

Get the web site real path:

[REDACTED: potential weaponization content removed]

Execute command (command with parameter:`new java.lang.String[]{"cat","/etc/passwd"}`):

[REDACTED: potential weaponization content removed]

![](1.jpeg)
