# 第7章：Inbound / Outbound を超やさしく整理 🚪➡️⬅️✨

（ヘキサゴナル＝Ports & Adapters の“方向感覚”をゲットする回だよ〜🧭💕）

---

## 1) まず、今日のゴール 🎯✨

この章が終わったら、こんな状態になってればOKだよ😊

* 「これ、Inbound？ Outbound？」を**迷わず分類**できる👍
* 「Portはどこに置く？」が**ブレなくなる**🔌✨
* 図を見たときに、**矢印の向き（誰が誰を呼ぶ？）**が読める👀🧠

---

## 2) いちばん大事な考え方：**“アプリの中心から見て”どっち向き？** 🏰🛡️

Inbound / Outbound は、ネットワークとかHTTPの向きじゃなくてね…

**アプリの中心（ユースケース／ドメイン）**を真ん中に置いたときに、

* **Inbound（外→中）**：外の世界が中心に「やって〜！」って頼みに来る
* **Outbound（中→外）**：中心が外の世界に「お願い〜！」って頼みに行く

って整理すると一発で迷子が減るよ😊✨

---

## 3) 超かんたん定義（暗記用）📌✨

### Inbound（外→中）🚪➡️🧡

* 例：画面ボタン、HTTPリクエスト、CLIコマンド、イベント受信
* 役割：外の入力を受けて、中心（ユースケース）を呼ぶ
* 別名：**Primary / Driving**（「アプリを動かしに来る側」）
  ※この呼び方は“Primary/Secondary adapters”の説明でよく出るよ🧩 ([Code With Arho][1])

### Outbound（中→外）⬅️➡️💙

* 例：DB保存、ファイル保存、外部API呼び出し、メール送信、時刻取得
* 役割：中心が必要とする外部機能を提供する
* 別名：**Secondary / Driven**（「アプリに呼ばれる側」） ([Code With Arho][1])

---

## 4) “Port”と“Adapter”を方向で結びつける 🔌🧩✨

ここで混乱しがちだから、超ていねいにいくね😊

### ✅ Port（ポート）＝約束（interface）🔌

* **中心が持つ「こうして欲しい」契約**
* つまり：中心の都合で決める（外の事情で決めない）
* これがヘキサゴナルの核だよ🛡️
  （Cockburnの原典でも「UIやDBなしで動くように作る」思想が強いよ） ([Alistair Cockburn][2])

### ✅ Adapter（アダプタ）＝変換係（実装）🧩

* 外の世界の都合（HTTP/DB/SDK/ライブラリ）を吸収して
* Portの形に合わせて “翻訳” してくれる係

---

## 5) 1枚でわかる：流れの図（ToDoミニのイメージ）📝✨

（中心＝UseCase。外側＝UI/DBなど）

```text
[ユーザー] 
   ↓ クリック/コマンド/HTTP  (Inbound)
[Inbound Adapter]  例: CLI / HTTP Controller
   ↓ Portの形にして呼ぶ
[Inbound Port]     例: AddTodoUseCase
   ↓（実体はUseCaseクラスでもOK）
[UseCase / Domain] ここが中心🏰
   ↓ 外部が必要になったら
[Outbound Port]    例: TodoRepository
   ↓ 実装は外側
[Outbound Adapter] 例: InMemoryRepo / FileRepo / DB
   ↓
[DB/ファイル/外部API]
```

---

## 6) 具体例で「分類」してみよっか 😊🔍✨

### 🎀 Inbound になりがちリスト（外→中）🚪➡️

* HTTPのルーティング（Expressの `POST /todos` とか）🌐
* 画面のボタンクリック（フロントなら）🖱️
* CLIの `todo add "買い物"` みたいなコマンド⌨️
* イベント受信（Webhook/キューのconsume）📨

### 🧊 Outbound になりがちリスト（中→外）⬅️➡️

* DBへの保存／取得 💾
* ファイル読み書き 📄
* 外部API呼び出し（決済、翻訳、地図…）🌍
* 時刻取得（Clock）⏰
* UUID発行（ID生成）🆔
* ログ出力（※置き場所は設計次第だけど、外側に寄せがち）🪪

---

## 7) ここが超重要：**“中心がPortを持つ”** ルール 📌🛡️

Inbound/Outboundの整理で、最終的に守りたいのはこれ👇

* ✅ **中心がPort（約束）を定義する**
* ✅ 外側は、そのPortに合わせてAdapterを作る
* ✅ 外側の技術が変わっても、中心はなるべく無傷💖

これが「差し替え気持ちいい〜🥹✨」の正体だよ！

---

## 8) ミニコード：Inbound/Outbound を“形”で見て安心する 🧩🔌

### Inbound Port（中心の入口）🚪🔌

「ToDo追加してね」っていう入口の約束：

