# scrapy / scrapyd-unacc

- 来源: c:\Users\29530\Desktop\DM\vulhub\scrapy\scrapyd-unacc\README.md
- Vulhub 相对路径: scrapy/scrapyd-unacc/README.md
- 脱敏代码块: 2

---
# Scrapyd Pre-Auth Remote Code Execution

[中文版本(Chinese version)](README.zh-cn.md)

Scrapyd is an application for deploying and running Scrapy spiders. It enables users to deploy (upload) projects and control their spiders using a JSON API.

References: <https://www.leavesongs.com/PENETRATION/attack-scrapy.html>

## Start server

Execution the following command to start a scrapyd server:

```bash
docker compose up -d
```

After scrapyd is deployed, the server is listening on `http://your-ip:6800`.

## Reproduce

Build a evil egg archive:

[REDACTED: potential weaponization content removed]

Upload evil egg to the scrapyd server:

[REDACTED: potential weaponization content removed]

reverse shell is available:

![](1.png)
