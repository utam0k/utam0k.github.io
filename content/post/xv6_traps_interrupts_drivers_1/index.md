---
title: "詳解xv6 Traps, interrupts, and drivers 1"
date: 2019-06-25T09:00:00+09:00
tags: [xv6, os]
---

[詳解xv6の目次]({{< ref "post/xv6_index">}})  
[前の記事]({{< ref "post/xv6_pagetable_2">}})
- - -
本章では特別な役割をもったいろいろなレジスタが出現します。  
ここでは詳しい説明を避けます~~サボります~~。  
その代わりに[素晴らしい資料のリンク](https://ja.wikibooks.org/wiki/X86%E3%82%A2%E3%82%BB%E3%83%B3%E3%83%96%E3%83%A9/x86%E3%82%A2%E3%83%BC%E3%82%AD%E3%83%86%E3%82%AF%E3%83%81%E3%83%A3#%E6%B1%8E%E7%94%A8%E3%83%AC%E3%82%B8%E3%82%B9%E3%82%BF_(GPR))を貼っておきます。適宜確認することをおすすめします。

# Systems calls, exceptions, and interrupts
ユーザプログラムからカーネルに変わる3パターン

1. システムコール(Sytem call)
1. 例外(Exception)
1. 割り込み(Interrupt), トラップ(Trap)
  - `int`命令で呼ばれる
  - トラップ: 現在実行中のプロセスが発生させるもの
  - 割り込み: 現在実行中のプロセスとは関係ない

# X86 protection
**$ 保護レベル**  
`%cs`レジスタの下位2ビットがCPLを示す  

- DPL(Descriptor Privilege Level)
- CPL(Current Privilege Level)

0レベル: カーネルモード  
3レベル: ユーザモード  

**$ IDT**  
IDT: Interrupt Descriptor Table  
割り込みとそれに対応するハンドラのテーブル  
カーネルはこのテーブルを作る必要がある  
[詳しいおすすめ記事](http://softwaretechnique.jp/OS_Development/kernel_development02.html)


**$ int命令の処理**  

- `int n`: n番目のIDTエントリの例外
- 処理中に`%cs` `%eip`を操作する  
  `%cs` `%eip`は操作されても困らないようにする必要がある(スタックに退避させるなど)
- int命令の処理手順(ハードウェアがやる)
  1. IDTからn番目のディスクリプタをフェッチ
  2. `%cs`のCPLフィールドをチェックが`DPL`以下であることを確認
  3. ターゲットセグメントセレクタがPL<CPLであった場合にのみ、CPUの内部レジスタである`%esp`と`%ss`を保存
  4. `%ss`と`%esp`をタスクセグメントディスクリプタからロード
  5. `%ss` `%esp` `%eflags` `%cs` `%eip`の順でスタックに積む
  6. `%eflags`の割り込み可能フラグ(IF)をクリア
  7. `%cs`と`%eip`にディスクリプタの値(詳細は5章, `switchuvm()`でTSSに値をセットしている)をセット

    > {{< figure src="https://raw.githubusercontent.com/msyksphinz/xv6_translate/master/images/figure3-01.JPG" caption="int実行後のスタックの状態" attr="" attrlink="" >}}
    Source: [commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)

`ret`ではなく`iret`命令で`int`命令のスタックを回復

# Code: Assembly trap handlers
`main.c`から呼ばれる`tvinit()`でIDTのセット(not load)  

- `trap.c`

    ``` c
    17 void
    18 tvinit(void)
    19 {
    20   int i;
    21
    22   for(i = 0; i < 256; i++)
    23     SETGATE(idt[i], 0, SEG_KCODE<<3, vectors[i], 0);
    24   SETGATE(idt[T_SYSCALL], 1, SEG_KCODE<<3, vectors[T_SYSCALL], DPL_USER);
    25
    26   initlock(&tickslock, "time");
    27 } 
    ```
    L22-23: 256個のIDTエントリを`vectors`に対応しているハンドラにセット  
    L24: システムコール用のIDTエントリをセット
     - T_SYSCALL(=64番目のエントリ)だけはユーザレベル(∵ 第4引数がDPL_USER)で呼び出し可能
     - 第二引数が1、つまりトラップである

        ``` c
        161 // - istrap: 1 for a trap (= exception) gate, 0 for an interrupt gate.
        162 //   interrupt gate clears FL_IF, trap gate leaves FL_IF alone
        163 // - sel: Code segment selector for interrupt/trap handler
        164 // - off: Offset in code segment for interrupt/trap handler
        165 // - dpl: Descriptor Privilege Level -
        166 //        the privilege level required for software to invoke
        167 //        this interrupt/trap gate explicitly using an int instruction.
        168 #define SETGATE(gate, istrap, sel, off, d)                \
        ```
  - `vectors.pl`  
    `vectors`(アセンブリ: `vectors.S`)を作るPerl製のコードジェネレータ

        ``` perl
        29 # sample output:
        30 #   # handlers
        31 #   .globl alltraps
        32 #   .globl vector0
        33 #   vector0:
        34 #     pushl $0
        35 #     pushl $0
        36 #     jmp alltraps
        37 #   ...
        ```
    - L34 - 35: 後述する`trapframe`に値をセット
      - L34: `trapframe`の`err`の値  
        処理によってはCPUによって自動で積まれる(e.x. PageFault)
      - L35: `trapframe`の`trapno`の値  
        何の処理なのかを振り分ける値(`trap()`で使われる)
    - L36: 全てのvectorは`alltraps`に飛ぶ

  - `mmu.h`

        ``` c
        147 // Gate descriptors for interrupts and traps
        148 struct gatedesc {
        149   uint off_15_0 : 16;   // low 16 bits of offset in segment
        150   uint cs : 16;         // code segment selector
        151   uint args : 5;        // # args, 0 for interrupt/trap gates
        152   uint rsv1 : 3;        // reserved(should be zero I guess)
        153   uint type : 4;        // type(STS_{IG32,TG32})
        154   uint s : 1;           // must be 0 (system)
        155   uint dpl : 2;         // descriptor(meaning new) privilege level
        156   uint p : 1;           // Present
        157   uint off_31_16 : 16;  // high bits of offset in segment
        158 };
        ~~~
        160 // Set up a normal interrupt/trap gate descriptor.
        161 // - istrap: 1 for a trap (= exception) gate, 0 for an interrupt gate.
        162 //   interrupt gate clears FL_IF, trap gate leaves FL_IF alone
        163 // - sel: Code segment selector for interrupt/trap handler
        164 // - off: Offset in code segment for interrupt/trap handler
        165 // - dpl: Descriptor Privilege Level -
        166 //        the privilege level required for software to invoke
        167 //        this interrupt/trap gate explicitly using an int instruction.
        168 #define SETGATE(gate, istrap, sel, off, d)                \
        169 {                                                         \
        170   (gate).off_15_0 = (uint)(off) & 0xffff;                \
        171   (gate).cs = (sel);                                      \
        172   (gate).args = 0;                                        \
        173   (gate).rsv1 = 0;                                        \
        174   (gate).type = (istrap) ? STS_TG32 : STS_IG32;           \
        175   (gate).s = 0;                                           \
        176   (gate).dpl = (d);                                       \
        177   (gate).p = 1;                                           \
        178   (gate).off_31_16 = (uint)(off) >> 16;                  \
        179 }
        ```
        > {{< figure src="https://i.gyazo.com/8fa3b6b45d6da3faa39f58f1102946dc.png" caption="Intel SDM Volume 3 Chapter 6" attr="" attrlink="" >}}

ここまででIDEのセットが終わりました。次に実際に呼び出されたときの処理を見ていきます。  
まずは前述したとおり、全てのハンドラは`alltraps`を呼び出します。  

- `alltraps`  
    構造体`trapframe`を構築し, 構築した`trapframe`を引数として`trap()`呼び出す  
  - `x86.h`

        ``` c
        147 //PAGEBREAK: 36
        148 // Layout of the trap frame built on the stack by the
        149 // hardware and by trapasm.S, and passed to trap().
        150 struct trapframe {
        151   // registers as pushed by pusha
        152   uint edi;
        153   uint esi;
        154   uint ebp;
        155   uint oesp;      // useless & ignored
        156   uint ebx;
        157   uint edx;
        158   uint ecx;
        159   uint eax;
        160
        161   // rest of trap frame
        162   ushort gs;
        163   ushort padding1;
        164   ushort fs;
        165   ushort padding2;
        166   ushort es;
        167   ushort padding3;
        168   ushort ds;
        169   ushort padding4;
        170   uint trapno;
        171
        172   // below here defined by x86 hardware
        173   uint err;
        174   uint eip;
        175   ushort cs;
        176   ushort padding5;
        177   uint es;
        178
        179   // below here only when crossing rings, such as from user to kernel
        180   uint esp;
        181   ushort ss;
        182   ushort padding6;
        183 };
        ```
        `alltraps`が呼び出される時点でL182 - 169まではスタックに積んである状態
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
        12
        13   # Set up data segments.
        14   movw $(SEG_KDATA<<3), %ax
        15   movw %ax, %ds
        16   movw %ax, %es
        17
        18   # Call trap(tf), where tf=%esp
        19   pushl %esp
        20   call trap
        21   addl $4, %esp
        22
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
        - L6 - 11: `trapframe`を構築  
        - L15 - 16: データセグメントをセットする
          - `%ds`: データセグメント
          - `%es`: エクストラセグメント  

          > {{< figure src="https://i.gyazo.com/4359a1ecc77942c016a757401ac0a4f6.jpg" caption="L16でのスタックの状態" attr="" attrlink="" >}}
          Source: [commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)

        - L18 - 20: `trap()`を作ったtrap構造体を引数にして呼び出す
          - L19: trapへの引数として構築した`trapframe`構造体のポイント(現在の`%esp`)を渡す
          - L20: 呼び出し  
          - L21: trapへの渡した引数(L19)を`%esp`を加算することでpop
        - L26 - 30: L6 - 11のも巻き戻し
        - L31: trapnoとerrorcodeをスキップ
        - L32: `iret`
          - Interrupt Return
          - pop `%cs` `%eip` `%flags` `%esp` `%ss`(異なる特権へのリターンのため)
          - 中断していたプログラム(スタックに積まれているアドレス)を再開

# Code: C trap handler
  - `trap()`
    `alltraps`から呼ばれる

    ``` c
    36 //PAGEBREAK: 41
    37 void
    38 trap(struct trapframe *tf)
    39 {
    40   if(tf->trapno == T_SYSCALL){
    41     if(myproc()->killed)
    42       exit();
    43     myproc()->tf = tf;
    44     syscall();
    45     if(myproc()->killed)
    46       exit();
    47     return;
    48   }
    49
    50   switch(tf->trapno){
                .
                .
                .
    ```
    IDTエントリにセットされているハンドラで積まれている`trapno`によって処理を振り分ける

# Code: System calls
ここでは`trap()`から呼び出されるのがシステムコールの場合の処理を追っていきます。  
まずは最初のシステムコールの呼び方みてxv6でのシステムコールの呼び方を見ていきます。(該当の章は Code: The first system call)

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
  - L11 - 12: 引数をスタックに積む
  - L13: システムコールから戻るときのアドレスをスタックに積む
    - 最初のシステムコールのため戻ってくることはないため適当な値
    - `call`命令は自動的に戻るときのアドレスをスタックに積む
  - L14: `%eax`に該当するシステムコールの番号を格納
  - L15: `int`でシステムコールを呼び出し

xv6のシステムコールの処理を追っていきます。  
前述した`trap()`から`syscall()`が呼ばれたところからです。  

- `syscall.c`

    ``` c
    131 void
    132 syscall(void)
    133 {
    134   int num;
    135   struct proc *curproc = myproc();
    136
    137   num = curproc->tf->eax;
    138   if(num > 0 && num < NELEM(syscalls) && syscalls[num]) {
    139     curproc->tf->eax = syscalls[num]();
    140   } else {
    141     cprintf("%d %s: unknown sys call %d\n",
    142             curproc->pid, curproc->name, num);
    143     curproc->tf->eax = -1;
    144   }
    145 }
    ```

  - L137: `trapframe`の`%eax`から該当するシステムコールの番号を取り出し呼ぶ
  - L139, 143: 返り値を`trapframe`の`%eax`に格納
    - システムコールは`%eax`に返り値が格納されている
    - L143: エラー時の処理
    - L139: システムコールの実行
  
          ``` c
          107 static int (*syscalls[])(void) = {
          108 [SYS_fork]    sys_fork,
          109 [SYS_exit]    sys_exit,
          110 [SYS_wait]    sys_wait,
          111 [SYS_pipe]    sys_pipe,
          112 [SYS_read]    sys_read,
          113 [SYS_kill]    sys_kill,
          114 [SYS_exec]    sys_exec,
                    .
                    .
                    .
          ```
- 引数のヘルパー関数: `argint()`   
  前提: システムコールの呼び出しはスタック(`tf->esp`)に積まれている  
  - 使われ方の例

        ``` c
        286 int
        287 sys_open(void)
        288 {
        289   char *path;
        290   int fd, omode;
        291   struct file *f;
        292   struct inode *ip;
        293
        294   if(argstr(0, &path) < 0 || argint(1, &omode) < 0)
        295     return -1;
        ```
        - L294: 
          - 第1引数: 何個目の引数か
          - 第2引数: 引数の値を入れる変数
  - `syscall.c`

        ``` c
        48 // Fetch the nth 32-bit system call argument.
        49 int
        50 argint(int n, int *ip)
        51 {
        52   return fetchint((myproc()->tf->esp) + 4 + 4*n, ip);
        53 }
        ``` 
        - L52: 
          - `+4`: `call`命令で積まれた戻るためのアドレスが格納されている
          - `+4*n`: 該当の引数まで
  - `syscall.c`

        ``` c
        16 // Fetch the int at addr from the current process.
        17 int
        18 fetchint(uint addr, int *ip)
        19 {
        20   struct proc *curproc = myproc();
        21
        22   if(addr >= curproc->sz || addr+4 > curproc->sz)
        23     return -1;
        24   *ip = *(int*)(addr);
        25   return 0;
        26 }
        ```
      - L22: ユーザー空間からの引数なので注意が必要
      - L24: 読み込む

- 他にも`argptr()` `argstr()` `argfd()`などある

# Exercises
[commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)
についてる問題の僕の回答を載せておきます。  

> Add a new system call to get the current UTC time and return it to the user program. You may want to use the helper function, cmostime (7552), to read the real time clock. The file date.h contains the definition of the struct rtcdate (0950), which you will provide as an argument to cmostime as a pointer.

[回答gist](https://gist.github.com/utam0k/1c04a96d7d1f16885f85562a5747bcf7)

次回は`trap()`から呼び出されるのが割り込みだった場合の処理、ドライバを追っていきます。