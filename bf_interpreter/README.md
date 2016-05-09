# The Brainfuck Interpreter

## Introduction

### Brainfuck the programming language

[Brainfuck](https://en.wikipedia.org/wiki/Brainfuck) is one of the many [esoteric programmming languages](https://en.wikipedia.org/wiki/Esoteric_programming_language). Defined by wiki, these languages are to test the boundaries of computers. Brainfuck comes from the slang "Brain fuck", which refers to things so complicated or unusual that they exceed the limits of one's understanding. This is true because of the only 8 operators in brainfuck. A brainfuck program consists of a long (default 30000) array initialized to zero, a data pointer initialized to zero, and the 8 operators. When working, the BF program is just like a Turing Machine. The operators are mentioned below:

1.  `>`  Increment the data pointer (to point to the cell to the right).

2.  `<`  Decrement the data pointer (to point to the cell to the left).

3.  `+`  Increment the byte at the data pointer.

4.  `-`  Decrement the byte at the data pointer.

5.  `.`  Output the byte at the data pointer.

6.  `,`  Accept one byte of input, storing its value in the byte at the data pointer.

7.  `[`  If the byte at the data pointer is zero, then instead of moving the instruction pointer forward to the next command, jump it forward to the command after the matching `]` command.

8.  `]`  If the byte at the data pointer is nonzero, then instead of moving the instruction pointer forward to the next command, jump it back to the command after the matching `]` command.

(Come from the brainfuck manual page)

There are also some extended operators:

9.  `#`  The debug operator, prints the values of 20 cell values, 10 before the data pointer, 10 after.

10. `(`  Defines a function (in the [pbrain](http://www.parkscomputing.com/2014/04/pbrain/) extension), whose name is the value in the current cell.

11. `)`  Ends the definition of the function.

12. `:`  Calls the function whose name is the value in the current cell.

13. `=`  Quit the program with the value in the current cell.

14. `!`  Save the current tape to file.

15. `?`  Load the tape from the file.

And another extention uses numbers to reduce the number of operators used. For example, use `5+` instead of `+++++`

You can also find other esoteric languages [here](http://esolangs.org/wiki/Language_list)

### Introduction to BF (dont use bad words...) programming

There is a very good tutorial [here](http://www.iwriteiam.nl/Ha_BF.html). There are also good BF resources at the site, like BF interpreters written in BF. But I guess the man who wrote it will be "brainfucked" ...

## My Interpreter

I made the interpreter using the most original features, as mentioned below:

1. Each cell uses one byte (0 ~ 255).
2. The length of the tape is 30000.

And the `#` debug extension.

## Usage

### Console mode

In the Console Mode, the BF program is used as an interactive python console, in which the tape in conserved until you exit the program with <kbd>CTRL-C</kbd> or `EOF` (<kbd>CTRL-D</kbd>). Type codes as you would when you write BF programs.

### File mode

In the File Mode you need to feed the program a filename, and it will run the file according to the 9 operators (8 operators and the `#` for debug).
