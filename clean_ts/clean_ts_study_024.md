# 第24章：Portって何？（内側が欲しい“能力”）🎯🔌✨

この章でやることはシンプルだよ😊
**「UseCase（内側）が外側にお願いしたいこと」を、`Port`（＝インターフェース）として言語化**できるようになること！💪💕

---

## 1) Portはなに？ひとことで言うと…🧠✨

**Port = 内側（UseCase）が「外側にこうしてほしい！」ってお願いするときの“窓口”**だよ🪟🔌

* 内側は「保存して」「取り出して」「通知して」みたいに**能力（やってほしいこと）**を言う
* 外側はその能力を満たす**実装（Adapter）**を差し込む

この「Port（窓口）」の考え方は、Ports & Adapters（ヘキサゴナル）でも中心アイデアで、**Portは“目的のある会話（purposeful conversation）”を表す**って説明されるよ📞✨ ([Alistair Cockburn][1])

---

## 2) Portがないと、何がつらいの？😵‍💫🧨

たとえば、UseCaseの中でいきなりDBライブラリを触り始めたら…👇

* UseCaseがDB都合（SQL/テーブル/接続/例外）に引っ張られる🗄️💥
* テストのたびにDBが必要になって、遅い＆面倒😇🧪
* DBをSQLite→別のDBに変えたいだけなのに、UseCaseまで修正地獄😱

クリーンアーキはこういう**関心の分離**を狙う設計で、中心（ビジネスルール）を外側の詳細から守るのが主目的だよ🛡️✨ ([Clean Coder Blog][2])
（ヘキサゴナルでも「UIやデータストアに依存せずテストできる」などが強調されるよ🧪🎉） ([AWS ドキュメント][3])

---

## 3) PortとAdapterの関係を、ミニ図でつかむ🧩🔁

* **Port**：内側が欲しい能力（インターフェース）
* **Adapter**：外側の具体実装（SQLite版、InMemory版…）

イメージはこれ👇

* UseCase（内側） → **Port（お願い口）** → Adapter（外側の実装）
* 内側は「どうやるか」を知らない、ただ「これして」と言うだけ😊

---

## 4) このミニTaskアプリで、Portは何になる？🗒️🔌✨

題材のユースケースは **Create / Complete / List** だったよね？😊
この3つをやるとき、UseCaseが外側にお願いしたいことを抜き出すと…👇

### CreateTaskが外側にお願いしそうなこと📝

* 新しいTaskを保存してほしい💾
* 新しいIDを発行してほしい（ID生成）🆔✨
* （必要なら）今の時刻を教えてほしい⏰

### CompleteTaskが外側にお願いしそうなこと✅

* 対象TaskをIDで取ってきてほしい🔎
* 更新後のTaskを保存してほしい💾

### ListTasksが外側にお願いしそうなこと👀

* Task一覧を取ってきてほしい📚

つまり現時点のPort候補は、だいたいこんな感じになるよ👇

* `TaskRepository`（保存・取得・一覧）🗄️
* `IdGenerator`（ID発行）🆔
* `Clock`（時刻）⏰

> 注意⚠️：この章は「Portって何？」がテーマだから、**APIを完璧に確定するのは次章（第25章）でOK**だよ😉✨

---

## 5) Port設計のコツ：外側都合じゃなく「内側都合」💘

Portで超大事なのはこれ👇

### ✅ Portは「技術名」じゃなく「能力名」

* ❌ `SqliteTaskRepository`（技術名が入ってる）
* ✅ `TaskRepository` / `TaskStore`（能力の名前）

技術が変わっても、内側が欲しいのは「保存」「取得」みたいな能力だよね😊✨

### ✅ Portは「どうやるか」を語らない

Portは “依頼書” だから、こういうのは書かない🙅‍♀️

* SQL文
* HTTPのヘッダ
* DB接続
* ライブラリ固有の型

内側は外側の詳細を知らないのが正義🛡️💕

---

## 6) TypeScriptでのPortの書き方（最小例）✍️🧩

ここでは「Port＝interface」って形で書くのが一番わかりやすいよ😊

たとえば `TaskRepository` Port（超ミニ版）👇

```ts
// src/usecases/ports/TaskRepository.ts
import { Task } from "../../entities/task/Task";

export interface TaskRepository {
  save(task: Task): Promise<void>;
  findById(id: string): Promise<Task | null>;
  list(): Promise<Task[]>;
}
```

ポイント🌟

* **PortはUseCase側の言葉**で書く（`Task` を中心に）💗
* `Promise` にしておくと、DBでもメモリでも同じ顔で扱えるよ😊（I/Oっぽさを吸収）

次に、UseCase側は **具体実装を知らずに** こうやって使うだけ👇

