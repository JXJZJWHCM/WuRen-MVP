# struts2 / s2-045

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-045\README.zh-cn.md
- Vulhub 相对路径: struts2/s2-045/README.zh-cn.md
- CVE: CVE-2017-5638
- 脱敏代码块: 1

---
# S2-045 远程代码执行漏洞（CVE-2017-5638）

影响版本: Struts 2.3.5 - Struts 2.3.31, Struts 2.5 - Struts 2.5.10

漏洞详情:

 - http://struts.apache.org/docs/s2-045.html
 - https://blog.csdn.net/u011721501/article/details/60768657
 - https://paper.seebug.org/247/

## 漏洞环境

执行如下命令启动struts2 2.3.30：

```
docker compose up -d
```

环境启动后，访问`http://your-ip:8080`即可看到上传页面。

## 漏洞复现

直接发送如下数据包，可见`233*233`已成功执行：

[REDACTED: potential weaponization content removed]

![](1.png)
