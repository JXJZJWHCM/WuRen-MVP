# php / 8.1-backdoor

- 来源: c:\Users\29530\Desktop\DM\vulhub\php\8.1-backdoor\README.md
- Vulhub 相对路径: php/8.1-backdoor/README.md
- 脱敏代码块: 1

---
# PHP 8.1.0-dev User-Agentt Backdoor Remote Code Execution

[中文版本(Chinese version)](README.zh-cn.md)

PHP version 8.1.0-dev was implanted with a backdoor on March 28, 2021, but the backdoor was quickly discovered and removed. When this backdoor is present on a server, an attacker can execute arbitrary code by sending a **User-Agentt** header.

References:

- https://news-web.php.net/php.internals/113838
- https://github.com/php/php-src/commit/c730aa26bd52829a49f2ad284b181b7e82a68d7d
- https://github.com/php/php-src/commit/2b0f239b211c7544ebc7a4cd2c977a5b7a11ed8a

## Vulnerable Environment

Start a PHP 8.1-dev server with the backdoor.

```
docker compose up -d
```

After the environment is started, the service runs at ``http://your-ip:8080``.

## Vulnerability Reproduce

Send the following request to execute the code `var_dump(233*233);`:

[REDACTED: potential weaponization content removed]

![](1.png)
