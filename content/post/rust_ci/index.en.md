---
title: "Introducing CircleCI for Rust"
date: 2018-05-24T16:34:42+09:00
tags: [tech, rust]
---

I’m building my first Rust project—a homebrew shell called [mican](https://github.com/utam0k/mican)—and set up CircleCI for it. Here’s what I did.

## lint
[rust-clippy](https://github.com/rust-lang-nursery/rust-clippy) is the well-known linter. It’s great at telling you things like “this would be nicer as `if let`,” which is very helpful (and humbling) for beginners who don’t yet know idiomatic Rust. The `help` URLs explain why a pattern is wrong.

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

Installing clippy requires a nightly toolchain. Some nightly versions break clippy; I hit that and even sent a [PR](https://github.com/rust-lang-nursery/rust-clippy/pull/2775). So in CI, pin the Rust version. Install via cargo and choose the strictness level; `clippy_pedantic` is the strictest.

``` yaml
- run:
  name: lint
  command: |
    export PATH=~/.cargo/bin:$PATH
    rustup install nightly-2018-05-16
    cargo +nightly-2018-05-16 install clippy --vers 0.0.200 --force
    cargo +nightly-2018-05-16 clippy --release -- -Dclippy_pedantic
```

## Test coverage
I used [kcov](http://simonkagstrom.github.io/kcov/) plus [Codecov](https://codecov.io). kcov currently supports only line coverage, not branch coverage (see [discussion](https://github.com/SimonKagstrom/kcov/issues/27)).

Codecov is easy to swap for other services; kcov has [many examples](https://github.com/SimonKagstrom/kcov/tree/master/doc). If you know a better approach to coverage, please tell me.

For mican it looks [like this](https://codecov.io/gh/utam0k/mican).

Install kcov:
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

Run coverage:
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

## Full config
Here’s the full `config.yaml` for mican. It adds Rust installation and the needed tools.

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
