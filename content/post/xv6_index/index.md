---
title: "教育版UNIX v6解説 ~詳解xv6~"
subtitle: "詳解xv6 目次"
date: 2019-03-05T18:35:00+09:00
tags : [xv6, os]
---

### はじめに
本記事はMITのOSの授業で使われているxv6の解説をコードレベルでする記事です。  
xv6はUNIX v6をベースとし、x86で動くようにANSI Cで再実装されたOSです。

[もっとはじめに]({{<ref "post/xv6_intro">}})

- xv6の特徴
- 書くこと書かないこと
- 本記事の読み方
- xv6の動かし方、デバッグ方法

### 本編
1. [Page tables 1]({{< ref "post/xv6_pagetable_1" >}})
    - アドレススペースの作成
    - カーネルのページング設定
1. [Page tabels 2]({{< ref "post/xv6_pagetable_2" >}})
    - メモリアロケータ
    - sbrk()
    - exec()
1. Traps interrupts, and drivers (__coming soon__)
    - システムコール
    - 割り込み
    - ディスクドライバ
1. Locking (__coming soon__)
    - 並列処理
1. Scheduling (__coming soon__)
    - スケジューリング
    - sleepとwakeup
    - パイプ
    - wait, exit, kill
1. File system 1 (__coming soon__)
    - ファイルシステムの概要
    - Bufferキャッシュ層
    - Logging層
    - ジャーナリング
    - ブロックアロケータ
1. File system 2 (__coming soon__)
    - Inode層
1. File system 3 (__coming soon__)
    - Directory層
    - Path name
1. File system 4 (__coming soon__)
    - Descriptor層

---
コメントや間違いなどがある場合は[Twitter](https://twitter.com/utam0k)に連絡してもらうか
[Issue](https://github.com/utam0k/utam0k.github.io/issues/1)に書いていただくと助かります。
