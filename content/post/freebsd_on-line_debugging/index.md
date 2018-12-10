---
title: "FreeBSDのオンラインデバッグ with QEMU"
date: 2018-12-09T00:00:00+09:00
isCJKLanguage: true
draft: true
---

この記事は[自作OS Advent Calendar 2018](https://adventar.org/calendars/2915)の12日目の記事です。

# はじめに
最近xv6の教科書を読んでみている。  
xv6の教科書ではQEMUの`-s`オプションを用いたデバッグが推奨されている。  
`-s`オプションは`-gdb tcp::1234`の省略版でこのオプションを付けてQEMUを使うと`1234`番ポートでgdbserverを立ち上げてくれる。  
あとはgdbで`target remote :1234`とかをするとQEMUにアタッチされていい感じにデバッグされる。
FreeBSDでこれができたらコードリーディングとか捗りそう。
ということでQEMUの`-s`オプションでFreeBSDのカーネルのデバッグをしてみた。

# デバッグ構成
今回デバッグするのに2つのFreeBSDが必要になる。   

|          内容                    | 仮想化                    | 名称     |
|:--------------------------------:|:-------------------------:|:--------:|
| デバッグする側のFreeBSD          | KVM                       | `Source` |
| デバッグされる側のFreeBSD        | QEMU                      | `Target` |
| 2つのFreeBSDを動かしているホスト | &nbsp;&nbsp;&nbsp;&nbsp;× | `Host`   |

# やり方
## 1. カーネルの再構築

## 2. 転送
`Source`の`/boot/kernel/`以下のファイルを全て`Target`の`/boot/kernel/`に送りつけます。

```sh
$ scp -P 20022 kernel/* root@127.0.0.1:/boot/kernel
```

この際に`strip -x`とかするとシンボル情報がなくなってスマートになります。

## 3. kgdb
`Source`で`kgdb`[^kgdb]を起動させます。
[^kgdb]:https://en.wikipedia.org/wiki/KGDB

```sh
$ kgdb /boot/kernel/kernel
```

**でけた!**
{{% figure src="constitution.jpg" %}}

これだけでもシステムコールがどういう感じで呼ばれてるか少しわかるかと思います。
やったー！


# 終わりに
これでいい感じにFreeBSDのカーネルコードリーディングができそうです。
たぶん、本来は2つをシリアル通信でつなげてやるんだと思うんですがQEMUの機能でやってみました。
明日の[自作OS Advent Calendar 2018](https://adventar.org/calendars/2915)は[garasubo](https://twitter.com/garasubo)さんの「Rust + Cortex-M (予定)」です。  
お！今年の自作OSはRustが多いですね。Rust好きとしては楽しいです。

## 参考文献
- [FreeBSD Documentation](https://www.freebsd.org/doc/en/books/developers-handbook/kerneldebug-online-gdb.html)
