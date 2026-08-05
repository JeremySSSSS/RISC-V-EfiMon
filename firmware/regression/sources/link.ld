OUTPUT_ARCH(riscv)
ENTRY(_start)

MEMORY
{
    L2 (rwx) : ORIGIN = 0x1c008000, LENGTH = 64K
}

SECTIONS
{
    . = ORIGIN(L2);

    .text : ALIGN(4)
    {
        KEEP(*(.text.start))
        *(.text .text.*)
    } > L2

    .rodata : ALIGN(4)
    {
        *(.rodata .rodata.*)
    } > L2

    .data : ALIGN(4)
    {
        *(.data .data.*)
    } > L2

    .bss (NOLOAD) : ALIGN(4)
    {
        __bss_start = .;
        *(.bss .bss.*)
        *(COMMON)
        __bss_end = .;
    } > L2

    __stack_top = ORIGIN(L2) + LENGTH(L2);
}
