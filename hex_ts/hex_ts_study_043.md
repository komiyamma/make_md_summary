# 43. まとめ：今日の合言葉3つ（再掲）🎁💖


([Past chat][1])([Past chat][2])

# 第43章：まとめ🎁💖「今日の合言葉3つ」だけ覚えて帰ろ〜！🛡️🔌🧩✨

この章はね、いままで作ってきた ToDo ミニアプリを思い出しながら、**迷子にならない“3つの合言葉”**を体に染み込ませる回だよ〜😊🌸
（ここ、ちゃんと入ると一気に設計がラクになるやつ！✨）

---

## 43.1 今日の合言葉3つ（再掲）🎁💖

* **中心を守る🛡️**
* **約束はPort🔌**
* **変換はAdapter🧩**

これが言えたら、もう半分勝ち〜！😆✨

---

## 43.2 合言葉①「中心を守る🛡️」＝ルールは“城の中心”に置く🏰

### ✅ 中心ってどこ？

* **domain**：ルールのコア（不変条件・状態・禁止事項）🧠
* **app（usecase）**：手順と判断（何を呼ぶか、どの順でやるか）🎮

中心は **「このアプリの正しさ」** を守る場所だよ💖

### ✅ 中心に置くもの（例）📝

* タイトル空は禁止🚫
* 完了の二重適用は禁止🚫（DoneにDoneはしない）
* 「追加できたら保存する」みたいな手順📌

### ❌ 中心に置かないもの（例）😱

* HTTPのRequest/Response
* DBのORMモデル
* ファイルパスやJSONの読み書き
* `console.log` だらけ（中心は静かに…🤫）

### 🧠 ミニ合言葉（追加）

**「中心は“外の都合”を知らない🙅‍♀️」**
中心が外の型を知った瞬間、城壁が崩れやすいよ〜💥

---

## 43.3 合言葉②「約束はPort🔌」＝中心が欲しい“差し込み口”を決める

### ✅ Portってなに？

中心（usecase）が「外にお願いしたいこと」を **interfaceで約束**するやつだよ🔌✨
例：保存したい、時間が欲しい、IDが欲しい…みたいな。

### ✅ コツは「最小の約束」✂️✨

Portがデカいと、中心が外に引っぱられて苦しくなる😵‍💫
だから **“いま必要な分だけ”** でOK！

#### 例：TodoRepositoryPort（最小）

```ts
export interface TodoRepositoryPort {
  save(todo: Todo): Promise<void>;
  findAll(): Promise<Todo[]>;
  findById(id: TodoId): Promise<Todo | null>;
}
```

### ⚠️ Portが太りがちな危険サイン🐘🍔

* `saveOrUpdateOrDeleteOrSearchOrWhatever()` みたいに何でも入り始めた
* DBの検索条件がそのままPortに漏れてる
* 「とりあえずRepositoryに全部」になってる

そんな時は、**“ユースケースの言葉”**に寄せて分割するとスッキリするよ😊✨

---

## 43.4 合言葉③「変換はAdapter🧩」＝外の都合を吸収する翻訳係🔁

### ✅ Adapterの役割（超シンプル）

* **外の形式 → 中のDTO/型** に変換
* **中の結果 → 外の形式** に整形
* I/Oの失敗を受けて、中心に影響を広げない（包む）🧯

### ✅ Adapterは「薄い」が正義🥗✨

薄い＝やることが少ない＝壊れにくい＝テストも簡単😆💕

### ❌ Adapterが太ったら負け😱

* ルール判断（タイトル空なら…とか）をAdapterでやり始めた
* 状態遷移（completeの二重防止）をAdapterでやり始めた
* 巨大`if`や業務フローが生えた

---

## 43.5 迷ったらこの「3問」だけで判定しよ🧭✨

何をどこに置くか迷ったら、これでOK😊💡

### Q1：それは“ルール”？（正しさの話？）🧠

* YES → **domain**（or usecase）🛡️
* NO → 次へ

