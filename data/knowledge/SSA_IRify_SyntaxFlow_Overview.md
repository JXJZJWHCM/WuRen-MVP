# SSA.to / IRify / SyntaxFlow：编译器级 SSA-IR 安全扫描概览

## 背景与定位
传统 SAST 往往依赖“语言 AST + 框架适配 + 规则库”，在跨语言、跨模板/子语言（如 JSP、Freemarker、SpEL）与跨过程数据流方面容易遇到精度与性能瓶颈。

SSA.to 的路线是把程序编译为统一的 SSA 形式中间表示（SSA-IR），再对 SSA 数据库进行查询与数据流分析，从而在跨文件/跨包、路径敏感、过程间与 OOP 场景下获得更统一的分析模型与表达能力。

## IRify / SSA-IR 的关键点（从站点描述抽象）
- 多语言/多框架：覆盖 Java（含 Freemarker、SpEL、EL、JSP 等子语言）、Golang、PHP、JavaScript/EcmaScript，并强调对 SpringBoot 的深度支持
- 分析技术：基于 SSA 的 Use-Def 链、Phi 节点、控制流图（CFG）结合数据流分析，支持自顶向下与自底向上链路
- 存储与规则：使用 SQLite 存储 IR 数据库；通过 SyntaxFlow 这一 DSL 对 IR 产物进行扫描，并可将分析经验沉淀为规则

## SyntaxFlow 是什么
SyntaxFlow 是面向 SSA 数据库的专用查询语言/DSL：
- 通过抹除语言 AST 差异，把分支/循环映射到基本块与 Phi 结构，统一分析模型
- 支持 Use-Def 链追踪、控制流分析、上下文敏感的过程间分析、OOP 到 SSA 的映射与跨过程追踪
- 结果可映射回源码位置（文件/行列范围）用于证据闭环

## 与 雾刃渗透测试系统1.0 的协同方式（建议）
### 1) 作为“代码审计阶段”的增强扫描器
- 在 Code Audit 阶段先做轻量规则扫描（本项目内置 `code_audit`）定位明显风险
- 再用 SSA/SyntaxFlow 做“跨过程 + 路径敏感”的深度分析，重点覆盖：
  - 命令执行/SQL 注入/模板注入等数据流型漏洞
  - 框架入口识别（例如 Java 注解语义/控制器入口）
  - 净化函数（sanitizer）与过滤链路的识别（减少误报）

### 2) 规则沉淀为 Skills/Knowledge/Playbooks
- Skills：写成“如何编写/调试规则”的操作手册（Quick Start、数据流过滤、集合运算、NativeCall）
- Knowledge：写成“某类漏洞的 SSA 识别思路与常见误报点”（source/sink/sanitizer 建模）
- Playbooks：写成“审计发现 → 复现验证 → 修复建议”的闭环

## 参考
- SSA.to 主页（IRify/SSA-IR/SQLite/SyntaxFlow 概览）：https://ssa.to/
- SyntaxFlow 简介：https://ssa.to/en/syntaxflow-guide/intro
