---
title: Kubernetes における cgroup v2 でのOut-Of-Memory 問題の解決
slug: k8s-oom-group
date: 2025-09-02T00:00:00+09:00
speakerdeck_id: 72bf309d1ce7449e914f52fa620d4b04
speakerdeck_url: https://speakerdeck.com/pfn/kubernetes-meetup-tokyo-71-kubelet-oom-group
event: "Kubernetes Meetup Tokyo #71"
tags: [slides, k8s, cgroup]
description: "Kubernetes Meetup Tokyo #71 登壇資料"
draft: false
---

Kubernetes v1.28 への更新後、PFN でジョブが OOM で終了する問題に直面しました。本発表では cgroup v2 環境での OOM 問題の詳細と、kubelet に `singleProcessOOMKill` を追加して解決した経緯を紹介します。実装時の苦労や詳細にも触れています。
https://github.com/kubernetes/kubernetes/pull/126096
イベントサイト: https://k8sjp.connpass.com/event/365262/
