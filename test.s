section .text
global _start

_start:
    sub esp, 16        
    mov esi, input
    lea edi, [esp]
copy:
    lodsb
    stosb             
    test al, al
    jnz copy
    mov ecx, 16