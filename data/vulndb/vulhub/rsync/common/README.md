# rsync / common

- 来源: c:\Users\29530\Desktop\DM\vulhub\rsync\common\README.md
- Vulhub 相对路径: rsync/common/README.md
- 脱敏代码块: 4

---
# Rsync Unauthorized Access

[中文版本(Chinese version)](README.zh-cn.md)

Rsync is a data backup tool for Linux that supports remote file transfer through rsync protocol and ssh protocol. The rsync protocol listens on port 873 by default. If the target has enabled rsync service and hasn't configured ACL or access password, we can read and write files on the target server.

## Environment Setup

Compile and run the rsync server:

```
docker compose build
docker compose up -d
```

After the environment starts, we can access it using the rsync command:

[REDACTED: potential weaponization content removed]

You can view the list of module names:

![](1.png)

## Vulnerability Reproduction

As shown above, there is a src module. Let's list the files under this module:

[REDACTED: potential weaponization content removed]

![](2.png)

This is a Linux root directory, and we can download any file:

[REDACTED: potential weaponization content removed]

Or write any file:

[REDACTED: potential weaponization content removed]

We wrote a cron task and successfully got a reverse shell:

![](3.png)
