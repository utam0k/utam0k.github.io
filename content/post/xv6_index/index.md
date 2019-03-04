---
title: "詳解xv6 目次"
date: 2019-03-04T15:04:55+09:00
draft: true
---

### はじめに  
xv6はMITが開発している現代版Unix V6です。  
x86アーキテクチャで動作するようになっています。  
お手元のLinuxで簡単に動作させれます。  
本記事ではその詳細についてMITが公開している[commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf) 
を元にソースコードレベルで解説していきます。
### 読み方  
以下サンプルです。  

- `filename.c`  

    ``` c
    1 int main()
    2 {
    3     printf("Hello world!");
    ~~~
    8     return 0;
    9 }
    ```
- L1: 関数宣言  
- L3: 表示  
- L4: 返り値  

`L行数`がソースコードの何行目のことかを指しており、右側に解説を書きます。
`~~~`は省略を表します。


***
## 本編
1. [Page tables 1]({{< ref "post/xv6_pagetable_1" >}})
    - アドレススペースの作成
    - カーネルのページング設定
1. Page tabels 2 (coming soon)
    - メモリアロケータ
1. Traps interrupts, and drivers (coming soon)
1. Locking (coming soon)
1. Scheduling (coming soon)
1. File system 1 (coming soon)
1. File system 2 (coming soon)
1. File system 3 (coming soon)
1. File system 4 (coming soon)
