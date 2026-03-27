# java / rmi-registry-bind-deserialization-bypass

- 来源: c:\Users\29530\Desktop\DM\vulhub\java\rmi-registry-bind-deserialization-bypass\README.md
- Vulhub 相对路径: java/rmi-registry-bind-deserialization-bypass/README.md
- 脱敏代码块: 2

---
# Java < JDK8u232_b09 RMI Registry Deserialization Remote Code Execution Bypass

[中文版本(Chinese version)](README.zh-cn.md)

Java Remote Method Invocation (RMI) is used for remote procedure calls in Java. Although remote binding is typically disabled, RMI Registry contains a remote binding functionality that can be exploited. By forging serialized data (implementing the Remote interface or dynamically proxying objects that implement the Remote interface) during the binding process, an attacker can trigger a deserialization vulnerability in the Registry when it processes the data.

Since JDK 8u121, the Registry implements a whitelist restriction for deserialized classes:

[REDACTED: potential weaponization content removed]

We need to find exploitable classes within these whitelisted classes. For more details, see [A Discussion on RMI Registry Deserialization Issues](https://blog.0kami.cn/blog/2020/rmi-registry-security-problem-20200206/), this article introduces the bypass methods that use JRMPListener to bypass the whitelist restriction.

References:

- <https://blog.0kami.cn/blog/2020/rmi-registry-security-problem-20200206/>
- <https://github.com/wh1t3p1g/ysoserial>

## Environment Setup

Execute the following commands to compile and start the RMI Registry and server:

```
docker compose build
docker compose run -e RMIIP=your-ip -p 1099:1099 rmi
```

Replace `your-ip` with your server's IP address. The client will use this IP to connect to the server.

After startup, the RMI Registry will be listening on port 1099.

## Vulnerability Reproduction

Use RMIRegistryExploit2 or RMIRegistryExploit3 from [ysoserial](https://github.com/wh1t3p1g/ysoserial)'s exploit package to perform the attack:

[REDACTED: potential weaponization content removed]

![](1.png)

The Registry will return an error, but this is normal and the command will still execute successfully.
