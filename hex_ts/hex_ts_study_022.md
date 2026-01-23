# 第22章：Outbound Port（Repository）を決める 💾🔌✨

この章はひとことで言うと、**「アプリの中心（ユースケース）が、保存先の都合に振り回されないための“約束”を決める回」**だよ〜😊🌸
Repository は **“保存のお願い窓口”**（Outbound Port）って感じ！🔌💖

---

## 1. 今日のゴール 🎯✨

この章が終わったら、次ができるようになるよ😊

* ✅ Repository（Outbound Port）が **なぜ必要か** 説明できる
* ✅ ToDoアプリに必要な **最小のRepositoryインターフェース** を自分で決められる
* ✅ 「Repositoryが何でも屋になる事故」を **未然に防げる** 🚫🧹

---

## 2. Repositoryってなに？（超やさしく）🧺💡

Repository は、ざっくり言うと

> **「ドメインのオブジェクトを“メモリ上のコレクションみたいに扱える”ようにする仕組み」**

ってイメージでOK😊🧺
「配列っぽく `追加/取得/検索` できるように見せる」みたいな発想だね✨
（この“コレクションっぽい”説明は Martin Fowler の定義が有名だよ）([martinfowler.com][1])

そして重要なのがここ👇

* Repository は **DBのためのクラス** じゃない
* Repository は **中心（ドメイン/ユースケース）のための“契約（interface）”** 🔌✨
* 実装（DB/ファイル/メモリ）は外側（Adapter）が担当 🧩💪

「中心に interface（抽象）を置いて、外側が実装する」って考え方は、RepositoryをDDDの文脈で説明する資料でもよくこう書かれるよ📌([Microsoft Learn][2])

---

## 3. なんで“Outbound Port”として切るの？🧭🔥

ヘキサゴナルの気持ちよさはここ😍

* 中心は **「保存が必要」** だけ知ってればいい
* **「どこに」「どうやって」保存するか** は外側が吸収する

つまり中心はこう言うだけ：

> 「Todoを保存して」🔌
> 「idでTodoちょうだい」🔌

この **“お願いの形”が Port（interface）** だよ〜😊✨
中心が **自分に都合のいい形でPortを定義できる** のが強い💪
（Hexagonal の説明でも “coreは自分が定義したportだけに依存する” みたいに語られるよ）([Architectural Metapatterns][3])

---

## 4. Repository Port の決め方（手順）🪜✨

Repository って、最初にDBを見て決めるとだいたい失敗する😵‍💫💥
うまくいく順番はこれ👇

### 手順A：ユースケースから必要な操作だけ拾う 🧠➡️🔌

今回のToDoユースケース（例）：

* AddTodo ✅
* CompleteTodo ✅
* ListTodos ✅

ここから “保存に必要なこと” を抜き出すよ📝✨

* AddTodo：保存したい → `save(todo)`
* CompleteTodo：idで探す → `findById(id)`、更新して保存 → `save(todo)`
* ListTodos：一覧ほしい → `list()`

**はい、もうこれでほぼ完成😆🎉**
Portは「ユースケースが必要な分だけ」でOK！

---

## 5. よくある事故（先に潰す）🚨😇

### ❌ 事故①：なんでもRepository 🧹💥

「RepositoryってCRUD全部あるよね？」でこうなる👇

* `create/update/delete/find/search/rawQuery/executeSql...` 😵‍💫
* さらに「便利メソッド」増殖で地獄🐘

**症状：**

* どのユースケースもRepositoryに依存しまくり
* 仕様変更のたびにRepositoryが太る🍔
* テストもつらい😇

### ✅ 対策：Repositoryは“最小の約束”✂️🔌

* **今のユースケースに必要な分だけ**
* “将来使うかも”は一旦いらない🙅‍♀️✨

---

## 6. Repository Port の形（TSでのおすすめ）🧩✨

### ポイント1：Repositoryは“ドメイン型”を扱ってOK 🧠💞

Repositoryは **中心側の契約** だから、返すのが `Todo` でも全然OK😊
（DBの行とかORMモデルは外側の話！）

### ポイント2：非同期（Promise）に寄せるのがおすすめ ⏳✨

InMemoryでも `Promise` にしておくと、後でDB/ファイルに差し替えてもユースケースが無傷😍
（I/Oは将来ほぼ非同期になるからね）

---

## 7. 実装してみよう：TodoRepositoryPort 💾🔌

フォルダ例：`src/app/ports/TodoRepositoryPort.ts` みたいな感じ📁✨
（置き場所はプロジェクト流儀でOKだよ😊）

```ts
// src/app/ports/TodoRepositoryPort.ts
import { Todo } from "../../domain/todo/Todo";
import { TodoId } from "../../domain/todo/TodoId";

export interface TodoRepositoryPort {
  /** Todoを保存する（新規でも更新でもOKにするのが簡単✨） */
  save(todo: Todo): Promise<void>;

  /** idで1件取得（なければnull） */
  findById(id: TodoId): Promise<Todo | null>;

  /** 一覧取得（まずはシンプルに全件でOK😊） */
  list(): Promise<Todo[]>;
}
```

