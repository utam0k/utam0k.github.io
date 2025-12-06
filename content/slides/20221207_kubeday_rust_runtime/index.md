---
title: Possibility of OCI Container Runtime with Rust
slug: kubeday-rust-runtime
date: 2022-12-07T00:00:00+09:00
speakerdeck_id: 18df783196cf4e14b84c557db8c8784f
speakerdeck_url: https://speakerdeck.com/utam0k/possibility-of-oci-container-runtime-with-rust
event: KubeDay Japan 2022
tags: [slides, rust, oci]
description: "KubeDay Japan 2022 登壇資料"
draft: false
---

近年、Rust は Linux カーネルの「第2言語」採用などで注目を集めています。私は OCI Runtime 周辺で Rust 製コンテナランタイム youki を 1 年半以上開発し、カーネル寄りの層で Rust が相性の良い理由を実感してきました。youki は現在 OCI Runtime 仕様のリファレンス実装の 1 つに掲載され、docker や podman から利用できるレベルです。次のステップとして Kubernetes での利用を見据えています。このセッションでは youki 開発で得た知見を通じて、コンテナランタイムにおける Rust 活用の可能性を紹介します。冒頭では OCI Runtime に馴染みのない方向けに cgroups や Linux namespace などの基礎も触れます。

KubeDay Japan にて登壇。
https://events.linuxfoundation.org/kubeday-japan/
https://sched.co/1C8lS
