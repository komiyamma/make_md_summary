# 39. アンチパターン①：中心がHTTP/DB型を知っちゃう 😱


# 第39章：アンチパターン①「中心がHTTP/DB型を知っちゃう」😱🔌🏰

この章はね、**ヘキサゴナルでいちばん“やらかしやすい地雷”**を踏まない練習だよ〜！💣😵‍💫
結論から言うと…

**中心（domain/app）は、HTTPやDBの型を知らないのが正解**🛡️✨
（＝中心は“ルール”、外側は“I/O”！）

---

## 2026/1時点の周辺メモ📌✨（最新リサーチ）

* TypeScriptの安定版は **5.9.3 が Latest**（GitHub releasesでLatest表示）だよ🧡 ([GitHub][1])
* 公式ブログで **TypeScript 6.0 は「5.9→7.0への橋渡し」**って説明されてるよ🌉 ([Microsoft for Developers][2])
* Node.jsは **v24がActive LTS**、**v25がCurrent**（2026-01-12/19更新）だよ🟢 ([Node.js][3])
* TS 5.9 のリリースノートに、Node向けに安定設定 **`--module node20`** が出てるよ（`nodenext`みたいに挙動が変わり続けない想定）🧩 ([typescriptlang.org][4])
* ESLintは v9 から **Flat Config がデフォルト**になってるよ🧹✨ ([eslint.org][5])
* バリデーションは境界（Adapter）でやるのが相性良くて、Zodは **v4がstable**、最近だと **v4.3.0** のリリースもあるよ✅ ([Zod][6])

---

## 1) 今日のゴール🎯💖

* 「中心がHTTP/DB型を知ってる」状態を見抜ける👀✨
* **DTOと変換をAdapterに押し出して**、中心を“静かに”できる🛡️
* “直し方テンプレ”で、迷わずリファクタできる🔧🎀

---

## 2) このアンチパターン、何がダメなの？😵‍💫💥

### 起きがちな症状あるある😇

* domain/app の中に **`Request` / `Response`** が出てくる🌐😱
* domain/app の中に **ORMの型（例：Prismaの`Todo`型）** が出てくる💾😱
* “中心の関数”の引数が、HTTPっぽい（`req.body`前提）📮😱
* テストしようとしたら、ExpressやDBを立てる羽目になる🧪💥

### それ、何が困るの？

* **入口差し替えできない**（CLI→HTTPにしたいだけなのに中心が壊れる）🔁😵
* **DB差し替えできない**（InMemory→SQLite→Postgres…のたびに中心が汚れる）💾➡️💾😵
* **テストが重くなる**（中心のテストなのにI/Oが混ざる）🧪🐢

---

## 3) ダメ例①：中心がHTTP型を知っちゃう😱🌐

たとえばこんなの👇（**置き場所が中心側**だとアウト！）

```ts
// ❌ src/app/addTodo.ts（中心側に置いちゃダメ！）
import type { Request, Response } from "express";

export async function addTodo(req: Request, res: Response) {
  const title = req.body.title; // HTTP前提が中心に入ってる😱
  // ... ドメイン処理や保存 ...
  res.json({ ok: true });
}
```

これだと、CLIから呼びたい時も「Request/Responseどうすんの？」ってなるよね🥺💦
中心が “HTTPの都合” に縛られちゃう。

---

## 4) ダメ例②：中心がDB/ORM型を知っちゃう😱💾

```ts
// ❌ src/domain/Todo.ts（中心側に置いちゃダメ！）
import type { Todo as PrismaTodo } from "@prisma/client";

export function isDone(todo: PrismaTodo) {
  return todo.completed;
}
```

この瞬間、中心は **Prismaという外界**に依存するよね😱
DBを変えたら、中心も巻き添えで大工事…🏗️💥

---

## 5) 正しい形：中心は「DTO」と「自分の型」だけ🛡️✨

### まず “中心が知っていいもの” を固定しよ📌

* ✅ domain：`Todo`（自分のルールの型）
* ✅ app：`AddTodoInput` / `AddTodoOutput`（DTO）
* ✅ port：`TodoRepositoryPort`（約束）
* ❌ HTTPの`Request/Response`
* ❌ ORMのモデル型

---

## 6) 直し方の完成形（ざっくり全体図）🏰🔌🧩

* **HTTP Adapter**：`Request` を読んでDTOに変換📮🔁
* **UseCase（中心）**：DTOだけで仕事する🧠✨
* **DB Adapter**：中心の`Todo` ↔ DBの行（Record）を変換💾🔁

---

## 7) 実装例：DTOを中心に置く📮✨

```ts
// ✅ src/app/dto/AddTodoDto.ts（中心OK）
export type AddTodoInput = {
  title: string;
};

export type AddTodoOutput = {
  id: string;
  title: string;
  completed: boolean;
};
```

---

## 8) 実装例：Port（約束）を中心に置く🔌✨

```ts
// ✅ src/app/ports/TodoRepositoryPort.ts（中心OK）
import type { Todo } from "../../domain/Todo";

export interface TodoRepositoryPort {
  save(todo: Todo): Promise<void>;
  findAll(): Promise<Todo[]>;
}
```

---

## 9) 実装例：UseCaseはHTTPもDBも知らない🙅‍♀️✨

