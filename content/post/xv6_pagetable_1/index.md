---
title: "詳解xv6 Page tables 1"
date: 2019-03-05T18:35:02+09:00
tags : [xv6, os]
---

[詳解xv6の目次]({{< ref "post/xv6_index">}})  
[次の記事]({{< ref "post/xv6_pagetable_2">}})
- - -

# 単語説明
- PA(Physical Address): 物理アドレス
- VA(Virtual Address): 仮想アドレス

#### ページング関係
- [ページングについて参考にしたサイト](http://softwaretechnique.jp/OS_Development/kernel_development07.html)
- PTE: ページテーブルエントリ
    - xv6では1PTEで4KBのアドレス空間を表現する

    - > [![Image](https://gyazo.com/76f1ccd02fb190c6e714b3f2cca72e2e/thumb/1000)](https://gyazo.com/76f1ccd02fb190c6e714b3f2cca72e2e)
        Source: [０から作るOS開発　ページングその１　ページとPTEとPDE](http://softwaretechnique.jp/OS_Development/kernel_development07.html)
    - 4KB分のメモリの最初のアドレスを設定する
    - ページテーブルはPTEが1024個で構成されている
        - 1ページテーブルで4KB * 1024  = 4MBのアドレス空間を表現できる
- PDE: ページディレクトリエントリ
    - ページテーブルを指す  

    - > [![Image](https://gyazo.com/1498fc91c4888457c8f88dca9f3c65d8/thumb/1000)](https://gyazo.com/1498fc91c4888457c8f88dca9f3c65d8)
        Source: [０から作るOS開発　ページングその１　ページとPTEとPDE](http://softwaretechnique.jp/OS_Development/kernel_development07.html)
- PDT: ページディレクトリテーブル
    - ソースコード内では`pgdir`で表される
    - PDEを1024個で構成されるテーブル
    - 1PDTで4MB * 1024  = 4GBのアドレス空間を表現できる

```
Page Directory Table         4MB*1024=4GB
+-------------------------------------------------------------------+
| +---------+           +---------+                    +---------+  |
| | PDE[0]  |           | PDE[1]  |         ...        |PDE[1023]|  |
| +----+----+           +----+----+                    +----+----+  |
|      |                     |                              |       |
+-------------------------------------------------------------------+
       |                     |                              |
       v                     v                              v
+--------------+      +--------------+               +--------------+  +--+
| +----------+ |      | +----------+ |               | +----------+ |     |
| |  PTE[0]  | |      | |  PTE[0]  | |               | |  PTE[0]  | |     |
| +----------+ |      | +----------+ |               | +----------+ |     |
| +----------+ |      | +----------+ |               | +----------+ |     |
| |  PTE[1]  | |      | |  PTE[1]  | |      ...      | |  PTE[1]  | |     |
| +----------+ |      | +----------+ |               | +----------+ |     | 4KB*1024=4MB
|       .      |      |       .      |               |       .      |     |
|       .      |      |       .      |               |       .      |     |
|       .      |      |       .      |               |       .      |     |
| +----------+ |      | +----------+ |               | +----------+ |     |
| | PTE[1023]| |      | | PTE[1023]| |               | | PTE[1023]| |     |
| +----------+ |      | +----------+ |               | +----------+ |     |
+--------------+      +--------------+               +--------------+  +--+
   Page Table            Page Table                     Page Table
```

#  Code: creating an address space
本章ではxv6が作るカーネルのアドレス空間、つまりページングの設定を行うコードの解説です。
カーネルのアドレス空間のVAとPAは図のようにマッピングしていきます。  
**本章の解説するコードの目的は図のマッピングを作ることです。**

> {{% figure src="memorylayout.png" %}}
Source: [commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)

どのプロセスにもカーネル用の仮想アドレス空間が設定されています。
図のように1プロセスには4GBの仮想メモリ空間が割り当てられますが、
KERNBASE~4GBまではカーネル用の仮想アドレス空間になっています。
カーネル用のアドレス空間はVAとPAが必ず図のように固定でマッピングされます。

### シーケンス図
エラー処理等を省いたざっくりとしたシーケンスです。
今見ている関数はどこから呼ばれるんだっけとなったときに見てもらえればと思います。
{{% figure src="sequence_without_error_handling.png" %}}

### main()
メイン関数

- `main.c`

    ```c
    14 // Bootstrap processor starts running C code here.
    15 // Allocate a real stack and switch to it, first
    16 // doing some setup required for memory allocator to work.
    17 int
    18 main(void)
    19 {
    20   kinit1(end, P2V(4*1024*1024)); // phys page allocator
    21   kvmalloc();      // kernel page table
    ~~~
    37   mpmain();        // finish this processor's setup
    38 }
    ```
- L21: カーネル用ページテーブルの作成

### kvmalloc()
カーネル用のページテーブルを作成して作成したページテーブルに切り替える

- 作成するのはページディレクトリエントリを1つのみ  
- [setupkvm()]({{< ref "#setupkvm">}})はPDEを返すがそれを先頭アドレスとしたPDTとも見れる
- `vm.c`  

    ```c
    138 // Allocate one page table for the machine for the kernel address
    139 // space for scheduler processes.
    140 void
    141 kvmalloc(void)
    142 {
    143   kpgdir = setupkvm();
    144   switchkvm();
    145 }
    ```

### switchkvm()
カーネル用のページテーブルに切り替え

- `vm.c`

    ```c
    147 // Switch h/w page table register to the kernel-only page table,
    148 // for when no process is running.
    149 void
    150 switchkvm(void)
    151 {
    152   lcr3(V2P(kpgdir));   // switch to the kernel page table
    153 }
    ```
- L152: `cr3`レジスタを更新
    - PDTの変更、つまりメモリ空間を変える
    - `cr3` を別のページディレクトリに切り替える = プロセス空間の切り替えに相当
        - `cr3`が`pde[0]`を指せばおっけ

### V2P()

- `memlayout.h`

    ```c
     8 #define KERNBASE 0x80000000         // First kernel virtual address
    ~~~
    11 #define V2P(a) (((uint) (a)) - KERNBASE)
    ```
- L11: カーネルの物理メモリは決め打ちでわかる
- > {{% figure src="memorylayout_red.png" %}}
Source: [commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf) + 赤色書き加え

### setupkvm()
カーネルのPDEを作成

- `vm.c`

    ```c
    103 // This table defines the kernel's mappings, which are present in
    104 // every process's page table.
    105 static struct kmap {
    106   void *virt;
    107   uint phys_start;
    108   uint phys_end;
    109   int perm;
    110 } kmap[] = {
    111  { (void*)KERNBASE, 0,             EXTMEM,    PTE_W}, // I/O space
    112  { (void*)KERNLINK, V2P(KERNLINK), V2P(data), 0},     // kern text+rodata
    113  { (void*)data,     V2P(data),     PHYSTOP,   PTE_W}, // kern data+memory
    114  { (void*)DEVSPACE, DEVSPACE,      0,         PTE_W}, // more devices
    115 };
    116
    117 // Set up kernel part of a page table.
    118 pde_t*
    119 setupkvm(void)
    120 {
    121   pde_t *pgdir;
    122   struct kmap *k;
    123
    124   if((pgdir = (pde_t*)kalloc()) == 0)
    125     return 0;
    126   memset(pgdir, 0, PGSIZE);
    127   if (P2V(PHYSTOP) > (void*)DEVSPACE)
    128     panic("PHYSTOP too high");
    129   for(k = kmap; k < &kmap[NELEM(kmap)]; k++)
    130     if(mappages(pgdir, k->virt, k->phys_end - k->phys_start,
    131                 (uint)k->phys_start, k->perm) < 0) {
    132       freevm(pgdir);
    133       return 0;
    134     }
    135   return pgdir;
    136 }
    ```
 
- L105 - 115: `kmap[]`はカーネル用のページングの設定
    - メモリレイアウトの図(Fig2.2)と照らし合わせるとわかりやすい
- L124 - 126: `pgdir`の領域を確保
    - 4096/32 = 128 pte
        - 4エントリしか使用しない(`kmap[]`より)
    - `kalloc()`: カーネルは未使用のページのリスト(`freelist`)で管理している
        - 詳細は次章
        - `kalloc.c`

            ```c
            79 // Allocate one 4096-byte page of physical memory.
            80 // Returns a pointer that the kernel can use.
            81 // Returns 0 if the memory cannot be allocated.
            82 char*
            83 kalloc(void)
            84 {
            85   struct run *r;
            86
            87   if(kmem.use_lock)
            88     acquire(&kmem.lock);
            89   r = kmem.freelist;
            90   if(r)
            91     kmem.freelist = r->next;
            92   if(kmem.use_lock)
            93     release(&kmem.lock);
            94   return (char*)r;
            95 }
        ```
- L129 - 134: `pgdir`を`kmap[]`にあわせていく

### mappages()
仮想アドレスと物理アドレスを紐づける

- `vm.c`

    ```c
    57 // Create PTEs for virtual addresses starting at va that refer to
    58 // physical addresses starting at pa. va and size might not
    59 // be page-aligned.
    60 static int
    61 mappages(pde_t *pgdir, void *va, uint size, uint pa, int perm)
    62 {
    63   char *a, *last;
    64   pte_t *pte;
    65
    66   a = (char*)PGROUNDDOWN((uint)va);
    67   last = (char*)PGROUNDDOWN(((uint)va) + size - 1);
    68   for(;;){
    69     if((pte = walkpgdir(pgdir, a, 1)) == 0)
    70       return -1;
    71     if(*pte & PTE_P)
    72       panic("remap");
    73     *pte = pa | perm | PTE_P;
    74     if(a == last)
    75       break;
    76     a += PGSIZE;
    77     pa += PGSIZE;
    78   }
    79   return 0;
    80 }
    ```
- 引数
    - `pgdir`: ページディレクトリテーブルの先頭アドレス
    - `va`: 仮想アドレス
    - `size`: マッピングするサイズ
    - `pa`: 物理アドレス
    - `perm`: permission
- L66 - 67: PGSIZEにそろえる
    - ex) `PGROUNDDOWN(8193)` => 8192(PGSIZE * 2)
- L69: `va`に対応するページエントリを見つける
- L73: ページテーブルエントリを更新(`pa` + `perm`)
    - `|`で下位12bitの`pa`を上書き(4*3=12byte)  
    - `mmu.h`

        ```c
        93 // Page table/directory entry flags.
        94 #define PTE_P           0x001   // Present
        95 #define PTE_W           0x002   // Writeable
        96 #define PTE_U           0x004   // User
        97 #define PTE_PS          0x080   // Page Size
        ```
- L76 - 77: `PGSIZE`を増やして繰り返す

### walkpgdir() 
`pgdir`の`va`に対応するPTEを見つける

- `vm.c`

    ```c
    32 // Return the address of the PTE in page table pgdir
    33 // that corresponds to virtual address va.  If alloc!=0,
    34 // create any required page table pages.
    35 static pte_t *
    36 walkpgdir(pde_t *pgdir, const void *va, int alloc)
    37 {
    38   pde_t *pde;
    39   pte_t *pgtab;
    40
    41   pde = &pgdir[PDX(va)];
    42   if(*pde & PTE_P){
    43     pgtab = (pte_t*)P2V(PTE_ADDR(*pde));
    44   } else {
    45     if(!alloc || (pgtab = (pte_t*)kalloc()) == 0)
    46       return 0;
    47     // Make sure all those PTE_P bits are zero.
    48     memset(pgtab, 0, PGSIZE);
    49     // The permissions here are overly generous, but they can
    50     // be further restricted by the permissions in the page table
    51     // entries, if necessary.
    52     *pde = V2P(pgtab) | PTE_P | PTE_W | PTE_U;
    53   }
    54   return &pgtab[PTX(va)];
    55 }
    ```
- L41: PDEを取得
    - `mmu.h`

        ```c
        65 // A virtual address 'la' has a three-part structure as follows:
        66 //
        67 // +--------10------+-------10-------+---------12----------+
        68 // | Page Directory |   Page Table   | Offset within Page  |
        69 // |      Index     |      Index     |                     |
        70 // +----------------+----------------+---------------------+
        71 //  \--- PDX(va) --/ \--- PTX(va) --/
        72
        73 // page directory index
        74 #define PDX(va)         (((uint)(va) >> PDXSHIFT) & 0x3FF)
        75
        76 // page table index
        77 #define PTX(va)         (((uint)(va) >> PTXSHIFT) & 0x3FF)
        ~~~
        87 #define PTXSHIFT        12      // offset of PTX in a linear address
        88 #define PDXSHIFT        22      // offset of PDX in a linear address
        ```
    - L67 - 71: 仮想アドレスの構成
        - 前半10bitがPDEのインデックス
        - 次の10bitがPTEのインデックス
    - `pgdir[PDX(va)]`: 該当するPDEを見つける
    - `pgtab[PTX(va)]`: 該当のPTEを見つける
- L42 - 43: PDEが存在した場合
    - `mmu.h`

        ```c
         99 // Address in page table or page directory entry
        100 #define PTE_ADDR(pte)   ((uint)(pte) & ~0xFFF)
        ```
    - > [![Image](https://gyazo.com/1498fc91c4888457c8f88dca9f3c65d8/thumb/1000)](https://gyazo.com/1498fc91c4888457c8f88dca9f3c65d8)
        Source: [０から作るOS開発　ページングその１　ページとPTEとPDE](http://softwaretechnique.jp/OS_Development/kernel_development07.html)
- L44 - 53: 引数の`alloc`が真ならば新たにページテーブルを作成し`pde`を更新

### まとめ
{{% figure src="sequence.png" %}}

---
コメントや間違いなどがある場合は[Twitter](https://twitter.com/utam0k)に連絡してもらうか
[Issue](https://github.com/utam0k/utam0k.github.io/issues/1)に書いていただくと助かります。
