---
title: "xv6 Deep Dive Traps, interrupts, and drivers 1"
date: 2019-07-08T00:00:00+09:00
tags: [xv6, os]
---

[xv6 Deep Dive table of contents]({{< ref "post/xv6_index">}})  
[Previous post]({{< ref "post/xv6_pagetable_2">}})  
[Next post]({{< ref "post/xv6_scheduling_1" >}})
- - -
This chapter introduces several special-purpose registers. I won’t explain each one here—see this [excellent reference](https://ja.wikibooks.org/wiki/X86%E3%82%A2%E3%82%BB%E3%83%B3%E3%83%96%E3%83%A9/x86%E3%82%A2%E3%83%BC%E3%82%AD%E3%83%86%E3%82%AF%E3%83%81%E3%83%A3#%E6%B1%8E%E7%94%A8%E3%83%AC%E3%82%B8%E3%82%B9%E3%82%BF_(GPR)) when needed.

# Systems calls, exceptions, and interrupts
Three ways control moves from a user program into the kernel:

1. System call
1. Exception
1. Interrupt / trap
  - Issued by the `int` instruction
  - Trap: caused by the currently running process
  - Interrupt: unrelated to the current process

# x86 protection
**Protection levels**  
Lower two bits of `%cs` are the CPL (Current Privilege Level).

- DPL (Descriptor Privilege Level)
- CPL (Current Privilege Level)

Level 0: kernel mode; Level 3: user mode.

**IDT**  
Interrupt Descriptor Table: maps interrupts to handlers. The kernel must build this table. [Great article (JP)](http://softwaretechnique.jp/OS_Development/kernel_development02.html).

**`int` handling**

- `int n`: triggers the nth IDT entry.
- `%cs` and `%eip` are manipulated, so we must preserve them (e.g., push to stack).
- Hardware steps for `int`:
  1. Fetch descriptor n from IDT.
  2. Check `%cs` CPL ≤ descriptor DPL.
  3. Only if target selector DPL ≤ CPL, save `%esp` and `%ss` (internal CPU regs).
  4. Load `%ss`/`%esp` from task segment descriptor.
  5. Push `%ss` `%esp` `%eflags` `%cs` `%eip` onto the stack.
  6. Clear IF (interrupt-enable) in `%eflags`.
  7. Load `%cs`/`%eip` from the descriptor (set in Chapter 5’s `switchuvm()` via TSS).

    > {{< figure src="https://raw.githubusercontent.com/msyksphinz/xv6_translate/master/images/figure3-01.JPG" caption="Stack state after int" attr="" attrlink="" >}}
    Source: [commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)

`iret` (not `ret`) restores the stack created by `int`.

# Code: Assembly trap handlers
`tvinit()` (called from `main.c`) sets the IDT.

- `trap.c`

    ``` c
    17 void
    18 tvinit(void)
    19 {
    20   int i;

    22   for(i = 0; i < 256; i++)
    23     SETGATE(idt[i], 0, SEG_KCODE<<3, vectors[i], 0);
    24   SETGATE(idt[T_SYSCALL], 1, SEG_KCODE<<3, vectors[T_SYSCALL], DPL_USER);

    26   initlock(&tickslock, "time");
    27 } 
    ```
    - L22-23: Set all 256 IDT entries to handlers in `vectors`.
    - L24: Set system-call IDT entry. Only T_SYSCALL (entry 64) is callable from user (fourth arg is DPL_USER). Second arg 1 marks it as a trap gate.

        ``` c
        161 // - istrap: 1 for a trap (= exception) gate, 0 for an interrupt gate.
        162 //   interrupt gate clears FL_IF, trap gate leaves FL_IF alone
        163 // - sel: Code segment selector for interrupt/trap handler
        164 // - off: Offset in code segment for interrupt/trap handler
        165 // - dpl: Descriptor Privilege Level -
        166 //        privilege required to invoke via int instruction.
        #define SETGATE(gate, istrap, sel, off, d) ...
        ```
  - `vectors.pl`: Perl code generator that produces `vectors.S` (the `vectors` array).

        ``` perl
        29 # sample output:
        30 #   # handlers
        31 #   .globl alltraps
        32 #   .globl vector0
        33 #   vector0:
        34 #     pushl $0
        35 #     pushl $0
        36 #     jmp alltraps
        ```
      - L34: value for `trapframe.err` (CPU pushes for some traps, e.g., page fault).
      - L35: value for `trapframe.trapno` (used by `trap()` to dispatch).
      - L36: All vectors jump to `alltraps`.

  - `mmu.h`

        ``` c
        147 // Gate descriptors for interrupts and traps
        struct gatedesc { ... };
        ~~~
        #define SETGATE(gate, istrap, sel, off, d) ...
        ```
        > {{< figure src="https://i.gyazo.com/8fa3b6b45d6da3faa39f58f1102946dc.png" caption="Intel SDM Vol 3 Ch.6" attr="" attrlink="" >}}

With the IDT set, next see what happens when a trap actually occurs. Every handler jumps to `alltraps`.

- `alltraps` builds a `trapframe` on the stack, then calls `trap()` with it.
  - `x86.h`

        ``` c
        147 // Layout of the trap frame built on the stack ... passed to trap().
        struct trapframe {
          // pushed by pusha
          uint edi, esi, ebp, oesp, ebx, edx, ecx, eax;
          // rest
          ushort gs; ushort padding1; ushort fs; ushort padding2;
          ushort es; ushort padding3; ushort ds; ushort padding4;
          uint trapno;
          // by hardware
          uint err; uint eip; ushort cs; ushort padding5; uint es;
          // when crossing rings
          uint esp; ushort ss; ushort padding6;
        };
        ```
        By the time `alltraps` runs, everything from `ss` up through `trapno` is already on the stack.
  - `trapasm.S`

        ``` c
         3   # vectors.S sends all traps here.
         4 .globl alltraps
         5 alltraps:
         6   # Build trap frame.
         7   pushl %ds
         8   pushl %es
         9   pushl %fs
        10   pushl %gs
        11   pushal

        13   # Set up data segments.
        14   movw $(SEG_KDATA<<3), %ax
        15   movw %ax, %ds
        16   movw %ax, %es

        18   # Call trap(tf), where tf=%esp
        19   pushl %esp
        20   call trap
        21   addl $4, %esp

        23   # Return falls through to trapret...
        24 .globl trapret
        25 trapret:
        26   popal
        27   popl %gs
        28   popl %fs
        29   popl %es
        30   popl %ds
        31   addl $0x8, %esp  # trapno and errcode
        32   iret
        ```
        - L6-11: Build the rest of the `trapframe`.
        - L15-16: Set data segments (`%ds`, `%es`).

          > {{< figure src="https://i.gyazo.com/4359a1ecc77942c016a757401ac0a4f6.jpg" caption="Stack after L16" attr="" attrlink="" >}}
          Source: [commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)

        - L18-20: Call `trap()` with pointer to the built `trapframe` (`%esp`).
        - L26-30: Pop what was pushed at L6-11.
        - L31: Skip `trapno` and `errcode`.
        - L32: `iret` — pops `%cs` `%eip` `%eflags` `%esp` `%ss` (for ring changes) and resumes the interrupted program.

# Code: C trap handler
- `trap()` — called from `alltraps`.

    ``` c
    36 void
    37 trap(struct trapframe *tf)
    38 {
    39   if(tf->trapno == T_SYSCALL){
    40     if(myproc()->killed)
    41       exit();
    42     myproc()->tf = tf;
    43     syscall();
    44     if(myproc()->killed)
    45       exit();
    46     return;
    47   }
    
    50   switch(tf->trapno){
                .
                .
                .
    ```
    Dispatch based on `trapno` pushed by the IDT handler.

# Code: System calls
Here we follow the system-call path from `trap()`. First, how the very first system call is made (see “Code: The first system call”).

- `initcode.S`

    ``` c
    8 # exec(init, argv)
    9 .globl start
    10 start:
    11   pushl $argv
    12   pushl $init
    13   pushl $0  // where caller pc would be
    14   movl $SYS_exec, %eax
    15   int $T_SYSCALL
    ```
  - L11-12: Push arguments.
  - L13: Push return address for the syscall. This first syscall never returns, so any value is fine (`call` would normally push it automatically).
  - L14: Put syscall number in `%eax`.
  - L15: Trigger syscall with `int`.

From `trap()` the flow enters `syscall()`.

- `syscall.c`

    ``` c
    131 void
    132 syscall(void)
    133 {
    134   int num;
    135   struct proc *curproc = myproc();

    137   num = curproc->tf->eax;
    138   if(num > 0 && num < NELEM(syscalls) && syscalls[num]) {
    139     curproc->tf->eax = syscalls[num]();
    140   } else {
    141     cprintf("%d %s: unknown sys call %d\n",
    142             curproc->pid, curproc->name, num);
    143     curproc->tf->eax = -1;
    144   }
    }
    ```

  - L137: Take the syscall number from `%eax` in the trapframe.
  - L139/143: Place the return value in `%eax` (syscall return register). L143 handles unknown syscalls.

        ``` c
        107 static int (*syscalls[])(void) = {
        108 [SYS_fork]    sys_fork,
        109 [SYS_exit]    sys_exit,
        110 [SYS_wait]    sys_wait,
        111 [SYS_pipe]    sys_pipe,
        112 [SYS_read]    sys_read,
        113 [SYS_kill]    sys_kill,
        114 [SYS_exec]    sys_exec,
                    ...
        ```
- Helper for args: `argint()`  
  Syscall arguments are on the user stack (`tf->esp`). Example usage:

        ``` c
        286 int
        287 sys_open(void)
        288 {
        289   char *path;
        290   int fd, omode;
        291   struct file *f;
        292   struct inode *ip;

        294   if(argstr(0, &path) < 0 || argint(1, &omode) < 0)
        295     return -1;
        ```
        - First argument is the index, second is where to store the value.
  - `syscall.c`

        ``` c
        48 // Fetch the nth 32-bit system call argument.
        49 int
        50 argint(int n, int *ip)
        51 {
        52   return fetchint((myproc()->tf->esp) + 4 + 4*n, ip);
        }
        ``` 
        - `+4`: skip return address pushed by `call`.
        - `+4*n`: advance to the nth argument.
  - `syscall.c`

        ``` c
        16 // Fetch the int at addr from the current process.
        17 int
        18 fetchint(uint addr, int *ip)
        19 {
        20   struct proc *curproc = myproc();

        22   if(addr >= curproc->sz || addr+4 > curproc->sz)
        23     return -1;
        24   *ip = *(int*)(addr);
        25   return 0;
        }
        ```
      - L22: Validate user-space address.
      - L24: Read it.

- Other helpers include `argptr()`, `argstr()`, `argfd()`.

# Exercises
My answer to the exercise in the [commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf):

> Add a new system call to get the current UTC time and return it to the user program. You may want to use the helper function cmostime (7552) to read the real-time clock. The file date.h contains the definition of struct rtcdate (0950), which you will provide as an argument to cmostime as a pointer.

[Answer gist](https://gist.github.com/utam0k/1c04a96d7d1f16885f85562a5747bcf7)

Next time we’ll follow what happens when `trap()` handles an interrupt and look at drivers.

---
If you have comments or corrections, please contact me on [Twitter](https://twitter.com/utam0k) or open an [Issue](https://github.com/utam0k/utam0k.github.io/issues/1).
