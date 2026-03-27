# apereo-cas / 4.1-rce

- 来源: c:\Users\29530\Desktop\DM\vulhub\apereo-cas\4.1-rce\README.zh-cn.md
- Vulhub 相对路径: apereo-cas/4.1-rce/README.zh-cn.md
- 脱敏代码块: 3

---
# Apereo CAS 4.1 反序列化命令执行漏洞

Apereo CAS是一款Apereo发布的集中认证服务平台，常被用于企业内部单点登录系统。其4.1.7版本之前存在一处默认密钥的问题，利用这个默认密钥我们可以构造恶意信息触发目标反序列化漏洞，进而执行任意命令。

参考链接：

- https://apereo.github.io/2016/04/08/commonsvulndisc/

## 环境搭建

执行如下命令启动一个Apereo CAS 4.1.5：

```
docker compose up -d
```

环境启动后，访问`http://your-ip:8080/cas/login`即可查看到登录页面。

## 漏洞复现

漏洞原理实际上是Webflow中使用了默认密钥`changeit`：

[REDACTED: potential weaponization content removed]

我们使用[Apereo-CAS-Attack](https://github.com/vulhub/Apereo-CAS-Attack)来复现这个漏洞。使用ysoserial的CommonsCollections4生成加密后的Payload：

[REDACTED: potential weaponization content removed]

![](1.png)

然后我们登录CAS并抓包，将Body中的`execution`值替换成上面生成的Payload发送：

[REDACTED: potential weaponization content removed]

![](2.png)

登录Apereo CAS，可见`touch /tmp/success`已成功执行：

![](3.png)
