The Simple Symbol Programming Language
======================================

# Introduction

## Overview

This is the first programming language that I write. After completing the [Brainfuck Interpreter](https://github.com/Irides-Chromium/compiler/bf_interpreter/) and some further extensions, I discover that writing a interpreter like that isn't that hard. Unlike languages like C, it has only one byte for every instruction instead of `char`, for example. So, inspired by brainfuck, I want to write a language myself, and I try to make it as simple as brainfuck, but not that *brainfuck*. It currently has about 25 operators (they are all symbols), two tapes (extendable up to 8), and one special register, but it is still undergoing an improvement and the design hasn't complete yet at this moment.

## Syntax

### Operators (commands)

0. byte description
1.  `~` switch between tapes.
2.  `#` jump to a cell.
3.  `@` add the value of current cell to the one in another tape.
4.  `$` return the value of one cell (index specified).
5.  `%` set the current cell with a modulo (divisor specified).
6.  `^` set the current cell with a power (power specified).
7.  `!` add the value of a cell in another tape to the current cell.
8.  `*` set the current cell with a mutiplication (factor specified).
9.  `(` starts the definition of a *function* (not procedure).
10. `)` ends the definition of a *function* (not procedure).
11. `+` set the current cell with a addition (factor specified).
12. `-` set the current cell with a substraction (factor specified).
13. `<` move the pointer to the left (difference specified).
14. `>` move the pointer to the right (difference specified).
15. `[` starts a loop (like in brainfuck).
16. `]` ends a loop (like in brainfuck).
17. `{` starts a small scope (for expressions).
18. `}` ends a small scope (for expressions).
19. `:` calls a *function* (reference specified).
20. `;` returns a value (value specified, in a function).
21. `,` reads in a byte (like in brainfuck).
22. `.` output the current cell (like in brainfuck).
23. `=` exit the program (value specified).
24. `?` if, current cell examined.
25. `/` set the current cell with a division (divisor specified).

And other options of operators: `_`, `\`, `!`.

### Behaviour and types of the operands.

+------+-----------+----------+--------+---------+---------+
|      | number of | implicit | explicit operand | default |
| byte | operands  | operands | number | present |  value  |
+------+-----------+----------+--------+---------+---------+
| `~`  |     1     |    0     |   1    |    0    |  next   |
+------+-----------+----------+--------+---------+---------+
| `#`  |     1     |    0     |   1    |    0    |no effect|
+------+-----------+----------+--------+---------+---------+
| `@`  |     1     |    0     |   1    |    0    |  cell   |
+------+-----------+----------+--------+---------+---------+
| `$`  |     1     |    0     |   1    |    0    |  cell   |
+------+-----------+----------+--------+---------+---------+
| `%`  |     2     |    1     |   1    |    0    |    2    |
+------+-----------+----------+--------+---------+---------+
| `^`  |     2     |    1     |   1    |    0    |    2    |
+------+-----------+----------+--------+---------+---------+
| `!`  |     1     |    0     |   1    |    0    |  next   |
+------+-----------+----------+--------+---------+---------+
| `*`  |     2     |    1     |   1    |    0    |    2    |
+------+-----------+----------+--------+---------+---------+
| `(`  |     0     |    0     |   0    |  none   |  none   |
+------+-----------+----------+--------+---------+---------+
| `)`  |     0     |    0     |   0    |  none   |  none   |
+------+-----------+----------+--------+---------+---------+
| `+`  |     2     |    1     |   1    |    0    |    1    |
+------+-----------+----------+--------+---------+---------+
| `-`  |     2     |    1     |   1    |    0    |    1    |
+------+-----------+----------+--------+---------+---------+
| `<`  |     1     |    1     |   1    |    0    |    1    |
+------+-----------+----------+--------+---------+---------+
| `>`  |     1     |    1     |   1    |    0    |    1    |
+------+-----------+----------+--------+---------+---------+
| `[`  |     0     |    0     |   0    |  none   |  none   |
+------+-----------+----------+--------+---------+---------+
| `]`  |     0     |    0     |   0    |  none   |  none   |
+------+-----------+----------+--------+---------+---------+
| `{`  |     0     |    0     |   0    |  none   |  none   |
+------+-----------+----------+--------+---------+---------+
| `}`  |     0     |    0     |   0    |  none   |  none   |
+------+-----------+----------+--------+---------+---------+
| `:`  |     1     |    0     |   1    |    0    |  cell   |
+------+-----------+----------+--------+---------+---------+
| `;`  |     1     |    0     |   1    |    0    |  cell   |
+------+-----------+----------+--------+---------+---------+
| `,`  |     1     |    0     |   0    |  none   |  none   |
+------+-----------+----------+--------+---------+---------+
| `.`  |     1     |    0     |   1    |    0    |  cell   |
+------+-----------+----------+--------+---------+---------+
| `=`  |     1     |    0     |   1    |    0    |  cell   |
+------+-----------+----------+--------+---------+---------+
| `?`  |     1     |    0     |   1    |    1    |  none   |
+------+-----------+----------+--------+---------+---------+
| `/`  |     2     |    1     |   1    |    0    |    2    |
+------+-----------+----------+--------+---------+---------+

*NOTE:* If one operand has an implicit operand, it means it operates on the current cell. If one operand has an explicit operand, it means the next byte *may* be parsed. Present means "need to be present". 0 means no, 1 means yes, none means there is no explicit operand.

### Registers (cells)

The Simple-Symble language has 2 register types: the tape registers and one expression register. The expression register is used when an expression after a operator is used. The operators in the expression do their operations as normal, but instead of the tape cells, they operate on the expression cell. And, the expression cell would keep its value until the next expression. In the next {}-expression (i.e. expression enclosed by `{` and `}`), an expression of `$_` will hold the old expression cell value.

### Other syntax

The Simple-Symble language uses a "binary-syntax": binary-parsing and binary-expression. Binary-expression means that an expression consists of two parts: the operator and an optional expression (as shown in the table above). The optional expression may be a single byte, or an expression enclosed by `{` and `}`. For a single-byte-expression, there are only a few bytes will work. For those which won't work, it is reserved for the next parsing and no syntax error comes out. This is called the "binary-parsing". A stand alone {}-expression (i.e. left from the last parsing) will have no meaning. Because there is no operation being operated (i.e. no operator with this expression was parsed)

The only syntax error that may occur is the matching problem. If there is no matching brackets (`()`, `[]`, `{}`), the interpreter will give an error.
