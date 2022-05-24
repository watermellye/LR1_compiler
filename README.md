# LR1_compiler

选择MIPS32作为目标平台，生成的目标代码可在（硬件课使用的）MARS 4.5（跨平台的MIPS编辑器和模拟器）中直接运行。

## 词法分析器
虽然是用C++写的，但是其实里面是正则匹配，偷懒了。

## 语法语义分析器
- [x] 过程文件：项目、first集、每个项目的闭包集合、项目集族、Go表
- [x] 输出：Action-Goto表、分析栈、语法树（使用pyecharts生成）
- [x] Warning(print) 和 Error(raise Exception) 提示
- [ ] 逻辑运算（&&  ||）中的截断

## 目标代码生成器
- [x] 赋值、单/双目运算（**含浮点类型（float）支持**）、分支指令
- [x] 函数调用（通过$sp传参并维护返回地址，返回值（若有）存于$v0）
- [x] bool类型支持（不完整，bool按照int存储了，导致每次逻辑运算前需要强转）
- [ ] 待用及活跃信息表
- [ ] 基本块划分、DAG 优化、循环优化（强度削弱、删除归纳变量）等

## 其它

运行方法：修改了输入源代码后，先运行```词法分析器.cpp```，再运行```语法语义分析器+目标代码生成器.py```，即可。

本项目采用python编写。虽然说这种底层的东西最好还是使用C++来完成，更加“原汁原味”；但秉承着“代码以简洁优先”，“能写出来就算成功”，“人和代码有一个能跑就行”的原则，最终选择了python。~~直到最后也没有做class封装，没有分文件。~~

语法分析（含语法树生成）、语义分析（中间代码生成）、目标代码生成，合计不到1000行。本项目所有代码均为自己编写，从编译原理大作业到编译原理课设，共花费10天完成。

本项目求 First 集和求单个项目的闭包部分的算法，以及关于浮点数的支持（自动类型转换的逻辑），可供参考。

代码注释写的很粗糙，逻辑详见报告3.1（主要函数分析与设计）

其余如输入输出、测试数据等一切，详见报告。
