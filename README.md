# LR1_compiler

没有实现逻辑运算中的截断（&& ||）

bool类型按照int存储了，导致每次逻辑运算前需要强转。

使用了MIPS32作为目标平台，生成的目标代码可在（硬件课使用的）MARS 4.5（跨平台的MIPS编辑器和模拟器）中直接运行。
