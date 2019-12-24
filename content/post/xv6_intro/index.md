---
title: "詳解xv6 はじめに"
date: 2019-03-05T18:35:01+09:00
tags : [xv6, os]
---
[詳解xv6の目次]({{< ref "post/xv6_index">}})
***

### はじめに  
xv6はMITが開発している現代版Unix V6です。
x86アーキテクチャで動作するようになっています。
お手元のPCで簡単に動作させれます。

本記事ではその詳細についてMITが公開している。
[xv6, a simple, Unix-like teaching operating system](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)(以下 commentary/textbook)
を元にソースコードレベルで解説していきます。
そのため、基本的には[commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)に書いてあることを
要約したり説明を付け足したりした記事になります。

筆者もOS初心者であり、OS入門するために半年前位[^*]からxv6のコードリーディングを始めました。
しかし、初心者には難しい面もありました。
本記事は筆者がxv6のコードリーディングを始めた時にこういう解説記事があったらうれしかったなという思いで本記事を書いています。
今からxv6のコードリーディングを始める人の助けになればと思います。
[^*]: 執筆時は2019-03

間違った解説をしている可能性も十分にあるためその際は指摘した頂けると幸いです。
また、筆者はLinux等の実際のOSに詳しいわけではありません。
Linuxだとこんな風にやってるなどアドバイスを頂けると喜びます。
コメントや間違いなどがある場合は[Twitter](https://twitter.com/utam0k)に連絡してもらうか
[Issue](https://github.com/utam0k/utam0k.github.io/issues/1)に書いていただくと助かります。

### xv6の特徴
- Unix 6vがベース
- OSの基本的なアイディアが詰まっている
- ANSI Cで書かれている
- x86(2019年版からはRISC-V)
- コード量が1万行ないくらい


### 書くこと書かないこと
#### 書くこと
- xv6のコードの解説
- x86の仕組み
- OS特有の用語についての説明

#### 書かないこと
- なぜその機能がOSに必要なのか   
e.g. ページングはなぜ必要なのか
- アセンブリやC言語のこと

### 本記事の読み方  
章のタイトルが日本語なのは本記事の独自解説です。
英語タイトルの場合は[commentary/textbook](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)
にも同じタイトル名があり、その章の解説になります。

以下コード解説のサンプルです。  

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

### xv6の動かし方
筆者はUbuntu 18.04とDebian GNU/Linux 9.4 (stretch)で動かしています。
他のOSでも基本的には`gcc`と`qemu`があれば動かせれると思います。
`Makefile`を見ると`Mac OS X`の記述もあるのでコメントアウトしてみるとできるかもしれません。

#### 動かす
[このサイト](https://gcallah.github.io/OperatingSystems/xv6Install.html)が参考になりそうです。

1. 必要なツールのインストール

    ```
    $ sudo apt install git nasm build-essential qemu gdb
    ```
1. コードをもってくる

    ```
    $ git clone git://github.com/mit-pdos/xv6-public.git
    $ cd xv6-public
    $ git checkout xv6-rev11
    ```

1. Make
一度動かすと`kill`コマンドで消すしかなさそうです。

    ```
    $ make qemu     # GUIありの起動
    $ make qemu-nox # GUIなしの起動
    ```

#### デバッグ(GDB)
1. 起動  

    ```
    $ make qemu-nox-gdb # Booting with gdbserver
    ```
1. アタッチ  
xv6を動かした状態で別でシェルを起動させてgdbを起動させます。

    ```
    $ cd <path to xv6>
    $ gdb
    ```
gdbで以下のコマンド実行します。

    ```
    (gdb) source .gdbinit
    ```
1. デバッグ  
僕はよくgdbで変数の値などを見て動かしながらコードを読んでいました。  
**gdbで試しながらするのは結構おすすめです。**  
試しに`mkdir`のコマンドを少し覗いてみます。
gdb側で以下のコマンドを実行します。

    ```
    (gdb) b sys_mkdir
    (gdb) layout src
    (gdb) continue
    ```
起動したxv6側で`mkdir`を実行します。

    ```
    $ mkdir test
    ```

    するとgdb側で反応があると成功です。
1. xv6を落とす  
gdb側でxv6を落とします。
    
    ```
    (gdb) kill
    ```
