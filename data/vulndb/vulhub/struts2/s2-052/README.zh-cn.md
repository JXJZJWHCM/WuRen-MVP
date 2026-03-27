# struts2 / s2-052

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-052\README.zh-cn.md
- Vulhub 相对路径: struts2/s2-052/README.zh-cn.md
- 脱敏代码块: 3

---
# S2-052 远程代码执行漏洞

影响版本: Struts 2.1.2 - Struts 2.3.33, Struts 2.5 - Struts 2.5.12

漏洞详情:

 - http://struts.apache.org/docs/s2-052.html
 - https://yq.aliyun.com/articles/197926

## 测试环境搭建

```
docker compose up -d
```

## 漏洞说明

Struts2-Rest-Plugin是让Struts2能够实现Restful API的一个插件，其根据Content-Type或URI扩展名来判断用户传入的数据包类型，有如下映射表：

扩展名 | Content-Type | 解析方法
---- | ---- | ----
xml | application/xml | xstream
json | application/json | jsonlib或jackson(可选)
xhtml | application/xhtml+xml | 无
无 | application/x-www-form-urlencoded | 无
无 | multipart/form-data | 无

jsonlib无法引入任意对象，而xstream在默认情况下是可以引入任意对象的（针对1.5.x以前的版本），方法就是直接通过xml的tag name指定需要实例化的类名：

[REDACTED: potential weaponization content removed]

所以，我们可以通过反序列化引入任意类造成远程命令执行漏洞，只需要找到一个在Struts2库中适用的gedget。

## 漏洞复现

启动环境后，访问`http://your-ip:8080/orders.xhtml`即可看到showcase页面。由于rest-plugin会根据URI扩展名或Content-Type来判断解析方法，所以我们只需要修改orders.xhtml为orders.xml或修改Content-Type头为application/xml，即可在Body中传递XML数据。

所以，最后发送的数据包为：

[REDACTED: potential weaponization content removed]

以上数据包成功执行的话，会在docker容器内创建文件`/tmp/success`，执行`docker compose exec struts2 ls /tmp/`即可看到。

此外，我们还可以下载一个jspx的webshell：

![](01.png)

还有一些更简单的利用方法，就不在此赘述了。

## 漏洞修复

struts2.5.13中，按照xstream给出的缓解措施（ http://x-stream.github.io/security.html ），增加了反序列化时的白名单：

[REDACTED: potential weaponization content removed]

但此时可能会影响以前代码的业务逻辑，所以谨慎升级，也没有特别好的办法，就是逐一排除老代码，去掉不在白名单中的类。
