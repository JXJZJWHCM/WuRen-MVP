# aj-report / CNVD-2024-15077

- 来源: c:\Users\29530\Desktop\DM\vulhub\aj-report\CNVD-2024-15077\README.zh-cn.md
- Vulhub 相对路径: aj-report/CNVD-2024-15077/README.zh-cn.md
- 脱敏代码块: 1

---
# AJ-Report 认证绕过与远程代码执行漏洞（CNVD-2024-15077）

AJ-Report是全开源的一个BI平台。在其1.4.0版本及以前，存在一处认证绕过漏洞，攻击者利用该漏洞可以绕过权限校验并执行任意代码。

参考链接：

- <https://xz.aliyun.com/t/14460>
- <https://github.com/wy876/POC/blob/main/AJ-Report%E5%BC%80%E6%BA%90%E6%95%B0%E6%8D%AE%E5%A4%A7%E5%B1%8F%E5%AD%98%E5%9C%A8%E8%BF%9C%E7%A8%8B%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E.md>

## 漏洞环境

执行如下命令启动一个AJ-Report 1.4.0服务器：

```
docker compose up -d
```

服务启动后，你可以在`http://your-ip:9095`查看到登录页面。

## 漏洞复现

要利用该漏洞，只需要发送如下数据包：

[REDACTED: potential weaponization content removed]

可见，`id`命令已经执行成功：

![](1.png)
