# struts2 / s2-048

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-048\README.md
- Vulhub 相对路径: struts2/s2-048/README.md
- 脱敏代码块: 2

---
# S2-048 Remote Code Execution Vulnerablity

[中文版本(Chinese version)](README.zh-cn.md)

Affected Version: 2.0.0 - 2.3.32

Details:

 - http://struts.apache.org/docs/s2-048.html
 - http://bobao.360.cn/learning/detail/4078.html
 - http://xxlegend.com/2017/07/08/S2-048%20%E5%8A%A8%E6%80%81%E5%88%86%E6%9E%90/

## Setup

```
docker compose up -d
```

## Exploit

This environment is a struts-2.3.32 showcase, in tomcat-8.5. After the environment run, visit the `http://your-ip:8080/showcase/` to view struts2 showcase.

Access Integration/Struts 1 Integration:

![](01.png)

The OGNL expression vulnerability position is `Gangster Name` form.

Enter `${233*233}` to see the results of the execution:

![](02.png)

Refer S2-045's sandbox bypass method, here is my POC:

[REDACTED: potential weaponization content removed]

![](03.png)

Of course, you can also use the POC of s2-045 directly (need Burpsuite):

[REDACTED: potential weaponization content removed]
