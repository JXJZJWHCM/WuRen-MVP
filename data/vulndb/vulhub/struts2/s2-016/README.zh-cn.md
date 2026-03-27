# struts2 / s2-016

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-016\README.zh-cn.md
- Vulhub 相对路径: struts2/s2-016/README.zh-cn.md
- 脱敏代码块: 3

---
# S2-016 远程代码执行漏洞

影响版本: 2.0.0 - 2.3.15

漏洞详情:

 - http://struts.apache.org/docs/s2-016.html
 - http://www.freebuf.com/articles/web/25337.html

## 测试环境搭建

```
docker compose build
docker compose up -d
```

## 漏洞复现

在struts2中，DefaultActionMapper类支持以"action:"、"redirect:"、"redirectAction:"作为导航或是重定向前缀，但是这些前缀后面同时可以跟OGNL表达式，由于struts2没有对这些前缀做过滤，导致利用OGNL表达式调用java静态方法执行任意系统命令。

所以，访问`http://your-ip:8080/index.action?redirect:OGNL表达式`即可执行OGNL表达式。

执行命令：

[REDACTED: potential weaponization content removed]

获取web目录：

[REDACTED: potential weaponization content removed]

写入webshell：

[REDACTED: potential weaponization content removed]

执行结果：

![](01.png)
