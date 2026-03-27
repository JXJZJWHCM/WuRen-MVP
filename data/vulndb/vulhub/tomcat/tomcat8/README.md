# tomcat / tomcat8

- 来源: c:\Users\29530\Desktop\DM\vulhub\tomcat\tomcat8\README.md
- Vulhub 相对路径: tomcat/tomcat8/README.md
- 脱敏代码块: 1

---
# Tomcat7+ Weak Password && Backend Getshell Vulnerability

[中文版本(Chinese version)](README.zh-cn.md)

Tomcat version: 8.0

## Introduction

Tomcat supports deploying the war files through backend, so we can directly place the webshell into the web directory. In order to access the backend, permissions are needed.

Permissions of Tomcat7+ are as follows:

 - manager（backend management）
   - manager-gui (permission of html pages)
   - manager-status (permission to view status)
   - manager-script (permission of text interface and the status permission)
   - manager-jmx (jmx permissions, and status permissions)
 - host-manager (virtual host management)
   - admin-gui (permission of html pages)
   - admin-script (permission of text interface)

To know more about the permissions, please read: http://tomcat.apache.org/tomcat-8.5-doc/manager-howto.html

Permissions of users are configured in the ` conf/tomcat-users.xml ` file:

[REDACTED: potential weaponization content removed]

As can be seen, user tomcat has all of the permissions mentioned above, and the password is `tomcat`.

There are no users by default in Tomcat8 through normal installation, and the manager page only allows local IP to visit. Only if the administrator has manually modified these properties can we make an attack.

## Environment and Test

Just run：

```
docker compose up -d
```

Open the tomcat management page `http://your-ip:8080/manager/html`，enter the weak password `tomcat:tomcat`，then access the backend：

![](1.png)

Upload war package and then get shell directly.