```ts
export interface AddTodoUseCase {
  execute(input: { title: string }): Promise<{ id: string }>;
}
```

### Outbound Port（中心が外にお願いする口）💾🔌

「保存してね」っていうお願い口：

```ts
export interface TodoRepository {
  save(todo: { id: string; title: string; completed: boolean }): Promise<void>;
}
```

### Inbound Adapter（外→中の翻訳係）⌨️🧩

CLIが受けた文字列を、Portの形にして呼ぶ：

```ts
export async function cliAdd(title: string, addTodo: AddTodoUseCase) {
  // 入口側で軽く整える（parse/validate寄り）
  const trimmed = title.trim();

  const result = await addTodo.execute({ title: trimmed });
  console.log(`added! id=${result.id}`);
}
```

### Outbound Adapter（中→外の実装係）📄🧩

Repositoryの実装（外側の都合を担当）：

```ts
export class InMemoryTodoRepository implements TodoRepository {
  private store: Array<{ id: string; title: string; completed: boolean }> = [];

  async save(todo: { id: string; title: string; completed: boolean }) {
    this.store.push(todo);
  }
}
```

「どっちがどっち？」は **“中心から見て方向”** を思い出せば大丈夫だよ😊🧭✨

---

## 9) よくある勘違い集 😵‍💫💥（ここで潰す！）

### ❌ 勘違い1：「HTTPはInboundでしょ？じゃあHTTPクライアントもInbound？」

→ **違うよ〜！**

* HTTPサーバで受ける（Request来る）＝**Inbound**
* 外部APIに投げに行く（fetch/axios）＝**Outbound**
  「中心が外へお願いしに行く」ならOutboundだよ🌐⬅️➡️

### ❌ 勘違い2：「PortはAdapter側に置くんじゃないの？」

→ 基本は **中心がPortを持つ** が軸だよ🛡️
（原典の思想も“中心を外部から独立させる”が強いよ） ([Alistair Cockburn][2])

### ❌ 勘違い3：「Inbound Portって本当に必要？直でUseCase呼べばよくない？」

→ 小さいうちは直でも動く！でもね…

* 「入口を複数にしたい（CLI→HTTP→GUI）」
* 「入口の差し替えテストしたい」
  みたいになった時、Portのありがたみが出るよ😊✨
  （設計は“未来の痛み”を少し先払いする感じ💸）

---

## 10) AIに頼るとめっちゃ捗る使い方 🤖💖（第7章向け）

### ✅ 使っていい頼み方（分類・レビュー向き）

* 「この部品は inbound/outbound どっち？理由も！」
* 「このAdapter、変換以外の責務が混ざってない？」
* 「Portがデカすぎない？最小化案ちょうだい✂️」

### ⚠️ ちょい注意（芯は自分で握る）

* 「Port設計そのもの」を丸投げすると、依存の向きを崩されやすいことある🥲
  なので AI には **“案を出させて、あなたが採用判断”** が最強だよ💪✨

---

## 11) まとめ 🎁💖（今日の覚え方）

* Inbound：**外→中**（アプリを動かしに来る）🚪➡️
* Outbound：**中→外**（アプリがお願いしに行く）⬅️➡️
* Port：**中心の約束（interface）**🔌
* Adapter：**外側の翻訳＆実装**🧩
* 合言葉：「**中心がPortを持つ**」🛡️✨

---

## 12) 次章のチラ見せ 👀✨

次の第8章は、いよいよ **依存の向き（中心は外を知らない！）** に突入だよ🧭🔥
第7章で “Inbound/Outbound の整理” ができた人は、ここめっちゃスムーズに入れるはず😊💕

---

### 📝 おまけ：超ミニ課題（3分）⏱️✨

次の部品を「Inbound / Outbound」に分類してみてね😊

1. `POST /todos` のルート処理
2. `TodoRepository.save()`
3. ファイルにJSONを書き込む処理
4. `fetch("https://api.example.com/...")`
5. CLIコマンド `todo add`

（答え：1 Inbound、2 Outbound Port、3 Outbound Adapter、4 Outbound Adapter、5 Inbound Adapter だよ〜🎉）

---

🔎 ちなみに「最近の開発環境の空気感メモ」だけ置いとくね：TypeScriptの安定版は npm 上では 5.9.3 が “Latest” 表示で、TypeScript 7（Go移植）の進捗アップデートも出てるよ（この教材は“今すぐ普通に開発できる現実ライン”を優先して組んでいくね） ([npmjs.com][3])

[1]: https://www.arhohuttunen.com/hexagonal-architecture/?utm_source=chatgpt.com "Hexagonal Architecture Explained"
[2]: https://alistair.cockburn.us/hexagonal-architecture?utm_source=chatgpt.com "hexagonal-architecture - Alistair Cockburn"
[3]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "typescript"
