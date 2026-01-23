# 第5章 Portってなに？（差し込み口＝約束）🔌😊

この章は「Port＝中心（ユースケース/ドメイン）が外側にお願いする“約束”」を、ちゃんと体でわかるようにする回だよ〜🧠💕
Ports & Adapters（ヘキサゴナル）は、**中心を外側（UI/DB/外部API/ファイル）から独立させる**のが主目的で、その“接続点”が Port なのです🔌🛡️ ([Alistair Cockburn][1])

---

## 1) まず結論：Portは「中心が決める、やってほしいことリスト」📜✨

Port はざっくり言うと、

* **中心が外側に対して「こうやって呼んでね」「これを返してね」って決める“約束”**
* そして外側は、その約束に合わせて実装（＝Adapter）する

っていう関係だよ🔌🧩

ポイントはここ👇
✅ **Portは“中心側が持つ”**（中心が主導権を握る）
✅ **外側の都合（DBの形、HTTPの形、フレームワークの型）を中心に持ち込まない**
この思想が Ports & Adapters の核だよ〜🛡️ ([Alistair Cockburn][1])

---

## 2) 「Port＝interface」って思ってOK？🤔➡️ だいたいOK！🙆‍♀️

TypeScriptだと Port はたいてい **interface**（または type）で表現するよ✨
理由はシンプルで、

* 約束＝「メソッド名」「引数」「戻り値」
* 実装は外側に置く（Adapterがやる）

って形にぴったりだから😊

---

## 3) Portには2種類あるよ（超重要）🚪➡️⬅️

### 🟦 Inbound Port（外→中）🚪🔌

外側（CLI/HTTP/UI）が、中心のユースケースを呼ぶための入口。
例：AddTodo, CompleteTodo, ListTodos みたいな「アプリの操作」🎮

### 🟧 Outbound Port（中→外）💾🔌

中心が、外側（DB/ファイル/外部API）にお願いするための出口。
例：Todo を保存する、取得する、通知する、時間を取る…など⏰📨

この分類は Ports & Adapters の定番整理だよ📌 ([ウィキペディア][2])

---

## 4) Port設計のコツ：「最小の約束」にする✂️✨

Portって、作り方を間違えると一気にしんどくなるの…😵‍💫
だから合言葉はこれ👇

### ✅ “最小の約束”にするコツ3つ🌱

1. **ユースケースが本当に必要な操作だけに絞る**
2. **外側の事情が透ける名前/型にしない**（HTTPっぽい、DBっぽい、ファイルっぽいのNG🙅‍♀️）
3. **「なんでもできるポート」を作らない**（巨大化の原因🐘🍔）

---

## 5) 例で体感：ToDoミニの Port を作ってみる📝💖

ここでは「中心が欲しい約束」を、まず書いちゃうよ😊
（Adapterは次章で実装するイメージ🧩）

### 5-1) Inbound Port（ユースケース入口）🚪🔌

```ts
// app/ports/inbound/AddTodoPort.ts
export interface AddTodoPort {
  execute(input: { title: string }): Promise<{ id: string }>;
}

// app/ports/inbound/ListTodosPort.ts
export interface ListTodosPort {
  execute(): Promise<Array<{ id: string; title: string; completed: boolean }>>;
}
```

* **execute** だけで十分なことが多いよ（まずは迷子防止🧭✨）
* input/output は「外に見せる形」なので、ここではシンプルにしてOK📮

### 5-2) Outbound Port（保存のお願い）💾🔌

```ts
// app/ports/outbound/TodoRepositoryPort.ts
export interface TodoRepositoryPort {
  save(todo: { id: string; title: string; completed: boolean }): Promise<void>;
  findById(id: string): Promise<{ id: string; title: string; completed: boolean } | null>;
  list(): Promise<Array<{ id: string; title: string; completed: boolean }>>;
}
```

ここでの気持ちはね👇
中心「ToDoを保存したい。**どう保存するかは知らん！**」🧠🛡️
外側「了解！配列でもファイルでもDBでも、任せて！」🧩✨

