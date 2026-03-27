# aj-report / CNVD-2024-15077

- 来源: c:\Users\29530\Desktop\DM\vulhub\aj-report\CNVD-2024-15077\README.md
- Vulhub 相对路径: aj-report/CNVD-2024-15077/README.md
- 脱敏代码块: 1

---
# AJ-Report Authentication Bypass and Remote Code Execution (CNVD-2024-15077)

[中文版本(Chinese version)](README.zh-cn.md)

AJ-Report is an open source BI platform. In the version 1.4.0 and before, there is a authentication bypass issue and the attacker is able to perform arbitrary code execution through the issue.

References:

- <https://xz.aliyun.com/t/14460>
- <https://github.com/wy876/POC/blob/main/AJ-Report%E5%BC%80%E6%BA%90%E6%95%B0%E6%8D%AE%E5%A4%A7%E5%B1%8F%E5%AD%98%E5%9C%A8%E8%BF%9C%E7%A8%8B%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E.md>

## Vulnerable environment

Execute following command to start a AJ-Report server 1.4.0:

```
docker compose up -d
```

After the server is started, you can see the login page of AJ-Report through `http://your-ip:9095`.

## Exploit

To exploit the issue by following request:

[REDACTED: potential weaponization content removed]

As you can see, `id` command is executed successfully:

![](1.png)
