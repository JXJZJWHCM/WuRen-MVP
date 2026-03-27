# struts2 / s2-059

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-059\README.zh-cn.md
- Vulhub 相对路径: struts2/s2-059/README.zh-cn.md
- CVE: CVE-2019-0230, CVE-2018-11776
- 脱敏代码块: 1

---
# Struts2 S2-059 远程代码执行漏洞(CVE-2019-0230)

Apache Struts框架, 会对某些特定的标签的属性值，比如id属性进行二次解析，所以攻击者可以传递将在呈现标签属性时再次解析的OGNL表达式，造成OGNL表达式注入。从而可能造成远程执行代码。

影响版本: Struts 2.0.0 - Struts 2.5.20

参考链接：

- https://cwiki.apache.org/confluence/display/WW/S2-059
- https://securitylab.github.com/research/ognl-apache-struts-exploit-CVE-2018-11776

## 漏洞环境

启动 Struts 2.5.16环境:

```
docker compose up -d
```

启动环境之后访问`http://your-ip:8080/?id=1` 就可以看到测试界面

## 漏洞复现

访问 `http://your-ip:8080/?id=%25%7B233*233%7D`，可以发现233*233的结果被解析到了id属性中：

![1.png](1.png)

《[OGNL Apache Struts exploit: Weaponizing a sandbox bypass (CVE-2018-11776)](https://securitylab.github.com/research/ognl-apache-struts-exploit-CVE-2018-11776)》给出了绕过struts2.5.16版本的沙盒的poc，利用这个poc可以达到执行系统命令。

通过如下Python脚本复现漏洞：

[REDACTED: potential weaponization content removed]

执行poc之后，进入容器发现`touch /tmp/success`已成功执行。

![2.png](2.png)
