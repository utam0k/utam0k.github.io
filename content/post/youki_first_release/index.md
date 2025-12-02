---
title: Hello, youki!
date: 2021-12-27T00:00:00+09:00
categories: [tech]
tags: [rust, youki]
local_share_img: ogp.png
description: "Rust版OCIコンテナランタイムyoukiのファーストリリース"
---

<div class="blankslate">
  <p class="my-12 h1 text-underline text-center text-mono"> Hello, youki! </p>
  <p>この記事はyoukiのv0.0.1リリースの思い出に書いた記事です</p>
<a href="https://github.com/containers/youki/releases/tag/v0.0.1" target="_blank" rel="noopener noreferrer" class="btn-legacy btn-primary" type="button">View Relase Note</a>
</div>

<div class="flash">
  <a href="https://www.utam0k.jp/en/blog/2021/12/27/youki_first_release/" target="_blank" rel="noopener noreferrer">英語記事</a>のほうがより詳しい内容になっています。
</div>

## 🤔 youkiとは

[OCI Runtime Specification](https://github.com/opencontainers/runtime-spec/blob/c2389c3cb60aed4ffc206d6b7dbd12d2abaeefe5/implementations.md#runtime-container)に載っているOCIコンテナランタイム[^what_is_oci_cr]の1つでRustで実装されています。
簡単に言うとコンテナを実際に作るソフトウェアです。

<div class="my-4">
  <center>
  <a href="https://github.com/containers/youki"><img src="link_card_youki.svg"></a>
  </center>
</div>

実際に動いている様子はこんな感じです。
このツイートの時に日本の冬が終わるまでにリリースと宣言していたので今回のリリースで一安心してます。
<center>
<blockquote class="twitter-tweet"><p lang="en" dir="ltr">🥳 Youki, the OCI container runtime written in Rust(<a href="https://twitter.com/rustlang?ref_src=twsrc%5Etfw">@rustlang</a>), passed all the integration tests of runtime_tools prepared by <a href="https://twitter.com/OCI_ORG?ref_src=twsrc%5Etfw">@OCI_ORG</a>. I hope to first release it by the end of the cold season in Japan. Please look forward to it.<a href="https://t.co/Pj2uWRnZG6">https://t.co/Pj2uWRnZG6</a> <a href="https://t.co/5hLvzJTMny">pic.twitter.com/5hLvzJTMny</a></p>&mdash; utam0k (@utam0k) <a href="https://twitter.com/utam0k/status/1442429917136781317?ref_src=twsrc%5Etfw">September 27, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
</center>

### youkiは何がうれしいのか

コンテナを利用する側と、OCIコンテナランタイムを開発する側の2種類の目線から細かいところは無視して一番インパクトが大きそうなうれしさを紹介させてください。

<div class="border-bottom mb-2">コンテナ利用者目線</div>

コンテナの起動から削除までの1サイクルの実行速度の向上が一番体感できるうれしさだと思います。
簡単にですが、私のローカル環境での実行速度のベンチマーク結果です。

<center>

| Runtime |   Time (mean ± σ)   |  Range (min … max)  |
| :-----: | :-----------------: | :-----------------: |
|  youki  | 198.4 ms ±  52.1 ms | 97.2 ms … 296.1 ms  |
|  runc   | 352.3 ms ±  53.3 ms | 248.3 ms … 772.2 ms |
|  crun   | 153.5 ms ±  21.6 ms | 80.9 ms … 196.6 ms  |
</center>

<details>
<summary>ベンチマークの詳細</summary>

  - A command used for the benchmark  
      ```console
      $ hyperfine --prepare 'sudo sync; echo 3 | sudo tee /proc/sys/vm/drop_caches' --warmup 10 --min-runs 100 'sudo ./youki create -b tutorial a && sudo ./youki start a && sudo ./youki delete -f a'
      ```
  - Enviroment  
      ```console
      $ ./youki info
      Version           0.0.1
      Kernel-Release    5.11.0-41-generic
      Kernel-Version    #45-Ubuntu SMP Fri Nov 5 11:37:01 UTC 2021
      Architecture      x86_64
      Operating System  Ubuntu 21.04
      Cores             12
      Total Memory      32025
      Cgroup setup      hybrid
      Cgroup mounts
        blkio           /sys/fs/cgroup/blkio
        cpu             /sys/fs/cgroup/cpu,cpuacct
        cpuacct         /sys/fs/cgroup/cpu,cpuacct
        cpuset          /sys/fs/cgroup/cpuset
        devices         /sys/fs/cgroup/devices
        freezer         /sys/fs/cgroup/freezer
        hugetlb         /sys/fs/cgroup/hugetlb
        memory          /sys/fs/cgroup/memory
        net_cls         /sys/fs/cgroup/net_cls,net_prio
        net_prio        /sys/fs/cgroup/net_cls,net_prio
        perf_event      /sys/fs/cgroup/perf_event
        pids            /sys/fs/cgroup/pids
        unified         /sys/fs/cgroup/unified
      CGroup v2 controllers
        cpu             detached
        cpuset          detached
        hugetlb         detached
        io              detached
        memory          detached
        pids            detached
        device          attached
      Namespaces        enabled
        mount           enabled
        uts             enabled
        ipc             enabled
        user            enabled
        pid             enabled
        network         enabled
        cgroup          enabled
      $ ./youki --version
      youki version 0.0.1
      commit: 0.0.1-0-0be33bf
      $ runc -v
      runc version 1.0.0-rc93
      commit: 12644e614e25b05da6fd08a38ffa0cfe1903fdec
      spec: 1.0.2-dev
      go: go1.13.15
      libseccomp: 2.5.1
      $ crun --version
      crun version 0.19.1.45-4cc7
      commit: 4cc7fa1124cce75dc26e12186d9cbeabded2b710
      spec: 1.0.0
      +SYSTEMD +SELINUX +APPARMOR +CAP +SECCOMP +EBPF +CRIU +YAJL
      ```
</details>

<div class="border-bottom mb-2">OCIコンテナランタイム開発者目線</div>

開発が楽になります。OCIコンテナランタイム[^1]というソフトウェアは強くLinuxカーネルの機能に依存しています。
利用するカーネルの機能の中にはマルチスレッドで動作していては効果が発揮されないものもあります。
これはつまり、言語のランタイムなどがある場合、ランタイムがマルチスレッドでは困るということです。
Rustの場合はその制約をクリアし、さらにメモリ安全であり、ゼロコスト抽象化の恩恵を受けながら開発を進めることができます。
こんなにOCIコンテナランタイムの実装にちょうどよい言語はなかなかないかなと思います。

### youkiの不安点

まだまだできたてほやほやです。
OCI Runtime仕様にはないがコンテナ界隈ではスタンダードな機能が全て実装されているかというとまだまだです。
実運用されている実績もまだないです。
これらを補うために、containerdなどのハイレベルコンテナランタイムのインテグレーションをruncではなく強制的にyoukiに置き換えてyoukiのCIに組み込むことを挑戦しています。少々お待ちください。

### 実装状況
OCIコンテナランタイム[^1]では仕様の実装以外にも実世界で使われている様々な機能の実装が必要です。
youkiのv.0.0.1のリリース時点での実装状況は以下のような感じです。
なかなかがんばってるでしょ😉

|        Feature        |                   Description                   |                                                State                                                |
| :-------------------: | :---------------------------------------------: | :-------------------------------------------------------------------------------------------------: |
|        Docker         |               Running via Docker                |                                                 ✅                                                  |
|        Podman         |               Running via Podman                |                                                 ✅                                                  |
|      pivot_root       |            Change the root directory            |                                                 ✅                                                  |
|        Mounts         |    Mount files and directories to container     |                                                 ✅                                                  |
|      Namespaces       |         Isolation of various resources          |                                                 ✅                                                  |
|     Capabilities      |            Limiting root privileges             |                                                 ✅                                                  |
|      Cgroups v1       |            Resource limitations, etc            |                                                 ✅                                                  |
|      Cgroups v2       |             Improved version of v1              | Support is complete except for devices. WIP on [#78](https://github.com/containers/youki/issues/78) |
| Systemd cgroup driver |        Setting up a cgroup using systemd        |                                                 ✅                                                  |
|        Seccomp        |             Filtering system calls              |                                                 ✅                                                  |
|         Hooks         | Add custom processing during container creation |                                                 ✅                                                  |
|       Rootless        |   Running a container without root privileges   |                                                 ✅                                                  |
|    OCI Compliance     |        Compliance with OCI Runtime Spec         |                                 ✅ 50 out of 50 test cases passing                                  |

## 💪 モチベーション

なぜ我々はyoukiを実装し続けているのでしょうか。

* Rustという言語  
楽しい。我々はRustらしいコードを目指しています。

* コンテナランタイム界隈への貢献  
OCIランタイムの仕様にはスタンダードになっているが、仕様にはないものがあります。
これは他のコンテナランタイムが発展することでしっかりと仕様に落とし込まれるのではないかと思っています。  
また、youkiで出来たcrateの提供をできる限り行おうとしています。実際に[containers/oci-spec-rs](https://github.com/containers/oci-spec-rs)をcrateとしてyouki本体のコードから切り離して提供しています。

* 探求心  
新しいOCIコンテナランタイムは古いカーネルのサポートなどはしません。
そうすることでio_uringやclone3など新しい機能を使える可能性を秘めています。わくわくしますね。

* なんて言ったてプログラミングは楽しい  
皆さんプログラミング好きですか？僕はOSSを楽しんでいます。

## 🤝 Youkiへの参加

YoukiはRustでコンテナランタイムを勉強したい方やみなさんの意見をいつでも募集しています。

- [意見やアイディアを気軽に投稿できるissue](https://github.com/containers/youki/issues/10)
- [Discord](https://discord.gg/zHnyXKSQFD)
- [@utam0k](https://twitter.com/utam0k)

また、開発としての最初の参加方法として[good first issue](https://github.com/containers/youki/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22)を用意しています。
もし、good first issueがなくて困った場合はDiscordやTwitterで僕に聞いてみてください。


## 👣 歴史

完全に私事ですが、最初のコミットをしたうたもくがyoukiを作るまでの経緯を書かせてください。

<div class="TimelineItem">
  <div class="TimelineItem-badge color-bg-danger-emphasis color-fg-on-emphasis">
  <svg width="16" height="16" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
  </svg>    
  </div>
  <div class="TimelineItem-body">
    <a href="https://www.amazon.co.jp/dp/4297118378">イラストでわかるDockerとKubernetes</a>と出会う
  </div>
</div>
<div class="TimelineItem">
  <div class="TimelineItem-badge color-bg-success-emphasis color-fg-on-emphasis">
      <svg class="octicon octicon-git-commit" viewBox="0 0 14 16" version="1.1" width="14" height="16" aria-hidden="true">
      <path fill-rule="evenodd" d="M10.86 7c-.45-1.72-2-3-3.86-3-1.86 0-3.41 1.28-3.86 3H0v2h3.14c.45 1.72 2 3 3.86 3 1.86 0 3.41-1.28 3.86-3H14V7h-3.14zM7 10.2c-1.22 0-2.2-.98-2.2-2.2 0-1.22.98-2.2 2.2-2.2 1.22 0 2.2.98 2.2 2.2 0 1.22-.98 2.2-2.2 2.2z"></path>
    </svg>
  </div>
  <div class="TimelineItem-body">
    Oracleが作っていて既にアーカイブされた<a href="https://github.com/oracle/railcar">railcar</a>を学ぶ
  </div>
</div>
<div class="TimelineItem">
  <div class="TimelineItem-badge color-bg-accent-emphasis color-fg-on-emphasis">
    <svg weight="16" height="16" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path></svg>
  </div>
  <div class="TimelineItem-body">
    現在のyoukiとなるRustのコンテナランタイムの実装を始める。
    <blockquote class="twitter-tweet"><p lang="ja" dir="ltr">Rustで作ってます。公開できる形になったら、そのうち公開するかもです...<br>最低限でdockerでHelloWorldするまでの道みたいな文書あると面白いかな。気が向いたら...文書書くの苦手...<br>まだエラーとかいっぱい出てる... <a href="https://t.co/jLsaVQH9Vl">pic.twitter.com/jLsaVQH9Vl</a></p>&mdash; utam0k (@utam0k) <a href="https://twitter.com/utam0k/status/1355709762759888900?ref_src=twsrc%5Etfw">January 31, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
  </div>
</div>
<div class="TimelineItem">
  <div class="TimelineItem-badge color-bg-success-emphasis color-fg-on-emphasis">
    <svg weight="16" height="16" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"></path></svg>
  </div>
  <div class="TimelineItem-body">
    <a href="https://www.reddit.com/r/programming/comments/niv8cg/youki_a_container_runtime_in_rust_passed_all_the/">Reddit</a>などで注目を集めて開発者が集まる
  </div>
</div>
<div class="TimelineItem">
  <div class="TimelineItem-badge color-bg-success-emphasis color-fg-on-emphasis">
    <svg weight="16" height="16" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"></path></svg>
  </div>
  <div class="TimelineItem-body">
    うたもく個人からcontainersへの移管
    <blockquote class="twitter-tweet"><p lang="en" dir="ltr">🎉 I joined the containers organization, which is developing podman and crun. And I moved youki under containers.<a href="https://t.co/dMTFxrZKUZ">https://t.co/dMTFxrZKUZ</a> <a href="https://t.co/qx2nnvyvxw">pic.twitter.com/qx2nnvyvxw</a></p>&mdash; utam0k (@utam0k) <a href="https://twitter.com/utam0k/status/1400763774995374085?ref_src=twsrc%5Etfw">June 4, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
  </div>
</div>
<div class="TimelineItem">
  <div class="TimelineItem-badge color-bg-success-emphasis color-fg-on-emphasis">
    <svg weight="16" height="16" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
  </div>
  <div class="TimelineItem-body">
    注目度が上がり、開発者が続々と増える
  </div>
</div>
<div class="TimelineItem">
  <div class="TimelineItem-badge color-bg-success-emphasis color-fg-on-emphasis">
    <svg weight="16" height="16" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path></svg>
  </div>
  <div class="TimelineItem-body">
    Youkiファーストリリース
  </div>
</div>

## 🥰 謝辞
素晴らしいコラボレータの方々ありがとうございます。
[Thomas Schubart](https://github.com/Furisto)、[yihuaf](https://github.com/yihuaf)、[YJDoc2](https://github.com/YJDoc2)、[tommady](https://github.com/tommady)、[Yukang](https://github.com/chenyukang) 、[Travis Sturzl](https://github.com/tsturzl) 

また、協力してくださった[containers](https://github.com/containers)のみなさんありがとうございます。
特に、[Sascha Grunert](https://github.com/saschagrunert), [Giuseppe Scrivano](https://github.com/giuseppe) and [Daniel J Walsh](https://github.com/rhatdan)ありがとうございます。

Thanks to all the people who already contributed!  
{{% figure src="contributors.svg" %}}

## 💬 最後に

みなさんのコントリビュートをいつだって待っています。
スポンサー機能とか開放していないので、よかったらスターをつけてくれると開発者の励みになります。
<script async defer src="https://buttons.github.io/buttons.js"></script>
<center>
<a class="github-button" href="https://github.com/containers/youki" data-color-scheme="no-preference: light; light: light; dark: dark;" data-size="large" data-show-count="true" aria-label="Star containers/youki on GitHub">Star</a>
</center>

[^what_is_oci_cr]: OCIコンテナランタイムについては以前に[ODC2021](https://www.youtube.com/watch?v=YRlzYpbj4I0)、[Rust.Tokyo 2021](https://rust.tokyo/2021/lineup/5)、[第15回 コンテナ技術の情報交換会](https://ct-study.connpass.com/event/223739/)(習熟度順)で発表させてもらっているのでそれらを参照してみてください
[^1]: この記事のOCIコンテナランタイムはVM型ではなくnamespaceなどを用いたタイプのOCIコンテナランタイムを指しています
