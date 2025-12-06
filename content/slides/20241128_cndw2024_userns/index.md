---
title: 次のコンテナセキュリティの時代 - User Namespace With a Pod / CloudNative Days Winter 2024
slug: cndw2024-user-namespace
date: 2024-11-28T00:00:00+09:00
speakerdeck_id: 795965eb892c4f0da30f77111a57e67e
speakerdeck_url: https://speakerdeck.com/pfn/cloudnative-days-2024-usernamespace-with-a-pod
event: CloudNative Days Winter 2024
tags: [slides, k8s, security]
description: "CloudNative Days Winter 2024 登壇資料"
draft: false
---

本セッションでは GA が近づいている Kubernetes の新機能の「User Namespace」について説明します。本機能は 2016 年から要望のあったコミュニティ待望の機能です。また、「User Namespace」 を用いた Pod は過去にあったコンテナランタイムの脆弱性の多くに対して有効な防御策となります。
ただし、本機能はコンテナランタイムなどの周辺知識がないと一見何が起きているのかを理解するのが難しい側面もあります。そのため、本セッションはまず始めに現状のコンテナについての復習から入り、なぜ「User Namespace」が過去の CVE に対して有効かを説明します。その後、知識だけではなくハンズオンなどを用いて本機能のコアの部分に手を動かして触れる機会を提供します。
本セッションが「User Namespace」をあなたの環境で運用するための手助けになることを期待しています。

イベントサイト: https://event.cloudnativedays.jp/cndw2024
