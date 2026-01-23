# 45. 自主課題（提出形式まで）📝🎀


# 第45章：自主課題（提出形式つき）📝🎀

ここは「理解したつもり」を卒業して、“差し替えできる中心🛡️”を体に覚えさせる回だよ〜！😊✨
課題A/B/Cをやると、ヘキサゴナルの気持ちよさ（中心そのまま・外だけ交換🔁）がガチで分かるようになる👍💕

---

## 0) まず今日の“提出物”のルールだよ📦✨

### ✅ 提出物（最低限セット）

* Gitのブランチを3本（A/B/C それぞれ）🌿

  * `ch45-a-db-repo`
  * `ch45-b-notify-port`
  * `ch45-c-state-machine`
* 各ブランチに **README**（後述テンプレ）📄
* **テストが通ること** 🧪✅（最低：ユースケース中心）
* **中心が外側を知らないこと** 🛡️（import方向の自己チェックあり）

### ✅ 推奨コマンド（提出前セルフチェック）🔍

* `npm run typecheck`
* `npm test`（Vitest想定🧪）
* `npm run lint`（ESLint v9のflat config想定🧹）

※ TypeScriptの安定版は npm 上で `5.9.3` が “Latest” として案内されているよ（2026-01時点）。([NPM][1])
※ ESLint v9 は `eslint.config.js` の flat config がデフォルトだよ。([ESLint][2])
※ Vitest は v4 が出てるよ。([Vitest][3])

---

## 1) README テンプレ（これを埋めれば提出になる）🧁✨

```md
# Chapter45 Submission ✅

## 1. 何をやった？（A/B/Cの概要）
- A: DB版Repositoryへ差し替え
- B: 通知Port追加（ダミー実装）
- C: 状態追加（簡易状態機械）

## 2. 実行方法
- npm i
- npm run typecheck
- npm test
- npm run lint
- （任意）npm run dev / npm start

## 3. アーキテクチャ（超短く）
- domain: ルール（不変条件）
- app: ユースケース（手順と判断）
- adapters: I/O実装（変換と呼び出し）

## 4. “中心を守れた”証拠
- domain/app が adapters を import してない（チェック方法を書く）

## 5. つまずき＆学び（3行で）
- 例：Portを大きくしすぎた → 最小に戻した、など
```

---

## 2) 共通の合格ライン（A/B/Cぜんぶ同じ）🛡️🔥

### ✅ 合格ライン 5つ✨

1. **domain/app が adapters を import しない** 🙅‍♀️
2. **Port は最小の約束**（でかくしない）🔌✂️
3. **Adapter は薄い**（変換＆呼び出しだけ）🧩🥗
4. **Composition Root だけが new する** 🧩🏗️
5. **ユースケースのテストが読み物みたい** 🧪📖

### 🔍 依存チェック（超かんたん自己ルール）

* `src/domain/**` と `src/app/**` 内のimportに `adapters` が出たらアウト⚠️
* 迷ったら：**外の型（HTTP/DB/ライブラリの型）を中心に入れない** 🙅‍♀️

---

## 3) 課題A：Repository を “DB版”に差し替え🔁💾（中心は無修正で！）

### 🎯 ゴール

「保存先が DB に変わっても、ユースケースは1行も変えない」✅✨
（変わるのは **Outbound Adapter と Composition Root だけ** が理想💖）

### 🧭 おすすめ方針（Windowsでつまずきにくい順）

* ① **SQLite（ローカルファイルDB）**：手軽・1台で完結🪄
* ② Postgres（Dockerなど）：本格派向け🐳
  ※ Node は v24 が Active LTS なので、まずは LTS で固めるのが安全だよ〜。([Node.js][4])
  （セキュリティ更新も出てるので、使ってる系統は上げようね🔒）([Node.js][5])

### ✅ 手順（SQLiteルート例）🪜

1. **DB用のOutbound Adapterを新規作成**

   * `SqliteTodoRepository` みたいな名前にする
   * 既存の `TodoRepositoryPort` を implements する🔌
2. **DBのテーブル設計を決める**（最小でOK）

   * `todos(id TEXT PRIMARY KEY, title TEXT, status TEXT, created_at TEXT ...)`
3. **Adapterの責務はここまで**🥗

   * domain型 ↔ DB行 の変換
   * insert/select/update の呼び出し
   * DBエラーを「外側エラー」にまとめる（例：`InfrastructureError`）
4. **Composition Rootで差し替える** 🧩🏗️

   * 本番：`SqliteTodoRepository`
   * テスト：`InMemoryTodoRepository`（今まで通り）
5. **テスト**🧪

   * ユースケース単体テストは InMemory のまま高速で✅
   * 追加で「DB版の軽い結合テスト」を1本だけ（任意だけど強い💪）

### 🧯 “あるある地雷”😵‍💫

* ❌ Adapterに「タイトル空禁止」とか書き始める（それ domain！）
* ❌ Portに「検索条件いっぱい」「ページング全部」盛る（最小じゃない）
* ✅ 迷ったら：「ユースケースが必要とした分だけ」Portに出す✂️

### 🧪 提出で光るテスト例✨

* 「DB版でも Add→List→Complete が通る」
* 「DBエラーを、HTTP/CLIに漏らさず、外側でメッセージ化できる」

---

## 4) 課題B：通知（ダミー）Port を追加📨🤖（Port設計の練習！）

### 🎯 ゴール

