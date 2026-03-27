# struts2 / s2-052

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-052\README.md
- Vulhub 相对路径: struts2/s2-052/README.md
- 脱敏代码块: 1

---
# S2-052 Remote Code Execution Vulnerablity

[中文版本(Chinese version)](README.zh-cn.md)

Affected Version: Struts 2.1.2 - Struts 2.3.33, Struts 2.5 - Struts 2.5.12

Details:

 - http://struts.apache.org/docs/s2-052.html
 - https://yq.aliyun.com/articles/197926

## Setup

```
docker compose up -d
```

## Exploit

After launching the environment, visit `http://your-ip:8080/orders.xhtml` to see the showcase page. We need modify the `orders.xhtml` to `order.xml` or modify the `Content-Type` header to `application/xml` to pass the XML data in the body.

So, the package is:

[REDACTED: potential weaponization content removed]

If the packet is executed, the file `/tmp/success` will be created in the docker container. We execute `docker compose exec struts2 ls /tmp/`, and we can see `success`.

In addition, we can also download a jspx webshell:

![](01.png)
