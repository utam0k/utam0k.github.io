---
title: "xv6 Deep Dive Page tables 2"
date: 2019-04-25T09:00:00+09:00
tags: [xv6, os]
---

[xv6 Deep Dive table of contents]({{< ref "post/xv6_index">}})  
[Previous post]({{< ref "post/xv6_pagetable_1">}})  
[Next post]({{< ref "post/xv6_traps_interrupts_drivers_1">}})
- - -

# Code: Physical memory allocator
## Big picture
- Register physical memory, page by page, in the linked list `freelist` ([kinit1()]({{<ref "#kinit1">}}), [kinit2()]({{<ref "#kinit2">}})).
    - `kalloc.c`

        ```c
        16 struct run {
        17   struct run *next;
        18 };
        
        20 struct {
        21   struct spinlock lock;
        22   int use_lock;
        23   struct run *freelist;
        24 } kmem;
        ```
- Provide pages to whoever asks ([kalloc()]({{<ref "#kalloc">}})).

### Sequence diagram
Rough flow. If you get lost inside the functions, glance here.
{{% figure src="sequence.png" %}}

### Memory layout (reprint)
The layout from [the previous post]({{< ref "post/xv6_pagetable_1">}}); we use it a lot here.

{{% figure src="memorylayout.png" %}}
Source: [commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)

Relationship between VA and PA:

| Name | Virtual address | Physical address |
|:--:|:--:|:--:|
| end | end | V2P(end) |
| PHYSTOP | P2V(PHYSTOP) | PHYSTOP |
| KERNBASE | KERNBASE | V2P(KERNBASE) |

### main()
- `main.c`

    ```c
    17 int
    18 main(void)
    19 {
    20   kinit1(end, P2V(4*1024*1024)); // phys page allocator
    21   kvmalloc();      // kernel page table
    ~~~
    35   kinit2(P2V(4*1024*1024), P2V(PHYSTOP)); // must come after startothers()
             ~~~
    38 }
    ```
    - L20: Register end–4 MB with the page allocator.
    - Up to L20 the PDT is `entrypgdir`:
        - `main.c`

            ```c
              97 // The boot page table used in entry.S and entryother.S.
              98 // Page directories (and page tables) must start on page boundaries,
              99 // hence the __aligned__ attribute.
             100 // PTE_PS in a page directory entry enables 4Mbyte pages.

             102 __attribute__((__aligned__(PGSIZE)))
             103 pde_t entrypgdir[NPDENTRIES] = {
             104   // Map VA's [0, 4MB) to PA's [0, 4MB)
             105   [0] = (0) | PTE_P | PTE_W | PTE_PS,
             106   // Map VA's [KERNBASE, KERNBASE+4MB) to PA's [0, 4MB)
             107   [KERNBASE>>PDXSHIFT] = (0) | PTE_P | PTE_W | PTE_PS,
             108 };
            ```
            - L105: VA [0, 4 MB) -> PA [0, 4 MB)
            - L106: VA [KERNBASE, KERNBASE+4 MB) -> PA [0, 4 MB) — both map to the same PA.
    - L21: Create and install the kernel PDT.
    - L22: Register 4 MB–PHYSTOP with the allocator.
    - Why split into [kinit1()]({{<ref "#kinit1">}}) and [kinit2()]({{<ref "#kinit2">}})?
        - `entry.S` only maps physical 0–4 MB, so only that range is usable at first.
        - `kinit1()` plus later `kvmalloc()` sets up the real paging (needs allocator—bootstrap issue).
        - `kinit2()` then registers everything above 4 MB.

### kinit1()
- `kalloc.c`

    ```c
    26 // Initialization happens in two phases.
    27 // 1. main() calls kinit1() while still using entrypgdir to place just
    28 // the pages mapped by entrypgdir on free list.
    29 // 2. main() calls kinit2() with the rest of the physical pages
    30 // after installing a full page table that maps them on all cores.
    31 void
    32 kinit1(void *vstart, void *vend)
    33 {
    34   initlock(&kmem.lock, "kmem");
    35   kmem.use_lock = 0;
    36   freerange(vstart, vend);
    }
    ```
    - `vstart`: end, `vend`: P2V(4*1024*1024)
    - L34-35: Initialize lock but leave it off (locking needs the allocator, so can’t use yet).
    - L36: Register the region (`vstart`–`vend`) in `freelist`.

