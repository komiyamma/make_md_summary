# 第8章 依存の向き（これだけは最重要）🧭🔥

〜「中心は外側を知らない🙅‍♀️／外側は中心を知っていい👌」の話だよ〜

---

## 1) 今日のゴール🎯✨

この章が終わったら、次の3つができるようになるよ😊💖

* 「依存の向き」って何かを、自分の言葉で説明できる🗣️✨
* コードを見て「それ、中心が外側知っちゃってない？😱」を発見できる👀🔍
* “差し替え” と “テスト” がラクになる理由を体感できる🔁🧪🎉

---

## 2) まず「依存」ってなに？🤔💭

ここでいう依存は、超ざっくり言うと…

* **`import` してる**（＝その型や関数を知らないと書けない）📦
* **具体クラスを `new` してる**（＝実装にベタ貼り）🧱
* **フレームワーク型を直接受け取ってる**（Expressの`Request`とか）🌐

この「知ってなきゃ書けない」状態が増えるほど、変更が怖くなるよ〜😵‍💫💥

---

## 3) 依存の向き：いちばん大事なルール📌🔥

### ✅ ルールはこれだけ（まず暗記でOK）🧠✨

* **中心（ドメイン/ユースケース）は外側（DB/HTTP/FS）を知らない🙅‍♀️**
* **外側（DB/HTTP/FS）は中心を知っていい👌**

イメージはこんな感じ👇（矢印＝`import`の向き）

```text
[ adapters (HTTP/DB/FS) ]  --->  [ app (usecases/ports) ]  --->  [ domain ]
          外側                         中心寄り                   ど真ん中
```

これが守れると、中心がずっとキレイで強いままになる🛡️✨

---

## 4) つまずきポイント⚠️：「実行の流れ」と「依存の向き」が逆っぽく見える😵

ここ、初心者さんが混乱しがち〜！😣💦

* **依存（import）の向き**：外 → 中 ✅
* **実行（処理）の流れ**：中 → 外 が起きることもある ✅

たとえばユースケースが「保存してね」って言うとき、実際の保存は外側（DB/FS）がやるよね💾
でも中心は「DB保存のやり方」を知らなくていいの😊

👉 ここで出るのが **Port🔌（約束）** だよ！

---

## 5) 「依存が逆転」すると何がうれしいの？🎁✨

### うれしいことランキング🏆💕

* **差し替えが一瞬**：DBを変える／APIを変えるが怖くない🔁
* **テストが爆速**：外部なしでユースケースだけテストできる🧪⚡
* **変更が局所化**：HTTPの仕様変更しても中心は無傷✅

この “中心が無傷” が、ヘキサゴナルの気持ちよさだよ〜😊💖

---

## 6) ダメな例😱：中心が外側を知っちゃう

たとえばユースケースの中で、DBクライアントを直に触ると…終わる😵‍💫💥

```ts
// app/usecases/AddTodo.ts （←ここは中心寄りなのに…）
import { PrismaClient } from "@prisma/client"; // 😱 外側の都合を知ってる

const prisma = new PrismaClient();

export async function addTodo(title: string) {
  return prisma.todo.create({ data: { title, completed: false } });
}
```

これだと…

* DB変更でユースケース死亡💀
* テストでDBが必要になってツラい😵
* “中心”のはずが「外側の詳細置き場」になる📦

---

## 7) 良い例😊：中心はPort（約束）だけ知る🔌✨

### 7-1) 中心が決める「約束（Port）」

```ts
// app/ports/TodoRepositoryPort.ts
export type TodoDTO = { id: string; title: string; completed: boolean };

export interface TodoRepositoryPort {
  add(title: string): Promise<TodoDTO>;
  list(): Promise<TodoDTO[]>;
}
```

### 7-2) ユースケースはPortにだけ依存する🛡️

```ts
// app/usecases/AddTodo.ts
import type { TodoRepositoryPort, TodoDTO } from "../ports/TodoRepositoryPort";

export class AddTodo {
  constructor(private readonly repo: TodoRepositoryPort) {}

  async execute(title: string): Promise<TodoDTO> {
    const trimmed = title.trim();
    if (trimmed.length === 0) throw new Error("タイトル空はダメだよ🚫");

    return this.repo.add(trimmed);
  }
}
```

💡ポイント💖

* ユースケースは **DBもHTTPも知らない🙅‍♀️**
* でも「保存して」ってお願いはできる（Portがあるから）🔌✨

---

