# DEC VAX MACRO V05-00 Macro Assembler

Authentic 32-bit DEC VAX MACRO V05-00 Assembler (`vaxmacro`) targeting OpenVMS VAX V5.5-2 and `vmslink` / `vms_vm`.

## Features
- **Assembler Directives**: `.TITLE`, `.SUBTITLE`, `.IDENT`, `.PSECT`, `.ENTRY <name>, ^M<...>`, `.GLOBAL`, `.LONG`, `.WORD`, `.BYTE`, `.BLKL`, `.BLKW`, `.BLKB`, `.ASCIZ`, `.ASCII`, `.ASCID`, `.MACRO ... .ENDM`, `.PRINT`, `$PUTMSG_S`, `.END`.
- **32-Bit VAX Instructions & Registers (`R0`–`R11`, `AP`, `FP`, `SP`, `PC`)**: `MOVL`, `MOVW`, `MOVB`, `MOVZBL`, `MNEGL`, `CLRL`, `INCL`, `DECL`, `ADDL2`, `ADDL3`, `SUBL2`, `SUBL3`, `MULL2`, `MULL3`, `DIVL2`, `DIVL3`, `BICL2`, `BISL2`, `XORL2`, `CMPL`, `TSTL`, `JMP`, `BRB`, `BRW`, `BEQL`, `BNEQ`, `BLSS`, `BGTR`, `BLEQ`, `BGEQ`, `SOBGTR`, `SOBGEQ`, `AOBLSS`, `AOBLEQ`, `JSB`, `RSB`, `PUSHAL`, `PUSHL`, `CALLS`, `RET`.

## Usage
```bash
make build
./compiler/vaxmacro samples/DEMO.MAR -o samples/DEMO.OBJ -l samples/DEMO.LST
../VAX-BASIC/linker/vmslink -o samples/DEMO.EXE samples/DEMO.OBJ
./samples/DEMO.EXE
```
