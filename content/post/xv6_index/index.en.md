---
title: "Annotated xv6 (Education Edition UNIX v6)"
subtitle: "Annotated xv6 table of contents"
date: 2019-03-05T18:35:00+09:00
tags: [xv6, os]
---

### Introduction
These articles explain xv6—the teaching OS used in MIT’s OS course—at code level. xv6 is a reimplementation of UNIX v6 in ANSI C that runs on x86.

[Read this first]({{< ref "post/xv6_intro" >}})

- Features of xv6
- What will / won’t be covered
- How to read these posts
- How to run and debug xv6

### Main series
1. [Page tables 1]({{< ref "post/xv6_pagetable_1" >}})
    - Building address spaces
    - Kernel paging setup
1. [Page tables 2]({{< ref "post/xv6_pagetable_2" >}})
    - Memory allocator
    - sbrk()
    - exec()
1. [Traps, interrupts, and drivers 1]({{< ref "post/xv6_traps_interrupts_drivers_1" >}})
    - IDT
    - System calls
1. Traps, interrupts, and drivers 2 (__coming soon__)
    - Interrupts
    - Disk driver
1. Locking (__coming soon__)
    - Concurrency
1. [Scheduling 1]({{< ref "post/xv6_scheduling_1" >}})
    - Context switch
    - Scheduling
1. Scheduling 2 (__coming soon__)
    - sleep and wakeup
    - Pipes
    - wait, exit, kill
1. File system 1 (__coming soon__)
    - File-system overview
    - Buffer cache layer
    - Logging layer
    - Journaling
    - Block allocator
1. File system 2 (__coming soon__)
    - Inode layer
1. File system 3 (__coming soon__)
    - Directory layer
    - Path name
1. File system 4 (__coming soon__)
    - Descriptor layer

---
If you have comments or corrections, please contact me on [Twitter](https://twitter.com/utam0k) or open an [Issue](https://github.com/utam0k/utam0k.github.io/issues/1).
