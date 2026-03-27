# ecshop / xianzhi-2017-02-82239600

- 来源: c:\Users\29530\Desktop\DM\vulhub\ecshop\xianzhi-2017-02-82239600\README.md
- Vulhub 相对路径: ecshop/xianzhi-2017-02-82239600/README.md
- 脱敏代码块: 2

---
# ECShop 2.x/3.x SQL Injection / Remote Code Execution Vulnerability

[中文版本(Chinese version)](README.zh-cn.md)

ECShop is a B2C independent shop system for companies and individuals to quickly build personalized online store. This system is a cross-platform open source program based on PHP language and MYSQL database architecture.

In 2017 and previous versions, there was a SQL injection vulnerability that could inject payload and eventually lead to code execution vulnerabilities. The latest version of 3.6.0 has fixed the vulnerability, and vulhub uses its latest version 2.7.3 and 3.6.0 non-latest version versions to reproduce the vulnerability.

Reference link:

- https://paper.seebug.org/691/

## Environment setup

Run the following commands to start environment

```
docker compose up -d
```

After the environment start, visit `http://your-ip:8080`, you will see the 2.7.3 installation page. Visit `http://your-ip:8081`, you will see the 3.6.0 installation page.

Install both of them, mysql address is `mysql`, mysql account and password are `root`, the database name is free to fill in, but the database names of 2.7.3 and 3.6.0 can not be the same.

As the picture shows:

![](0.png)

## Exploit

There is a script that can generate POC for 2.x and 3.x:

[REDACTED: potential weaponization content removed]

Put POC in the HTTP-Referer:

[REDACTED: potential weaponization content removed]

Result of 2.x:

![](1.png)

Result of 3.x:

![](2.png)
