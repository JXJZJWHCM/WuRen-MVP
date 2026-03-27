# fastjson / 1.2.24-rce

- 来源: c:\Users\29530\Desktop\DM\vulhub\fastjson\1.2.24-rce\README.md
- Vulhub 相对路径: fastjson/1.2.24-rce/README.md
- CVE: CVE-2017-18349
- 脱敏代码块: 4

---
# Fastjson 1.2.24 Deserialization Remote Command Execution (CVE-2017-18349)

[中文版本(Chinese version)](README.zh-cn.md)

Fastjson is a JSON parser developed by Alibaba. During the JSON parsing process, it supports using autoType to instantiate a specific class and call its set/get methods to access properties. By identifying relevant methods in the code, malicious exploitation chains can be constructed.

References:

- <https://www.freebuf.com/vuls/208339.html>
- <http://xxlegend.com/2017/04/29/title-%20fastjson%20%E8%BF%9C%E7%A8%8B%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96poc%E7%9A%84%E6%9E%84%E9%80%A0%E5%92%8C%E5%88%86%E6%9E%90/>

## Environment Setup

Execute the following command to start the test server that use Fastjson 1.2.24 as the default JSON parser:

```
docker compose up -d
```

After the server is started, visit `http://your-ip:8090` to see a JSON format output.

You can update the server information by POSTing a JSON object to this address:

[REDACTED: potential weaponization content removed]

## Vulnerability Reproduction

Since the target environment is Java 8u102, which doesn't have the `com.sun.jndi.rmi.object.trustURLCodebase` restriction, we can use the `com.sun.rowset.JdbcRowSetImpl` exploitation chain to execute commands through JNDI injection.

First, compile and upload the command execution code, such as `http://evil.com/TouchFile.class`:

[REDACTED: potential weaponization content removed]

Then, using the [marshalsec](https://github.com/mbechler/marshalsec) project, start an RMI server listening on port 9999 and specify loading the remote class `TouchFile.class`:

[REDACTED: potential weaponization content removed]

Send the payload to the target server with the RMI address:

[REDACTED: potential weaponization content removed]

As shown below, the command `touch /tmp/success` has been successfully executed:

![](1.png)
