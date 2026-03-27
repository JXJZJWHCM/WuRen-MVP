# mojarra / jsf-viewstate-deserialization

- 来源: c:\Users\29530\Desktop\DM\vulhub\mojarra\jsf-viewstate-deserialization\README.zh-cn.md
- Vulhub 相对路径: mojarra/jsf-viewstate-deserialization/README.zh-cn.md
- 脱敏代码块: 1

---
# Mojarra JSF ViewState 反序列化漏洞

JavaServer Faces (JSF) 是一种用于构建 Web 应用程序的标准，Mojarra是一个实现了JSF的框架。在其2.1.29-08、2.0.11-04版本之前，没有对JSF中的ViewState进行加密，进而导致攻击者可以构造恶意的序列化ViewState对象对服务器进行攻击。

参考链接：

- https://www.alphabot.com/security/blog/2017/java/Misconfigured-JSF-ViewStates-can-lead-to-severe-RCE-vulnerabilities.html
- https://www.exploit-db.com/docs/48126
- https://www.synacktiv.com/ressources/JSF_ViewState_InYourFace.pdf

## 环境搭建

执行如下命令启动一个使用了JDK7u21和mojarra 2.1.28的JSF应用：

```
docker compose up -d
```

环境启动后，访问`http://your-ip:8080`即可查看到demo页面。

## 漏洞复现

JSF的ViewState结构如下：

![](1.png)

根据这个结构，我们使用ysoserial的Jdk7u21利用链来生成一段合法的Payload：

[REDACTED: potential weaponization content removed]

然后，我们提交表单并抓包，修改其中`javax.faces.ViewState`字段的值为上述Payload（别忘了URL编码）：

![](2.png)

`touch /tmp/success`已成功执行：

![](3.png)