### freerange()
- `kalloc.c`

    ```c
    46 void
    47 freerange(void *vstart, void *vend)
    48 {
    49   char *p;
    50   p = (char*)PGROUNDUP((uint)vstart);
    51   for(; p + PGSIZE <= (char*)vend; p += PGSIZE)
    52     kfree(p);
    }
    ```
    - L50: Align to PGSIZE.
    - L51-52: Call [kfree()]({{<ref "#kfree">}}) for each page.

### kfree()
Remove the page (start address) from `freelist`.

- `kalloc.c`

    ```c
    54 //PAGEBREAK: 21
    55 // Free the page of physical memory pointed at by v,
    56 // which normally should have been returned by a
    57 // call to kalloc().  (The exception is when
    58 // initializing the allocator; see kinit above.)
    59 void
    60 kfree(char *v)
    61 {
    62   struct run *r;

    64   if((uint)v % PGSIZE || v < end || V2P(v) >= PHYSTOP)
    65     panic("kfree");

    67   // Fill with junk to catch dangling refs.
    68   memset(v, 1, PGSIZE);

    70   if(kmem.use_lock)
    71     acquire(&kmem.lock);
    72   r = (struct run*)v;
    73   r->next = kmem.freelist;
    74   kmem.freelist = r;
    75   if(kmem.use_lock)
    76     release(&kmem.lock);
    }
    ```
    - L64: Error checks—`v` must be PGSIZE-aligned and within free memory (end–P2V(PHYSTOP)).
    - L68: Fill with 1s up to `v+PGSIZE`.
    - L72-74: Add `v` to `freelist`.
    - L70-71, L75-76: Locking (to avoid corrupting the list).

### kinit2()
- `kalloc.c`

    ```c
    39 void
    40 kinit2(void *vstart, void *vend)
    41 {
    42   freerange(vstart, vend);
    43   kmem.use_lock = 1;
    }
    ```
    - L42: Register physical 4 MB–PHYSTOP in the free list.
    - L43: Enable locking (see Locking for details).

### kalloc()
Provide a physical page (PGSIZE).

- `kalloc.c`

    ```c
    79 // Allocate one 4096-byte page of physical memory.
    80 // Returns a pointer that the kernel can use.
    81 // Returns 0 if the memory cannot be allocated.
    82 char*
    83 kalloc(void)
    84 {
    85   struct run *r;

    87   if(kmem.use_lock)
    88     acquire(&kmem.lock);
    89   r = kmem.freelist;
    90   if(r)
    91     kmem.freelist = r->next;
    92   if(kmem.use_lock)
    93     release(&kmem.lock);
    94   return (char*)r;
    }
    ```
    - L89-91: Pop one from `freelist`.
    - L87-88, L92-93: Locking.

# Code: sbrk
### sys_sbrk()
System call to grow/shrink the current process’s memory size.

- `sysproc.c`

    ```c
    45 int
    46 sys_sbrk(void)
    47 {
    48   int addr;
    49   int n;

    51   if(argint(0, &n) < 0)
    52     return -1;
    53   addr = myproc()->sz;
    54   if(growproc(n) < 0)
    55     return -1;
    56   return addr;
    }
    ```
    - L51-52: Parse the argument (details later).
    - L54: Grow memory ([growproc()]({{<ref "#growproc">}})).

### growproc()
Increase memory allocated to the running process (i.e., add paging entries).

- `proc.c`

    ```c
    156 // Grow current process's memory by n bytes.
    157 // Return 0 on success, -1 on failure.
    158 int
    159 growproc(int n)
    160 {
    161   uint sz;
    162   struct proc *curproc = myproc();

    164   sz = curproc->sz;
    165   if(n > 0){
    166     if((sz = allocuvm(curproc->pgdir, sz, sz + n)) == 0)
    167       return -1;
    168   } else if(n < 0){
    169     if((sz = deallocuvm(curproc->pgdir, sz, sz + n)) == 0)
    170       return -1;
    171   }
    172   curproc->sz = sz;
    173   switchuvm(curproc);
    174   return 0;
    }
    ```
    - L162: Get current process.
    - L165-167: Growing memory ([allocuvm()]({{<ref "#allocuvm">}})).
    - L168-171: Shrinking memory ([deallocuvm()]({{<ref "#deallocuvm">}})).

### deallocuvm()
Remove allocated physical memory from `freelist`.

