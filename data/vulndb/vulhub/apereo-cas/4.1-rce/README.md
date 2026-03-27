# apereo-cas / 4.1-rce

- 来源: c:\Users\29530\Desktop\DM\vulhub\apereo-cas\4.1-rce\README.md
- Vulhub 相对路径: apereo-cas/4.1-rce/README.md
- 脱敏代码块: 3

---
# Apereo CAS 4.1 Deserialization RCE Vulnerability

[中文版本(Chinese version)](README.zh-cn.md)

Apereo CAS is a enterprise single sign-on system. There is an issue in CAS’s attempts to deserialize objects via the Apache Commons Collections library, which cased a RCE vulnerability.

Reference:

- https://apereo.github.io/2016/04/08/commonsvulndisc/

## Environment Setup

Execute following commands to start an Apereo CAS 4.1.5：

```
docker compose up -d
```

After the Apereo CAS is started, visiting `http://your-ip:8080/cas/login` to see the login page.

## Exploit

The out-of-the-box default configuration of Apereo CAS before 4.1.7, is using a default secret key `changeit`:

[REDACTED: potential weaponization content removed]

We can try to use [Apereo-CAS-Attack](https://github.com/vulhub/Apereo-CAS-Attack) to generate a encrypted [ysoserial](https://github.com/frohoff/ysoserial)'s serialized object:

[REDACTED: potential weaponization content removed]

![](1.png)

Then, intercept and modify the http request from login action of `/cas/login`, put the payload into `execution`'s value:

[REDACTED: potential weaponization content removed]

![](2.png)

Congrats, `touch /tmp/success` has been successfully executed:

![](3.png)
