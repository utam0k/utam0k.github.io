---
title: A method of self-made C compiler which even a beginner can do
subtitle: C compiler written by Rust.
date: 2018-10-12T12:15:41+09:00
lastmod: 2018-11-27T12:00:00+09:00
tags : [rust, compiler]
---

## Introduction
Recently, self-made C compilers are popular in Japan because a lecture was held to teach about who to make them.
I did not participate in it but it seemed fun!!! However, how can I do this???
There were no compiler experts around me. Oh My God...   
※ **I have many many friends!**  
It is difficult to make a C compiler without relying on anyone!?
But I want to know about compilers because they are like too blackboxes for me.
Even though I looked at various books about compilers, 
I did not understand them at all, so I thought that the only way to do it was to model [9cc](https://github.com/rui314/9cc).
Anyway, I have been transplanting all of the [9cc](https://github.com/rui314/9cc) first commit to Rust.
[9cc](https://github.com/rui314/9cc) is a C compiler written by [rui314](https://twitter.com/rui314).
Codes of [9cc] (https://github.com/rui314/9cc) are very readable and very easy to transplant.
[9cc](https://github.com/rui314/9cc) is ***God***.
I think that the C compiler you create with this method will require little prior knowledge.
To be honest, you just have to do it.
I would be pleased if this would be helpful for those who would like to do the same thing.

## Deliverable
**My self-made C compiler: [r9cc](https://github.com/utam0k/r9cc)**   

I was [challenging](https://github.com/utam0k/r8cc) the same thing with 9cc's previous work [8cc](https://github.com/rui314/8cc).
However It stalled and [9cc](https://github.com/rui314/9cc) came out,
so I switched to [9cc](https://github.com/rui314/9cc).
Actually, this is my second challenge.

In [r9cc](https://github.com/utam0k/r9cc), the first capital letter of the commit message is simply ported commit from [9cc](https://github.com/rui314/9cc).
Since I became tired of writing in English quikly, 
I will show readers that [r9cc](https://github.com/utam0k/r9cc) can compile this code.
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
- Function call with arguments
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

I was surprised that various C codes could be compiled with only using these features.

## Things to be careful of
#### Understand what I am doing
It is possible to rewrite to Rust without considering each commit perhaps.
I think that **continuing despite not understanding anything** is the most avoidable thing.
I implemented it with as much as possible what the commit I was working on was doing.
I was implementing it after grasping the whole commit by the following procedure.

1. Reading a commit message.
2. Reading the added test codes.
3. Reading the entire code of commit.

In addition to this, I was grasping the rough flow by looking at the +5 commit positions of the commit I am now doing.
I think that it is good to check whether I can properly grasp the code by trying to implement the unique function.

#### Step by step
[First commit] (https://github.com/utam0k/r9cc/commit/b8b44544eb51d6229f19033a5048043e628ab55a) of [r9cc] (https://github.com/utam0k/r9cc) is as simple as this.  
[Fist commit](https://github.com/rui314/9cc/commit/56e94442ae8844688d5390851e5b29ba0c946e2f) of [9cc](https://github.com/rui314/9cc) also like this.
It just returns a number.  
**Is anyone likely to be able to look at this!?**  
There was not a type in the early days.
It is not a policy to make syntactic analysis only first, but whole of up to where to output the assembly is made **evenly**.
Although I wanted to make big things, I did it a bit at a time.

## Motivation
**I don't have anyone to talk with about the compiler because I don't have friends who are interested in compilers in the real world.**  
So, I had to keep my motivation by somehow trying my best with strong will.
Because I had no confidence to have a strong will, I thought about a way to keep motivation.
I think that here is the big wall when I do it by myself.
I think that it is possible to keep my motivation by having a goal.
I would like to set a self-host as a big goal, but I could not do it because [r9cc](https://github.com/rui314/9cc) is written by Rust.
So, I settled with a parent host as a big goal.
The word `parent host` means that r9cc can compile [9cc](https://github.com/rui314/9cc).
However, I thought about a smaller goal because I was unlikely to keep motivation with just this goal.
The small goal is aimed at a reasonable commit of [9cc] (https://github.com/rui314/9cc).
I chose commits that make me excited.  
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

Do you feel excited by just seeing the title of the commit message? Yes, you do.
I got it little by little with the motivation that `#include` will work or if it can be done by commit here, it is really fun.

As you add examples, tension also increases a lot.
It is only [nqueen.c](https://github.com/rui314/9cc/blob/master/examples/nqueen.c) if it is [9cc](https://github.com/rui314/9cc),
but [fib.c](https://github.com/utam0k/r9cc/blob/master/examples/fib.c) and [prime.c](https://github.com/utam0k/r9cc/blob/master/examples/prime.c) 
have also been added in [r9cc](https://github.com/utam0k/r9cc).
It's fun when I compiled my code.

## Conclusion
For the time being I was able to compile `#include`, so I made an article.
Creating [r9cc] (https://github.com/utam0k/r9cc) improves programming skills, 
and furthermore, I think that the world of the compiler that I did not understand at all was just a glimpse.
In the future, I will aim for a `parent host` and go on a little by little.
I think that it would be interesting if the self-made C compiler population increased even a little,
because self-made C compiling is very fun and recommended!
***I am still a beginner about Rust so I'm waiting for a good pull request.***  
I'd like to write another article about the technical point unique to Rust.
Even if I say  
***I can develop C language a little***   
it may be tolerated.
Special thanks for [9cc](https://github.com/rui314/9cc) and [rui314](https://twitter.com/rui314).
plz awesome.

## Additional detail information
It took me about 1.5 weeks to be able to compile somthing like a general C compiler.
It was about 2 months until `#include` was made.
If you have any questions please do not hesitate to contact me on [Twitter](https://twitter.com/utam0k).

I learned:

- Assembly
- Behavior of C language
- Role of various registers
- Stack

## tcfm
Finally, I will introduce [Turing Complete FM](https://turingcomplete.fm/), which [rui314](https://twitter.com/rui314) is doing.
You can listen mainly about low layer stories such as C compiler's story.
