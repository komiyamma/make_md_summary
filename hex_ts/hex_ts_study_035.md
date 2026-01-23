# 35. Composition Root：依存の組み立て（合体場所）🧩🏗️


# 第35章：Composition Root（依存の組み立て＝合体場所）🧩🏗️✨

この章はひとことで言うと **「new（生成）を1か所に集めて、差し替え自由にする回」** だよ〜！🎉
ヘキサゴナルで作った「中心（ドメイン＆ユースケース）」を、外側（CLI/HTTP/ファイル保存など）と **安全に合体** させる場所が **Composition Root** 💡

---

## 1) この章のゴール 🎯✨

できるようになること👇

* 「Composition Rootって何？」を自分の言葉で説明できる 🗣️
* **依存の組み立て** を `1ファイル` に集約できる 🧩
* **本番は FileRepo / テストは InMemoryRepo** みたいな切替ができる 🔁✨
* 「中心を汚さない」まま入口（CLI/HTTP）を増やせる 🌐⌨️

---

## 2) Composition Rootってなに？🧩

**アプリの入口（エントリポイント）に近い場所で、オブジェクトの依存関係を全部つなぐ“合体場所”** のことだよ🏗️
DI（依存性注入）の考え方では「ここ以外で volatile な依存（DB/HTTP/FSなど）を new しない」が超重要ポイント！🔥
“Poor Man’s DI（手動DI）でもOK”っていうのが有名な考え方だよ。([InfoQ][1])

> ざっくり：
> **きれいに分けてきた部品たちを、最後にここでだけ “あえて結合する”** 😌🧩

---

## 3) なぜ1か所に集めるの？（うれしさ）🥰✨

### ✅ うれしさ①：修正が怖くなくなる 😌🛡️

File保存をDB保存にしたくなっても、中心はいじらず **合体場所だけ変更** でいける。

### ✅ うれしさ②：テストが爆速になる 🧪⚡

テストは **InMemory** に差し替えるだけ。ファイルもネットも不要！

### ✅ うれしさ③：newが散らばらない（迷子防止）🧭

「あれ？どこでRepo作ってるの？」が消える！
**newはここ！** って断言できるのが強い💪

---

## 4) まず “ダメな例” を見て感覚をつかむ 🙅‍♀️💥

### ❌ ダメ：ユースケースが勝手に外側を作る（中心が汚れる）

```ts
// app/usecases/AddTodo.ts（悪い例）
import { JsonFileTodoRepository } from "../adapters/JsonFileTodoRepository"; // ←中心が外側を知ってる😱

export class AddTodo {
  async execute(title: string) {
    const repo = new JsonFileTodoRepository("todos.json"); // ←中心でnewしてる😱
    await repo.save({ title });
  }
}
```

これ、後で **DBに変えたい** ってなった瞬間に地獄…🥲
中心が外側の都合（ファイルパスとか）に縛られるからね。

---

## 5) Composition Rootの“鉄のルール”🧱🔥

### ルールA：外側の new は Composition Root に集める 🧩

* DB / ファイル / HTTPクライアント / Logger / UUID生成 / Clock…など
  「環境で変わるもの」は **合体場所で作る**！

### ルールB：中心には “interface（Port）” だけ渡す 🔌

* 中心は `TodoRepositoryPort` だけ知ってればOK👌

### ルールC：DIコンテナは “使ってもいいけど漏らさない” 🧰⚠️

使うなら **Composition Root内だけ**。外に `container.get()` を持ち出すと一気に事故る（Service Locatorっぽくなる）😵‍💫
「コンテナは合体場所の中で完結させる」が王道だよ。([InfoQ][1])

---

## 6) 実装していこう：Composition Root を作る 🏗️✨

ここでは ToDoミニで、こんな切替を目標にするよ👇

* 本番：`JsonFileTodoRepository`
* テスト：`InMemoryTodoRepository`
* 入口：CLI と HTTP の両方が同じ中心を使う

### 6-1) 置き場所（おすすめ）📁

例：

* `src/compositionRoot.ts` ← ここが合体場所💖
* `src/cli/main.ts`（CLI起動）
* `src/http/server.ts`（HTTP起動）

---

## 7) 合体場所の設計：Configを “型で” 固める 🧠✨

「環境変数とか引数の文字列」をそのまま使うと、タイポで死ぬよね😇
だから **Configはunion型でカチカチ** にするのがおすすめ！

```ts
// src/compositionRoot.ts
export type AppConfig = Readonly<{
  storage: "memory" | "file";
  dataFilePath: string; // storage=file の時に使う
}>;
```

---

## 8) Composition Root 本体：依存をつないで “アプリ本体” を返す 🧩🏗️

ポイントはこれ👇

