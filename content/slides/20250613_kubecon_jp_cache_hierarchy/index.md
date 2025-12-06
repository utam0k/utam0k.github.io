---
title: New Cache Hierarchy for Container Images and OCI Artifacts in Kubernetes Clusters using Containerd / KubeCon + CloudNativeCon Japan
slug: kubecon-jp-2025-cache-hierarchy
date: 2025-06-13T00:00:00+09:00
speakerdeck_id: 963567122dfc4197ad9a1ae0d5501f14
speakerdeck_url: https://speakerdeck.com/pfn/20250616_kubecon-cloudnativecon-japan_pfn
event: "KubeCon + CloudNativeCon Japan 2025"
tags: [slides, k8s, cache, cri]
description: "KubeCon + CloudNativeCon Japan 2025 登壇資料"
co_presenters: true
draft: false
---

One of the key bottlenecks in Kubernetes pod startup is the time taken to pull container images and OCI artifacts. It’s also costly to fetch large container images from the registry often. To tackle this problem, we developed a cache system with the following features:

* New Cache Hierarchy: Images pulled by pods are shared across the entire cluster, enabling cluster-wide optimization, not only cluster-local cache.
* Ninja: Users experience faster container image pulls without any changes on their part. Just like a ninja, the system stealthily enhances performance.
* Preheating: It supports pushing images to preheat the cache for subsequent pulls.

Deployed in a production cluster, the cache system has achieved a cache hit rate of around 95%, significantly reducing pod startup times and network communication with registries. Attendees will learn practical insights into leveraging cache and CRI to optimize image and OCI artifact pulls, ultimately enhancing cluster efficiency.
https://sched.co/1x708
