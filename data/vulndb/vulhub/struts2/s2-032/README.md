# struts2 / s2-032

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-032\README.md
- Vulhub 相对路径: struts2/s2-032/README.md
- CVE: CVE-2016-3081
- 脱敏代码块: 1

---
# S2-032 Remote Code Execution Vulnerablity（CVE-2016-3081）

[中文版本(Chinese version)](README.zh-cn.md)

Affected Version: Struts 2.3.20 - Struts Struts 2.3.28 (except 2.3.20.3 and 2.3.24.3)

References:

 - https://cwiki.apache.org/confluence/display/WW/S2-032
 - https://www.cnblogs.com/mrchang/p/6501428.html

## Setup

Execute the following command to start the Struts2 2.3.28：

```
docker compose up -d
```

After the container is running, visit `http://your-ip:8080` that you can see an example page.

## Exploitation

There’s a feature embedded in Struts 2 that lets the "!" (bang) character invoke a method other than execute. It is called “Dynamic Method Invocation” aka DMI.

A simple way to use DMI is to provide HTTP parameters prefixed with `method:`. For example in the URL it could be `/category.action?method:create=foo`, the parameter value is ignored.

The method name of DMI will be evaluated by OGNL expression engine, which would cause the RCE vulnerability.

Visit following URL to trigger the `id` command:

[REDACTED: potential weaponization content removed]

![](1.png)
