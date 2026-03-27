# solr / Remote-Streaming-Fileread

- 来源: c:\Users\29530\Desktop\DM\vulhub\solr\Remote-Streaming-Fileread\README.md
- Vulhub 相对路径: solr/Remote-Streaming-Fileread/README.md
- 脱敏代码块: 2

---
# Apache Solr RemoteStreaming Arbitrary File Reading and SSRF

[中文版本(Chinese version)](README.zh-cn.md)

Apache Solr is an open-source search server. When Apache Solr does not have authentication enabled, an attacker can craft a request to enable specific configurations, potentially leading to Server-Side Request Forgery (SSRF) or arbitrary file reading vulnerabilities.

References:

- <https://mp.weixin.qq.com/s/3WuWUGO61gM0dBpwqTfenQ>

## Environment Setup

Execute the following command to start an Apache Solr 8.8.1 server:

```
docker compose up -d
```

After the server starts, you can access the Apache Solr management interface at `http://your-ip:8983/`.

## Vulnerability Reproduction

First, visit `http://your-ip:8983/solr/admin/cores?indexInfo=false&wt=json` to extract the database name:

![](1.png)

Send the following request to modify the configuration of the `demo` core and enable `RemoteStreaming`:

[REDACTED: potential weaponization content removed]

![](2.png)

Then, you can read arbitrary files through the `stream.url` parameter:

[REDACTED: potential weaponization content removed]

![](3.png)
