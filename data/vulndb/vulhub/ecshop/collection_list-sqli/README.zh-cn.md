# ecshop / collection_list-sqli

- 来源: c:\Users\29530\Desktop\DM\vulhub\ecshop\collection_list-sqli\README.zh-cn.md
- Vulhub 相对路径: ecshop/collection_list-sqli/README.zh-cn.md
- 脱敏代码块: 2

---
# ECShop 4.x Collection List SQL注入漏洞

ECShop是一个流行的开源电子商务系统。在ECShop 4.x版本的`collection_list`功能中存在SQL注入漏洞，攻击者可以通过`insert_`函数执行任意SQL查询。

参考链接：

- <https://mp.weixin.qq.com/s/xHioArEpoAqGlHJPfq3Jiw>
- <http://foreversong.cn/archives/1556>

## 环境搭建

执行如下命令启动ECShop 4.0.6：

```
docker compose up -d
```

环境启动后，访问`http://your-ip:8080`进入安装向导。在安装过程中：

- 将数据库地址设置为`mysql`
- 将数据库用户名和密码都设置为`root`

## 漏洞复现

此漏洞原理与[xianzhi-2017-02-82239600](https://github.com/vulhub/vulhub/tree/master/ecshop/xianzhi-2017-02-82239600)类似，可以利用任意`insert_`函数进行SQL注入。

有多个`insert_`函数可以用于漏洞利用。例如，使用`insert_user_account`：

[REDACTED: potential weaponization content removed]

![](1.png)

注意：在尝试漏洞利用之前，必须先以普通用户身份登录。

另外，你也可以使用`insert_pay_log`，如下例所示：

[REDACTED: potential weaponization content removed]

![](2.png)