```ts
// src/usecases/createTask/CreateTaskInteractor.ts
import { TaskRepository } from "../ports/TaskRepository";
import { IdGenerator } from "../ports/IdGenerator";
import { Task } from "../../entities/task/Task";

export class CreateTaskInteractor {
  constructor(
    private readonly repo: TaskRepository,
    private readonly idGen: IdGenerator,
  ) {}

  async execute(title: string): Promise<{ id: string }> {
    const id = this.idGen.newId();
    const task = Task.create({ id, title });

    await this.repo.save(task);

    return { id };
  }
}
```

ここが気持ちいいところ😍✨
**UseCaseは “repoがSQLiteか” を1ミリも知らない**。だから差し替えがラクになる🎉🔁

---

## 7) Portを作る手順（迷子にならない3ステップ）🧭✨

### ステップ①：UseCaseを「手順」に分解する🧩

例：CompleteTask

1. Taskを取る
2. 完了にする（Entityルール）
3. 保存する

### ステップ②：「外側が必要な行」に印をつける🖊️

* 「Taskを取る」「保存する」→ 外側っぽい✅
* 「完了にする」→ 内側（Entityの仕事）✅

### ステップ③：印がついた行を“能力”にまとめてPortにする🔌

* 取る＋保存 → `TaskRepository`
* ID発行 → `IdGenerator`
* 時刻 → `Clock`

この流れ、めっちゃ大事だよ〜😊✨

---

## 8) よくある失敗あるある（先に潰そっ）💣😇

### ❌ 失敗1：Portがデカすぎる（巨大Repository）🐘

最初から「なんでもできるRepository」にしがち…
→ 次章（第25章）で **最小メソッド主義** をやるから、ここでは「膨らませない意識」を持っておけばOK😉✨

### ❌ 失敗2：Port名が技術寄り⚙️

* `DatabaseService` とか `SqlClient` とか…
  → それ、内側の言葉じゃない😭
  内側は「Taskを保存したい」なの！

### ❌ 失敗3：Portが外側の型を返す📦💥

* DBのRow型とか、HTTPレスポンス型とか
  → 内側が外側に汚染されちゃう😵‍💫

---

## 9) ちょい最新メモ（2026のいま）🆕✨

* **TypeScriptは 5.9 のリリースノートが更新されてる**よ（2026年1月更新）🧠✨ ([TypeScript][4])
* **Node.jsは v24 がLTS（Active LTS）で更新されている**（2026-01-13のリリースもあるよ）🟢 ([Node.js][5])

このへんはビルド設定やモジュール周りに影響しやすいけど、**Port自体の考え方は不変**だよ😊🔌

---

## 10) 理解チェック（1問）✅📝✨

Q：次のうち「Portとして適切な名前」はどれ？（理由も言えたら満点💯）
A. `SqliteTaskRepository`
B. `TaskRepository`

👉 正解：**B** 🎉
理由：Portは「能力」を表すから、技術名（Sqlite）を入れない😊✨

---

## 11) 今章の提出物（成果物）📦🎁

* ✅ 「Create / Complete / List」から抽出した **Port候補のリスト**（3〜5個）
* ✅ 各Portに **1行説明**（“内側が欲しい能力”として）
* ✅ `TaskRepository` の `interface`（最小でOK）

---

## 12) AI相棒🤖✨（コピペで使えるプロンプト）

### Port候補出し🔌

「````
CreateTask / CompleteTask / ListTasks の手順を箇条書きにして、外側に依頼すべき“能力”だけを抽出してPort名候補を10個出して。技術名（DB名/HTTP名）は禁止。

`````」

### Portがデカすぎる診断🐘➡️🫧
「````  
このPort interfaceのメソッド一覧を見て、責務が大きすぎるところを指摘して。分割案も2パターン提案して（例：Reader/Writer分割など）。  
````」

### 命名チェック🧼
「````  
このPort名は内側（業務）寄り？外側（技術）寄り？理由を添えて、より良い名前案を5つ出して。  
````」

---

次の第25章では、この章で出した `TaskRepository` を **“最小メソッド主義”でキレイに確定**していくよ🗄️✨  
「巨大Repository化」しないコツ、そこで一気に掴もうね😊💪💕
::contentReference[oaicite:5]{index=5}
`````

[1]: https://alistair.cockburn.us/hexagonal-architecture?utm_source=chatgpt.com "hexagonal-architecture - Alistair Cockburn"
[2]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "Clean Architecture by Uncle Bob - The Clean Code Blog"
[3]: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html?utm_source=chatgpt.com "Hexagonal architecture pattern - AWS Prescriptive Guidance"
[4]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[5]: https://nodejs.org/en/blog/release/v24.13.0?utm_source=chatgpt.com "Node.js 24.13.0 (LTS)"
