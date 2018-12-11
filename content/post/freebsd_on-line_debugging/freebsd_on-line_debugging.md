---
title: "FreeBSDのオンラインカーネルデバッグ with QEMU"
date: 2018-12-12T00:00:00+09:00
isCJKLanguage: true
tags : [freebsd, os, gdb]
---

この記事は[自作OS Advent Calendar 2018](https://adventar.org/calendars/2915)の12日目の記事です。

# はじめに
最近xv6の教科書を読んでみている。
xv6の教科書ではQEMUの`-s`オプションを用いたデバッグが推奨されている。  
`-s`オプションは`-gdb tcp::1234`の省略版でこのオプションを付けてQEMUを使うと`1234`番ポートでgdbserverを立ち上げてくれる。  
あとはgdbで`target remote :1234`とかをするとQEMUにアタッチされていい感じにデバッグできる。
FreeBSDでこれができたらコードリーディングとか捗りそう...  
いろいろ試行錯誤してみたらできました。  
ということでQEMUの`-s`オプションでFreeBSDのカーネルのデバッグをしてみました。

# デバッグ構成
今回デバッグするのに2つのFreeBSDが必要になる。   

|    内容          | OS                     | 仮想化                    | ここでの名称 |
|:----------------:|:----------------------:|:-------------------------:|:------------:|
| デバッグする側   | FreeBSD 11.2           | KVM                       | `Source`     |
| デバッグされる側 | FreeBSD 11.2           | QEMU                      | `Target`     |
| ホスト           | Ubuntu 18.04.1 Desktop | &nbsp;&nbsp;&nbsp;&nbsp;× | `Host`       |

`Source`の方はKVMを使っていますがなんでもよいと思います。  
ただし、`Source`の方でカーネル再構築を行います。

`Host`の`20022`番ポートが`Target`の`22`番ポートにリダイレクトされるように設定した。
`Host`と`Source`は`192.168.122.0/24`で通信できるようにした。  
この辺は`Host`からFreeBSDに相互で通信できれば特に問題ないと思われる。  

{{% figure src="constitution.png" %}}

# やり方
### 1. FreeBSDのインストール
まずは`Source`と`Target`を用意します。
詳しいインストールの方法[^bsdinstall] は割愛します。
[^bsdinstall]:https://www.freebsd.org/doc/en/books/handbook/bsdinstall.html
同じバージョン、アーキテクチャでインストールしていきます。  
私の環境ではFreeBSD-11.2-RELEASE-amd64を選択しました。  

`Target`のインストール準備として`Host`で以下のコマンド実行します。  
`-redir tcp:20022::22`のオプションで`Host`の`20022`番ポートが`Target`の`22`番ポートにリダイレクトされるようにしています。
```
$ qemu-img create -f qcow freebsd_debug.img 30G
$ qemu-system-x86_64 -m 4096 -hda freebsd_debug.img -boot c -cdrom FreeBSD-11.2-RELEASE-amd64-dvd1.iso -redir tcp:20022::22
```

**※`Source`は`src`を含むようにしましょう※**  

{{% figure src="include_src.png" %}}

`Source`と`Target`ともに起動させます。  

### 2. カーネルの再構築
`Source`のカーネルを再構築してデバッグ情報を含むようにします。
カーネルの再構築はFreeBSDのバージョンによって多少異なる点があるので自分が選択したバージョンに合わせましょう。
まずはもとの設定ファイルをコピーします。
```
$ cd /usr/src/sys/amd64/conf
$ cp GENERIC MYKERNEL
```
MYKERNELの設定に以下を足します。
```
makeoptions DEBUG=-g
options KDB
options DDB
```
実際のMYKERNELを[gists](https://gist.github.com/utam0k/d46552bf552fb5121d929f8dd444f745)にあげておきます。
該当箇所は[24](https://gist.github.com/utam0k/d46552bf552fb5121d929f8dd444f745#file-mykernel-L24)/
[83](https://gist.github.com/utam0k/d46552bf552fb5121d929f8dd444f745#file-mykernel-L83)/
[85](https://gist.github.com/utam0k/d46552bf552fb5121d929f8dd444f745#file-mykernel-L85)行目です。

再構築をします。
```
$ cd /usr/src
$ make buildkernel KERNCONF=MYKERNEL
$ make installkernel KERNCONF=MYKERNEL
```
`make buildkernel`は時間がかかるのでここでコーヒーブレイクです。  
終わったら`Source`を再起動させましょう。

### 3. 転送
`Source`の`/boot/kernel/`以下のファイルを全て`Target`の`/boot/kernel/`に送りつけます。
`Host`で以下のコマンドを実行しました。

```
$ scp -r root@192.168.122.2:/boot/kernel .
$ scp -P 20022 kernel/* root@127.0.0.1:/boot/kernel
```

2行目のコマンドの前に`Host`で`strip -x`とかするとシンボル情報がなくなってスマートになります。
```
$ du kernel -h
123M    kernel
$ sudo strip -x kernel/*.ko
$ sudo strip -x kernel/kernel
$ du kernel -h
117M    kernel
```

### 4. 再起動
`Target`をシャットダウンさせます。
`Target`を`-s`オプションを付けて起動させます。
これでgdbserver立ち上げてくれます。

```
$ qemu-system-x86_64 -m 4096 -hda freebsd_debug.img -boot c -cdrom FreeBSD-11.2-RELEASE-amd64-dvd1.iso -redir tcp:20022::22  -s
```
これに加えて`-S`オプションを付けると起動からデバッグできます。

### 5. kgdb
kgdb[^kgdb]はカーネルデバッグのためのデバッガーです。
[^kgdb]:https://en.wikipedia.org/wiki/KGDB
`Source`でkgdbを起動させて`Host`で起動しているQEMUにアタッチします。
この時点で`Target`は停止します。  
ここからは好きにデバッグしてみてください。
ここでは動作の確認のために`sys_mkdir`にブレイクポイントを設定して、`Source`の動作を再開させます。

```
$ kgdb /boot/kernel/kernel
GNU gdb 6.1.1 [FreeBSD]
...
This GDB was configured as "amd64-marcel-freebsd"...
(kgdb) target remote 192.168.122.1:1234
...
(kgdb) b sys_mkdir
Breakpoint 1 at 0xffffffff80bdac14: file /usr/src/sys/kern/vfs_syscalls.c, line 3337.
(kgdb) c
Continuing.
```

そしておもむろに`Target`で`mkdir test`を実行すると  
**きちんと止まった！でけた!**

{{% figure src="result.jpg" %}}

クリックすると画像は大きくなります。

これだけでもシステムコールがどういう感じで呼ばれてるか少しわかるかと思います。  
**やったー！**


# 終わりに
これでいい感じにFreeBSDのカーネルコードリーディングができそうです。  
やっぱりコードとにらめっこするよりも実行しながらできると楽しいですね。  
たぶん、本来は2つをシリアル通信でつなげてやるんだと思うんですがQEMUの機能でやってみました。  
なぜFreeBSDなのかという疑問については聞かないでください。  
明日の[自作OS Advent Calendar 2018](https://adventar.org/calendars/2915)は[garasubo](https://twitter.com/garasubo)さんの「Rust + Cortex-M (予定)」です。  
お！Rust好きとしては楽しみです。

## 参考文献
- [FreeBSD Documentation](https://www.freebsd.org/doc/en/books/developers-handbook/kerneldebug-online-gdb.html)
