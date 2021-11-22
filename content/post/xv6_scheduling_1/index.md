---
title: "詳解xv6 Scheduling 1"
date: 2019-12-20T00:00:00+09:00
tags: [xv6, os]
---

[詳解xv6の目次]({{< ref "post/xv6_index">}})  
[前の記事]({{< ref "post/xv6_traps_interrupts_drivers_1">}})
- - -

- - -
### アドベントカレンダーの読者向け説明用
[自作OSアドベントカレンダー 2019](https://adventar.org/calendars/4027) の20日目の記事です。  
この記事はxv6の説明をシリーズでしているスケジュール編です。  
アドベントカレンダー向けに話が完結しそうなスケジューラの話を選びました。  
xv6というなぜこのシリーズを書いているのか、OSの説明や動かし方はこのシリーズの[はじめに]({{< ref "post/xv6_intro" >}})をよんでくださると助かります。
- - -

この章は以下のように説明をしていきます。

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

> {{< figure src="fig5-1.png" >}}
Source: [commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)


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
L11-12: 引数で`context`の`**old`と`*new`が渡されている

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
タイマー割り込みで`yield()`が呼ばれる。  
`trap.c`
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
L388: `ptable`のロックを取得  
L389: 動かしているプロセスを`RUNNING`から`RUNNABLE`にする  
L390: `shed()`を呼び出す  
L391: `ptable`のロックを解放(プロセス再開はここから)  

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
L371: 他のCPUがプロセスの状態等を書き換える可能性があるためロック  
L380: スケジューラにコンテキストスイッチ

`ptable`のロックについて  

- `yield()`でロックを取得して開放している
- `sched()`は`yield()`(呼び出し元)がロックの取得/解放しているのが前提になっているが普通ではない
- コンテキストスイッチの場合`swtch()`の実行中は不変条件を満たしていない状態になる
  ロックされていない場合
    - プロセスAが実行中に`yield()`が呼び出され状態を`RUNNABLE`にセットし、`swtch()`がプロセスAのカーネルスタックの使用する
    - しかし別のCPUがプロセスAが`RUNNABLE`なのでプロセスAを実行することを決定するかもしれない

## scheduler()
いよいよ、メインのスケジューリングの箇所です。  
次に動かすプロセスを見つけて、コンテキストスイッチします。  
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
L329: 無限ループになっている  
L335-337: 次に動かすプロセス(`RUNNEABLE`なプロセス)`p`を探す  
L343: `p`のTSS(Task State Segment)をTRにセットして、割り込みなどがあった時に`p`のカーネルスタックになるようにする  
L342: `myproc()`で実行中のプロセスを取得できるようにセット

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

L346: `p`にコンテキストスイッチ  
L347: メモリ空間の切り替え([switchkvm]({{< ref "post/xv6_pagetable_1" >}}/#switchkvm))  
L351: 動いているプロセスはスケジューラなため、リセットしておく  

もし実行できるプロセスが見つからなかった時の想定  
L334/353: 実行できるプロセスを探している間のみ`ptable`をロック

  - `ptable`がロックしたままの状態でアイドルすると他のCPUもコンテキストスイッチや`ptable`を必要とするシステムコールができなくなる
  - プロセスの状態を`RUNNABLE`にできなくなる
  - pidの重複を防ぐ
  - プロセステーブルの重複を防ぐ

L331: 割り込みの許可

  - シェルなどはよくI/O待ち状態で実行できない状態になるのに割り込み不可の状態でアイドルするとI/O待ちは永遠に終わらなくなる

- - -
xv6のコンテキストスイッチからスケジューリングまでを追ってみました。  
gdbを使いデバッグしながら動作を確認すると楽しくコードを読めると思います！  
明日は[SugarHigh_bin](https://adventar.org/users/20256)さんの「メモリモデルを考慮した並行記号ファジング」です。  
- - -

---
コメントや間違いなどがある場合は[Twitter](https://twitter.com/utam0k)に連絡してもらうか
[Issue](https://github.com/utam0k/utam0k.github.io/issues/1)に書いていただくと助かります