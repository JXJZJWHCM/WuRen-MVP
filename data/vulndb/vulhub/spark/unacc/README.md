# spark / unacc

- 来源: c:\Users\29530\Desktop\DM\vulhub\spark\unacc\README.md
- Vulhub 相对路径: spark/unacc/README.md
- 脱敏代码块: 3

---
# Apache Spark Unauthorized Access Leads to Remote Code Execution

[中文版本(Chinese version)](README.zh-cn.md)

Apache Spark is a cluster computing system that allows users to submit applications to the management node for cluster execution. If the management node has not enabled ACL (Access Control List), it becomes possible to execute arbitrary code in the cluster.

Reference links:

 - https://weibo.com/ttarticle/p/show?id=2309404187794313453016
 - https://xz.aliyun.com/t/2490

## Vulnerability Environment

Execute the following command to start an Apache Spark cluster in standalone mode, which includes one master and one slave:

```
docker compose up -d
```

After the environment starts, visit `http://your-ip:8080` to access the master's management page, and `http://your-ip:8081` to access the slave's management page.

## Vulnerability Reproduce

The essence of this vulnerability is that unauthorized users can submit an application to the management node, where this application is actually malicious code.

There are two ways to submit applications:

1. Using REST API
2. Using submissions gateway (integrated in port 7077)

The application can be written in Java or Python. Here's a simple example class (from reference link 1):

[REDACTED: potential weaponization content removed]

Compile it into a JAR file and host it on any HTTP or FTP server, for example: `https://github.com/aRe00t/rce-over-spark/raw/master/Exploit.jar`.

### Submitting Application via REST API

In standalone mode, the master starts an HTTP server on port 6066. We can submit a REST-formatted API request to this port:

[REDACTED: potential weaponization content removed]

Here, `spark.jars` is the compiled application, mainClass is the class to run, and appArgs are the parameters passed to the application.

![](1.png)

The response will contain a submissionId. You can then view the execution results by visiting `http://your-ip:8081/logPage/?driverId={submissionId}&logType=stdout`:

![](2.png)

Note: While the application is submitted to the master, the results are viewed in the slave that actually executes the application (default port 8081). In real-world scenarios, there might be multiple slaves.

### Using the Submissions Gateway

If port 6066 is inaccessible or has access controls, we can use the master's main port 7077 to submit applications.

This can be done using Apache Spark's built-in script `bin/spark-submit`:

[REDACTED: potential weaponization content removed]

If the master parameter you specify is a REST server, this script will first try to submit the application using the REST API; if it's not a REST server, it will fall back to using the submission gateway.

The results can be viewed in the same way as described above.