「中心が `console.log` や Slack API を知らずに、通知できる」✨
＝ **通知は Outbound Port** にするのが王道だよ🔌

### ✅ 仕様（シンプルでOK）🍰

* 何かが起きたら通知する

  * 例：Todo追加時 / 完了時
* 通知の中身は “文字列1本” から始めよう😊

  * `notify(message: string): Promise<void>` みたいな最小で👍

### ✅ 手順🪜

1. `NotificationPort` を作る🔌
2. ユースケースに注入して呼ぶ（成功したときだけでOK）✅
3. Adapterを2つ用意する🧩

   * `ConsoleNotificationAdapter`（CLI/HTTPで見る用）🖥️
   * `InMemoryNotificationAdapter`（テスト用：配列に溜める）🧪
4. Composition Rootで差し替える🏗️✨

### 🧪 テスト例（めっちゃ気持ちいいやつ）💖

* AddTodoしたら `notify` が1回呼ばれる
* 完了で `notify` が呼ばれる
* 失敗（タイトル空）では呼ばれない🚫

### 🧨 地雷

* ❌ Portを「メール送信の細かい項目」まで持たせる（大きすぎ）
* ✅ まずは「通知したい」という意図だけをPortにする🫶

---

## 5) 課題C：状態追加で “状態機械の入口” を体験🚦✨

### 🎯 ゴール

「状態が増えても、ルールが散らからない」🧠❤️
**if地獄を、ドメインの“遷移ルール”に閉じ込める** のが勝ち！

### ✅ 仕様例（おすすめ）🍓

* 状態：`Pending` → `Done` → `Archived`
* 禁止：

  * `Archived` を `Done` に戻すの禁止🙅‍♀️
  * `Done` を二重適用禁止（既にやったやつ）🚫

### ✅ 手順🪜

1. domainに `TodoStatus`（ユニオン型など）追加🧩
2. 状態遷移関数を domain に置く（超重要）🧷

   * `complete()` / `archive()` みたいな形
3. ユースケースは「手順」だけに寄せる🎮➡️🧠

   * 「できる？」の判断は domain へ
4. Repository/DTO/Adapter側の変換を更新🔁

   * File/DB/HTTPの表現（文字列） ↔ domain（型）
5. テスト🧪

   * OK遷移（Pending→Done）
   * NG遷移（Archived→Done）でエラーになる

### 💥 地雷

* ❌ HTTPの文字列（`"done"`）を domain で直接扱い始める
* ✅ domainは “意味のある型” で守って、外側で変換🧩✨

---

## 6) 採点ルーブリック（自己採点できるやつ）📊✅

### S（めちゃ良い）🌟

* 中心無修正で差し替え成功（A）
* Portが最小で、Adapterが薄い
* テストが読みやすい（仕様書みたい）🧪📖
* READMEに「中心を守った証拠」と「学び」がある

### A（良い）👍

* 動く＆テストある
* ちょい太いところがあるけど、境界は守れてる

### B（惜しい）🥺

* Adapterにルールが混ざる / Portが肥大化
* Composition Rootが散らばる（newが色んな所に出る）

---

## 7) AI拡張の“使い方テンプレ”（そのまま投げてOK）🤖📝

### 🔌 Portがデカくなってないか？

```text
このPortは最小の約束になっていますか？
- UseCaseが本当に必要な操作だけに絞れている？
- 外部事情（DB/HTTP）の都合が混ざっていない？
改善案があれば、Portを分割する案も出して。
```

### 🧩 Adapterが太ってないか？

```text
このAdapterは「変換」と「呼び出し」だけに収まっていますか？
- 業務ルール（禁止事項や判断）が入っていない？
- if/for が増えてきた理由を指摘して、移動先（domain/app）を提案して。
```

### 🛡️ 中心が外側を見てないか？

```text
domain/app が adapters や外部ライブラリの型に依存していないか確認して。
依存していたら、DTO/Port/変換のどれで切るべきか提案して。
```

---

## 8) 仕上げチェック（提出前の最終儀式）🎀✨

* ✅ `domain/app` を開いて、外部ライブラリのimportが無いか見る👀
* ✅ 「変換はAdapterに置いた？」🔁
* ✅ 「判断はdomain/appに置いた？」🧠
* ✅ テストが“仕様の文章”として読める？🧪📖
* ✅ READMEがテンプレ通り埋まってる？📄

---

## 9) ちょい最新トピック（知ってると気分が上がる）⚡

* TypeScript は 5.9 系が安定していて、今後は TypeScript 7 の “ネイティブ化” でビルドが大幅高速化する流れが公式から出てるよ（進捗報告あり）。([Microsoft for Developers][6])
  ※ いまの課題はそこに依存しないから、安心して“設計の筋トレ”に集中でOK😊💪

---

やる順番で迷ったら、**おすすめは B → A → C** だよ☺️✨
（Portを最小にする感覚🔌 → 差し替え体験🔁 → ルール増加への耐性🚦）

続けて、あなたの今のToDoミニアプリの構成に合わせて「AをSQLiteでやる場合のファイル配置案📁」も具体的に書いていいよ〜？🫶

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "typescript"
[2]: https://eslint.org/blog/2024/04/eslint-v9.0.0-released/?utm_source=chatgpt.com "ESLint v9.0.0 released - ESLint - Pluggable JavaScript Linter"
[3]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[5]: https://nodejs.org/en/blog/vulnerability/december-2025-security-releases?utm_source=chatgpt.com "Tuesday, January 13, 2026 Security Releases"
[6]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"