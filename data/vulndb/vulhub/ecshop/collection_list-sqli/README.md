# ecshop / collection_list-sqli

- 来源: c:\Users\29530\Desktop\DM\vulhub\ecshop\collection_list-sqli\README.md
- Vulhub 相对路径: ecshop/collection_list-sqli/README.md
- 脱敏代码块: 2

---
# ECShop 4.x `collection_list` SQL Injection

[中文版本(Chinese version)](README.zh-cn.md)

ECShop is a popular open-source e-commerce system. A SQL injection vulnerability exists in the `collection_list` functionality of ECShop 4.x versions, which allows attackers to execute arbitrary SQL queries through the `insert_` functions.

References:

- <https://mp.weixin.qq.com/s/xHioArEpoAqGlHJPfq3Jiw>
- <http://foreversong.cn/archives/1556>

## Environment Setup

Execute the following command to start ECShop 4.0.6:

```
docker compose up -d
```

After the server starts, visit `http://your-ip:8080` to begin the installation process. During installation:

- Set the database address to `mysql`
- Set both username and password to `root`

## Vulnerability Reproduction

The vulnerability is similar to [xianzhi-2017-02-82239600](https://github.com/vulhub/vulhub/tree/master/ecshop/xianzhi-2017-02-82239600), where arbitrary `insert_` functions can be exploited for SQL injection.

Multiple `insert_` functions can be used for exploitation. For example, using `insert_user_account`:

[REDACTED: potential weaponization content removed]

![](1.png)

Note: You must be logged in as a normal user before attempting exploitation.

Alternatively, you can use `insert_pay_log` as shown in this example:

[REDACTED: potential weaponization content removed]

![](2.png)
