# struts2 / s2-032

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-032\README.zh-cn.md
- Vulhub 相对路径: struts2/s2-032/README.zh-cn.md
- CVE: CVE-2016-3081
- 脱敏代码块: 1

---
# S2-032 远程代码执行漏洞（CVE-2016-3081）

影响版本: Struts 2.3.20 - Struts Struts 2.3.28 (except 2.3.20.3 and 2.3.24.3)

漏洞详情:

 - https://cwiki.apache.org/confluence/display/WW/S2-032
 - https://www.cnblogs.com/mrchang/p/6501428.html

## 漏洞环境

执行如下命令启动struts2 2.3.28：

```
docker compose up -d
```

环境启动后，访问`http://your-ip:8080`即可看到默认页面。

## 漏洞复现

Struts2在开启了动态方法调用（Dynamic Method Invocation）的情况下，可以使用`method:<name>`的方式来调用名字是`<name>`的方法，而这个方法名将会进行OGNL表达式计算，导致远程命令执行漏洞。

直接请求如下URL，即可执行`id`命令：

[REDACTED: potential weaponization content removed]

![](1.png)