> `findById` の “見つからない” を `null` にするのは、最初は分かりやすいからおすすめ😊
> （エラー設計をしっかりやるのは後の章で育てよう🌱✨）

---

## 8. ユースケース側はこうなる（中心がスッキリ😍）🧠✨

例：CompleteTodo の雰囲気👇

```ts
// src/app/usecases/CompleteTodo.ts
import { TodoId } from "../../domain/todo/TodoId";
import { TodoRepositoryPort } from "../ports/TodoRepositoryPort";

export class CompleteTodo {
  constructor(private readonly repo: TodoRepositoryPort) {}

  async execute(input: { id: string }): Promise<void> {
    const id = TodoId.fromString(input.id);

    const todo = await this.repo.findById(id);
    if (!todo) {
      // ここは後の章で「仕様エラー」にしていくと超キレイ✨
      throw new Error("Todo not found");
    }

    todo.complete();           // ← ドメインのルール（例：二重完了禁止）✨
    await this.repo.save(todo);
  }
}
```

見て見て！👀✨
ユースケースは **DBもファイルも一切知らない** 🙅‍♀️💕
「依存の向き」守れてる感が気持ちいい〜〜〜😆🛡️

---

## 9. “良いRepository Port”チェックリスト ✅🔎✨

Repositoryを決めたら、これでセルフチェックしてね😊

* ✅ メソッド名が **ユースケースの言葉** になってる？（技術用語まみれじゃない？）🗣️
* ✅ **最小限**？（今のユースケースが使ってない操作が混ざってない？）✂️
* ✅ 引数/戻り値に **DB都合の型** が混ざってない？（Row/ORM/SQLなど）🚫
* ✅ “便利そう”で `query(sql: string)` とか生やしてない？（だいたい破滅😇）🧨
* ✅ 例外や失敗の表現が **一貫** してる？（null / throw / Resultが混在してない？）🧯

---

## 10. AI（Copilot/Codex）に頼むなら、ここだけ頼ろう🤖✨

AIに手伝ってもらうのはめっちゃOK！😍
でも **Port設計の芯** は人間が握ろう🛡️✨（ここ崩れると全部崩れる😇）

### ✅ 使ってOK：候補出し・命名

* 「このユースケースに必要なRepositoryメソッド候補を3案出して」
* 「命名をユビキタス言語寄りに直して」

### ⚠️ 注意：AIがやりがち事故

* いきなり `GenericRepository<T>` を提案してくる（だいたい要らない😂）
* CRUD全部盛りを提案してくる（太る🍔）

#### コピペ用プロンプト（おすすめ）📝🤖

```text
次のユースケースに必要な「最小のRepository interface」を提案して。
- AddTodo: 追加
- CompleteTodo: 完了（id指定）
- ListTodos: 一覧
注意：
- CRUD全部は不要
- DB都合の型（Row/ORM/SQL）を出さない
- メソッド数は最小（3〜4個まで）
```

---

## 11. ミニ課題（手を動かすやつ🖐️🎀）

### 課題A：Repository Port を “今の仕様だけ” で完成させる 💾✨

* `save / findById / list` の3つだけで一旦完成にする😊

### 課題B：Listに “完了/未完了フィルタ” を追加してみる 🔍✅

やるならこういう方向がオススメ👇（増やしすぎ注意！）

```ts
list(filter?: { completed?: boolean }): Promise<Todo[]>;
```

「ユースケースが必要になったら足す」🌱 これで勝ち✌️✨

---

## 12. おまけ：2026/01/23 時点の“周辺メモ”🗓️✨

* Node.js は **v24 系が Active LTS**、v25 系が Current という位置づけだよ📌([Node.js][4])
* 2026年1月中旬に **24.13.0 (LTS) のセキュリティリリース** も出てるよ🔐([Node.js][5])
* TypeScript は 2025年末の公式ブログで **6.0が“JS実装として最後の系統”**、7系へ進む話が出てるよ🧠✨([Microsoft for Developers][6])

（この章の本題はRepository設計だから、ここは軽くでOKだよ😊🌸）

---

## まとめ 🎁💖

Repository（Outbound Port）はこう覚えよう😊🔌

* **Repositoryは中心の“お願い窓口”** 💾🔌
* **ユースケースから逆算して最小にする** ✂️✨
* **DB都合を中心に入れない** 🙅‍♀️🛡️
* **太ったら負け** 🍔⚠️

次の章では、Repository以外の小さな外部依存（Clock/UUIDなど）も同じノリで切って、テストが急にラクになる魔法をかけるよ〜〜🪄🧪✨

[1]: https://martinfowler.com/eaaCatalog/repository.html?utm_source=chatgpt.com "Repository"
[2]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design?utm_source=chatgpt.com "Designing the infrastructure persistence layer - .NET"
[3]: https://metapatterns.io/implementation-metapatterns/hexagonal-architecture/?utm_source=chatgpt.com "Hexagonal Architecture | Architectural Metapatterns"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[5]: https://nodejs.org/en/blog/release/v24.13.0?utm_source=chatgpt.com "Node.js 24.13.0 (LTS)"
[6]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
