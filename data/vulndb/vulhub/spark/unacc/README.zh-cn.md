# spark / unacc

- 来源: c:\Users\29530\Desktop\DM\vulhub\spark\unacc\README.zh-cn.md
- Vulhub 相对路径: spark/unacc/README.zh-cn.md
- 脱敏代码块: 3

---
# Apache Spark 未授权访问导致远程代码执行

Apache Spark是一款集群计算系统，其支持用户向管理节点提交应用，并分发给集群执行。如果管理节点未启动ACL（访问控制），我们将可以在集群中执行任意代码。

参考链接：

 - https://weibo.com/ttarticle/p/show?id=2309404187794313453016
 - https://xz.aliyun.com/t/2490

## 漏洞环境

执行如下命令，将以standalone模式启动一个Apache Spark集群，集群里有一个master与一个slave：

```
docker compose up -d
```

环境启动后，访问`http://your-ip:8080`即可看到master的管理页面，访问`http://your-ip:8081`即可看到slave的管理页面。

## 漏洞利用

该漏洞本质是未授权的用户可以向管理节点提交一个应用，这个应用实际上是恶意代码。

提交方式有两种：

1. 利用REST API
2. 利用submissions网关（集成在7077端口中）

应用可以是Java或Python，就是一个最简单的类，如（参考链接1）：

[REDACTED: potential weaponization content removed]

将其编译成JAR，放在任意一个HTTP或FTP上，如`https://github.com/aRe00t/rce-over-spark/raw/master/Exploit.jar`。

### 用REST API方式提交应用

standalone模式下，master将在6066端口启动一个HTTP服务器，我们向这个端口提交REST格式的API：

[REDACTED: potential weaponization content removed]

其中，`spark.jars`即是编译好的应用，mainClass是待运行的类，appArgs是传给应用的参数。

![](1.png)

返回的包中有submissionId，然后访问`http://your-ip:8081/logPage/?driverId={submissionId}&logType=stdout`，即可查看执行结果：

![](2.png)

注意，提交应用是在master中，查看结果是在具体执行这个应用的slave里（默认8081端口）。实战中，由于slave可能有多个。

### 利用submissions网关

如果6066端口不能访问，或做了权限控制，我们可以利用master的主端口7077，来提交应用。

方法是利用Apache Spark自带的脚本`bin/spark-submit`：

[REDACTED: potential weaponization content removed]

如果你指定的master参数是rest服务器，这个脚本会先尝试使用rest api来提交应用；如果发现不是rest服务器，则会降级到使用submission gateway来提交应用。

查看结果的方式与前面一致。
