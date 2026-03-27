# struts2 / s2-046

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-046\README.md
- Vulhub 相对路径: struts2/s2-046/README.md
- CVE: CVE-2017-5638
- 脱敏代码块: 1

---
# S2-046 Remote Code Execution Vulnerablity（CVE-2017-5638）

[中文版本(Chinese version)](README.zh-cn.md)

Affected Version: Struts 2.3.5 - Struts 2.3.31, Struts 2.5 - Struts 2.5.10

References:

 - https://cwiki.apache.org/confluence/display/WW/S2-046
 - https://xz.aliyun.com/t/221

## Setup

Execute the following command to start the Struts2 2.3.30：

```
docker compose up -d
```

After the container is running, visit `http://your-ip:8080` that you can see an example of the upload page.

## Exploitation

As same as S2-045, S2-046 is also the OGNL injection but occurs at filename field of the upload request, and a NUL byte is needed to split payload and the remaining strings.

A simple Python POC for Verifying the vulnerability:

[REDACTED: potential weaponization content removed]

`233*233` has been successfully executed:

![](1.png)
