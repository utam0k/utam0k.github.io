---
title: "Annotated xv6 Scheduling 1"
date: 2019-12-20T00:00:00+09:00
tags: [xv6, os]
---

[Annotated xv6 table of contents]({{< ref "post/xv6_index">}})  
[Previous post]({{< ref "post/xv6_traps_interrupts_drivers_1">}})
- - -

- - -
### Note for Advent Calendar readers
This is Day 20 of the [Homebrew OS Advent Calendar 2019](https://adventar.org/calendars/4027). It’s part of my xv6 explanation series, focusing on scheduling because it’s self-contained for this event. For why xv6, how the series works, or how to run it, please read the [introduction]({{< ref "post/xv6_intro" >}}).
- - -

This chapter covers:

1. How context switching works (this post)
1. How the scheduler switches processes (this post)
1. How sleep/wakeup switches processes (next post)

# Scheduling sequence diagram
Here’s the rough flow from a timer interrupt to the scheduler picking the next process. Over time the “new” process becomes the “old” one. The point where the new process resumes is right after it previously called `swtch()` when it was the old process.

{{% figure src="sequence.png" %}}

# Code: Context switching
How xv6 switches processes. Key points:

1. Each CPU has its own scheduler.
1. Each process keeps its own kernel stack.

> {{< figure src="fig5-1.png" >}}
Source: [commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)

The figure shows, at a high level, two user processes (shell and cat) being switched by the scheduler.

1. The shell process enters its kernel thread via a system call or interrupt (e.g., timer interrupt).
1. Save the shell process context.
1. Context switch to the scheduler thread.
1. Run scheduling.
1. Context switch to the cat process’s kernel thread.
1. Restore its context and continue in cat.

## swtch()
This function saves/restores a thread. Switching threads essentially means changing `%eip` and `%esp`.
`entry.c`
```c
 9 .globl swtch
10 swtch:
11   movl 4(%esp), %eax
12   movl 8(%esp), %edx
13
14   # Save old callee-saved registers
15   pushl %ebp
16   pushl %ebx
17   pushl %esi
18   pushl %edi
19
20   # Switch stacks
21   movl %esp, (%eax)
22   movl %edx, %esp
23
24   # Load new callee-saved registers
25   popl %edi
26   popl %esi
27   popl %ebx
28   popl %ebp
29   ret
```
L11-12: Arguments pass pointers to `context` `**old` and `*new`.

  - `proc.h`

    ```c
    27 struct context {
    28   uint edi;
    29   uint esi;
    30   uint ebx;
    31   uint ebp;
    32   uint eip;
    33 };
    ```

L14-18: Save the current process’s `context` (callee-saved registers).

  - `eip` is saved by the call instruction.

L21: Store the current stack pointer (the saved context) into `old`.
L22: Set the stack pointer to `new`.
L24-29: Restore the new process’s `context`.

  - `ret` restores `eip`.

# Code: Scheduling
## trap()
On timer interrupt, `yield()` is called. `trap.c`
```c
36 void
37 trap(struct trapframe *tf)
~~~
103   // Force process to give up CPU on clock tick.
104   // If interrupts were on while locks held, would need to check nlock.
105   if(myproc() && myproc()->state == RUNNING &&
106      tf->trapno == T_IRQ0+IRQ_TIMER)
107     yield();
```

## yield()
`proc.c`
```c
384 // Give up the CPU for one scheduling round.
385 void
386 yield(void)
387 {
388   acquire(&ptable.lock);  //DOC: yieldlock
389   myproc()->state = RUNNABLE;
390   sched();
391   release(&ptable.lock);
392 }
```
L388: Acquire `ptable` lock.  
L389: Mark the current process `RUNNABLE` instead of `RUNNING`.  
L390: Call `sched()`.  
L391: Release `ptable` lock (execution resumes here after switching back).

## sched()
`proc.c`
```c
365 void
366 sched(void)
367 {
371   if(!holding(&ptable.lock))
372     panic("sched ptable.lock");
~~~
379   intena = mycpu()->intena;
380   swtch(&p->context, mycpu()->scheduler);
381   mycpu()->intena = intena;
382 }
```
L371: Ensure the lock is held so other CPUs can’t change process state.  
L380: Context switch to the scheduler.

About the `ptable` lock:

- `yield()` acquires/releases it.
- `sched()` assumes the caller already holds/releases it; unusual but necessary.
- During `swtch()` invariants aren’t maintained; without the lock, another CPU could see process A as `RUNNABLE`, choose it, while A’s kernel stack is mid-switch.

## scheduler()
Now the main scheduling loop: find the next process and switch.
`proc.c`
```c
322 void
323 scheduler(void)
324 {
325   struct proc *p;
326   struct cpu *c = mycpu();
327   c->proc = 0;
328
329   for(;;){
330     // Enable interrupts on this processor.
331     sti();
332
333     // Loop over process table looking for process to run.
334     acquire(&ptable.lock);
335     for(p = ptable.proc; p < &ptable.proc[NPROC]; p++){
336       if(p->state != RUNNABLE)
337         continue;
338
339       // Switch to chosen process.  It is the process's job
340       // to release ptable.lock and then reacquire it
341       // before jumping back to us.
342       c->proc = p;
343       switchuvm(p);
344       p->state = RUNNING;
345
346       swtch(&(c->scheduler), p->context);
347       switchkvm();
348
349       // Process is done running for now.
350       // It should have changed its p->state before coming back.
351       c->proc = 0;
352     }
353     release(&ptable.lock);
354
355   }
356 }
```
L329: Infinite loop.  
L335-337: Search for a `RUNNABLE` process `p`.  
L343: Set `p`’s TSS (Task State Segment) in TR so interrupts use `p`’s kernel stack.  
L342: Set `c->proc` so `myproc()` returns the running process.

  - `proc.c`

     ```c
     57 struct proc*
     58 myproc(void) {
     59   struct cpu *c;
     60   struct proc *p;
     61   pushcli();
     62   c = mycpu();
     63   p = c->proc;
     64   popcli();
     65   return p;
     66 }
     ```

L346: Context switch to `p`.  
L347: Switch address spaces ([switchkvm]({{< ref "post/xv6_pagetable_1" >}}/#switchkvm)).  
L351: When back in the scheduler, clear `c->proc`.

If no runnable process is found:  
L334/353: Lock `ptable` only while searching.

- If the scheduler idled while holding the lock, other CPUs couldn’t context-switch or run syscalls needing `ptable`.
- Processes couldn’t be marked `RUNNABLE`.
- Prevents duplicate pids and duplicated process table entries.

L331: Enable interrupts.

- Shell etc. are often blocked on I/O; if interrupts were disabled while idling, I/O waits would never finish.

- - -
We traced xv6 from context switch to scheduling. Debugging with gdb while reading the code makes it more fun! Tomorrow’s Advent post is [SugarHigh_bin](https://adventar.org/users/20256) on “Concurrent symbolic fuzzing with memory model awareness.”
- - -

---
If you have comments or corrections, please contact me on [Twitter](https://twitter.com/utam0k) or open an [Issue](https://github.com/utam0k/utam0k.github.io/issues/1).
