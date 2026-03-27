# MITM 插件：SSRF 公网出网检测 | Yak Program Language

- 来源: https://www.yaklang.com/products/Plugin-repository/best-practice/mitm-plug/
- 抓取时间: 2026-02-06T07:03:46Z

---
## 依赖条件： #

- 需要配置 yak bridge 公网部署方案详情见 https://github.com/yaklang/yak-bridge-docker
- 使用 Yakit 配置好公网镜像

## SSRF 检测原理： #

### 触发条件： #

- 流经 MITM 的流量，应该过滤一下参数，疑似 SSRF 参数应该参与测试
- 参数条件： 参数名直接相关 redirect / url / url_callback / webhook  / target .... 等 参数值为 http(s?):// 开头的，可以直接替换成我们想要的 SSRF 目标

- 参数名直接相关 redirect / url / url_callback / webhook  / target .... 等
- 参数值为 http(s?):// 开头的，可以直接替换成我们想要的 SSRF 目标

### yaklang.io 公网镜像反连体系 #

- 基础知识： https://www.yaklang.io/products/professional/yakit-in-practice-reverse
- 当 yak 镜像服务器映射在公网的时候，任何连入镜像服务器的请求将会被记录下来，如果携带 Token，也会被记录并且直接被对应到 SSRF 的漏洞中。
- 上述经过替换的携带 SSRF Payload 的请求触发了请求，将会直接在数据库中记录下详细的请求反连情况，对应的 Token 也会对应到漏洞上。

## 案例： #

### 搭建靶场 #

我们在本地构建一个 SSRF 的靶站，代码非常简单

当我们运行我们的靶站在 http://127.0.0.1:8084/ssrf?url=http://www.baidu.com 的时候，浏览器返回内容如下：

### 测试过程 #

我们打开 Yakit 的中间人劫持平台

勾选“插件自动加载”，选择想要的插件启动劫持

我们构建一个请求，以 MITM 设置为代理：

```
rsp
,
 err 
:=
 http
.
Get
(
    
`http://127.0.0.1:8084/ssrf?url=https://baidu.com`
,
 
    http
.
proxy
(
"http://127.0.0.1:8083"
)
,
)
die
(
err
)


http
.
show
(
rsp
)
```

当我们执行该请求的时候，MITM 劫持平台将会收到该请求，并且在请求流经过程中，会镜像一份出来到 SSRF HTTP Public 插件，SSRF 插件执行之后将会在右边输出结果：

当我们打开反连之后：

## 核心原理 #

### 核心代码 #

其实大家观察上述内容，发现我们引用一个 SSRF 插件即可解决这个问题，那么这个插件是如何编写并且发挥作用的呢？

我们在这里可以看到插件源码，接下来就插件源码的核心原理给大家做简要描述

代码的结构非常非常简单：

我们关注参数列表规则和镜像流量函数：

### 核心流程 #

我们发现检测的步骤其实可以非常简单对应到我们的检测思路中。如果大家无法很容易理解代码中的内容，我总结了一个基本的测试流程。

## 扩展与Bypass： #

当然熟悉的同学，很容易发现，插件的代码并不完美，仍然有许多需要改进的地方：比如

- Host 混淆技术（与 127.0.0.1混淆来 bypass 各种检查）
- 使用 schema 混淆 bypass 检查
- 非标准位置的测试：JSON 中的 SSRF 检测
- ....

我们发现如果需要覆盖上面内容，插件仍然有很大的进步和发展空间，但是相应的发包量就会变大。
如果需要找到一个均衡的点，则需要更细节的控制，完善脚本的检测逻辑。

- 依赖条件：
- SSRF 检测原理： 触发条件： yaklang.io 公网镜像反连体系
- 案例： 搭建靶场 测试过程
- 核心原理 核心代码 核心流程
- 扩展与Bypass：

- 触发条件：
- yaklang.io 公网镜像反连体系

- 搭建靶场
- 测试过程

- 核心代码
- 核心流程