### Q2：それは“手順”？（順番・分岐・判断の流れ？）🎮

* YES → **usecase（app）** 🛡️
* NO → 次へ

### Q3：それは“外の都合”？（HTTP/DB/ファイル/CLI等）🌐💾⌨️

* YES → **adapter** 🧩
  そして「差し替えたいなら」**portを切る🔌**

この3問、テスト前に毎回やると強いよ💪✨

---

## 43.6 30秒セルフチェック📝✅（Yesが多いほどキレイ！）

* 中心（domain/usecase）はHTTPを知らない🙅‍♀️
* 中心はDBの型を知らない🙅‍♀️
* Adapterは変換とI/Oだけしてる🥗
* ルールはdomain/usecaseに寄ってる🛡️
* 差し替えたい外部依存はPortになってる🔌
* テストがInMemoryで速い🧪⚡

YESが増えるほど、ヘキサゴナルっぽさ爆上がり〜！✨✨

---

## 43.7 5分ミニ実践🔧✨：「直結のつらさ」を合言葉で分解する

### 😵‍💫 直結（つらい）

* “保存したい”のに、ファイル形式やパスや例外が中心に混ざってくる
* ルールが散らばって、修正が怖くなる

### 😊 合言葉で分解する（超ざっくり手順）

1. **中心を守る🛡️**：ルールと手順だけ残す
2. **約束はPort🔌**：保存・取得をinterfaceにする
3. **変換はAdapter🧩**：JSON/ファイル/HTTPは外で吸収

この3ステップを「呪文」みたいに回すと、だいたい片付くよ🪄✨

---

## 43.8 そのまま使えるAIレビュー質問テンプレ🤖✅

コピペでOKだよ〜😊💕

* 「この差分で、**中心が外部型（HTTP/DB/FS）を参照してないか**チェックして」
* 「Adapterが**業務ルール（バリデーションや状態遷移）を持ってないか**見て」
* 「Portが大きすぎない？ **最小化できる案**を出して」
* 「このユースケース、**テストがInMemoryで書ける形**になってる？」

---

## 43.9 まとめカード📸✨（スクショ推奨！）

* **中心を守る🛡️**：正しさ（ルール/手順）だけ置く
* **約束はPort🔌**：中心が外へお願いするinterface（最小で！）
* **変換はAdapter🧩**：外の都合を翻訳して中心を汚さない（薄く！）

---

## 43.10 2026年っぽい“足元情報”メモ🗂️✨（安心して進めるために）

* TypeScript は **npm上の最新が 5.9.3**（2026年1月時点の表示）だよ。 ([NPM][3])
* TypeScriptチームは **5.9 → 6.0（橋渡し）→ 7.0（ネイティブ化）**の流れを説明してるよ。 ([Microsoft for Developers][4])
* Node.js は **v24がActive LTS**で、v25がCurrent、みたいに線が分かれてるよ。 ([Node.js][5])
* テストは Vitest 側で **Vitest 4.0**が出て大きめ更新が入ってるよ。 ([vitest.dev][6])
* Lintは ESLint が **v10 のRC**を出していて、移行の話が出てるよ。 ([eslint.org][7])

（“最新だからエラい”じゃなくて、**道具の変化を知っておくとハマりが減る**って感じね😊✨）

---

ここまでできたら、もう設計の迷子率がガクッと下がるはず！😆💖
次は「クリーンアーキとの関係」へ橋渡しして、親戚関係をスッキリさせよ〜🌉✨

[1]: https://chatgpt.com/c/6972e69a-8e08-8321-b4f6-596e652a4f69 "Adapterの役割と注意点"
[2]: https://chatgpt.com/c/6972c89e-f628-8323-b961-a6c3c8dea31e "AI拡張準備ガイド"
[3]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "typescript"
[4]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[5]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[6]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[7]: https://eslint.org/blog/2026/01/eslint-v10.0.0-rc.0-released/?utm_source=chatgpt.com "ESLint v10.0.0-rc.0 released"