ENTRY(_start)
SECTIONS {
  . = 0x080000C0;
  .text : { KEEP(*(.text.start)) *(.text*) *(.rodata*) }
  .data : { *(.data*) }
  .bss (NOLOAD) : { __bss_start__ = .; *(.bss*) *(COMMON); __bss_end__ = .; }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.eh_frame*) *(.comment*) *(.ARM.attributes*) }
}
