# yapi / unacc

- 来源: c:\Users\29530\Desktop\DM\vulhub\yapi\unacc\README.md
- Vulhub 相对路径: yapi/unacc/README.md
- 脱敏代码块: 1

---
# YApi Registration and Mock Remote Code Execution

[中文版本(Chinese version)](README.zh-cn.md)

YApi is a API management tool developed by Node.JS. If registration of the YApi server is enabled, attackers will be able to execute arbitrary Javascript code in the Mock page.

References:

- <https://paper.seebug.org/1639/>
- <https://www.freebuf.com/vuls/279967.html>

## Vulnerability Environment

Execute following command to start a YApi server 1.9.2:

```
docker compose up -d
```

After the server is started, browse the `http://localhost:3000` to see the index page of the YApi.

## Vulnerability Reproduce

Register a normal user then create a project and an interface:

![](1.png)

![](2.png)

There is a "Mock Tab" that you can input JavaScript code, put the evil code into textarea:

[REDACTED: potential weaponization content removed]

![](3.png)

Then, go back to the preview tab and see the Mock URL:

![](4.png)

Open that URL, Mock script is executed and you can see the output:

![](5.png)
