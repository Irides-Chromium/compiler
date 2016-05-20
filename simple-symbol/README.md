The Simple Symbol Programming Language
======================================

# Introduction

## Overview

This is the first programming language that I write. After completing the [Brainfuck Interpreter](https://github.com/Irides-Chromium/compiler/bf_interpreter/) and some further extensions, I discover that writing a interpreter like that isn't that hard. Unlike languages like C, it has only one byte for every instruction instead of `char`, for example. So, inspired by brainfuck, I want to write a language myself, and I try to make it as simple as brainfuck, but not that *brainfuck*. It currently has about 25 operators (they are all symbols), two tapes (extendable up to 8), and one special register, but it is still undergoing an improvement and the design hasn't complete yet at this moment.

## Operators (commands)

    byte type   description
 1. `~`  [+] switch between tapes.
 2. `!`  [+] jump to a cell.
 3. `@`  [@] add the value of current cell to the one in another tape.
 4. `#`  [+] add the value of the pointer to the current cell.
 5. `$`  [@] return the value of one cell (index specified).
 6. `%`  [+] set the current cell with a modulo (divisor specified).
 7. `^`  [+] set the current cell with a power (power specified).
 8. `&`  [@] add the value of a cell in another tape to the current cell.
 9. `*`  [+] set the current cell with a mutiplication (factor specified).
10. `(`  [0] starts the definition of a *function* (not procedure).
11. `)`  [0] ends the definition of a *function* (not procedure).
12. `+`  [+] set the current cell with a addition (factor specified).
13. `-`  [+] set the current cell with a substraction (factor specified).
14. `<`  [+] move the pointer to the left (difference specified).
15. `>`  [+] move the pointer to the right (difference specified).
16. `[`  [0] starts a loop (like in brainfuck).
17. `]`  [0] ends a loop (like in brainfuck).
18. `{`  [0] starts a small scope (for expressions).
19. `}`  [0] ends a small scope (for expressions).
20. `:`  [@] calls a *function* (reference specified).
21. `;`  [@] returns a value (value specified, in a function).
22. `,`  [+] reads in a byte (like in brainfuck).
23. `.`  [+] output the current cell (like in brainfuck).
24. `=`  [@] exit the program (value specified).
25. `?`  [0] if, current cell examined.
26. `/`  [+] set the current cell with a division (divisor specified).

And other options of operators: `_`, `\`, `!`.

**NOTE:** 