* Adapter を作る
* UseCase を作る（Portを注入）
* Inbound（CLI/HTTP）から使いやすい形で返す

```ts
// src/compositionRoot.ts
import path from "node:path";

import { InMemoryTodoRepository } from "./adapters/outbound/InMemoryTodoRepository";
import { JsonFileTodoRepository } from "./adapters/outbound/JsonFileTodoRepository";

import { AddTodoUseCase } from "./app/usecases/AddTodoUseCase";
import { CompleteTodoUseCase } from "./app/usecases/CompleteTodoUseCase";
import { ListTodosUseCase } from "./app/usecases/ListTodosUseCase";

export type AppConfig = Readonly<{
  storage: "memory" | "file";
  dataFilePath: string;
}>;

export type App = Readonly<{
  addTodo: AddTodoUseCase;
  completeTodo: CompleteTodoUseCase;
  listTodos: ListTodosUseCase;
}>;

function createTodoRepository(config: AppConfig) {
  if (config.storage === "file") {
    // Windowsでも安全なパスにするなら join 推奨🪟✨
    const filePath = path.resolve(config.dataFilePath);
    return new JsonFileTodoRepository(filePath);
  }
  return new InMemoryTodoRepository();
}

export function buildApp(config: AppConfig): App {
  // ① Outbound Adapter を選ぶ🧩
  const todoRepo = createTodoRepository(config);

  // ② UseCase を組み立てる🧠❤️（Portを注入）
  const addTodo = new AddTodoUseCase(todoRepo);
  const completeTodo = new CompleteTodoUseCase(todoRepo);
  const listTodos = new ListTodosUseCase(todoRepo);

  // ③ Inbound側が使える形にまとめて返す🎁
  return {
    addTodo,
    completeTodo,
    listTodos,
  };
}
```

**ここが最高に大事**：
中心側（UseCase）は `JsonFileTodoRepository` の存在を1ミリも知らない😌🛡️

---

## 9) CLI起動側：合体場所を呼んで、入口は薄くする ⌨️✨

```ts
// src/cli/main.ts
import { buildApp, type AppConfig } from "../compositionRoot";

function readConfigFromArgs(): AppConfig {
  // 例：node dist/cli/main.js --storage=file --file=./data/todos.json
  const args = new Map<string, string>();
  for (const token of process.argv.slice(2)) {
    const [k, v] = token.split("=");
    if (k && v) args.set(k.replace(/^--/, ""), v);
  }

  const storage = (args.get("storage") ?? "memory") as AppConfig["storage"];
  const dataFilePath = args.get("file") ?? "./data/todos.json";

  return { storage, dataFilePath };
}

async function main() {
  const config = readConfigFromArgs();
  const app = buildApp(config);

  // 入口は “呼ぶだけ” に徹する💖
  // ここでは例として「追加」だけ
  await app.addTodo.execute({ title: "buy milk" });

  const list = await app.listTodos.execute({});
  console.log(list);
}

main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
```

CLIは「翻訳して呼ぶだけ」って感じにできると、超ヘキサゴナルっぽいよ〜😊🔌

---

## 10) HTTP起動側：ルートは薄く、中心はそのまま 🌐✨

```ts
// src/http/server.ts
import http from "node:http";
import { buildApp } from "../compositionRoot";

const app = buildApp({ storage: "file", dataFilePath: "./data/todos.json" });

const server = http.createServer(async (req, res) => {
  if (req.method === "GET" && req.url === "/todos") {
    const list = await app.listTodos.execute({});
    res.writeHead(200, { "content-type": "application/json; charset=utf-8" });
    res.end(JSON.stringify(list));
    return;
  }

  res.writeHead(404);
  res.end("not found");
});

server.listen(3000, () => {
  console.log("http://localhost:3000");
});
```

HTTP側が増えても **中心は一切変更なし** ✅
この「変えなくていい」がご褒美だよ🥳💕

---

## 11) “差し替え戦略” の定番パターン集 🔁🎁

### パターン①：Configで切替（いちばんシンプル）🧩

* `storage: "file" | "memory"` で分岐
* 小規模ならこれで十分！

### パターン②：Factory関数で分離（おすすめ）🏭✨

* `createTodoRepository()` みたいに **生成だけ隔離**
* `buildApp()` が読みやすくなる😊

### パターン③：エントリごとに “別Composition Root” を持つ 🧠

* `buildCliApp()` / `buildHttpApp()` に分ける
  ただし初心者のうちは **1個でOK**（増やしすぎ注意⚠️）

---

## 12) テストで「気持ちよさ」を体験しよう 🧪💖

Vitest は v4 が出てるよ〜！([vitest.dev][2])
（ユニットテスト用途なら相性いい✨）

### 12-1) buildApp を “テスト用設定” で呼ぶだけ