この“中心は外側の具体を知らない”が、依存逆転の美味しさだよ〜🔁🧪 ([martinfowler.com][3])

---

## 6) やりがち事故：「Portが太る」😱🐘

### ❌ ダメ寄り例：巨大Port（なんでも屋）🧹😵

```ts
export interface TodoRepositoryPort {
  save(todo: any): Promise<void>;
  update(todo: any): Promise<void>;
  delete(id: string): Promise<void>;
  findById(id: string): Promise<any>;
  findByTitle(title: string): Promise<any[]>;
  search(query: string, page: number): Promise<any>;
  exportCsv(path: string): Promise<void>;
  importCsv(path: string): Promise<void>;
  // ...増殖
}
```

これ、最初は便利そうに見えるけど…
**中心が「外側の都合（CSVとか検索ページングとか）」に引っ張られて崩れていく**やつ😵‍💫💥

### ✅ 太り判定チェックリスト🥗✅

* Portのメソッド名が **技術の言葉** になってる（CSV/SQL/HTTP/ORM など）❌
* Portの引数/戻り値が **外部ライブラリの型** になってる❌
* 1つのPortが **複数の目的** を背負ってる（保存＋エクスポート＋検索UI事情）❌

Ports & Adapters は「中心を汚さない」が正義だよ🛡️✨ ([Thoughtworks][4])

---

## 7) Portが増えすぎて死ぬ問題💀➡️ 予防線を張ろう⚠️

Wikiでも「ポートの数や粒度は固定じゃない（極端にユースケースごとでもOK）」って言われるけど、**実務では“増えすぎ”が普通に事故る**の🥹 ([ウィキペディア][2])

だからおすすめはこれ👇

### ✅ ちょうどいい粒度の目安📏✨

* Inbound Port：**1ユースケース = 1 Port** から始める（迷子にならない）🧭
* Outbound Port：**外部の“種類”ごとに1 Port**（保存、通知、時間、外部API など）🧩
* そして「必要になったら分割」する（先に作りすぎない）🌱

---

## 8) AI拡張の使いどころ（Port編）🤖💖

AIは Port 設計で**やりがちな事故**があるの👇
「便利そうだから何でも入れちゃう」🐘🍔

なので、使い方はこうがおすすめ✨

### ✅ AIに頼ってOK（安全）🧰

* Portの命名案を複数出させる（言葉選び）🗣️
* 既にある Port を見せて「大きすぎない？」ってレビューさせる🔍
* input/output を「もっと小さくできる？」って削らせる✂️

### ⚠️ AIに任せすぎNG（危険）🧨

* 「Portの責務を決める」そのものを丸投げ
* 「将来必要そう」を理由にメソッド増やしまくる提案を採用

### コピペで使える質問テンプレ📝🤖

* 「この Port は“最小の約束”になってる？不要な操作が混ざってない？」
* 「技術都合（DB/HTTP/ファイル）っぽいメソッド名が混ざってない？」
* 「この Port の変更理由は1つに絞れてる？」

---

## 9) この章のまとめ🎁💖

* Port は **中心が外側に出す“約束”** 🔌
* Port は **中心が持つ**（主導権は中心）🛡️
* Port は **最小の約束** にする（太ったら負け🥗）
* Inbound/Outbound を分けると整理が楽になるよ🚪➡️⬅️

次章は、いよいよ **Adapter（実装）** に入って「この約束を外側でどう叶えるか」を作っていくよ〜🧩🚀✨

[1]: https://alistair.cockburn.us/hexagonal-architecture?utm_source=chatgpt.com "hexagonal-architecture - Alistair Cockburn"
[2]: https://en.wikipedia.org/wiki/Hexagonal_architecture_%28software%29?utm_source=chatgpt.com "Hexagonal architecture (software)"
[3]: https://martinfowler.com/articles/badri-hexagonal/?utm_source=chatgpt.com "Badri on Hexagonal Rails"
[4]: https://www.thoughtworks.com/insights/blog/architecture/demystify-software-architecture-patterns?utm_source=chatgpt.com "Demystifying software architecture patterns"
