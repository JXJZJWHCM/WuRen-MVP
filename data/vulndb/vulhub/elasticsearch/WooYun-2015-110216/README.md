# elasticsearch / WooYun-2015-110216

- 来源: c:\Users\29530\Desktop\DM\vulhub\elasticsearch\WooYun-2015-110216\README.md
- Vulhub 相对路径: elasticsearch/WooYun-2015-110216/README.md
- CVE: CVE-2015-5531
- 脱敏代码块: 3

---
# ElasticSearch Arbitrary File Upload (WooYun-2015-110216)

[中文版本(Chinese version)](README.zh-cn.md)

ElasticSearch is a distributed, RESTful search and analytics engine.

A vulnerability in ElasticSearch's backup functionality allows attackers to write arbitrary files to the filesystem, potentially leading to webshell upload when combined with other web services.

ElasticSearch includes a data backup feature that allows users to specify a path where backup data will be stored. Both the path and file names are controllable by the user.

If other web services (like Tomcat, PHP, etc.) are running on the same system, an attacker can exploit ElasticSearch's backup functionality to write a webshell to a web-accessible directory.

Similar to [CVE-2015-5531](../CVE-2015-5531/), this vulnerability is related to the backup repository functionality. In ElasticSearch versions after 1.5.1, the root path of backup repositories is restricted to the `path.repo` configuration option. If administrators don't configure this option, the backup functionality is disabled by default. Even if configured, writing a webshell is only possible if the web root is within the configured directory.

References:

- <http://cb.drops.wiki/bugs/wooyun-2015-0110216.html>

## Environment Setup

Execute the following commands to start a ElasticSearch server 1.5.1, and a Tomcat server is running on the same container:

```
docker compose up -d
```

After the environment starts, you can access the ElasticSearch server at `http://your-ip:9200`, and the Tomcat server at `http://your-ip:8080`.

Tomcat is installed in `/usr/local/tomcat` with its web directory at `/usr/local/tomcat/webapps`. ElasticSearch is installed in `/usr/share/elasticsearch`.

## Vulnerability Reproduction

Our goal is to use ElasticSearch to write a webshell into `/usr/local/tomcat/webapps`.

First, create a malicious index document:

[REDACTED: potential weaponization content removed]

Then create a malicious repository. The `location` value is the path where we want to write our file.

> Note: The Repositories path is interesting because it can write to any accessible location, and if the path doesn't exist, it will be created automatically. This means you can create arbitrary directories using the file access protocol. Here we point the path to Tomcat's web deployment directory because Tomcat will automatically create a new application when a folder is created in this directory (if the filename is wwwroot, the created application name will be wwwroot).

[REDACTED: potential weaponization content removed]

Verify and create the repository:

[REDACTED: potential weaponization content removed]

Done!

Access `http://127.0.0.1:8080/wwwroot/indices/yz.jsp/snapshot-yz.jsp` to find our uploaded webshell.

This shell allows writing arbitrary strings to test.jsp in the wwwroot directory. For example: `http://127.0.0.1:8080/wwwroot/indices/yz.jsp/snapshot-yz.jsp?f=success`. Then accessing /wwwroot/test.jsp will show "success":

![](1.png)
