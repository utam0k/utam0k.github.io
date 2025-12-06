---
title: Distributed Cache Empowers AI/ML Workloads on Kubernetes Cluster
slug: kubecon-na-2024-cache
date: 2024-11-26T00:00:00+09:00
speakerdeck_id: 02bfa2d556d049e989e835f3a6e58e93
speakerdeck_url: https://speakerdeck.com/pfn/kubecon-plus-cloudnativecon-north-america-2024
event: "KubeCon + CloudNativeCon North America 2024"
tags: [slides, k8s, cache, ai]
description: "Talk at KubeCon + CloudNativeCon North America 2024"
co_presenters: true
draft: false
---

Today, storage technologies play a fundamental role in the realm of AI/ML. Read performance is essential for swiftly moving datasets from storage to AI accelerators. However, the rapid enhancement of AI accelerators' performance often outpaces I/O, bottlenecks the training. Due to the scheduling of pods in Kubernetes across multiple nodes, utilizing node-local storage effectively presents a challenge. To address this, we introduce a distributed cache system built atop node-local storages, designed for AI/ML workloads. This cache system has been successfully deployed on our on-premise 1024+ GPUs Kubernetes cluster within a multi-tenancy environment. Throughout our two-year experience operating this cache system, we have overcome numerous hurdles across several components, including the I/O library, load balancers, and the storage backend. We will share the challenges and the solutions we implemented, leading to a system delivering 50+ GB/s throughput and less than 2ms latency.

https://kccncna2024.sched.com/event/1i7nw
