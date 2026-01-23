# 第19章：ユースケース入門①：アプリの中心って何？ 🎮➡️🧠✨

この章は「**アプリの中心（=やりたいことの手順と判断）**」を、ToDoミニで “体験” しちゃう回だよ〜😊📝💕

---

## 1) ユースケースってなに？（いちばんカンタンに）🧁✨

ユースケース（Use Case）は一言でいうと…

* **手順（Step）**：何をどんな順でやる？🧭
* **判断（Decision）**：ダメなときどうする？分岐どうする？🚦

をまとめた「**アプリの中心のシナリオ**」だよ😊💡

たとえば「ToDoを追加する」なら、

1. タイトルが空じゃない？（判断）🚫
2. ToDoを作る（手順）🧩
3. 保存する（手順）💾
4. 追加できた結果を返す（手順）📤

こういう流れが **ユースケース** 🎯✨

---

## 2) ドメイン（ルール）とユースケース（手順）の違い 🧠🆚📝

ざっくりイメージ👇

* **ドメイン（Entity/ValueObject）**：
  「タイトル空は禁止」みたいな **ルールそのもの** 🛡️
* **ユースケース**：
  そのルールを使って、**アプリとしてどう進めるか**（保存・取得・返す…）を決める 🎬

> ドメインは “ルール職人” 👩‍🍳
> ユースケースは “段取りマネージャ” 🧑‍💼✨

---

## 3) この章で作るユースケース3つ ✅✅✅

今回のToDoミニはこの3つでいくよ〜😊🧁

* **AddTodo**：追加する 📝➕
* **CompleteTodo**：完了にする ✅
* **ListTodos**：一覧を返す 📋

---

## 4) まずは（超ミニ）前章までの復習コード 🧩📝

「ドメインはルール持ち」なので、Todo自身が不正を拒否できる形にしておくよ😊
（第17〜18章の内容を、最小だけ再掲✨）

```ts
// src/domain/Todo.ts
export type TodoId = string;

export class Todo {
  private constructor(
    public readonly id: TodoId,
    public readonly title: string,
    public readonly completed: boolean,
  ) {}

  static create(id: TodoId, title: string): Todo {
    if (title.trim().length === 0) {
      throw new Error("title must not be empty");
    }
    return new Todo(id, title, false);
  }

  complete(): Todo {
    if (this.completed) {
      throw new Error("todo is already completed");
    }
    return new Todo(this.id, this.title, true);
  }
}
```

---

## 5) ユースケースは「外の仕組み」を知らない形にする 🧼✨

ユースケースは中心なので、ここでは **保存先（DB/ファイル）** を知らないでいたいよね😊

だから「保存してね」ってお願いする **インターフェース**（後でPortになるやつ）を “仮で” 置くよ🔌✨
（Portの正式な話はこの後の章でやるけど、ユースケースを書くために最低限だけ！）

```ts
// src/app/ports/TodoRepository.ts
import { Todo, TodoId } from "../../domain/Todo";

export interface TodoRepository {
  save(todo: Todo): Promise<void>;
  findById(id: TodoId): Promise<Todo | null>;
  findAll(): Promise<Todo[]>;
}
```

IDも本当は外部依存になりがち（UUIDとか）なので、ここも “お願い口” にしておくと後でラクだよ😊✨

```ts
// src/app/ports/IdGenerator.ts
export interface IdGenerator {
  newId(): string;
}
```

---

## 6) ユースケース① AddTodo（追加する）📝➕

### AddTodo の責務（ここ大事！）📌✨

* 入力を受け取る（タイトル）📥
* Todoを作る（ドメインのルールを使う）🧠
* 保存する（Repositoryにお願い）💾
* 結果を返す（「追加できたよ」）📤

```ts
// src/app/usecases/AddTodo.ts
import { Todo } from "../../domain/Todo";
import { TodoRepository } from "../ports/TodoRepository";
import { IdGenerator } from "../ports/IdGenerator";

export type AddTodoInput = {
  title: string;
};

export type AddTodoOutput = {
  id: string;
  title: string;
  completed: boolean;
};

export class AddTodo {
  constructor(
    private readonly repo: TodoRepository,
    private readonly idGen: IdGenerator,
  ) {}

  async execute(input: AddTodoInput): Promise<AddTodoOutput> {
    // ✅ 入口で軽く整える（空白だけとか）
    const title = input.title.trim();

    // ✅ ルールはドメインに判断してもらう
    const todo = Todo.create(this.idGen.newId(), title);

    // ✅ 保存は外側にお願い
    await this.repo.save(todo);

    // ✅ “外に返す形” はシンプルに（DTOは次章で本格化✨）
    return { id: todo.id, title: todo.title, completed: todo.completed };
  }
}
```

🎀ポイント：
ユースケースの中に **console.log** とか **fetch** とか **fs** が出てきたら、外側が混ざりはじめてるサインだよ😱💦（その辺はAdapter側へ）

---

