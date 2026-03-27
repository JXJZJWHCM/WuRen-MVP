# weblogic / ssrf

- 来源: c:\Users\29530\Desktop\DM\vulhub\weblogic\ssrf\README.md
- Vulhub 相对路径: weblogic/ssrf/README.md
- 脱敏代码块: 4

---
# Weblogic UDDI Explorer Server-Side Request Forgery (SSRF)

[中文版本(Chinese version)](README.zh-cn.md)

Oracle WebLogic Server is a Java-based enterprise application server. A Server-Side Request Forgery (SSRF) vulnerability exists in WebLogic's UDDI Explorer application, which allows attackers to send arbitrary HTTP requests through the server, potentially leading to internal network scanning or attacks against vulnerable internal services like Redis.

References:

- <https://github.com/vulhub/vulhub/tree/master/weblogic/ssrf>
- <https://foxglovesecurity.com/2015/11/06/what-is-server-side-request-forgery-ssrf/>
- <https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf>

## Environment Setup

Execute the following command to start a WebLogic server:

```
docker compose up -d
```

After the server starts, visit `http://your-ip:7001/uddiexplorer/` to access the UDDI Explorer application. No authentication is required.

## Vulnerability Reproduction

The SSRF vulnerability exists in the SearchPublicRegistries.jsp page. Using Burp Suite, we can send a request to `http://your-ip:7001/uddiexplorer/SearchPublicRegistries.jsp` to test this vulnerability.

First, we can try accessing an internal service like `http://127.0.0.1:7001`:

[REDACTED: potential weaponization content removed]

When accessing an available port, you will receive an error response with a status code. For non-HTTP protocols, you'll get a "did not have a valid SOAP content-type" error.

![](1.png)

When accessing a non-existent port, the response will be "could not connect over HTTP to server".

![](2.png)

By analyzing these different error messages, we can effectively scan the internal network.

### Redis Shell Exploitation

A notable characteristic of WebLogic's SSRF vulnerability is that despite being a GET request, we can inject newline characters using `%0a%0d`. Since services like Redis use newlines to separate commands, we can leverage this to attack internal Redis servers.

First, we scan the internal network for Redis servers (Docker networks typically use 172.* subnets) and find that `172.18.0.2:6379` is accessible:

![](3.png)

We can then send three Redis commands to write a shell script into `/etc/crontab`:

[REDACTED: potential weaponization content removed]

URL encode these commands:

[REDACTED: potential weaponization content removed]

Send the encoded payload through the SSRF vulnerability:

[REDACTED: potential weaponization content removed]

![](4.png)

Successfully obtaining a reverse shell:

![](5.png)

Note that there are several locations where cron jobs can be exploited:

- `/etc/crontab` (default system crontab)
- `/etc/cron.d/*` (system cron job directory)
- `/var/spool/cron/root` (CentOS root user cron file)
- `/var/spool/cron/crontabs/root` (Debian root user cron file)
