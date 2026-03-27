# struts2 / s2-061

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-061\README.md
- Vulhub 相对路径: struts2/s2-061/README.md
- CVE: CVE-2020-17530
- 脱敏代码块: 1

---
# Struts2 S2-061 Remote Code Execution Vulnerablity (CVE-2020-17530)

[中文版本(Chinese version)](README.zh-cn.md)

In the versions prior to Struts 2.5.25, when evaluated on raw user input in tag attributes, may lead to remote code execution.

This vulnerability is the bypass of the OGNL sandbox, which enhance after S2-059.

References:

- https://cwiki.apache.org/confluence/display/WW/S2-061
- https://github.com/ka1n4t/CVE-2020-17530
- https://www.anquanke.com/post/id/225252
- https://mp.weixin.qq.com/s/RD2HTMn-jFxDIs4-X95u6g

## Setup

Start a Struts 2.5.25 server:

```
docker compose up -d
```

After the environment is started, visit `http://your-ip:8080/` and you will see a simple page. It is just a copy application of the [S2-059](https://github.com/vulhub/vulhub/tree/master/struts2/s2-059), except for the different Struts versions.

## Exploit

Send the following request to execute the `id` command:

[REDACTED: potential weaponization content removed]

It can be seen that the result of the `id` command will be displayed on the page:

![](1.png)