## 7) ユースケース② CompleteTodo（完了にする）✅

### CompleteTodo の責務 📌✨

* 対象のTodoを取ってくる（id）🔎
* 存在しないならエラー（判断）🚫
* 完了にする（ドメインのルール）✅
* 保存する 💾

```ts
// src/app/usecases/CompleteTodo.ts
import { TodoRepository } from "../ports/TodoRepository";

export type CompleteTodoInput = {
  id: string;
};

export type CompleteTodoOutput = {
  id: string;
  title: string;
  completed: boolean;
};

export class CompleteTodo {
  constructor(private readonly repo: TodoRepository) {}

  async execute(input: CompleteTodoInput): Promise<CompleteTodoOutput> {
    const todo = await this.repo.findById(input.id);

    if (!todo) {
      throw new Error("todo not found");
    }

    // ✅ ルール（2回完了NG）はドメインが持つ
    const completedTodo = todo.complete();

    await this.repo.save(completedTodo);

    return {
      id: completedTodo.id,
      title: completedTodo.title,
      completed: completedTodo.completed,
    };
  }
}
```

---

## 8) ユースケース③ ListTodos（一覧を返す）📋✨

### ListTodos の責務 📌✨

* 全件取ってくる
* “返す形” に整える（外に見せやすく）

```ts
// src/app/usecases/ListTodos.ts
import { TodoRepository } from "../ports/TodoRepository";

export type ListTodosOutputItem = {
  id: string;
  title: string;
  completed: boolean;
};

export class ListTodos {
  constructor(private readonly repo: TodoRepository) {}

  async execute(): Promise<ListTodosOutputItem[]> {
    const todos = await this.repo.findAll();

    // ✅ domain型をそのまま外へ出さず “軽く整える”
    return todos.map((t) => ({
      id: t.id,
      title: t.title,
      completed: t.completed,
    }));
  }
}
```

---

## 9) ユースケースが「太ってきた」チェックリスト 🐘💦

ユースケースが肥大化すると、中心がゴチャつきやすいの🥺
次のどれかが出てきたら要注意🚨

* `req`, `res`（HTTPっぽい）🌐
* `fs`, `path`（ファイルっぽい）📄
* DBのORMモデルが出てくる（SQLっぽい）🧱
* 画面文言を作り始める（UIっぽい）🎨
* 巨大な `if/else` が並ぶ（整理不足のサイン）🧨

→ そうなったら **変換やI/OはAdapterへ** 🧩✨（ヘキサゴナルの気持ちよさポイント！）

---

## 10) AI（Copilot/Codex）に頼るならここが安全 🤖💖

ユースケースは “芯” なので、AIはこう使うのが安全だよ😊

### ✅ 使ってOK（時短！）

* `Input/Output` の型定義のたたき台を作らせる
* `execute()` のテンプレ形（constructorで依存注入）
* 例外ケースの洗い出し案（抜け防止）

### ⚠️ ちょい注意（最後は自分で決める）

* 「どの責務をUseCaseに置くか」
* 「ルールをdomainに置くか」
* 「Repositoryの形（どのメソッド必要？）」

#### そのまま使える質問テンプレ📝✨

* 「このUseCase、外部I/O（HTTP/DB/FS）混ざってない？」
* 「判断（バリデーション/存在チェック）が漏れてない？」
* 「ドメインのルールをUseCaseに書いちゃってない？」

---

## 11) （最新事情ちょいメモ）TypeScriptの“今どき”初期設定の空気感 🧠✨

最近のTypeScriptは、`tsc --init` の生成内容がかなり “現代寄り” に整理されてるよ（例：`module: nodenext`, `target: esnext`, `strict: true` など）🧰✨ ([Microsoft for Developers][1])
教材でもこの流れに合わせていくと、あとで設定で迷いにくい😊💕

（参考：現時点の安定版として TypeScript 5.9.2 が出てるよ）([GitHub][2])
（NodeもLTSが進んでるので、最新版寄りで組んでOKな空気だよ）([Node.js][3])

---

## 12) まとめ 🎁💖

この章でつかんだことはこれ！😊✨

* ユースケース＝**手順＋判断** 🎬🚦
* ドメイン＝**ルール担当** 🛡️
* ユースケース＝**段取り担当** 📝
* 保存やID発行みたいな外部事情は、**お願い口（Port）** にして中心を守る🔌✨

---

## 次（第20章）につながる予告 🌷✨

次はここを “もっとキレイに” するよ😊

* 入力・出力の形（DTO）をちゃんと整える 📮📤
* domain型を外へ漏らさない設計を固める 🛡️✨

必要なら、この章の3ユースケースを「フォルダ配置どこに置く？」まで含めた **完成形ツリー** も作るよ📁💕

[1]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/ "Announcing TypeScript 5.9 - TypeScript"
[2]: https://github.com/microsoft/TypeScript/releases/tag/v5.9.2 "Release TypeScript 5.9 · microsoft/TypeScript · GitHub"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
