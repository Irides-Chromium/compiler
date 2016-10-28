The Simple Symbol Programming Language
======================================

# Introduction

## Overview

This is the first programming language that I write. After completing the [Brainfuck Interpreter](https://github.com/Irides-Chromium/compiler/bf_interpreter/) and some further extensions, I discover that writing a interpreter like that isn't that hard. Unlike languages like C, it has only one byte for every instruction instead of something like `char`, for example. So, inspired by brainfuck, I want to write a language myself, and I try to make it as simple as brainfuck, but not that *brainfuck*. It currently has about 25 operators (they are all symbols), four tapes, and one special register.

Python3 uses Unicode for encoding, which is different from the original C-written interpreter using ascii for encoding. So I add the `putchar` module so that it will work more like the original version. If the `import putchar` line doesn't work properly, try to use the distribution package [here](https://github.com/Irides-Chromium/python_modules/tree/master/modules) to install compile and install the library.

## Syntax

### Operators (commands)

0. byte description
1.  `~` switch between tapes.
2.  `#` jump to a cell or return the cell number.
3.  `@` add the value of current cell or a value to the one in another tape.
4.  `$` return the value of one cell (index specified or current).
5.  `%` set the current cell with a modulo (divisor specified or 2).
6.  `^` set the current cell with a power (power specified or 2).
7.  `!` add the value of the cell in another tape to the current cell (with index specified or the last cell).
8.  `*` set the current cell with a mutiplication (factor specified or 2).
9.  `{` starts the definition of a *function* (not procedure).
10. `}` ends the definition of a *function* (not procedure).
11. `+` set the current cell with a addition (factor specified or 1).
12. `-` set the current cell with a substraction (factor specified or 1).
13. `<` move the pointer to the left (difference specified or 1).
14. `>` move the pointer to the right (difference specified or 1).
15. `[` starts a loop (like in brainfuck).
16. `]` ends a loop (like in brainfuck).
17. `(` starts a small scope (for expressions).
18. `)` ends a small scope (for expressions).
19. `:` calls a *function* (value specified or current cell).
20. `;` returns a value (value specified, in a sub-parsed expression).
21. `,` reads in a byte (like in brainfuck).
22. `.` output the current cell or a value specified(like in brainfuck).
23. `=` exit the program (value specified or current cell).
24. `?` if, current cell examined.
25. `/` set the current cell with a division (divisor specified or 2).

And there are some special expressions, which will be explained later.

### Behaviour and types of the params.

+------+-----------+----------+--------+---------+---------+
|      | number of | implicit |  explicit param  | default |
| byte |  params   |  params  | number | present |  value  |
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
| `{`  |     0     |    0     |   0    |  none   |  none   |
+------+-----------+----------+--------+---------+---------+
| `}`  |     0     |    0     |   0    |  none   |  none   |
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
| `(`  |     0     |    0     |   0    |  none   |  none   |
+------+-----------+----------+--------+---------+---------+
| `)`  |     0     |    0     |   0    |  none   |  none   |
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
| `?`  |     4     |    0     |   3    |    1    |  none   |
+------+-----------+----------+--------+---------+---------+
| `/`  |     2     |    1     |   1    |    0    |    2    |
+------+-----------+----------+--------+---------+---------+

*NOTE:* If one param has an implicit param, it means it operates on the current cell. If one param has an explicit param, it means the next byte *may* be parsed. Present means "need to be present". 0 means no, 1 means yes, none means there is no explicit param. For the default value, "cell" means default cell, "none" means there is no explicit param, "no effect" means no default value, others are indicated as numbers.

### Registers (cells)

The Simple-Symble language has 3 register types: the tape registers, one expression register and one pointer register. The expression register is used when an expression after a operator is used. The operators in the expression do their operations as normal, but instead of the tape cells, they operate on the expression cell. And, the expression cell would keep its value until the next expression. In the next ()-expression (i.e. expression enclosed by `(` and `)`), an expression of `$_` will hold the old expression cell value.

The pointer register is a read-only register, but its value changes if there is `<` or `>` operations. Its value can be retrived using `#`.

The tape registers are the ones where operations take place. In the behaviour table above, the ones which has a implicit param often set the value of the current register. The value of any tape registers can be retrived using `$`, with a index specified. The value of the current register can be retrived using only `$`, or `$#`.

### Other syntax

The Simple-Symble language uses a "binary-syntax": binary-parsing and binary-expression. Binary-expression means that an expression consists of two parts: the operator and an optional expression (as shown in the table above). The optional expression may be a single byte, or an expression enclosed by `(` and `)`. For a single-byte-expression, there are only a few bytes will work. For those which won't work, it is reserved for the next parsing and no syntax error comes out. This is called the "binary-parsing". A stand alone ()-expression (i.e. left from the last parsing) will have no meaning. Because there is no operation being operated (i.e. no operator with this expression was parsed)

The binary-parsing starts with any operator (single-byte expression). When the parsing encounters the second byte when parsing, if the third byte is also parsable for the second byte, it will parse the third for the second. For example, let a expression be `+$#` (though it can be shortened as `+$`). When parsing the `$` as the explicit param for `+`, because the `#` is parsable for `$`, so the `$#` will be an param for `+` instead of a single `$`. But an expression like `+$#++` will be parsed as `+($(#+))+` because it only parse two bytes (the second `+` is parsed for `#`, but the third `+` is left out, because `++` cannot be parsed as `+(+)`). The parsing ends when the next byte to parse is not parsable for the current byte.

In some situations, you may have one byte that is parsable for the previous one, but you don't want it to parse the two together, you can insert a non-parsable character, like " " (a space), between the two bytes. For example, an expression like `@+` may be parsed as "add one to the cell on the next tape". But if you want to parse it as "add current cell to the cell on the next tape, and add one to the current cell", you may want to write it like `@ +`, `@|+`, `@\+`, etc. because " ", "|", "\" are all non-parsable for `@`. Or, you can use `()` to enclose the expression you want.

*NOTE:* **parsable** means that the current byte and the next byte together is a valid expression. `++` is a sequence of `+` and will be parsed as `+(++)` (plus two to current cell, but more complicated than the former one), instead of a single valid expression, or the second `+` is **parsable** for the first `+` (you may call it as a *sequence of operators*, if you want, but `<>` are also included in this).

The only syntax error that may occur is the matching problem. If there is no matching brackets (`()`, `[]`, `{}`), the interpreter will give an error. The brackets can be nested.

### Overloading

Some of the operators are overloaded. There are two types of meaning of the operators: one is operation, and the other is expression. For instance, the operator `#` will jump to a register with index specified. But in an expression, it will return the index of current register. The difference between the two is the position it's at. In the latter one, it's being parsed as an expression instead of an operator. Because when in an expression, it operates on the expression register, and there is no index for it. Likewise, there is no pointer, so a `<` or `>` will have no effect.

### Structures

####Simple calculations

When an calculation operator is in operation, the cell are changed according to this:

cell {calc}= expr

where {calc} is one of the calculation operators (`+`, `-`, `/`, `*`, `%`, `^`), and expr is a expression or none.

####Array

Having a feature like brainfuck's, the tapes themselves are good arrays, but the operators makes it easier for programmers to get and set values of arrays. With the explicit param, you can specify which index the `$` operator takes.

For example, a get from an array would be like this:

    <+$$(#+)

if the tape is like this:

    0   index   arr[0]  arr[1]  arr[2] ...

####Conditionals

The conditionals are started by the operator `?`, with two bytes of comparison characters (>=, <=, ==, or >>, <<, or /=), and a compared value. So totally there are three params for `?`. In other languages, you may use less-equal to or larger than 0 to indicate `True` or `False`, but when comparing values, you *must* specify a 0, like using a `()`. But this will clear out the expression-cell. Otherwise, you may put a non-parsable character for `?`, then the interpreter will auto-detect the value in the current cell, and use the same convention for `True` and `False`.

The `?` operator discussed above denotes only the `if`; however, you can use `?!` for else (you may pass an expression to it to denote `else if` or `elif`), and `?\` for `endif`.

These are just the default behaviours, you may also use a ()-expression to specify the value you want to check.

####Loops

The loops uses a similar sematic structure as the conditionals. While the brainfuck only have `[]` for loops, you may add a conditional with no `endif` (`?\`) right before the `[` to have the interpreter check the conditional specified before every loop. For example, a loop would be like this:

    ??<(++++)[>+.<]

which tests if the loop cell is less than 4, moves the pointer to the right, adds one, outputs, moves the pointer to the left and start the next loop. Plus, in this situation, `[]` have *no* effect.
