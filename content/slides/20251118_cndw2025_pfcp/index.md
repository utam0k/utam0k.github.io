---
title: 単一Kubernetesクラスタで実現する AI/ML 向けクラウドサービス
slug: cndw2025-pfcp
date: 2025-11-18T00:00:00+09:00
speakerdeck_id: f1cad64027064bd79b6a0a6714dca2b0
speakerdeck_url: https://speakerdeck.com/pfn/ml-xiang-kekuraudosabisu
event: CloudNative Days Winter 2025
tags: [slides, k8s, ai, pfcp]
description: "CloudNative Days Winter 2025 登壇資料"
co_presenters: true
draft: false
---

PFNでは、AI/MLワークロード向けのクラウドサービスである「Preferred Computing Platform (PFCP)」をマルチテナントKubernetes基盤として提供しています。これらのワークロードで用いられるMN-CoreやGPUは貴重な計算リソースであるため、それらを無駄なく・効率よく利用することが重要です。クラスタをテナントごとに構築する場合は、個々のクラスタのリソースの空きを他テナントに融通しづらく、計算リソースの利用効率が低下します。PFCPは全テナントが同一のマルチテナント基盤を利用することでこの課題を解決し、より高い利用効率を実現します。一方で、同一の基盤上でテナントを安全かつ公平に収容する様々な仕組みが求められます。

本セッションでは、このようなマルチテナント基盤で重要となる、Kubernetes APIレベルでの権限分離とその強制、同一ホスト上でのプロセス・データの分離、同一ネットワーク内での通信分離等のアイソレーション技術、限られた計算リソースの公平制御、および課金システムについて、その実現のための技術と設計思想について説明します。

イベントサイト: https://event.cloudnativedays.jp/cndw2025/talks/2725
