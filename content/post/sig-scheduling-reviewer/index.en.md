---
title: Becoming a SIG-Scheduling Reviewer
date: 2025-12-09T00:00:00+09:00
categories: [tech, diary]
tags: [kubernetes, oss]
description: "I became a Kubernetes SIG-Scheduling Reviewer"
---

Hi there 👋

{{< github "https://github.com/kubernetes/kubernetes/pull/133355" >}}
{{< x user="utam0k" id="1953044009795915797" >}}

Today I'd like to share this news.
It feels a bit late to write about it, but since it's a memorable milestone, I wanted to document it.

# Roles in Kubernetes

This is one of the roles in the Kubernetes community.
The progression goes [Member → Reviewer → Approver](https://github.com/kubernetes/community/blob/2833580db42e109d935c608660b0130a40c93bd3/community-membership.md#community-membership). This post is about becoming a [Reviewer](https://github.com/kubernetes/community/blob/2833580db42e109d935c608660b0130a40c93bd3/community-membership.md#reviewer).
To become a Reviewer, you mainly need to meet the requirements of "creating 20+ PRs" and "reviewing 5+ PRs".
I feel there's a significant barrier here compared to the Member requirements.
For more details, sanposhiho wrote an excellent article, so please refer to that.

{{< ogp "https://sanposhiho.com/posts/scheduling-reviwer/" >}}

# What I Did

I became a Member in December 2023, and spent about 2 years steadily contributing.
When the requirements were within reach, I focused my efforts on SIG-Scheduling and pushed hard to complete them.

Here's what I specifically did:

- Participating in KEP implementations
  I participated in implementing several KEPs. SIG-Scheduling still has many KEPs, so feel free to check them out if you're interested.

- Picking up abandoned issues
  I found and addressed issues that had been left unattended. It's unglamorous work, but it matters.
  Good First Issues are highly competitive.
  Because of this, it's difficult to create 20 PRs from Good First Issues alone. So I looked for older issues that seemed to have been abandoned.

- Participating in reviews
  I actively reviewed areas I could understand, like scheduler_perf.

- Contributing to subprojects
  I occasionally contributed to subprojects under SIG-Scheduling. This isn't related to becoming a Reviewer, but I did it because it was fun.

# After Becoming a Reviewer

As a Reviewer, you start receiving review requests.
This forces you to catch up and read the code, which is very educational.
Honestly, this might be what I'm happiest about.

Also, joining an existing community as a completely new contributor has been a great learning experience. Naturally, Kubernetes has many talented engineers, and I've learned a lot from reviews. Since I'm essentially learning Go for the first time through Kubernetes, I often receive very helpful feedback. There are also many Kubernetes-specific utility libraries (e.g., Set) that I need to get familiar with.

I was happy when [@aojea](https://github.com/aojea), whom I had met at KubeCon, commented on my PR. The people I've met face-to-face at maintainer summits and KubeCon have been very welcoming, and I'm truly grateful.

I'll keep at it, one step at a time.
