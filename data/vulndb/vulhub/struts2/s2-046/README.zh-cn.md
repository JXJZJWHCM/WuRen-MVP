# struts2 / s2-046

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-046\README.zh-cn.md
- Vulhub 相对路径: struts2/s2-046/README.zh-cn.md
- CVE: CVE-2017-5638
- 脱敏代码块: 1

---
# S2-046 远程代码执行漏洞（CVE-2017-5638）

影响版本: Struts 2.3.5 - Struts 2.3.31, Struts 2.5 - Struts 2.5.10

漏洞详情:

 - https://cwiki.apache.org/confluence/display/WW/S2-046
 - https://xz.aliyun.com/t/221

## 漏洞环境

执行如下命令启动struts2 2.3.30：

```
docker compose up -d
```

环境启动后，访问`http://your-ip:8080`即可看到上传页面。

## 漏洞复现

与s2-045类似，但是输入点在文件上传的filename值位置，并需要使用`\x00`截断。

由于需要发送畸形数据包，我们简单使用原生socket编写payload：

[REDACTED: potential weaponization content removed]

`233*233`已成功执行：

![](1.png)
