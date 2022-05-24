.data
s: .space 88
fpconst_0: .float 0 # 一定有，方便float转bool用。
.text
b main

program:
lw $t1, 8($sp)
sw $t1, s+8
lw $t1, 4($sp)
sw $t1, s+12
lw $t1, 0($sp)
sw $t1, s+16
addi $sp, $sp, -4
sw, $ra, 0($sp) # 保存返回地址
# (program,  1) (':=', 0, None, 'i') type=int
addi $t1, $0, 0 # const int 0 -> $t1
move $t3, $t1 # i := 0
sw $t3, s+20 # $t3 -> int i

# (program,  2) ('+', 'b', 'c', '$1') type=int
ld $t1, s+12 # int b -> $t1
ld $t2, s+16 # int c -> $t2
add $t3, $t1, $t2 # $1 := b + c
sw $t3, s+28 # $t3 -> int $1

# (program,  3) ('>', 'a', '$1', '$2') type=int
ld $t1, s+8 # int a -> $t1
ld $t2, s+28 # int $1 -> $t2
sgt $t3, $t1, $t2 # $2 := a > $1
sw $t3, s+32 # $t3 -> int $2

# (program,  4) ('j=', '$2', 0, 10) type=bool
ld $t1, s+32 # int $2 -> $t1
sne $t1, $t1, 0 # int->bool
addi $t2, $0, 0 # const int 0 -> $t2
sne $t2, $t2, 0 # int->bool
beq $t1, $t2, program_10 # if $2 == 0 goto program_10

# (program,  5) ('*', 'b', 'c', '$3') type=int
ld $t1, s+12 # int b -> $t1
ld $t2, s+16 # int c -> $t2
mul $t3, $t1, $t2 # $3 := b * c
sw $t3, s+36 # $t3 -> int $3

# (program,  6) ('+', '$3', 1, '$4') type=int
ld $t1, s+36 # int $3 -> $t1
addi $t2, $0, 1 # const int 1 -> $t2
add $t3, $t1, $t2 # $4 := $3 + 1
sw $t3, s+40 # $t3 -> int $4

# (program,  7) ('+', 'a', '$4', '$5') type=int
ld $t1, s+8 # int a -> $t1
ld $t2, s+40 # int $4 -> $t2
add $t3, $t1, $t2 # $5 := a + $4
sw $t3, s+44 # $t3 -> int $5

# (program,  8) (':=', '$5', None, 'j') type=int
ld $t1, s+44 # int $5 -> $t1
move $t3, $t1 # j := $5
sw $t3, s+24 # $t3 -> int j

# (program,  9) ('j', None, None, 11) type=int
b program_11 # goto program_11

program_10:
# (program, 10) (':=', 'a', None, 'j') type=int
ld $t1, s+8 # int a -> $t1
move $t3, $t1 # j := a
sw $t3, s+24 # $t3 -> int j

program_11:
# (program, 11) ('<=', 'j', 100, '$6') type=int
ld $t1, s+24 # int j -> $t1
addi $t2, $0, 100 # const int 100 -> $t2
sle $t3, $t1, $t2 # $6 := j <= 100
sw $t3, s+48 # $t3 -> int $6

# (program, 12) ('j=', '$6', 0, 16) type=bool
ld $t1, s+48 # int $6 -> $t1
sne $t1, $t1, 0 # int->bool
addi $t2, $0, 0 # const int 0 -> $t2
sne $t2, $t2, 0 # int->bool
beq $t1, $t2, program_16 # if $6 == 0 goto program_16

# (program, 13) ('*', 'j', 2, '$7') type=int
ld $t1, s+24 # int j -> $t1
addi $t2, $0, 2 # const int 2 -> $t2
mul $t3, $t1, $t2 # $7 := j * 2
sw $t3, s+52 # $t3 -> int $7

# (program, 14) (':=', '$7', None, 'j') type=int
ld $t1, s+52 # int $7 -> $t1
move $t3, $t1 # j := $7
sw $t3, s+24 # $t3 -> int j

