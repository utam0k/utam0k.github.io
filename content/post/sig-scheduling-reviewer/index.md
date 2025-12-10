---
title: SIG-Scheduling の Reviewer になった
date: 2025-12-09T00:00:00+09:00
categories: [tech, diary]
tags: [kubernetes, oss]
description: "Kubernetes SIG-Scheduling の Reviewer になりました"
ogp_single_line: true
---

こんにちは。

{{< github "https://github.com/kubernetes/kubernetes/pull/133355" >}}
{{< x user="utam0k" id="1953044009795915797" >}}

今日はこの話をします。
今更という感じはありますが、せっかくの記念なので記事にしておきます。

# Kubernetes でのロール

Kubernetes コミュニティ上のロールの1つです。
ロールは [Member → Reviewer → Approver](https://github.com/kubernetes/community/blob/2833580db42e109d935c608660b0130a40c93bd3/community-membership.md#community-membership) となっていきます。今回はその 1 つの [Reviewer](https://github.com/kubernetes/community/blob/2833580db42e109d935c608660b0130a40c93bd3/community-membership.md#reviewer) になったという話です。
Reviewer になるためには主に「20個以上の PR を作る」「5個以上の PR のレビューをする」を満たす必要があります。
Member の条件よりもここには大きな壁があるように感じます。
詳しくは sanposhiho さんが素晴らしい記事を書いてくれているのでそちらを参照してください。

{{< ogp "https://sanposhiho.com/posts/scheduling-reviwer/" >}}

# やったこと

Member になったのが 2023年12月で、約2年かけてぼちぼち活動を続けていました。
条件クリアが見えてきたタイミングで、SIG-Scheduling にエフォートを寄せて、がっと集中してやりました。

具体的にやったことはこんな感じです。

- KEP の実装への参加 
  いくつかの KEP の実装に参加しました。SIG-Scheduling にはまだまだいろいろな KEP があるので興味があれば覗いてみてください。

- 落ちている issue を拾う  
  放置されている issue を見つけて対応していきました。地味ですがこれが大事。
  Good First Issue は争奪戦です。
  そのため、Good First Issue で 20 個の PR を作るのは難しいです。そのため、昔からあるもので放置されていそうなものを眺めたりしました。

- レビュー参加   
  scheduler_perf など、自分が理解できそうなところから積極的にレビューしていきました。

- サブプロジェクトへの貢献   
  SIG-Scheduling 配下のサブプロジェクトにもちょくちょく貢献しました。これは Reviewer とは関係ないですが、たのしいのでやっていました。

# Reviewer になって

Reviewer になると、レビュー依頼が来るようになります。
強制的にキャッチアップをしてコードを読むことになるので、とても勉強になります。
正直、これが一番うれしいかもしれません。

また、完全な新規のコントリビュータとして既存のコミュニティに入っていくのは学びが多かったです。当然、Kubernetes には優秀なエンジニアも多くレビューから多くの学びがあります。Kubernetes でほとんど初めて Go に入門しているので、かなりありがたい指摘をよくもらいます。あとは Kubernetes 独自の便利ライブラリ(e.g., Set)も多くこのあたりにもなれる必要があります。

KubeCon で会ったことのある [@aojea](https://github.com/aojea) が PR にコメントをくれたのは嬉しかったです。いままでメンテナサミットや KubeCon で F2F で会ったことある方々が温かく迎え入れてくれて大変うれしかったです。

ぼちぼちやっていきます。
