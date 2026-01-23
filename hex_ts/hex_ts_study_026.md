## 第26章：Outbound Adapter①：InMemoryRepository 🧠📦✨

ここでは「DBの代わりにメモリ（配列/Map）に保存するRepository」を作って、**“差し替えできる気持ちよさ”**を体で覚えます😊🔁💖
（あとで FileRepository や DB版に差し替える準備にもなるよ！）

---

## 1) 今日のゴール 🎯✨

できるようになること👇

* ✅ **Repository Port（約束）**に対して、**InMemoryのAdapter（実装）**を書ける
* ✅ UseCase側を変えずに、保存先だけ入れ替えられる（差し替え体験）🔁
* ✅ テストで「速い！簡単！」を味わう🧪⚡

---

## 2) InMemoryRepositoryって何がうれしいの？ 🥰

InMemoryは「アプリを落としたら消える」けど、それが逆に強い✨

* 🧪 **テストが爆速**（ファイル/DB待ちがゼロ）
* 🧩 **外部I/Oがない**から、設計の練習に集中できる
* 🔁 後で **File/DB** に差し替える時、中心（UseCase/Domain）を守れるか確認できる

---

## 3) 置き場所（迷子防止）📁🧭

この章ではこんな配置にします（例）👇

* `src/domain/...`（ドメイン：ルール）
* `src/app/...`（ユースケース＋Port）
* `src/adapters/outbound/...`（外側：Repositoryの実装）

---

## 4) Port（約束）を“非同期”にしておく理由 ⏳🔌

InMemoryは同期でできるけど、将来DBやファイルは基本非同期だよね？
だから **Portは最初からPromise** にしておくと、後で差し替えがスムーズ✨（設計の勝ち筋）

Node.jsのLTSは 2026-01 時点で v24 系が Active LTS として更新されています。なので「I/Oは非同期が基本」前提で進めてOKです😊 ([Node.js][1])

---

## 5) 実装していこう：InMemoryTodoRepository 🧠📦

ここからは「最小で気持ちよく」いきます💪✨
ポイントはこれ👇

* 🗺️ `Map` を使う（id → データ）
* 🧼 **Domainオブジェクトをそのまま保存しない**（参照が共有される事故を避ける）

  * なので **snapshot（素のデータ）**にして保存 → 取り出す時に復元✨

---

### 5-1) まず Port（TodoRepository）を用意（src/app/ports）🔌

※ もう作ってあるなら読み飛ばしてOK😊

```ts
// src/app/ports/TodoRepository.ts
import { Todo } from "../../domain/Todo";
import { TodoId } from "../../domain/TodoId";

export interface TodoRepository {
  save(todo: Todo): Promise<void>;
  findById(id: TodoId): Promise<Todo | null>;
  list(): Promise<Todo[]>;
}
```

---

### 5-2) Domain側（最小の例）🧠❤️

※ここも既にあるなら「形だけ」参考にしてね😊

```ts
// src/domain/TodoId.ts
export type TodoId = string;
```

```ts
// src/domain/Todo.ts
import { TodoId } from "./TodoId";

export type TodoSnapshot = {
  id: TodoId;
  title: string;
  completed: boolean;
};

export class Todo {
  private constructor(
    public readonly id: TodoId,
    public readonly title: string,
    public readonly completed: boolean,
  ) {}

  static create(args: { id: TodoId; title: string }): Todo {
    const title = args.title.trim();
    if (!title) throw new Error("Title must not be empty"); // ここは例（本当はDomainErrorにしてもOK）
    return new Todo(args.id, title, false);
  }

  complete(): Todo {
    if (this.completed) throw new Error("Todo already completed");
    return new Todo(this.id, this.title, true);
  }

  toSnapshot(): TodoSnapshot {
    return { id: this.id, title: this.title, completed: this.completed };
  }

  static fromSnapshot(s: TodoSnapshot): Todo {
    return new Todo(s.id, s.title, s.completed);
  }
}
```

---

### 5-3) InMemory Adapter（本命）🧩✨

```ts
// src/adapters/outbound/InMemoryTodoRepository.ts
import { Todo, TodoSnapshot } from "../../domain/Todo";
import { TodoId } from "../../domain/TodoId";
import { TodoRepository } from "../../app/ports/TodoRepository";

export class InMemoryTodoRepository implements TodoRepository {
  private readonly store = new Map<TodoId, TodoSnapshot>();

  async save(todo: Todo): Promise<void> {
    // ✅ Domainオブジェクトそのまま保存しない（参照事故防止）
    this.store.set(todo.id, todo.toSnapshot());
  }

  async findById(id: TodoId): Promise<Todo | null> {
    const snap = this.store.get(id);
    return snap ? Todo.fromSnapshot(structuredCloneSafe(snap)) : null;
  }

  async list(): Promise<Todo[]> {
    return [...this.store.values()].map((s) => Todo.fromSnapshot(structuredCloneSafe(s)));
  }
}

// Node/ブラウザのstructuredCloneが使えるならそれでOK。
// ない場合でも「深いコピーっぽいこと」ができれば十分（この教材では安全側に倒す）
function structuredCloneSafe<T>(v: T): T {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return typeof structuredClone === "function"
    ? structuredClone(v)
    : JSON.parse(JSON.stringify(v));
}
```

