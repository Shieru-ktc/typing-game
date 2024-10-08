# Typing Game

Python で作ったシンプルなタイピングゲームです。

## Features

- 柔軟なローマ字入力に対応
  - 「とっきょ」を「tokkyo」や「toxtukilyo」などで入力可能
  - 「ん」は「nn」または「xn」で入力可能。次キーが母音でなければ「n」でも入力可能。
- スコア送信に対応
  - このリポジトリにはスコアサーバーのコード及びエンドポイントは含まれていないため、ご自身で設定してください。

## Run locally

1. `venv`を作成（任意）
2. `requirements.txt`内のパッケージをインストール
3. `words.txt`を編集（任意）
4. `python game.py 10`でスタート。ランダムに 10 問出題する。

## Resources

このプロジェクトに用いている一部のリソースには、無料で公開されているものを流用しています。  
この場をお借りして御礼申し上げます。

### Font

フォントには[Google Fonts](https://fonts.google.com)の[Noto Sans JP](https://fonts.google.com/noto/specimen/Noto+Sans+JP)を使用しています。

### Sound

効果音には[効果音ラボ](https://soundeffect-lab.info/)のものを用いています。

## License

このプロジェクトは MIT ライセンスでライセンスされています。  
詳細は LICENSE ファイルを確認してください。