```ts
// src/app/usecases/AddTodoUseCase.test.ts
import { describe, it, expect } from "vitest";
import { buildApp } from "../../compositionRoot";

describe("AddTodoUseCase", () => {
  it("タイトル空はエラーになる", async () => {
    const app = buildApp({ storage: "memory", dataFilePath: "" });

    await expect(app.addTodo.execute({ title: "" })).rejects.toThrow();
  });

  it("追加できる", async () => {
    const app = buildApp({ storage: "memory", dataFilePath: "" });

    await app.addTodo.execute({ title: "study" });
    const list = await app.listTodos.execute({});

    expect(list.items.length).toBe(1);
  });
});
```

**ファイルI/Oなし**、**HTTPなし**、**速い**、**安定**🥹✨
これが Composition Root のご褒美🎁

---

## 13) よくある事故パターン（ここ注意！）😱⚠️

### 😱 事故①：あちこちで new し始める（Control Freak）

「便利だから…」で UseCase や Adapter 内に new を入れると、差し替え不能に戻る🥲
“揮発する依存は合体場所で作る”が基本だよ。([Zenn][3])

### 😵‍💫 事故②：どこでも `container.get()`（Service Locator化）

DIコンテナを使うなら **Composition Rootの中だけ**。外へ漏れると設計が崩れやすい💥 ([InfoQ][1])

### 😬 事故③：環境依存（ファイルパス等）を中心に混ぜる

中心に `process.env` とか `path` とか入れ始めると、どんどん汚れていく…🧼💦
そのへんは入口 or 合体場所で吸収しようね😊

---

## 14) 2026の “現場っぽい” 最新メモ（最低限）🧷✨

* Node.js は **v24 が Active LTS** 扱いで更新が続いてるよ（偶数系LTSが基本）([Node.js][4])
* 2026-01-13 のセキュリティリリースでは、24.x/22.x/20.x などが更新対象になってる（更新大事！）([Node.js][5])
* TypeScript は npm の `latest` として **5.9 系** が案内されてる（5.9のリリースノートも公式あり）([NPM][6])
* ESLint は v9 で “flat config” がデフォルト路線として整理されてきてるよ🧹([eslint.org][7])

（この章的には “Composition RootにLint/Test導入の依存が漏れないようにする” って意味で重要だよ😊）

---

## 15) AIに頼るならここが安全🤖✅

### ✅ 頼っていい（速くなる）

* Composition Root の雛形生成（関数の枠、Config型、Factory分離）
* “依存グラフ”の一覧化（どこが誰をnewしてるか）

### ⚠️ ちょい危険（AIが崩しがち）

* Port（interface）の粒度
* 依存の向き（中心→外側のimportを混ぜてくることがある😇）

### そのまま使える質問テンプレ📝🤖

* 「`src` の中で `new` が散らばってない？newしていい場所だけ教えて」
* 「中心（domain/app）が adapters を import してないかチェックして」
* 「Composition Root 以外で process.env を触ってないか探して」

---

## 16) まとめ：この章の合言葉 🎁💖

* **new は合体場所に集める** 🧩🏗️
* **中心には Port（約束）だけ渡す** 🔌
* **本番とテストは差し替えで勝つ** 🔁🧪✨

---

## 17) 自主課題（いい練習になるよ）📝🎀

### 課題A：Repoを “SQLite版” に差し替え（中心は無修正）🔁

* `SqliteTodoRepository` を adapters/outbound に追加
* 追加したら Composition Root の `createTodoRepository()` だけ変更！

### 課題B：入口を増やす（中心は無修正）🚪✨

* HTTPの `POST /todos` を足す
* DTO変換はHTTP側、中心は知らないままにする

### 課題C：buildAppを “依存グラフが見える形” に整える 🧠

* `createPorts()` / `createUseCases()` に分けて読みやすくする
  （やりすぎて分裂しすぎないように注意⚠️）

---

必要なら、今のあなたの章構成（第1〜34章）で作った ToDo ミニの **フォルダ構成に合わせて**、この第35章のコードを「そのままコピペで動く形」に寄せて書き直すよ😊💖

[1]: https://www.infoq.com/articles/DI-Mark-Seemann/?utm_source=chatgpt.com "Dependency Injection with Mark Seemann"
[2]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[3]: https://zenn.dev/satokiyo/articles/20230621-dependency-injection?utm_source=chatgpt.com "[読書] Dependency Injection Principles, Practices, and ..."
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[5]: https://nodejs.org/en/blog/vulnerability/december-2025-security-releases?utm_source=chatgpt.com "Tuesday, January 13, 2026 Security Releases"
[6]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "typescript"
[7]: https://eslint.org/blog/2025/05/eslint-v9.0.0-retrospective/?utm_source=chatgpt.com "ESLint v9.0.0: A retrospective"