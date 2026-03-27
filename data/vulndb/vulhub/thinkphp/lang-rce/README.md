# thinkphp / lang-rce

- 来源: c:\Users\29530\Desktop\DM\vulhub\thinkphp\lang-rce\README.md
- Vulhub 相对路径: thinkphp/lang-rce/README.md
- 脱敏代码块: 2

---
# ThinkPHP Lang Local File Inclusion

[中文版本(Chinese version)](README.zh-cn.md)

ThinkPHP is an extremely widely used PHP development framework in China. In the version prior to 6.0.13, a local restricted file inclusion issue exists in `lang` parameter if the developer enable multiple language pack.

Although this issue is only allowed to include ".php" file, the attacker is still able to use the "pearcmd.php" to write arbitrary file and execute code in the server.

References:

- <https://tttang.com/archive/1865/>
- <https://www.leavesongs.com/PENETRATION/docker-php-include-getshell.html#0x06-pearcmdphp> (about the "pearcmd.php trick")

## Vulnerability Environment

Execute following command to start a server that is developed by ThinkPHP v6.0.12:

```
docker compose up -d
```

After the server is started, browse the `http://your-ip:8080` to see the default welcome page of ThinkPHP.

## Exploit

Firstly, because the multiple language feature is not enabled by default, you can try to include the `public/index.php` to determine whether the vulnerability exists:

[REDACTED: potential weaponization content removed]

![](1.png)

The vulnerability exists if the server crashed and a 500 error response comes back.

Then, try to write data through "/usr/local/lib/php/pearcmd.php":

[REDACTED: potential weaponization content removed]

If the server response the output of pearcmd, which means the exploit is successful:

![](2.png)

As you can see, the `shell.php` is written in root directory of web:

![](3.png)
