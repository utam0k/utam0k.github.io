---
title: Self-made C compiler by oneself.
subtitle: C compiler written by Rust.
date: 2018-10-12T12:15:41+09:00
tags : [rust, compiler]
draft: true
---

## Introduction
セキュリティキャンを皮切りに自作Cコンパイラがとてもはやっていました。  
Recently, self-made C compiler is popular in Japan because a lecture was held to teach who to make it.
たのしそー僕もやりたい！！！！でもどうやるんだ？？？  
しかし僕の周りには知る限りではコンパイラに強い人はいませんでした。  
※ **I have many many friends!**  
誰にも頼ることなくCコンパイラを作るのは難しいのでは!?  
でもコンパイラは魔法みたいでいやだから知りたい。
本とかいろいろ眺めてみてもさっぱりわからなかったので誰でもできる方法はないかなーと考えたのが[9cc](https://github.com/rui314/9cc)をお手本にすることでした。
ということで[9cc](https://github.com/rui314/9cc)のファーストコミットからすべてRustにしてみました。
[9cc](https://github.com/rui314/9cc)は[rui314](https://twitter.com/rui314)さんがやられているCコンパイラです。
[9cc](https://github.com/rui314/9cc)のコードは可読性がとても高くとてもやりやすかったです。[9cc](https://github.com/rui314/9cc) ***神*** です。  
おそらくこの方法で作るCコンパイラは事前知識はほとんど必要なくできると思います。   
正直、やるだけだと思います(本当に *ｼｭｯ* です(ﾎﾝﾏ))。  
もし同じようなことをやりたい人の参考になればawesomeです。

## Deliverables
できあがっているブツ: [r9cc](https://github.com/utam0k/r9cc)   

[9cc](https://github.com/rui314/9cc)の前作である[8cc](https://github.com/rui314/8cc)でも同じことを[チャレンジしていた](https://github.com/utam0k/r8cc)のですが  
行き詰っていた & [9cc](https://github.com/rui314/9cc)がでた  
ということで[9cc](https://github.com/rui314/9cc)の方に切り替えました。
ということで実は2度目のチャレンジです。

[r9cc](https://github.com/utam0k/r9cc)ではコミットメッセージが大文字で始まるものが[9cc](https://github.com/rui314/9cc)から単純に移植しているものです。
小文字で始まるものは独自のリファクタリングだったり独自機能だったりします。
そろそろ日本語で書くのが疲れたので趣味で作った[r9cc](https://github.com/utam0k/r9cc)でもこのくらいのコードならコンパイルできるぜっていうのを読者に見せつけます。   
``` c
int fibdp[100];

int fib(int n) {
  if (n == 0 || n == 1) {
    return n;
  } else if (fibdp[n] != 0) {
    return fibdp[n];
  } else {
    fibdp[n] = fib(n-2) + fib(n-1);
    return fibdp[n];
  }
}

int main() {
  for (int i = 0; i < 100; i++)
    fibdp[i] = 0;
  int ans = fib(46);
  printf("%d\n", ans);
  return 0;
}
```

他にもこれくらいなら動きます。  

- 四則演算
- 論理演算
- ローカル変数
- グローバル変数
- 引数[あり|なし]の関数呼び出し
- 引数[あり|なし]の関数定義
- 配列
- ポインタ
- ++/\-\-
- char/int型
- 文字列リテラル
- 構造体
- extern
- #include
- コメント文

[r9cc](https://github.com/utam0k/r9cc)の独自機能として配列の初期化時の代入も作ってみたのでこんなのも動きます。
```c
int main() {
  int x[3] = {10, 11, 12};
  return x[1];
}
```

これだけでも結構いろいろなCのコードがコンパイルできてびっくりしました。

## 気を付けたこと
#### なにをしてるか把握する 
おそらく各コミットを何も考えないででRustに書き換えることも可能です。
このように**何もわからないままでもやり続けれてしまう**ことが1番怖いところだと思います。
Rustの力は上がるかもしれませんが本質であるコンパイラを知ることはできません。
Cじゃないの方が頭を使うかなと思ってRustにしました。
正直Cでもよいと思います。
できるだけ自分が作業しているコミットがなにをしているのかを意識して実装しました。
以下の手順で読んでみてコミット全体を把握してから実装することを徹底していました。

1. コミットメッセージを読む
2. 追加されたテストコードを読んでみる
3. コード全体を読む

これに加えて今やってるコミットの+5コミット位を眺めて大まかな流れを把握していました。  
独自機能を実装してみるのも自分がきちんとコードを把握できているのかチャックするのにはよいと思います。

#### ちょっとずつ
[r9cc](https://github.com/utam0k/r9cc)の[最初のコミット](https://github.com/utam0k/r9cc/commit/b8b44544eb51d6229f19033a5048043e628ab55a)はこんなもんです。
[9cc](https://github.com/rui314/9cc)の[最初のコミット](https://github.com/rui314/9cc/commit/56e94442ae8844688d5390851e5b29ba0c946e2f)ももちろんそうです。
数字を返すだけです。   
**こうみると誰でも出来そうじゃないですか!?**  
最初は型なんかありませんでした。  
構文解析だけを先に作るという方針ではなく、アセンブリを出力するところまでの**全体を均等的**に作っていきます。
でかいものを作りたい気持ちはありましたが、ちょっとずつやっていきました。

#### 変数名や順序(追記 2018-10-13)
変数名や関数の順番を[r9cc](https://github.com/utam0k/r9cc)とできるだけ一緒になるようにしました。
[r9cc](https://github.com/utam0k/r9cc)には関数が書かれている場所(?)順番(?)にも意味を持っているところがあります。
変数名や関数名もできるだけ一緒にしたほうがわかりやすくなると思います。

## モチベーション
**僕の周りにはコンパイラに興味のある人は少なかったためコンパイラについて話す相手はいませんでした。**  
そうなると自分のとても強い意志でがんばるかどうにかしてモチベーションを保つ必要がありました。  
僕には強い意志を持つ自信がなかったのでモチベーションを保つ方法を考えました。  
一人でやるときの大きな壁がここだと思います。  
目標を持つことでモチベーションを保つことができると思います。  
まず、大きな目標として[rui314](https://twitter.com/rui314)さんの[記事](https://note.mu/ruiu/n/n00ebc977fd60)でも述べられていますがセキュリティキャンプではセルフホストを設定していたみたいです。
[r9cc](https://github.com/utam0k/r9cc)はRustで書いているのでセルフホストはできないので今回はペアレントホストにしました。  
ペアレントホストは勝手に僕が考えたのですが、参考にしている[9cc](https://github.com/rui314/9cc)をコンパイルできるということです。  
ただ、この目標だけだとモチベーションを保てそうになかったのでもう少し小さな目標を考えました。  
小さな目標は[9cc](https://github.com/rui314/9cc)の適当なコミットを目標にしました。  
コミットの選び方は自分がわくわくするものを選んで勝手に目標にしていました。  
僕が選んだの  

- [Compile a single number to a program that exits with the given number.](https://github.com/rui314/9cc/commit/56e94442ae8844688d5390851e5b29ba0c946e2f)
- [Add variable.](https://github.com/rui314/9cc/commit/42e403e3de0c6457bc11ab14c55a9dad27ed82be)
- [Add zero-arity function definition.](https://github.com/rui314/9cc/commit/c7933acab4e410aa0c0c7a38358092208ace822d)
- [Add "for".](https://github.com/rui314/9cc/commit/b487b30ab0c600b764ea3a94e2502b68f5ee4194)
- [Add pointer.](https://github.com/rui314/9cc/commit/e43b738d6bb6ecd397e09b46346e0825a00d89e6)
- [Add examples/nqueen.c.](https://github.com/rui314/9cc/commit/63739ad7ef08ee7e037862dfa05739ce00abac5f)
- [Add struct definition. Only sizeof() is applicable. No member access.](https://github.com/rui314/9cc/commit/bf717fa5e53ebbae9f949515d3662f77af4ff4dd)
- [Add pre/post increment/decrement operators.](https://github.com/rui314/9cc/commit/a406a04660d848e083d7b39610409fd9ba497142)
- [Implement "#include".](https://github.com/rui314/9cc/commit/a382606b9728ca33f5dedae4f6ca5cc3c9404838)

コミットメッセージのタイトルだけでもわくわくしませんか。うん、しますね。  
ここまで行くと`#include`が動くとか楽しみすぎでしょというモチベーションで少しずつやっていきました。  

exampleも積極的に足していくとテンション爆上がりです。  
[9cc](https://github.com/rui314/9cc)だと[nqueen.c](https://github.com/rui314/9cc/blob/master/examples/nqueen.c)だけですが、
[r9cc](https://github.com/utam0k/r9cc)では[fib.c](https://github.com/utam0k/r9cc/blob/master/examples/fib.c)や[prime.c](https://github.com/utam0k/r9cc/blob/master/examples/prime.c)も足してみました。
自分が書いたコードがコンパイルできた時はたのしー。

## 終わりに
とりあえず`#include`までできたので記事にしてみました。
[r9cc](https://github.com/utam0k/r9cc)を作ることでコーディングはもちろんですが全然わからなかったコンパイラの世界が垣間見れたかなと思います。
今後はペアレントホスト目指してちょっとずつ進んでいきます。
自作Cコンパイラ人口が少しでも増えれば面白いかなと思います。  
自作Cコンパイラはやっていてめちゃめちゃ楽しいのでおすすめです！  
***Rustまだまだ初心者なのでこんな書き方の方がいいよ的なプルリク待ってます。***  
Rust固有のコンパイラを作るときに難したかった点はまた違う記事で書こうと思います。  
***ﾜﾀｼ ｽｺｼ ﾎﾝﾉｽｺｼ ｼｰｹﾞﾝｺﾞﾃﾞｷﾙ***  
くらいは言っても許されるかもしれない。  
このような機会を与えてくれた[9cc](https://github.com/rui314/9cc)に感謝感謝です。
plz awesome.

## 追記(2018-10-13)
C言語ぽくまで動くまでには1.5週間くらいでした。
`#include`ができるまでは2ヵ月くらいでした。
もし自作コンパイラやってみようと思ってくれた方で質問や困ったことあったら[Twitter](https://twitter.com/utam0k)で
DMなりメンションをもらえればできるだけ考えます！

学べたこと

- アセンブリ
- C言語の挙動
- いろいろなレジスタの役割
- スタックについて強くなった

## tcfm
[rui314](https://twitter.com/rui314)さんがやられている[Turing Complete FM](https://turingcomplete.fm/)の紹介をします。  
Cコンパイラの話など主に低レイヤの話が聞けます。  
世の中にはすごい人しかいないのではと思えます。   
