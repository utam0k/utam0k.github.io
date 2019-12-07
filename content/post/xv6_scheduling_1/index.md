---
title: "詳解xv6 Scheduling 1"
date: 2019-11-20T00:00:00+09:00
tags: [xv6, os]
draft: true
---

[詳解xv6の目次]({{< ref "post/xv6_index">}})  
{{< columns >}}
[前の記事]({{< ref "post/xv6_traps_interrupts_drivers_1">}})
{{< endcolumns >}}
- - -

- - -
### アドベントカレンダーの読者向け説明用
この記事はxv6の説明をシリーズでしているスケジュール編です。  
アドベントカレンダー向けに話が完結しそうなスケジューラの話を選びました。  
xv6というOSの説明や動かし方はこのシリーズの[はじめに]({{< ref "post/xv6_intro" >}})をよんでくださると助かります。
- - -

この章は話としては以下のように説明していきます。

1. コンテキストスイッチの方法(本記事)
1. スケジューラによるプロセス切り替えの説明(本記事)
1. sleep/wakeupでのプロセス切り替えの方法(次回の記事)

# スケジューリングのシーケンス図
ざっくりとタイマー割り込みからスケジューラが呼ばれ次のプロセスに移り変わるまでの流れです。  
newプロセスは時間が経過してシーケンス図でのoldプロセスに移り変わっていきます。  
newプロセスが処理を再開する箇所はnewプロセスがoldだった時の`swtch()`を呼び出した直後となるはずです。

{{% figure src="sequence.png" %}}

# Code: Context switching
xv6がどのようにしてプロセスの切り替えを行っているのか説明します。  
まず、抑えておいてほしい点です。

1. 各CPUごとにスケジューラが存在している
1. 各プロセスは自分自身のカーネルスタックを保持している

TODO: 図を入れる
図は２つのユーザプロセス(shellとcat)がスケジューラによってどのように切り替わるのを説明した大まかな図です。

1. shellプロセスはシステムコールや割り込み(e.g.タイマー割り込み)によってshellプロセスのカーネルスレッドに移行
1. shellプロセスのコンテキストを保存
1. スケジューラスレッドにコンテキストスイッチ
1. スケジューリングが走る
1. catプロセスのカーネルスレッドにコンテキストスイッチ
1. コンテキストをリストアしてcatプロセスに移行

## swtch()
スレッドのsave/restoreを行う関数  
違うスレッドへの変更は実質、`%eip`と`%esp`の変更を意味します。  
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
L11-12: 引数でoldとnewの`context`のポインタが渡されている

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

L14-18: 現在のプロセスの`context`の保存

  - callによって`eip`は保存されている

L21: 引数で渡されたoldに現在のスタックポインタ、つまり保存した`context`を代入
L22: 引数で渡されたnewをスタックポインタに変更する

L24-29: 新しいプロセスの`context`の復元

  - retによって`eip`は復元される

# Code: Scheduling
## trap()
## yield()
## sched()
## scheduler()
無限ループになっている  
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

---
コメントや間違いなどがある場合は[Twitter](https://twitter.com/utam0k)に連絡してもらうか
[Issue](https://github.com/utam0k/utam0k.github.io/issues/1)に書いていただくと助かります