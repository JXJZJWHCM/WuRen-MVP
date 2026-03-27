# v2board / 1.6-privilege-escalation

- 来源: c:\Users\29530\Desktop\DM\vulhub\v2board\1.6-privilege-escalation\README.md
- Vulhub 相对路径: v2board/1.6-privilege-escalation/README.md
- 脱敏代码块: 2

---
# V2board 1.6.1 Privilege Escalation

[中文版本(Chinese version)](README.zh-cn.md)

V2board is a multiple proxy protocol manage panel application interface. In the version of 1.6.1, it is introduced a redis cache mechanism to save the user session.

Since there is no distinction between administrator and normal user in the cache layer, resulting in normal users being able to use their token to access the administrator interface.

References:

- <https://github.com/v2board/v2board/commit/5976bcc65a61f7942ed4074b9274236d9d55d5f0>

## Vulnerable Environment

Execute following command to start the V2board 1.6.1:

```
docker compose up -d
```

After the server is started, browse the `http://localhost:8080` to see the default login page of the V2board.

## Exploit

First of all, you have to register a normal user.

Then, replace the email and password with your own data and login:

[REDACTED: potential weaponization content removed]

The server will response a "auth_data" to you:

![](1.png)

Copy it and end the following request with your "auth_data":

[REDACTED: potential weaponization content removed]

![](2.png)

This step is to let server save your authorization to Redis cache.

Finally, you are able to simply call all admin API with this authorization, for example `http://your-ip:8080/api/v1/admin/user/fetch`:

![](3.png)