## 8) 外側（Adapter）がPortを実装する🧩✨

```ts
// adapters/repository/InMemoryTodoRepositoryAdapter.ts
import type { TodoRepositoryPort, TodoDTO } from "../../app/ports/TodoRepositoryPort";

export class InMemoryTodoRepositoryAdapter implements TodoRepositoryPort {
  private items: TodoDTO[] = [];
  private seq = 1;

  async add(title: string): Promise<TodoDTO> {
    const todo: TodoDTO = { id: String(this.seq++), title, completed: false };
    this.items.push(todo);
    return todo;
  }

  async list(): Promise<TodoDTO[]> {
    return [...this.items];
  }
}
```

これで **テスト用にInMemory** がすぐ使える〜🧪✨

---

## 9) 依存の組み立て（Composition Root）で合体🧩🏗️

「どのAdapterを使うか」は **外側の仕事** だよ😊

```ts
// compositionRoot.ts
import { AddTodo } from "./app/usecases/AddTodo";
import { InMemoryTodoRepositoryAdapter } from "./adapters/repository/InMemoryTodoRepositoryAdapter";

const repo = new InMemoryTodoRepositoryAdapter();
export const addTodo = new AddTodo(repo);
```

中心はずっとピュア🧠✨
外側でだけ差し替える🔁💖

---

## 10) テストがラクになる瞬間🧪🎉

外部ゼロでユースケースだけテストできる！これは強い💪✨

```ts
import { test, expect } from "vitest";
import { AddTodo } from "../app/usecases/AddTodo";
import { InMemoryTodoRepositoryAdapter } from "../adapters/repository/InMemoryTodoRepositoryAdapter";

test("タイトル空はエラー🚫", async () => {
  const uc = new AddTodo(new InMemoryTodoRepositoryAdapter());
  await expect(() => uc.execute("   ")).rejects.toThrow();
});
```

---

## 11) “守り”のテク（事故を自動で止める）🧷✨

人間はうっかりするので、ルールで縛るのが最強😎🔒

### ✅ ESLintで「このフォルダからはここにimport禁止」を作れる

`import/no-restricted-paths` でディレクトリ単位の依存禁止ができるよ🧯✨ ([Zenn][1])

さらに「境界ルール」を専門に守るプラグインもあるよ（import-boundaries系）🧱✨ ([libraries.io][2])

（この章では“存在だけ”覚えておけばOK😊 次の章以降で育てよう🌱）

---

## 12) AI（Copilot/Codex）に頼むときのコツ🤖💖

AIって便利だけど、**依存の向きだけは平気で壊しがち**😇💥
なので、こう聞くのがオススメ👇

* 「この変更で、`app/` や `domain/` が `adapters/` を import してない？チェックして✅」
* 「ユースケースがHTTP/DBの型を参照してたら、Portに逃がして提案して🔌」
* 「Adapterが太ってない？（変換と呼び出し以外してない？）🥗」

---

## 13) 最新事情ちょいメモ🗞️✨（2026/01/23時点）

* TypeScript は **5.9 系が最新安定**（npmのlatestも5.9.3）だよ📌 ([NPM][3])
* Node.js は **24系がActive LTS**、25系はCurrent（奇数系はLTSにならない）という運用だよ🟢 ([Node.js][4])

（この章の結論はバージョンが変わっても不変だよ🛡️✨）

---

## 14) まとめ🎁💖（合言葉）

* **中心は外側を知らない🙅‍♀️**
* **外側は中心を知っていい👌**
* **中心が知るのはPort（約束）だけ🔌✨**

---

## 15) ミニ課題📝🎀

1. ユースケース内に `fs` や HTTP クライアントや DB クライアントの `import` があったら、Portに逃がしてみよ🔌✨
2. Repositoryを **InMemory → ファイル保存** に差し替える想像をして、「中心は1行も変えなくてOK？」を確認しよ🔁😊
3. AIに「依存の向きチェックして！」って頼んで、指摘が出るか試してみよ🤖✅

---

次の章では、この依存ルールを「フォルダ構成」とセットで“迷子にならない形”に固めていくよ〜📁🧭✨

[1]: https://zenn.dev/dev_commune/articles/853b3b45aa42c8?utm_source=chatgpt.com "ディレクトリ単位でTypeScriptの自動補完を制御する"
[2]: https://libraries.io/npm/eslint-plugin-import-boundaries?utm_source=chatgpt.com "eslint-plugin-import-boundaries 0.5.0 on npm"
[3]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "typescript"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
