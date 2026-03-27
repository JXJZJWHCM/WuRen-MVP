# Active Directory 速查（枚举与攻击面）

## 核心对象与常见字段
- User：`sAMAccountName`、`memberOf`、`userAccountControl`
- Group：`cn`、成员与嵌套
- Computer：`dNSHostName`、`servicePrincipalName`
- GPO：策略影响面（登录脚本、权限、审计）
- SPN：服务账号标识（Kerberoasting 入口）
- Delegation：委派配置（横向与提权的高频入口）
- ACL：对象权限边（GenericAll/WriteDacl/WriteOwner 等）

## 快速识别域环境
```bash
nmap -Pn -T4 -p 88,389,445,464,636,3268,3269 <target_or_range>
nmap -Pn -p 389,636 --script ldap-rootdse <dc_ip>
```

## LDAP 枚举模板（按环境调整 baseDN）
```bash
ldapsearch -x -H ldap://<dc_ip> -D '<domain>\\<user>' -w '<pass>' -b 'DC=example,DC=com' '(objectClass=user)' sAMAccountName memberOf
ldapsearch -x -H ldap://<dc_ip> -D '<domain>\\<user>' -w '<pass>' -b 'DC=example,DC=com' '(objectClass=computer)' dNSHostName
ldapsearch -x -H ldap://<dc_ip> -D '<domain>\\<user>' -w '<pass>' -b 'DC=example,DC=com' '(servicePrincipalName=*)' servicePrincipalName sAMAccountName
```

## Kerberos 攻击面（方向与常用工具）

### AS-REP Roasting（无需预认证账户）
- 目标：`Do not require Kerberos preauthentication` 的用户
- 工具：Impacket `GetNPUsers.py`
```bash
GetNPUsers.py <domain>/ -dc-ip <dc_ip> -usersfile users.txt -no-pass
```

### Kerberoasting（SPN 服务账户）
- 目标：存在 SPN 的服务账号
- 工具：Impacket `GetUserSPNs.py`
```bash
GetUserSPNs.py <domain>/<user>:'<pass>' -dc-ip <dc_ip> -request
```

## “高价值目标”清单（建议优先关注）
- 域控（DC）
- AD CS（证书服务：CA、Web Enrollment、证书模板）
- 文件服务器/备份服务器
- 跳板机/运维机（RDP/WinRM 会话密集）
- SCCM/WSUS/AV 管理端

## BloodHound 的价值（建议）
- 用图回答“从当前凭证能走到哪里”
- 优先关注边类型：`MemberOf`、`AdminTo`、`HasSession`、`GenericAll/WriteDacl/WriteOwner`、委派相关边
- 报告落点：用最短路径 + 每跳证据解释风险与修复

## 修复建议方向（用于报告）
- 最小权限与分层管理（Tiering），限制横向
- 收敛 WinRM/RDP 暴露面与可登录范围
- 审计与告警：登录失败、喷洒行为、异常票据请求、ACL 变更
- 清理过期/弱口令服务账号，收敛 SPN 与委派

