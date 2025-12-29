---
title: "OSS の脆弱性対応の舞台裏"
date: 2025-12-29T10:20:00+09:00
tags: [oss, security, youki]
description: "OSS の脆弱性対応の舞台裏でメンテナの努力を紹介します。"
draft: false
---

OSS では日々様々なセキュリティ対応がされています。[私自身も CVE を発行したり、対応をした経験があります。](https://github.com/advisories?query=credit%3Autam0k)

最近だと [CVE-2025-62596](https://nvd.nist.gov/vuln/detail/CVE-2025-62596) の対応をしました。

公開後の情報がまとまった CVE や以下のような Security Advisory を見ることは多くあると思います。

{{< figure src="advisory.png" caption="[GHSA-vf95-55w6-qmrf](https://github.com/youki-dev/youki/security/advisories/GHSA-vf95-55w6-qmrf)" >}}

実はその裏には対応者や、クレジットには載っていない関係者の努力が隠れています。
また、そういった公開までの舞台裏でどういう作業がされているかは表に書かれることは多くありません。
この記事では公開情報だけでは見えにくい、脆弱性報告を受けてからの議論、CVE 取得、公開までの流れを少し紹介します。

# Overview: OSS 脆弱性対応フロー

あくまでも一例ですが、GitHub で OSS を運用している場合の一般的な流れは以下のようなケースが多くあるのかなと思います。

1. 脆弱性の報告を受ける
2. 脆弱性を確認する
3. Security Advisory を作成し関係者を招待する
4. 関係者で議論し、脆弱性の概要と [CVSS](https://en.wikipedia.org/wiki/Common_Vulnerability_Scoring_System)(Common Vulnerability Scoring System) などのスコアを決める
5. CVE をリクエストして取得する
6. パッチを作成してレビュー
7. ベンダーや関連 OSS メンテナに連絡し、調整を行う
8. パッチをマージし、Security Advisory を公開する

1 と 2 については多くはメールでやりとりをされているかなと思います。3〜8 は GitHub の機能で完結します。

# 舞台裏で起きていること

ここからは各ステップで舞台裏で起きていることを深掘りします。

## 脆弱性の判定

最初は脆弱性と疑われる箇所について報告を受け、それが本当に脆弱性かどうかを判定します。  
まずどのような人が報告をしてくれるかというと以下のような方々をよくお見かけします:
- セキュリティベンダーのリサーチャー
- 大きな企業のセキュリティのリサーチャー
- 大学でセキュリティの研究をされている方

彼らから報告を受けるとまずは、メールなどで脆弱性かどうかの判定を行います。ここが一番重かったりします。
報告内容の再現が難しいこともあります。例えば、レースコンディション絡みの脆弱性は再現がぐっと難しくなります。

また、私の扱う領域ではいくつかの報告のケースで脆弱性の判定にはならず、仕様となることもあります。
結果的に脆弱性にならないケースでも、メンテナは時間をかけて検証や返信をします。
そのため、気軽に LLM などで投げられるとつらいです。実際に curl ではそのような問題について触れられています。

{{< ogp "https://www.linkedin.com/posts/danielstenberg_hackerone-curl-activity-7324820893862363136-glb1/">}}

## 議論

脆弱性の可能性があると認められると GitHub Security Advisory が作成されます。

{{< figure src="advisory.png" caption="一般的な Security Advisory の画面" >}}

実はこの Security Advisory には表に見えていない機能が多数存在しています。GitHub 様ありがとうー。
これらの機能は Security Advisory にコラボレーターとして招待された方だけが使えます。
コラボレーターにはメンテナだけではなく、報告者や関連する OSS のメンテナなどが招待されることが多いです。
まず、Security Advisory は作った時点では公開されていません。コラボレーターのみが見える形になります。
後述する手順で公開作業を行います。
コラボレーター同士は通常の GitHub の Issue のようにプライベートで議論されます。

{{< figure src="advisory_overview.jpg" caption="Security Advisory のコラボレーター画面" >}}

この機能を利用して脆弱性についての議論や PoC の作成が行われます。
また、CVSS スコアについても議論されます。

## CVE ID の取得

議論を通してこれは脆弱性だと認められると、CVE ID の取得に移ります。
Security Advisory の Overview や CVSS、影響バージョンなどを記入して、Request ボタンを押すと CVE ID の取得を GitHub がやってくれます。
メンテナは必要な項目を埋めて、ボタンを押すだけです。

{{< figure src="request_cve.png" caption="CVE ID リクエスト" >}}

ちなみに CVE が妥当かどうかも簡単に見てくれているようで、私は正当な理由で Reject をされたことがあります。  
_// その後、書き直して無事に取得できました。_

{{< figure src="CVE_reject.png" caption="CVE ID の取得が Reject された例" >}}

## 修正パッチの作成

さて、ここまでくるとパッチの作成です。実際には CVE ID の取得や議論と同時にパッチの作成に取りかかることもあります。
ここでは、GitHub の [temporary private fork](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/collaborating-in-a-temporary-private-fork-to-resolve-a-repository-security-vulnerability) という機能を利用します。
その名の通り関係者のみが閲覧可能なリポジトリが作成されます。そこで作られた PR が Security Advisory と紐付けられます。
その PR をマージすると fork 元の本体のリポジトリにそのまま取り込まれます。
これによって、関係者のみでパッチの作成やコードのレビューがいつもの開発体験で可能になっています。

{{< figure src="temporary_fork.png" caption="temporary private fork の画面" >}}

{{< alert warning >}}
ただし、temporary private fork では GitHub Actions が動きません。執筆時点では提供予定が見当たりません。
{{< github "https://github.com/github/roadmap/issues/627" >}}

実際にマージした後に CI が落ちてしまうということがありました。
ある程度の規模の OSS になると様々な環境をサポートしないといけないためこのあたりは厳しいのが現状です。
{{< /alert >}}

## 公開

パッチの PR の用意も完了し、CVE ID も取得できると公開の準備が整います。

ただし、すぐに公開するとは限りません。大規模に利用されている OSS の場合、公開と同時にユーザーがパッチを適用できるよう、主要なディストリビューションやクラウドベンダーに事前準備の時間を与えることがあります。
Open Container Initiative では [Embargo Policy](https://github.com/opencontainers/opencontainers.org/security/policy#disclosure-distribution-list) を定めて登録されているベンダーに事前に脆弱性やパッチの内容を共有しています。

準備が整ったら、Security Advisory の画面から "Publish advisory" ボタンを押すだけで公開完了です。手順自体は GitHub の公式ドキュメントがあります。
{{<ogp "https://docs.github.com/en/enterprise-cloud@latest/code-security/security-advisories/working-with-repository-security-advisories/publishing-a-repository-security-advisory#publishing-a-security-advisory" >}}

公開がされると Dependabot のアラートや CVE ページの更新が始まります。
CVE ページの更新は誰がどうやっているのかはよくわかりませんが、GitHub 側でやってくれているように見えます。
例えば、[CVE-2025-62596](https://nvd.nist.gov/vuln/detail/CVE-2025-62596) のページをみると GitHub が提供元として記載されています。私は特にこの部分を書いていません。

{{< figure src="cve_detail.jpg" caption="[CVE-2025-62596](https://nvd.nist.gov/vuln/detail/CVE-2025-62596)" >}}

# おわりに

このように OSS の脆弱性対応の裏には、ただパッチを書くだけではない作業が多数存在しています。
もし脆弱性の報告をするときは、わかりやすく再現性の高い PoC を添えるときっと喜ばれます。
今日も対応してくださっている開発者のみなさまありがとうございます。
