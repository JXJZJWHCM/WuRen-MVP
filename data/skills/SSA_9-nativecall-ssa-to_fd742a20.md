# 9. 原生扩展：重要的 NativeCall 机制 | SSA.to

- 来源: https://ssa.to/en/syntaxflow-guide/statements/sf-nativecall
- 抓取时间: 2026-02-06T07:30:43Z

---
SyntaxFlow 的高级关键特性之一是使用 NativeCall 函数。这些函数是预先定义的，可在语言内部提供各种实用功能。本教程将介绍 NativeCall 函数的概念，解释其用法，并提供可用函数的完整列表及其描述。

- 简介
- NativeCall 语法定义 完整的 eBNF 描述
- NativeCall 函数列表
- 总结

- 完整的 eBNF 描述

## 简介 ​

在 SyntaxFlow 中， NativeCall （原生调用）是预封装的函数，允许用户在规则中执行各种高级操作。这些函数用于操作、检查和转换数据结构，促进高级代码分析和转换任务。通过 NativeCall ，用户无需编写复杂的逻辑即可实现复杂的数据处理需求，大大提升了 SyntaxFlow 的灵活性和功能性。

## NativeCall 语法定义 ​

NativeCall 的语法结构如下：

```
<nativeCallName(arg1, argName="value", ...)>
```

其中：

- < ：标记 NativeCall 的开始。
- nativeCallName ：要使用的 NativeCall 函数名称。
- (...) ：包含函数参数的圆括号。
- > ：标记 NativeCall 的结束。

### 完整的 eBNF 描述 ​

```
nativeCall
    : '<' useNativeCall '>'
    ;
useNativeCall
    : identifier useDefCalcParams?
    ;
useDefCalcParams
    : '{' nativeCallActualParams? '}'
    | '(' nativeCallActualParams? ')'
    ;
nativeCallActualParams
    : lines? nativeCallActualParam (',' lines? nativeCallActualParam)* ','? lines?
    ;
nativeCallActualParam
    : (nativeCallActualParamKey (':' | '='))?  nativeCallActualParamValue
    ;
nativeCallActualParamKey
    : identifier
    ;
nativeCallActualParamValue
    : identifier | numberLiteral | '`' ~'`'* '`' | '$' identifier | hereDoc
    ;
```

## NativeCall 函数列表 ​

下表列出了 SyntaxFlow 中所有可用的 NativeCall 函数，以及它们的描述：

注意 ：上述函数列表是逐步演进的，可能并不包含全部的 NativeCall 函数。用户可以参考源码和相关规则了解更多未覆盖的 NativeCall 使用方法。在后续的案例中，我们会逐步为大家讲解 NativeCall 中的内容究竟都是如何使用的。

## 总结 ​

NativeCall 机制为 SyntaxFlow 提供了强大的扩展能力，使用户能够在规则中执行多种高级操作。通过预定义的 NativeCall 函数，用户可以高效地操作、检查和转换数据结构，完成复杂的代码分析任务。掌握 NativeCall 的使用方法和最佳实践，将显著提升代码审计和安全分析的效率与准确性。

- 简介
- NativeCall 语法定义 完整的 eBNF 描述
- NativeCall 函数列表
- 总结

- 完整的 eBNF 描述