# (program, 15) ('j', None, None, 11) type=int
b program_11 # goto program_11

program_16:
# (program, 16) ('return', None, None, 'j') type=int
ld $t1, s+24 # int j -> $t1
move $v0, $t1 # RETURN j
lw $ra, 0($sp)
addi $sp, $sp, 4
jr $ra

demo:
lw $t1, 0($sp)
sw $t1, s+56
addi $sp, $sp, -4
sw, $ra, 0($sp) # 保存返回地址
# (demo,  1) ('+', 'a', 2, '$1') type=int
ld $t1, s+56 # int a -> $t1
addi $t2, $0, 2 # const int 2 -> $t2
add $t3, $t1, $t2 # $1 := a + 2
sw $t3, s+60 # $t3 -> int $1

# (demo,  2) (':=', '$1', None, 'a') type=int
ld $t1, s+60 # int $1 -> $t1
move $t3, $t1 # a := $1
sw $t3, s+56 # $t3 -> int a

# (demo,  3) ('*', 'a', 2, '$2') type=int
ld $t1, s+56 # int a -> $t1
addi $t2, $0, 2 # const int 2 -> $t2
mul $t3, $t1, $t2 # $2 := a * 2
sw $t3, s+64 # $t3 -> int $2

# (demo,  4) ('return', None, None, '$2') type=int
ld $t1, s+64 # int $2 -> $t1
move $v0, $t1 # RETURN $2
lw $ra, 0($sp)
addi $sp, $sp, 4
jr $ra

main:
addi $sp, $sp, -4
sw, $ra, 0($sp) # 保存返回地址
# (main,  1) (':=', 3, None, 'a') type=int
addi $t1, $0, 3 # const int 3 -> $t1
move $t3, $t1 # a := 3
sw $t3, s+68 # $t3 -> int a

# (main,  2) (':=', 4, None, 'b') type=float
addi $t1, $0, 4 # const int 4 -> $t1
# int->float
mtc1, $t1, $f1
cvt.s.w $f1, $f1
mov.s $f3, $f1 # b := 4
s.s $f3, s+72 # $f3 -> float b

# (main,  3) (':=', 2, None, 'c') type=int
addi $t1, $0, 2 # const int 2 -> $t1
move $t3, $t1 # c := 2
sw $t3, s+76 # $t3 -> int c

# (main,  4) ('param', 'c', 0, 'demo') type=int
ld $t1, s+76 # int c -> $t1
addi $sp, $sp, -4
sw, $t1, 0($sp) # PUSH c

# (main,  5) ('call', 'demo', None, '$1') type=int
jal demo
addi $sp, $sp, 4 # 恢复sp
move, $t1, $v0
sw $t1, s+80 # $t1 -> int $1

# (main,  6) ('param', 'a', 0, 'program') type=int
ld $t1, s+68 # int a -> $t1
addi $sp, $sp, -4
sw, $t1, 0($sp) # PUSH a

# (main,  7) ('param', 'b', 1, 'program') type=int
l.s $f1, s+72 # float b -> $f1
# float->int
cvt.w.s $f1, $f1
mfc1, $t1, $f1
addi $sp, $sp, -4
sw, $t1, 0($sp) # PUSH b

# (main,  8) ('param', '$1', 2, 'program') type=int
ld $t1, s+80 # int $1 -> $t1
addi $sp, $sp, -4
sw, $t1, 0($sp) # PUSH $1

# (main,  9) ('call', 'program', None, '$2') type=int
jal program
addi $sp, $sp, 12 # 恢复sp
move, $t1, $v0
sw $t1, s+84 # $t1 -> int $2

# (main, 10) (':=', '$2', None, 'a') type=int
ld $t1, s+84 # int $2 -> $t1
move $t3, $t1 # a := $2
sw $t3, s+68 # $t3 -> int a

# (main, 11) ('return', None, None, None) type=int
lw $ra, 0($sp)
addi $sp, $sp, 4
jr $ra
