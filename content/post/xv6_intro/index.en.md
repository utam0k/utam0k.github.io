---
title: "Annotated xv6: Introduction"
date: 2019-03-05T18:35:01+09:00
tags: [xv6, os]
---
[Annotated xv6 table of contents]({{< ref "post/xv6_index" >}})
***

### Introduction
xv6 is a modernized Unix V6 developed at MIT. It runs on the x86 architecture and you can easily run it on your own PC.

These posts explain xv6 at source-code level based on MIT’s text *[xv6, a simple, Unix-like teaching operating system](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)* ("commentary/textbook" below). I summarize and add explanations to what is in the commentary/textbook.

I am an OS beginner; I started reading xv6 about six months before writing this[^*]. Some parts were hard for beginners. I’m writing the articles I wish I’d had when I started. I hope they help anyone beginning xv6 code reading.
[^*]: Written March 2019.

There may be mistakes—please point them out. I’m also not deeply versed in production OSes like Linux, so I’d appreciate tips like “Linux does it this way.” Contact me on [Twitter](https://twitter.com/utam0k) or open an [Issue](https://github.com/utam0k/utam0k.github.io/issues/1).

### Features of xv6
- Based on Unix V6
- Packed with OS fundamentals
- Written in ANSI C
- Runs on x86 (RISC-V starting with the 2019 edition)
- About ten thousand lines of code

### What will / won’t be covered
#### Covered
- Explanations of xv6 code
- How x86 works
- Explanations of OS-specific terms

#### Not covered
- Why an OS needs each feature (e.g., why paging is necessary)
- Details of assembly or C syntax

### How to read these posts
Japanese section titles are my own explanations. If a section title is in English, that title also exists in the commentary/textbook and I’m explaining that chapter.

Example of code annotations:

- `filename.c`

    ``` c
    1 int main()
    2 {
    3     printf("Hello world!");
    ~~~
    8     return 0;
    9 }
    ```
- L1: function declaration
- L3: print
- L4: return value

`L<number>` refers to the line number in source; explanations are on the right. `~~~` denotes omission.

### How to run xv6
I run it on Ubuntu 18.04 and Debian GNU/Linux 9.4 (stretch). It should basically work anywhere with `gcc` and `qemu`. The `Makefile` mentions Mac OS X, so try uncommenting the relevant lines.

#### Run
[This site](https://gcallah.github.io/OperatingSystems/xv6Install.html) is helpful.

1. Install required tools

    ```
    $ sudo apt install git nasm build-essential qemu gdb
    ```
1. Get the code

    ```
    $ git clone git://github.com/mit-pdos/xv6-public.git
    $ cd xv6-public
    $ git checkout xv6-rev11
    ```

1. Make
If you run it once, it seems you can only stop it with the `kill` command.

    ```
    $ make qemu     # with GUI
    $ make qemu-nox # headless
    ```

#### Debugging (GDB)
1. Start

    ```
    $ make qemu-nox-gdb # Booting with gdbserver
    ```
1. Attach
Launch another shell while xv6 is running and start gdb.

    ```
    $ cd <path to xv6>
    $ gdb
    ```
In gdb, run:

    ```
    (gdb) source .gdbinit
    ```
1. Debug
I often stepped through code in gdb to check variable values—highly recommended. As a quick look at `mkdir`, run these in gdb:

    ```
    (gdb) b sys_mkdir
    (gdb) layout src
    (gdb) continue
    ```
Then run `mkdir` inside xv6:

    ```
    $ mkdir test
    ```

    If gdb reacts, you’re attached.
1. Stop xv6
End xv6 from the gdb side.
    
    ```
    (gdb) kill
    ```
