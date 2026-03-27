---
name: windows-enumeration
description: Windows 主机与常见企业服务枚举（SMB/RDP/WinRM/LDAP）
version: 1.0.0
---

# Windows 枚举（SMB/RDP/WinRM/LDAP）

## 适用场景
- 外网/内网扫描发现目标可能是 Windows（445/3389/5985/389 等）
- 已有一组可能的域账号/本地账号，需要快速确认可用面与权限边界
- 需要为后续漏洞验证、横向与 AD 路径分析准备“可复现证据”

## 操作前提（授权与边界）
- 仅在已授权的渗透测试/内部安全评估环境使用
- 优先低噪声：先枚举与确认，再做爆破/喷洒/利用

## 快速端口与服务确认（第一轮）
```bash
nmap -sS -sV -T4 -Pn -p 135,139,445,3389,389,636,3268,3269,5985,5986,88,464,53,80,443 <target>
```

常用脚本（Windows/AD 识别）：
```bash
nmap -Pn -T4 -p 445 --script smb-os-discovery,smb2-security-mode,smb2-time,smb-protocols <target>
nmap -Pn -T4 -p 3389 --script rdp-enum-encryption,rdp-ntlm-info <target>
nmap -Pn -T4 -p 389,636 --script ldap-rootdse <target>
```

## SMB（445/139）枚举

### 1) 匿名/空会话探测
```bash
smbclient -L //<target> -N
smbmap -H <target>
enum4linux-ng -A <target>
```

### 2) 有凭证时的确认（推荐）
```bash
crackmapexec smb <target> -u <user> -p '<pass>' --shares
crackmapexec smb <target> -u <user> -p '<pass>' --sessions
crackmapexec smb <target> -u <user> -p '<pass>' --users
```

RPC/域信息（有些环境需要域/本地上下文）：
```bash
rpcclient -U '<user>%<pass>' <target> -c 'srvinfo'
rpcclient -U '<user>%<pass>' <target> -c 'enumdomusers'
rpcclient -U '<user>%<pass>' <target> -c 'enumdomgroups'
```

### 3) 共享与读写验证（证据留存）
```bash
smbclient //<target>/<share> -U '<user>%<pass>' -c 'ls'
smbclient //<target>/<share> -U '<user>%<pass>' -c 'put test.txt test.txt; ls; rm test.txt'
```

## RDP（3389）确认与风险点
```bash
nmap -Pn -p 3389 --script rdp-ntlm-info,rdp-enum-encryption <target>
```
- 关注 NLA、TLS、域名/主机名、可能泄露的 AD 域信息
- 若允许交互验证（授权环境）：优先用已知凭证验证可登录性，再考虑口令策略与锁定阈值

## WinRM（5985/5986）
探测与认证验证：
```bash
crackmapexec winrm <target> -u <user> -p '<pass>'
```

常见利用面（仅授权）：若 WinRM 可用，后续可配合远程执行/横向（注意记录登录成功证据与最小化痕迹）。

## LDAP/AD 入口（389/636/3268）
```bash
nmap -Pn -p 389,636,3268,3269 --script ldap-rootdse <target>
```

用已知凭证做目录枚举（示例模板，按环境调整 baseDN）：
```bash
ldapsearch -x -H ldap://<dc_ip> -D '<domain>\\<user>' -w '<pass>' -b 'DC=example,DC=com' '(objectClass=user)' sAMAccountName
```

## 常见“下一步”决策
- **发现可读/可写共享**：优先收集敏感文件（配置、备份、脚本、凭据痕迹），避免盲目投放
- **发现 WinRM/RDP 可登录**：先确认权限边界（本地管理员/域用户/受限组），再规划横向与提权
- **确认是域环境（DC/LDAP/Kerberos）**：进入 AD 路径分析（BloodHound/LDAP 枚举）与策略评估

## 证据留存清单（建议）
- Nmap 服务版本与脚本输出（445/3389/389）
- SMB 共享列表、权限与可写验证输出（smbmap/smbclient/cme）
- 认证成功/失败的最小证据（避免输出敏感口令到报告正文）

