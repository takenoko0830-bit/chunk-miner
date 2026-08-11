# Chunk Miner

英語の文章を再利用可能な「チャンク」に分解して蓄積し、そこから生成した例文を音声で流してリピート練習するアプリ。

設計の背景・意図・却下した案は [HANDOVER.md](HANDOVER.md) を参照。**実装に手を入れる前に必ず読むこと。**

## ファイル構成

```
index.html            # アプリ本体。これ1枚で完結（Vanilla JS、ビルド不要）
manifest.webmanifest  # ホーム画面に追加したときのアプリ定義
sw.js                 # オフラインで練習タブを動かすためのサービスワーカー
icons/                # アプリアイコン（180 / 192 / 512）
.nojekyll             # GitHub Pages の Jekyll 処理を止める
```

## ローカルで動かす

`index.html` を直接開いても動きますが、`file://` では Anthropic API への通信がブロックされ、
サービスワーカーも登録できません。次のようにローカルサーバ経由で開いてください。

```bash
python3 -m http.server 8765
```

`http://localhost:8765/` を開きます。

## GitHub Pages に公開する

iPhone から使うにはこれが必要です。`file://` では Safari が JS を制限するため、
ホスティングに置かないと iPhone では動きません。

### 1. GitHub にリポジトリを作る

github.com で新規リポジトリを作成します（例: `chunk-miner`）。README や .gitignore の
自動生成はオフにしてください。

**Public にする必要があります。** GitHub Pages を Private リポジトリで使うには GitHub Pro 以上が要ります。
Public にすると `index.html` の中身（同梱している症例プレゼンのサンプル英文と初期チャンク14件を含む）が
誰でも閲覧できる状態になります。APIキーはリポジトリには入らず、各端末のブラウザにのみ保存されるので、
公開されるのはアプリのコードと初期データだけです。

### 2. push する

`YOUR-NAME` を自分のアカウント名に置き換えて実行します。

```bash
git remote add origin https://github.com/YOUR-NAME/chunk-miner.git && git push -u origin main
```

### 3. Pages を有効にする

リポジトリの **Settings → Pages** を開き、**Source** を `Deploy from a branch`、
ブランチを `main` / `/ (root)` に設定して Save。1〜2分で公開されます。

公開先: `https://YOUR-NAME.github.io/chunk-miner/`

### 4. iPhone に入れる

1. Safari で上の URL を開く
2. 共有ボタン → **ホーム画面に追加**
3. アドレスバーのないアプリとして起動します
4. 「設定」タブで APIキーを入れる（端末ごとに必要）
5. Mac 側で「JSONで書き出す」→ iPhone で「JSONを読み込む」でチャンクを移す

### 更新するとき

```bash
git add -A && git commit -m "変更内容" && git push
```

push すると数十秒で反映されます。サービスワーカーはネットワーク優先なので、
アプリを開き直せば新しい版になります（キャッシュを消す操作は不要）。

## 制約

- **端末間で同期しない。** Mac と iPhone は別々に保存されます。JSON の書き出し／読み込みで手動で移します（統合方式なので重複しません）
- **iOS は画面ロックで読み上げが止まる。** Web Speech API の制限で、聞き流しには使えません
- **APIキーは localStorage に平文で保存される。** 個人端末専用の前提です。共有端末では使わないでください
