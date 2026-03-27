# struts2 / s2-008

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-008\README.md
- Vulhub 相对路径: struts2/s2-008/README.md
- 脱敏代码块: 1

---
# S2-008 Remote Code Execution Vulnerablity

[中文版本(Chinese version)](README.zh-cn.md)

Affected Version: 2.1.0 - 2.3.1

Details: http://struts.apache.org/docs/s2-008.html

## Setup

```
docker compose build
docker compose up -d
```

## Reference

http://rickgray.me/2016/05/06/review-struts2-remote-command-execution-vulnerabilities.html

> S2-008 involves multiple vulnerabilities. Cookie interceptor configuration problem can cause OGNL expressions execute, but most web containers (such as Tomcat) have character restrictions for cookie names, some key characters cannot be used. Another point is that if the struts2 turn on `devMode` mode, there are multiple debug interfaces that can directly view object information or execute commands. As Kxlzx(author) mentions, this situation is almost impossible in the real environment. So it becomes It's very useless, but I don't think it's absolute. It's possible to hack a struts2 application that turn on `debug` mode on the server as a backdoor.

For example, adding the parameter `?debug=command&expression=<OGNL EXP>` in `devMode` mode, OGNL expression will be executed directly and you can execute the command:

[REDACTED: potential weaponization content removed]
