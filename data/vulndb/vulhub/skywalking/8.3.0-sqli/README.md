# skywalking / 8.3.0-sqli

- 来源: c:\Users\29530\Desktop\DM\vulhub\skywalking\8.3.0-sqli\README.md
- Vulhub 相对路径: skywalking/8.3.0-sqli/README.md
- 脱敏代码块: 1

---
# Apache Skywalking 8.3.0 SQL Injection Vulnerability

[中文版本(Chinese version)](README.zh-cn.md)

Application performance monitor tool for distributed systems, especially designed for microservices, cloud native and container-based (Docker, Kubernetes, Mesos) architectures.

In GraphQL interfaces of Apache Skywalking 8.3.0 and previous, there is a H2 Database SQL injection vulnerability.

Reference link:

- https://mp.weixin.qq.com/s/hB-r523_4cM0jZMBOt6Vhw
- https://github.com/apache/skywalking/commit/0bd81495965d801315dd7417bb17333ae0eccf3b#diff-ec87a1cdf66cdb37574d9eafd4d72d99ed94a38c4a8ff2aa9c7b8daeff502a2c

## Vulnerability environment

Execute the following command to start an Apache Skywalking 8.3.0:

```
docker compose up -d
```

After the environment is started, visit `http://your-ip:8080` to view the Skywalking page.

## POC

I use GraphiQL's desktop app to send the following GraphQL query:

![](1.png)

It can be seen that the SQL statement has raised error, and the value of the `metricName` parameter has been injected ​​after `from`.

The HTTP request of this GraphQL query is:

[REDACTED: potential weaponization content removed]

For more in-depth exploit, you can research by yourself, and welcome to submit PR to us.
