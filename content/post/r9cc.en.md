---
title: Self-made C compiler by oneself.
subtitle: C compiler written by Rust.
date: 2018-10-12T12:15:41+09:00
tags : [rust, compiler]
draft: true
---

## Introduction
Recently, self-made C compiler is popular in Japan because a lecture was held to teach who to make it.
I did not participate in it but it seemed fun!!! However how can I do this???
There were no compiler experts around me. Oh My God...   
※ **I have many many friends!**  
It is difficult to make a C compiler without relying on anyone!?
But I want to know compiler because it is too blackbox for me.
Even though I looked at various books about compiler, 
I did not understand at all, so I thought that there was no way anyone could do it was to model [9cc](https://github.com/rui314/9cc).
Anyway I have transplanting all from the [9cc](https://github.com/rui314/9cc) first commit to Rust.
[9cc](https://github.com/rui314/9cc) is a C compiler wirtten by [rui314](https://twitter.com/rui314).
Codes of [9cc] (https://github.com/rui314/9cc) is very readable and very easy to do transplanting.
[9cc](https://github.com/rui314/9cc) is ***God***.
Perhaps I think that the C compiler you create with this method will require little prior knowledge.
To be honest, only do it.
I would be pleased if it would be helpful for those who would like to do the same thing.

## Deliverable
**My self-made C compiler: [r9cc](https://github.com/utam0k/r9cc)**   

I was [challenging](https://github.com/utam0k/r8cc) the same thing with 9cc's previous work [8cc](https://github.com/rui314/8cc).
However It was stalled and [9cc](https://github.com/rui314/9cc) came out.
So I switched to [9cc](https://github.com/rui314/9cc).
Actually, This is second challenge.

In [r9cc](https://github.com/utam0k/r9cc), the first capital letter of the commit message is simply ported commit from [9cc](https://github.com/rui314/9cc).
Since I was tired of writing in English soon, 
I show reader that [r9cc](https://github.com/utam0k/r9cc) can compile this code.
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

There are other features:

- Four arithmetic operations
- Logical operation
- Local variable
- Global variable
- Function call with args
- Function definition
- Array
- Pointer
- ++/\-\-
- char/int
- String literal
- Struct
- extern
- #include
- Comment

I also made assignments at the initialization of array as [r9cc](https://github.com/utam0k/r9cc)'s unique function, so this also works.
```c
int main() {
  int x[3] = {10, 11, 12};
  return x[1];
}
```

I was surprised that various C codes could be compiled quite a bit by only these features.

## Things to be careful
#### Understand what I am doing
It is possible to rewrite to Rust without considering each commit perhaps.
I think that **continuing despite not understanding anything** is the most avoidable thing.
I implemented it with as much as possible what the commit I was working on was doing.
I was implementing it after grasping the whole commit by the following procedure.

1. Reading a commit message.
2. Reading the added test codes.
3. Reading the entire code of commit.

In addition to this I was grasping the rough flow by looking at the +5 commit position of the commit now doing.
I think that it is good to check whether I can properly grasp the code by trying to implement the unique function.

#### Step by step
[First commit] (https://github.com/utam0k/r9cc/commit/b8b44544eb51d6229f19033a5048043e628ab55a) of [r9cc] (https://github.com/utam0k/r9cc) is as simple as this.  
[Fist commit](https://github.com/rui314/9cc/commit/56e94442ae8844688d5390851e5b29ba0c946e2f) of [9cc](https://github.com/rui314/9cc) also like this.
It just returns a number.  
**Is anyone likely to be able to look at this!?**  
There was not a type in the early days.
It is not a policy to make syntactic analysis only first, but whole of up to where to output the assembly is made **evenly**.
Although I wanted to make big things, I did it a bit at a time.

#### 変数名や順序(追記 2018-10-13)
変数名や関数の順番を[r9cc](https://github.com/utam0k/r9cc)とできるだけ一緒になるようにしました。
[r9cc](https://github.com/utam0k/r9cc)には関数が書かれている場所(?)順番(?)にも意味を持っているところがあります。
変数名や関数名もできるだけ一緒にしたほうがわかりやすくなると思います。

## Motivation
**I don't have anyone to talk about the compiler because I don't have friends who are interested in compiler in the real world.**  
So I had to keep my motivation by somehow trying my best with strong will.
Because I had no confidence to have a strong will, I thought about a way to keep motivation.
I think that here is the big wall when I do it by myself.
I think that it is possible to keep motivation by having a goal.
I would like to set a self host as a big goal, but I could not do it because [r9cc](https://github.com/rui314/9cc) is written by Rust.
So, I settled parent host as a big goal.
The word `parent host` means that r9cc can compile [9cc](https://github.com/rui314/9cc).
However, I thought about a little smaller goal because I was unlikely to keep motivation with just this goal.
A small goal aimed at a reasonable commit of [9cc] (https://github.com/rui314/9cc).
I chose commits that makes me exciting.  
I chose:

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
Do you feel excited about just only the title of the commit message? Yes, you do.
ここのコミットまでできれば`#include`が動くとか楽しみすぎでしょというモチベーションで少しずつやっていきました。  
I got it little by little with the motivation that `#include` will work or if it can be done to commit here, it is too fun.

As you add examples, the tension also increases a lot.
It is only [nqueen.c](https://github.com/rui314/9cc/blob/master/examples/nqueen.c) if it is [9cc](https://github.com/rui314/9cc),
but [fib.c](https://github.com/utam0k/r9cc/blob/master/examples/fib.c) and [prime.c](https://github.com/utam0k/r9cc/blob/master/examples/prime.c) 
have also been added in [r9cc](https://github.com/utam0k/r9cc).
It's fun when I compiled my code.

## Conclusion
For the time being I was able to compile `#include`, so I made an article.
Creating [r9cc] (https://github.com/utam0k/r9cc) improves programming skil, 
furthermore I think that the world of the compiler that I did not understand at all was a glimpse.
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
