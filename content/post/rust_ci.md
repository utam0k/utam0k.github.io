---
title: "RustでのCircleCiの導入"
date: 2018-05-24T16:34:42+09:00
tags : [tech, rust]
---

最近初めてのRust開発で自作シェルの[mican](https://github.com/utam0k/mican)を作っている。  
そこでCircleCiをがんばった。

## lint
Rustのlintとして[rust-clippy](https://github.com/rust-lang-nursery/rust-clippy)が有名。  
結構便利で```"if let"でもっとよくなるよ！```とかも教えてくれて助かる。よく怒られて神ってなる。  
僕もだが初心者だとRustっぽい構文がわからないので導入すると助かる。  
`help`のurlに行くと良い感じになぜだめなのか教えて頂けます。

``` rust
warning: writing `&Vec<_>` instead of `&[_]` involves one more reference and cannot be used with non-Vec-based slices.
   --> src/readline/reader.rs:154:29
    |
154 |     fn find_bind(&self, ch: &Vec<u8>) -> Option<Keybind> {
    |                             ^^^^^^^^ help: change this to: `&[u8]`
    |
    = note: #[warn(ptr_arg)] on by default
    = help: for further information visit https://rust-lang-nursery.github.io/rust-clippy/v0.0.200/index.html#ptr_arg

warning: `if _ { .. } else { .. }` is an expression
  --> src/readline/editor.rs:76:13
   |
76 | /             let index: usize;
77 | |             if self.completer_index > self.completions.len() {
78 | |                 self.completer_index = 1;
79 | |                 index = 1;
80 | |             } else {
81 | |                 index = self.completer_index;
82 | |             }
   | |_____________^ help: it is more idiomatic to write: `let index = if self.completer_index > self.completions.len() { ..; 1 } else { self.completer _index };`
   |
   = note: #[warn(useless_let_if_seq)] on by default
   = help: for further information visit https://rust-lang-nursery.github.io/rust-clippy/v0.0.200/index.html#useless_let_if_seq
```
rust-clippyの導入にはnightly版のRustが必要
CIの導入の際にnightly版のRustが必要になる。  
仕方のないことだが[rust-clippy](https://github.com/rust-lang-nursery/rust-clippy)は最新のnightlyだと動かないことがある。  
実際に最新版で動かなくて[プルリクエスト](https://github.com/rust-lang-nursery/rust-clippy/pull/2775)を出した。  
よってCIで導入する際はRustのバージョンを固定しましょう。  
インストールはcargoで簡単に入れれます。  
オプションでどのくらい厳しくチェックするかを決めれます。   
`clippy_pedantic`が一番厳しくチェックされます。

``` yaml
- run:
  name: lint
  command: |
    export PATH=~/.cargo/bin:$PATH
    rustup install nightly-2018-05-16
    cargo +nightly-2018-05-16 install clippy --vers 0.0.200 --force
    cargo +nightly-2018-05-16 clippy --release -- -Dclippy_pedantic
```

## テストカバレージ
[kcov](http://simonkagstrom.github.io/kcov/)と[Codecov](https://codecov.io)を使っていきます。  
現状だとkcovはラインカバレージのみのサポートなのでブランチカバレージ等はできません。  
[参考](https://github.com/SimonKagstrom/kcov/issues/27)  

[Codecov](https://codecov.io)以外にも簡単に他のも導入できます。
[kcov](http://simonkagstrom.github.io/kcov/)に[例](https://github.com/SimonKagstrom/kcov/tree/master/doc)がいっぱいあります。   
テストカバレージについてはもっと良い方法があったら教えてほしいです。  

[mican](https://github.com/utam0k/mican)だと[こんな感じ](https://codecov.io/gh/utam0k/mican)になります。

いんすとーる！
```yaml
- run:
  name: kcov
  command: |
      wget https://github.com/SimonKagstrom/kcov/archive/master.tar.gz
      tar xzf master.tar.gz
      cd kcov-master
      mkdir build
      cd build
      cmake ..
      make
      make install DESTDIR=../../kcov-build
      cd ../..
      rm -rf kcov-master
```

じっこう！
```yaml
- run:
  name: coverage
  command: |
    for file in target/debug/mican-*[^\.d]; do 
        mkdir -p "target/cov/$(basename $file)"; ./kcov-build/usr/local/bin/kcov --exclude-pattern=/.cargo,/usr/lib --verify "target/cov/$(basename $file)" "$file"; 
    done
    bash <(curl -s https://codecov.io/bash)
    echo "Uploaded code coverage"
```

## 全体
[mican](https://github.com/utam0k/mican)の`config.yaml`全体はこんな感じになります。  
Rust周りのインストールや必要なもののインストールが追加されています。 

```yaml 
version: 2

jobs:
  build:
    docker:
      - image: ubuntu:16.04

    working_directory: /opt/utam0k

    steps:
      - checkout
      - run:
          name: set up
          command: |
            set -eux
            apt-get update
            apt-get install -y wget build-essential libcurl4-openssl-dev libelf-dev libdw-dev binutils-dev cmake libiberty-dev pkg-config zlib1g-dev python curl
      - run:
          name: preparation 
          command: |
            wget "https://static.rust-lang.org/rustup/dist/x86_64-unknown-linux-gnu/rustup-init"
            chmod +x rustup-init
            ./rustup-init -y --no-modify-path --default-toolchain nightly
            RUSTUP=~/.cargo/bin/rustup
            CARGO=~/.cargo/bin/cargo
            chmod -R a+w $RUSTUP $CARGO
            rm rustup-init
            source ~/.cargo/env
      - run:
          name: lint
          command: |
            export PATH=~/.cargo/bin:$PATH
            rustup install nightly-2018-05-16
            cargo +nightly-2018-05-16 install clippy --vers 0.0.200 --force
            cargo +nightly-2018-05-16 clippy --release -- -Dclippy_pedantic
      - run:
          name: kcov
          command: |
              wget https://github.com/SimonKagstrom/kcov/archive/master.tar.gz
              tar xzf master.tar.gz
              cd kcov-master
              mkdir build
              cd build
              cmake ..
              make
              make install DESTDIR=../../kcov-build
              cd ../..
              rm -rf kcov-master
      - run:
          name: test
          command: |
            export PATH=~/.cargo/bin:$PATH
            cargo test
      - run:
          name: coverage
          command: |
            for file in target/debug/mican-*[^\.d]; do 
                mkdir -p "target/cov/$(basename $file)"; ./kcov-build/usr/local/bin/kcov --exclude-pattern=/.cargo,/usr/lib --verify "target/cov/$(basename $file)" "$file"; 
            done
            bash <(curl -s https://codecov.io/bash)
            echo "Uploaded code coverage"
```