> ✅ **Adapterは薄く！**
> ここでは「保存」「取り出し」「変換」だけ。
> **業務ルール（タイトル空禁止とか）をAdapterに書いたら負け**だよ〜😇🥗

---

## 6) 差し替え体験：UseCaseは何も知らない 🙅‍♀️✨

UseCaseは Port（TodoRepository）しか見ないので、InMemoryでもFileでもDBでもOKになります🔁💖
（例：AddTodoUseCase）

```ts
// src/app/usecases/AddTodoUseCase.ts
import { Todo } from "../../domain/Todo";
import { TodoRepository } from "../ports/TodoRepository";

export class AddTodoUseCase {
  constructor(private readonly repo: TodoRepository) {}

  async execute(input: { id: string; title: string }): Promise<void> {
    const todo = Todo.create({ id: input.id, title: input.title });
    await this.repo.save(todo);
  }
}
```

---

## 7) Composition Rootで組み立てる 🧩🏗️

「newする場所は1か所！」の体験をここでちょい入れ✨

```ts
// src/main.ts （例：CLIやHTTPの入口から呼ぶ前に）
import { InMemoryTodoRepository } from "./adapters/outbound/InMemoryTodoRepository";
import { AddTodoUseCase } from "./app/usecases/AddTodoUseCase";

const repo = new InMemoryTodoRepository();
const addTodo = new AddTodoUseCase(repo);

await addTodo.execute({ id: crypto.randomUUID(), title: "牛乳を買う🥛" });
console.log("追加できたよ〜🎉");
```

---

## 8) テストが一気に楽になるよ🧪⚡（Vitest例）

2026年初め時点で Vitest 4 系が提供されていて、移行ガイドも更新されています。なので「今から始める」なら Vitest 4 前提でOK😊 ([Vitest][2])

### 8-1) 最小セット（例）

```sh
npm i -D vitest
```

### 8-2) UseCaseテスト（InMemory差し替え！）

```ts
// src/app/usecases/AddTodoUseCase.test.ts
import { describe, it, expect } from "vitest";
import { InMemoryTodoRepository } from "../../adapters/outbound/InMemoryTodoRepository";
import { AddTodoUseCase } from "./AddTodoUseCase";

describe("AddTodoUseCase", () => {
  it("タイトルが正常なら保存される🎀", async () => {
    const repo = new InMemoryTodoRepository(); // ✅ テストごとにnew（リセット不要）
    const uc = new AddTodoUseCase(repo);

    await uc.execute({ id: "1", title: "レポート書く📚" });

    const all = await repo.list();
    expect(all).toHaveLength(1);
    expect(all[0].title).toBe("レポート書く📚");
    expect(all[0].completed).toBe(false);
  });
});
```

> 💡テストで `repo.reset()` したくなるけど…
> それをPortに入れると「本番Repositoryにもresetが必要」みたいな変な設計になりがち😵
> → **テストは repo を new し直す**のがきれい✨

---

## 9) “Adapterが薄いか”セルフチェック 🥗✅

InMemoryRepoに限らず、Outbound Adapterはこれで判定すると超ラク👇

* ✅ OK：DTO/スナップショット変換、保存、取得、例外ラップ
* ❌ NG：状態遷移（complete判定など）、巨大if、業務ルール、入力バリデーション
* ✅ OK：Map/配列の操作は「I/Oの都合」だからAdapter側
* ❌ NG：「タイトル空禁止」をRepositoryが勝手にやり始める（それ中心の仕事！）🛡️

---

## 10) AI拡張に頼むならこの聞き方が安全だよ🤖✨

コピペで使えるやつ置いとくね🎁

* 🧩 雛形生成プロンプト

  * 「`TodoRepository` を実装する `InMemoryTodoRepository` を TypeScriptで。Mapを使い、Domainオブジェクトを直接保存せず snapshot で保持。Portのメソッドは Promise。業務ルールは書かない」

* 🥗 薄さレビュー用

  * 「このAdapterに業務ルールや巨大ifが混ざってないかチェックして。混ざってたらどこを中心へ移すべきか指摘して」

---

## まとめ 🎁💖

* Outbound Adapter（InMemoryRepo）は **“差し替えできる設計”の練習台**🧠📦
* **Portは非同期**にしておくと、後で File/DB にしても中心が無傷🔁✨ ([Node.js][1])
* Adapterは **薄いほど正義**🥗（変換・呼び出しだけ！）

---

次の第27章は **FileRepository（JSON保存）**📄💾 で、いよいよ「I/O失敗」と仲良くなっていくよ…！😳🔧

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
