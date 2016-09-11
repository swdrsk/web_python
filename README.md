# web_python

Python2.7で動作確認

世界中のタイムラインからツイートを取得し、
返信先・タグ・webのリンクを除外して自分のアカウントで投稿するプログラム。

実行：stream_tweet.pyが実行用ファイル

OAuth認証が必要。上の階層にaccount.csvとしてcsv形式で保存する。
「アカウント名、consumer key, consumer keyの秘密鍵,access token,access tokenの秘密鍵」
の順に保存

例: "account.csv"
> account,consumer_key,consumer_secret,access_token,access_token_secret

> xxxx,xxxx,xxxx,xxxx,xxxx
