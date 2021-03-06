---
title: "GWにフロントエンド力を鍛えつつ飲食店の手助けをちょっとできた話"
date: 2020-05-10T22:30:00+09:00
tags: [tech, frontend]
---

# はじめに

GW を機に初めて、ちょっと本格的なフロントエンドに触れてみました。  
僕は本格的なフロントエンドに触れてこないまま生きてきたので、そろそろ重い腰をあげてお気持ちくらいはわかるようになろうかなと思ってやってみました。
プラスアルファでこのご時世で困っていたよく行く飲食店のお手伝いができました。  
そこの飲食店では世間的にテイクアウトを始めたが、ホームページの更新を自力でするのが大変...  
そこで前々から「作ってくれない？」みたいな話を冗談っぽく話していたので、この GW を機会に本当に挑戦してみました。

### 成果物

そして GW の暇を持て余して出来上がったサイトは[こちら](https://vineria-sorcuore.netlify.app)です。初挑戦にしてはなかなかいい感じになったかなと思ってます。  
MIT ライセンスで公開しているので、他の飲食店とか用に使ってもらっても構いません。  
https://github.com/utam0k/vineria-sorcuore

### 制約

1. 僕たちが介入せずにメニューの更新が簡単にできるようにする
1. なんとなくそれっぽデザインにする
1. レスポンシブデザイン
1. 0 円[^*]

[^*]: 僕も勉強がてらやっているのでもちろんお金等は受け取っていません。その代わりに OSS にすることは許してもらいました。

### 動機

- 業務でフロントエンドに触れる機会が増えてきた
- ほとんど触れてこなかったフロントエンドにそろそろ重い腰をあげてやろう
- 良い題材が見つかった

# 利用したツール・サービス

### Storybook

今回は複数人で開発したため、PR のレビュー用に [Storybook](https://storybook.js.org) を使いました。
GitHub Actions を使って `@deploy-storybook`ってコマンドを作り、このコマンドが PR のコメントに出現するのをトリガーとして、gh-pages にデプロイする感じにしてすごくありがたく使えました。
この技は色々なところに使えそうでよかったです。
{{% figure src="deploy-storybook.png" %}}

### メニューを簡単に更新できるようにする

今回最も特徴的だったのはここかなと思います。
結論から言うと google スプレッドシートを api にしました。

{{% figure src="takeout.png" %}}

苦労した点としてはレスポンスが遅いところですね。
ここは Google Apps Script にキャッシュ機能があったのでそれを使って 1s くらいに収まるようになんとかなりました。
そして、レスポンスが返ってくるまでの誤魔化しとして、スケルトンってやつを学びました。

### 画像

飲食店のホームページとなると素敵な写真が必要です。
僕たちは[Google フォト](https://www.google.com/intl/ja/photos/about/)を画像のホスティングサービスとして利用しました。
無料かつ、お店の人も写真をあげて更新しやすいと言う点で採用しました。

### next.js

React で開発するのに便利なやつ

### netflify

ホスティングには netlify を使いました。無料枠でそこそこ使えればよかったので、すごい理由があったわけではないです。  
https://www.netlify.com

### chakra-ui

それっぽいデザインをするやつ  
レスポンシブデザインにするのにすごい役立ちました！  
https://chakra-ui.com

### ペアプロツール

- VSCode の Live Share  
  超便利でした。特に shared server とかはびっくりしました。本当に便利ですね。
  ちなみに僕は普段は vim を使っています。
- Slack の通話  
  お絵かきができて、フロントエンド開発ではすごくいいですね。

## やり残している事

ドメインの取得ですね。これはお金がかかる事なのでメリットとデメリットを伝えて判断してもらっているところです。
狙いとしては、もし僕たちがバスに轢かれたりしても違うドメインに変更せず、新しいサイトを作れるかなと言うのが狙いです。

# 謝辞

今回はフロントエンドプロのお友達の[succie](https://twitter.com/succie319)とペアプロして教わりながらやりました。ありがとうございます。
またコントリビュータの[chao](https://twitter.com/chao7150)くん、[asakura](https://twitter.com/asakura_dev)くんにも助けてもらいました。ありがとうございます。
[1 冊ですべて身につく HTML & CSS と Web デザイン入門講座](https://www.sbcr.jp/product/4797398892/)を参考書として使わせてもらいました。

# 終わりに

最後に無事に robots.txt を消し去り、リリースできました。お店の人たちも喜んでくれたみたいでよかったです。
ちなみに画像や文言はインスタの DM とかでやってました。
一通りやってなんとなく雰囲気でフロントエンドが書けるようになった気になってきて、やってよかったなって気分に今、浸っています。  
エコシステム周り・CSS とか特に難しかったです。
flex ってやつ難しいですね...
他にもこんな感じでやるといいんじゃないとかあったら教えてもらえると助かります！ PR もお待ちしてます。  
ところで、明日から労働ってまじですか。
