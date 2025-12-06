---
title: Solving cgroup v2 OOM issues in Kubernetes
slug: k8s-oom-group
date: 2025-09-02T00:00:00+09:00
speakerdeck_id: 72bf309d1ce7449e914f52fa620d4b04
speakerdeck_url: https://speakerdeck.com/pfn/kubernetes-meetup-tokyo-71-kubelet-oom-group
event: "Kubernetes Meetup Tokyo #71"
tags: [slides, k8s, cgroup]
description: "Talk at Kubernetes Meetup Tokyo #71"
draft: false
---

After upgrading to Kubernetes v1.28, we hit jobs dying with OOM in cgroup v2 environments. This talk walks through the issue and how we fixed it by adding the kubelet option `singleProcessOOMKill`, including the implementation story and lessons learned.
https://github.com/kubernetes/kubernetes/pull/126096
Event page: https://k8sjp.connpass.com/event/365262/