- `vm.c`

    ```c
    251 // Deallocate user pages to bring the process size from oldsz to
    252 // newsz.  oldsz and newsz need not be page-aligned, nor does newsz
    253 // need to be less than oldsz.  oldsz can be larger than the actual
    254 // process size.  Returns the new process size.
    255 int
    256 deallocuvm(pde_t *pgdir, uint oldsz, uint newsz)
    257 {
    258   pte_t *pte;
    259   uint a, pa;

    261   if(newsz >= oldsz)
    262     return oldsz;

    264   a = PGROUNDUP(newsz);
    265   for(; a  < oldsz; a += PGSIZE){
    266     pte = walkpgdir(pgdir, (char*)a, 0);
    267     if(!pte)
    268       a = PGADDR(PDX(a) + 1, 0, 0) - PGSIZE;
    269     else if((*pte & PTE_P) != 0){
    270       pa = PTE_ADDR(*pte);
    271       if(pa == 0)
    272         panic("kfree");
    273       char *v = P2V(pa);
    274       kfree(v);
    275       *pte = 0;
    276     }
    277   }
    278   return newsz;
    }
    ```
    - L264: Align to PGSIZE.
    - L266: Look up the PTE. User virtual addresses start at 0, so `oldsz`/`newsz` are VAs. Because the third argument is 0, [walkpgdir()]({{<ref "post/xv6_pagetable_1#walkpgdir">}}) won’t allocate if absent.
    - L267-268: If the PTE is missing: `PDX(a)+1` is the next PDE index; `PGADDR(PDX(a)+1,0,0)-PGSIZE` is the address just before that next PDE’s range (minus PGSIZE because the loop adds PGSIZE next).
    - L269-275: If the PTE exists and `PTE_P` (page present) is set.
    - L270: Physical page start address (`PTE_ADDR`).

        ```c
         99 // Address in page table or page directory entry
        100 #define PTE_ADDR(pte)   ((uint)(pte) & ~0xFFF)
        101 #define PTE_FLAGS(pte)  ((uint)(pte) &  0xFFF)
        ```

    - L271-272, L275: If `pa` is zero that’s an error (initial PTEs are zero).
    - L273: `freelist` is managed in kernel space, so `P2V()` is usable.
    - L274: Free the physical page.

### allocuvm()
Allocate new physical memory.

- `vm.c`

    ```c
    219 // Allocate page tables and physical memory to grow process from oldsz to
    220 // newsz, which need not be page aligned.  Returns new size or 0 on error.
    221 int
    222 allocuvm(pde_t *pgdir, uint oldsz, uint newsz)
    223 {
    224   char *mem;
    225   uint a;

    227   if(newsz >= KERNBASE)
    228     return 0;
    229   if(newsz < oldsz)
    230     return oldsz;

    232   a = PGROUNDUP(oldsz);
    233   for(; a < newsz; a += PGSIZE){
    234     mem = kalloc();
    235     if(mem == 0){
    236       cprintf("allocuvm out of memory\n");
    237       deallocuvm(pgdir, newsz, oldsz);
    238       return 0;
    239     }
    240     memset(mem, 0, PGSIZE);
    241     if(mappages(pgdir, (char*)a, PGSIZE, V2P(mem), PTE_W|PTE_U) < 0){
    242       cprintf("allocuvm out of memory (2)\n");
    243       deallocuvm(pgdir, newsz, oldsz);
    244       kfree(mem);
    245       return 0;
    246     }
    247   }
    248   return newsz;
    }
    ```
    - L227-230: Error checks.
    - L232: Align to PGSIZE.
    - L233-247: Allocate as many pages as needed.
    - L234: Get a physical page ([kalloc()]({{<ref "#kalloc">}})).
    - L234-239: If no memory left.
    - L240: Zero-initialize.
    - L241-246: Map the VA to the physical page (uses [mappages()]({{<ref "post/xv6_pagetable_1#mappages">}}), [deallocuvm()]({{<ref "#deallocuvm">}}), [kfree()]({{<ref "#kfree">}})).

# Code: exec
System call to build the user address space.

