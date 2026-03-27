# phpmyadmin / WooYun-2016-199433

- 来源: c:\Users\29530\Desktop\DM\vulhub\phpmyadmin\WooYun-2016-199433\README.md
- Vulhub 相对路径: phpmyadmin/WooYun-2016-199433/README.md
- 脱敏代码块: 1

---
# Phpmyadmin Scripts/setup.php Deserialization Vulnerability (WooYun-2016-199433)

[中文版本(Chinese version)](README.zh-cn.md)

Affected version: 2.x

## Setup

Run the following command to start phpmyadmin:

```
docker compose up -d
```

Visit `http://your-ip:8080` and you will see the phpmyadmin home page. Because there is no connection to the database, we will get an error. But this vulnerability is not related to the database, so just ignore.

## Exploit

Send the following package to read `/etc/passwd`:

[REDACTED: potential weaponization content removed]

![](1.png)
