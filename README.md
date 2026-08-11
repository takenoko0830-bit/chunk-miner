# Chunk Miner

**公開先: https://takenoko0830-bit.github.io/chunk-miner/**

英語の文章を再利用可能な「チャンク」に分解して蓄積し、そこから生成した例文を音声で流してリピート練習するアプリ。

設計の背景・意図・却下した案は [HANDOVER.md](HANDOVER.md) を参照。**実装に手を入れる前に必ず読むこと。**

## ファイル構成

```
index.html             # アプリ本体。これ1枚で完結（Vanilla JS、ビルド不要）
chunks.json            # 共有ライブラリの正本。各端末が起動時に取得して統合する
chunks-YYYY-MM-DD.json # 各回の抽出結果（作業ファイル。正本ではない）
manifest.webmanifest   # ホーム画面に追加したときのアプリ定義
sw.js                  # オフラインで練習タブを動かすためのサービスワーカー
icons/                 # アプリアイコン（180 / 192 / 512）
.nojekyll              # GitHub Pages の Jekyll 処理を止める
```

## 端末間の同期

`chunks.json` が正本。アプリは起動するたびにこれを取得して統合するので、
**Mac で追加したチャンクは iPhone でアプリを開くだけで反映される。**

```
英文 → Claude Code が抽出 → chunks.json に統合 → git push
                                                    ↓
                       iPhone / Mac: アプリ起動時に自動で取り込み
```

**リポジトリ → 端末の一方向。** 端末側での編集・オンオフ・削除は正本に戻らない。
遭遇回数は正本とローカルの大きいほうを採るので、同期を繰り返しても増えない。

設定タブの「今すぐ取り込む」で手動実行もできる（通常は不要）。

## ローカルで動かす

`index.html` を直接開いても動きますが、`file://` では Anthropic API への通信がブロックされ、
サービスワーカーも登録できません。次のようにローカルサーバ経由で開いてください。

```bash
python3 -m http.server 8765
```

`http://localhost:8765/` を開きます。

## GitHub Pages（設定済み — 2026-08-11）

`file://` では Safari が JS を制限するため、iPhone から使うにはホスティングが必要。
以下は設定済みの内容の記録。作り直すときはこの手順をなぞる。

- リポジトリ: `takenoko0830-bit/chunk-miner`（**Public**）
- Pages: Source = `Deploy from a branch` / Branch = `main` / `(root)`
- 公開先: https://takenoko0830-bit.github.io/chunk-miner/

Public が必須（Private で Pages を使うには GitHub Pro 以上）。したがって `index.html` の
初期チャンク14件、同梱のサンプル英文、`chunks-*.json`、この README と HANDOVER.md は
誰でも閲覧できる。APIキーはリポジトリには入らず各端末のブラウザにのみ保存されるので、
公開されるのはアプリのコードとチャンクデータだけ。

### 認証について

push は HTTPS + Personal Access Token（classic）。GitHub はパスワード認証を廃止している。

- スコープは **`public_repo` だけでよい**。親の `repo` は非公開リポジトリまで含めた全権限で、
  この用途には過剰
- 初回の push でトークンを入力すると macOS のキーチェーンに保存され、以降は聞かれない
  （`credential.helper = osxkeychain`）
- ターミナル.app で実行すること。非対話シェルだと認証プロンプトに応答できず固まる

### iPhone に入れる

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