```ts
// ✅ src/app/usecases/AddTodoUseCase.ts（中心OK）
import type { TodoRepositoryPort } from "../ports/TodoRepositoryPort";
import type { AddTodoInput, AddTodoOutput } from "../dto/AddTodoDto";
import { Todo } from "../../domain/Todo";

export class AddTodoUseCase {
  constructor(private readonly repo: TodoRepositoryPort) {}

  async execute(input: AddTodoInput): Promise<AddTodoOutput> {
    const todo = Todo.create(input.title); // ルールはドメインへ🧠
    await this.repo.save(todo);

    return { id: todo.id, title: todo.title, completed: todo.completed };
  }
}
```

---

## 10) 実装例：HTTP Adapterで Request → DTO 変換する🌐🧩

ここが **翻訳係** だよ〜！📮🔁
（バリデーションもここでやるとキレイ✨ Zod v4は安定版だよ✅ ([Zod][6])）

```ts
// ✅ src/adapters/http/addTodoRoute.ts（外側OK）
import type { Request, Response } from "express";
import { z } from "zod";
import type { AddTodoUseCase } from "../../app/usecases/AddTodoUseCase";

const BodySchema = z.object({
  title: z.string().trim().min(1),
});

export function addTodoRoute(useCase: AddTodoUseCase) {
  return async (req: Request, res: Response) => {
    const parsed = BodySchema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ message: "title is required" });
    }

    const output = await useCase.execute({ title: parsed.data.title }); // DTOだけ渡す🧡
    return res.status(201).json(output);
  };
}
```

ポイントはこれ👇

* HTTPの型は **Adapterに閉じ込める**🔒
* 中心へ渡すのは **DTOだけ**📮✨

---

## 11) 実装例：DB Adapterで “中心のTodo ↔ DB行” を変換する💾🧩

ORMを使ってもOK！ただし **ORM型はAdapter内で完結**ね🙆‍♀️✨

```ts
// ✅ src/adapters/db/TodoRecord.ts（外側の型）
export type TodoRecord = {
  id: string;
  title: string;
  completed: 0 | 1; // DB都合の表現でもOK
};
```

```ts
// ✅ src/adapters/db/TodoMapper.ts（変換だけ担当）
import type { Todo } from "../../domain/Todo";
import type { TodoRecord } from "./TodoRecord";

export function toRecord(todo: Todo): TodoRecord {
  return { id: todo.id, title: todo.title, completed: todo.completed ? 1 : 0 };
}

export function toDomain(record: TodoRecord): Todo {
  // ドメイン生成に寄せる（不変条件を守る）🧠✨
  return { id: record.id, title: record.title, completed: record.completed === 1 };
}
```

---

## 12) “二度と混ぜない”ためのガード🧱✨（超おすすめ）

### ✅ ルール：中心から `adapters/` を import できないようにする

ESLint v9 は Flat Config がデフォルトだから、`eslint.config.*` で書くのが今風だよ🧹 ([eslint.org][5])

例（イメージ）👇

```js
// eslint.config.mjs（例）
export default [
  {
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            "@/adapters/*",
            "../adapters/*",
          ],
        },
      ],
    },
  },
];
```

※ 細かい設定はプロジェクト構成で変わるけど、考え方はこれだけでOK👌✨

---

## 13) “直し方テンプレ”🔧📌（迷ったらこの順で！）

1. **中心に混入してる外側型を探す**（Request/Response、ORM、SDK型）👀
2. **DTOを作る**（入力・出力の形を固定）📮
3. **Portを切る**（中心が欲しい最小の約束）🔌
4. **Adapterへ押し出す**（変換と呼び出しだけ残す）🧩
5. **中心のテストを書く**（I/Oなしで動くのが正義）🧪✨

---

## 14) Copilot/Codexに投げると強い質問テンプレ🤖📝✨

そのままコピペでOK〜！

* 「`src/domain` と `src/app` が `express` や `@prisma/client` を import していないか確認して。見つけたら、DTO/Adapterに押し出す案を出して」
* 「このファイルはAdapterが太ってない？“変換/呼び出し”以外（業務ルール）が入ってたら指摘して」
* 「UseCaseがHTTPステータスやレスポンス形を決めてない？決めてたら修正案出して」

---

## まとめ🎁💖

* **中心は外側（HTTP/DB）の型を知らない**🛡️
* **DTOとPortで“中心の言葉”を固定**📮🔌
* **変換はAdapterに閉じ込める**🧩🔒

---

## ミニ課題📝🎀

1. いまのプロジェクトで `Request` / `Response` / ORM型が **domain/appに混ざってないか検索**してみてね🔍
2. 1個だけ見つけたら、今日のテンプレ順で **DTO化→Adapterへ移動**してみよ🔧✨
3. 最後に「中心のテストがI/Oなしで通る」状態にできたら勝ち🏆🧪

必要なら、こみやんまの今のフォルダ構成に合わせて「検索ワード」と「移動先のディレクトリ案」まで具体化して一緒に直せるよ〜😊🔌🏰

[1]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
[2]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/ "Progress on TypeScript 7 - December 2025 - TypeScript"
[3]: https://nodejs.org/en/about/previous-releases "Node.js — Node.js Releases"
[4]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html "TypeScript: Documentation - TypeScript 5.9"
[5]: https://eslint.org/blog/2025/03/flat-config-extends-define-config-global-ignores/ "Evolving flat config with extends - ESLint - Pluggable JavaScript Linter"
[6]: https://zod.dev/v4 "Release notes | Zod"