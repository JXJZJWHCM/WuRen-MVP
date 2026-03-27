# struts2 / s2-012

- 来源: c:\Users\29530\Desktop\DM\vulhub\struts2\s2-012\README.zh-cn.md
- Vulhub 相对路径: struts2/s2-012/README.zh-cn.md
- 脱敏代码块: 2

---
# S2-012 远程代码执行漏洞

影响版本: 2.1.0 - 2.3.13

漏洞详情: http://struts.apache.org/docs/s2-012.html

## 测试环境搭建

```
docker compose build
docker compose up -d
```

## 原理

如果在配置 Action 中 Result 时使用了重定向类型，并且还使用 ${param_name} 作为重定向变量，例如：

[REDACTED: potential weaponization content removed]

这里 UserAction 中定义有一个 name 变量，当触发 redirect 类型返回时，Struts2 获取使用 ${name} 获取其值，在这个过程中会对 name 参数的值执行 OGNL 表达式解析，从而可以插入任意 OGNL 表达式导致命令执行。

## Exp

可以直接祭出s2-001中的回显POC，因为这里是没有沙盒，也没有限制任何特殊字符（为什么？）。

[REDACTED: potential weaponization content removed]

发送请求，执行命令：

![](1.png)