- `exec.c`

    ```c
    10 int
    11 exec(char *path, char **argv)
    12 {
    13   char *s, *last;
    14   int i, off;
    15   uint argc, sz, sp, ustack[3+MAXARG+1];
    16   struct elfhdr elf;
    17   struct inode *ip;
    18   struct proghdr ph;
    19   pde_t *pgdir, *oldpgdir;
    20   struct proc *curproc = myproc();
         ~~~ obtain inode for path
    30   pgdir = 0;

    32   // Check ELF header
         ~~~ validate ELF
    38   if((pgdir = setupkvm()) == 0)
    39     goto bad;

    41   // Load program into memory.
    42   sz = 0;
    43   for(i=0, off=elf.phoff; i<elf.phnum; i++, off+=sizeof(ph)){
    44     if(readi(ip, (char*)&ph, off, sizeof(ph)) != sizeof(ph))
    45       goto bad;
        ~~~ error checks
    52     if((sz = allocuvm(pgdir, sz, ph.vaddr + ph.memsz)) == 0)
    53       goto bad;
    54     if(ph.vaddr % PGSIZE != 0)
    55       goto bad;
    56     if(loaduvm(pgdir, (char*)ph.vaddr, ip, ph.off, ph.filesz) < 0)
    57       goto bad;
    58   }
         ~~~
    63   // Allocate two pages at the next page boundary.
    64   // Make the first inaccessible.  Use the second as the user stack.
    65   sz = PGROUNDUP(sz);
    66   if((sz = allocuvm(pgdir, sz, sz + 2*PGSIZE)) == 0)
    67     goto bad;
    68   clearpteu(pgdir, (char*)(sz - 2*PGSIZE));
    69   sp = sz;

    71   // Push argument strings, prepare rest of stack in ustack.
         ~~~ set up argv etc.
    90   // Save program name for debugging.
         ~~~ misc for debugging
    95
    96   // Commit to the user image.
    97   oldpgdir = curproc->pgdir;
    98   curproc->pgdir = pgdir;
         ~~~ set various curproc fields
    102   switchuvm(curproc);
    103   freevm(oldpgdir);
    104   return 0;

    106  bad:
         ~~~ error handling
    ```

    - L38: Map the kernel portion of memory.
    - L43-58: Load each ELF segment into memory.
    - L52: Allocate physical memory: `sz` = old size, `ph.vaddr + ph.memsz` = new size.
    - L56: Expand the inode data into the specified virtual address ([loaduvm()]({{<ref "#loaduvm">}})).
    - L65-67: Allocate two pages to properly catch overly large args that span pages.
    - L68: Make the first of those two pages inaccessible to user mode.
        - `vm.c`

            ``` c
            300 // Clear PTE_U on a page. Used to create an inaccessible
            301 // page beneath the user stack.
            302 void
            303 clearpteu(pde_t *pgdir, char *uva)
            304 {
            305   pte_t *pte;

            307   pte = walkpgdir(pgdir, uva, 0);
            308   if(pte == 0)
            309     panic("clearpteu");
            310   *pte &= ~PTE_U;
            }
            ```
            - Uses [walkpgdir()]({{<ref "post/xv6_pagetable_1#walkpgdir">}}).
    - L97,103: Free previously allocated physical memory.
    - L98: Install the newly built page table.
    - L102: Switch to the new page table.

### loaduvm()
Expand inode data into memory.

- `vm.c`
    
    ```c
    195 // Load a program segment into pgdir.  addr must be page-aligned
    196 // and the pages from addr to addr+sz must already be mapped.
    197 int
    198 loaduvm(pde_t *pgdir, char *addr, struct inode *ip, uint offset, uint sz)
    199 {
    200   uint i, pa, n;
    201   pte_t *pte;

    203   if((uint) addr % PGSIZE != 0)
    204     panic("loaduvm: addr must be page aligned");
    205   for(i = 0; i < sz; i += PGSIZE){
    206     if((pte = walkpgdir(pgdir, addr+i, 0)) == 0)
    207       panic("loaduvm: address should exist");
    208     pa = PTE_ADDR(*pte);
    209     if(sz - i < PGSIZE)
    210       n = sz - i;
    211     else
    212       n = PGSIZE;
    213     if(readi(ip, P2V(pa), offset+i, n) != n)
    214       return -1;
    215   }
    216   return 0;
    }
    ```
    - L203: Check alignment.
    - L205-215: For each PGSIZE chunk, copy inode data into physical memory.
    - L206-208: Find the physical address from the VA ([walkpgdir()]({{<ref "post/xv6_pagetable_1#walkpgdir">}})).
    - L209-212: If less than a page remains, read only that much.
    - L213-214: Copy data (details in the file-system chapter): `ip` inode, `P2V(pa)` destination, `offset+i` offset, `n` size.

---
If you have comments or corrections, please contact me on [Twitter](https://twitter.com/utam0k) or open an [Issue](https://github.com/utam0k/utam0k.github.io/issues/1).
