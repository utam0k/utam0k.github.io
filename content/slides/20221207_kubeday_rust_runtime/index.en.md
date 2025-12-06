---
title: Possibility of OCI Container Runtime with Rust
slug: kubeday-rust-runtime
date: 2022-12-07T00:00:00+09:00
speakerdeck_id: 18df783196cf4e14b84c557db8c8784f
speakerdeck_url: https://speakerdeck.com/utam0k/possibility-of-oci-container-runtime-with-rust
event: KubeDay Japan 2022
tags: [slides, rust, oci]
description: "KubeDay Japan 2022 talk: Possibility of OCI container runtime with Rust"
draft: false
---

It goes without saying that the Rust language has received a lot of attention in recent years, including the adoption of Rust as a second language in the Linux kernel. Toru has been exploring the possibility of developing a container runtime using Rust in the vicinity of OCI Runtime and developing youki, the OCI container runtime in Rust that he has worked on for over a year and a half. He thought it would be a good fit for the language since OCI Runtime requires development at a relatively kernel-like layer. Youki is now listed as one of the reference implementations of the OCI Runtime specification and is at a level where it can be used from docker and podman. The next step is to consider using it with Kubernetes. In this session, he will discuss the possibility of using Rust in a container runtime. He will share his experiences with youki. From these experiences, he feels that Rust is a language that should contribute more to the container runtime field. At the beginning of the presentation, he explains container technology such as cgroups and Linux namespaces for those who have not had much exposure to OCI Runtime.

At KubeDay Japan
https://events.linuxfoundation.org/kubeday-japan/
https://sched.co/1C8lS
