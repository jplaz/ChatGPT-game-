.syntax unified
.arm
.section .text.start,"ax",%progbits
.global _start
.type _start,%function
_start:
    ldr sp, =0x03007F00
    bl main
1:  b 1b
