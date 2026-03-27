# struts2 / s2-061

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-061\README.zh-cn.md
- Vulhub 相对路径: struts2/s2-061/README.zh-cn.md
- CVE: CVE-2020-17530
- 脱敏代码块: 1

---
# Struts2 S2-061 远程命令执行漏洞（CVE-2020-17530）

S2-061是对S2-059的绕过，Struts2官方对S2-059的修复方式是加强OGNL表达式沙盒，而S2-061绕过了该沙盒。该漏洞影响版本范围是Struts 2.0.0到Struts 2.5.25。

参考链接：

- https://cwiki.apache.org/confluence/display/WW/S2-061
- https://github.com/ka1n4t/CVE-2020-17530
- https://www.anquanke.com/post/id/225252
- https://mp.weixin.qq.com/s/RD2HTMn-jFxDIs4-X95u6g

## 漏洞环境

执行如下命令启动一个Struts2 2.5.25版本环境：

```
docker compose up -d
```

环境启动后，访问`http://target-ip:8080/index.action`查看到首页。

## 漏洞复现

发送如下数据包，即可执行`id`命令：

[REDACTED: potential weaponization content removed]

可见，`id`命令返回结果将直接显示在页面中：

![](1.png)
