# 第24章：Inbound Adapter①：CLIで最速成功⌨️🎉

この章は「**とにかく動く！**」を最短で作って、ヘキサゴナルの気持ちよさを体で覚える回だよ〜😊💖
GUIもHTTPもまだいらない！まずは **CLI（コマンド入力）**で、ユースケースを呼び出して成功体験しよ✨

---

## 1) 今日の完成イメージ🎯✨

PowerShellでこんな感じに打てるようにするよ👇

* 追加：`npm run cli -- add "牛乳を買う"` 🥛
* 一覧：`npm run cli -- list` 📋
* 完了：`npm run cli -- done <id>` ✅

ポイントはこれ👇
Inbound Adapter（CLI）は **薄く**！薄く！薄く！🥗✨

* ✅ 引数を読む（parse）
* ✅ ちょい入力チェック（validate）
* ✅ DTOに変換してユースケース呼ぶ（call）
* ✅ 表示用に整形して出す（present）
* ❌ ルール（タイトル空禁止とか）をここに書かない🙅‍♀️（それは中心の仕事🧠）

---

## 2) “最新”まわり：今どれ使うのが素直？📌🤖

開発中にTSをサクッと動かすのは **tsx** がラクだよ〜⚡

* `tsx` はTSをそのまま実行できる（ただし **型チェックはしない**）ので、**別で `tsc` を回す**のが基本だよ😊 ([Node.js][1])
* Nodeは **LTS** を使うのが安心（2026/01時点で Node 24 LTS のセキュリティリリースも出てるよ）🔒 ([Node.js][2])
* TypeScriptの最新系は **5.9** 系の情報が公式に出てるよ📘 ([TypeScript][3])

---

## 3) 実装の置き場所（迷子防止）📁🧭

この章では、CLI入口をここに置くよ👇

* `src/adapters/inbound/cli/`

  * `CliAdapter.ts`（薄い入口本体）
  * `main.ts`（とりあえず動かす用の組み立て＝簡易Composition Root）

> 本格的な “Composition Root 1か所縛り” は後ろの章でガッツリやるから、今日は **main.ts に仮で寄せる**感じでOKだよ😊🧩

---

## 4) まず `tsx` を入れて、CLIスクリプトを生やす🌱⚡

PowerShellで👇

```powershell
npm i -D tsx
```

`package.json` に scripts を追加👇（例）

```json
{
  "scripts": {
    "typecheck": "tsc -p tsconfig.json --noEmit",
    "cli": "tsx src/adapters/inbound/cli/main.ts"
  }
}
```

💡 `tsx` は型チェックしないから、実行前にこれを挟むクセが安心✨ ([Node.js][1])

* `npm run typecheck` ✅
* `npm run cli -- ...` ✅

---

## 5) CLI Adapter（入口）は「薄く」書く🥗⌨️

### 5-1. まずはユースケースを“関数”として受け取る🔌✨

CLIは「中心（ユースケース）をnewしない」。
**依存は外から渡される**形にしておくと、ヘキサっぽさが一気に出るよ😊🛡️

`src/adapters/inbound/cli/CliAdapter.ts`

```ts
type AddTodoInput = { title: string };
type AddTodoOutput = { id: string };

type DoneTodoInput = { id: string };

type ListTodosOutput = {
  items: Array<{ id: string; title: string; completed: boolean }>;
};

// ここが「Inbound Port」っぽい入口（関数にして簡略化）
type AddTodo = (input: AddTodoInput) => Promise<AddTodoOutput>;
type DoneTodo = (input: DoneTodoInput) => Promise<void>;
type ListTodos = () => Promise<ListTodosOutput>;

type Deps = {
  addTodo: AddTodo;
  doneTodo: DoneTodo;
  listTodos: ListTodos;
};

export class CliAdapter {
  constructor(private readonly deps: Deps) {}

  async run(argv: string[]): Promise<number> {
    const [command, ...rest] = argv;

    if (!command || command === "help" || command === "--help" || command === "-h") {
      this.printHelp();
      return 0;
    }

    try {
      switch (command) {
        case "add": {
          const title = rest.join(" ").trim();
          if (!title) {
            console.log("❌ タイトルが空だよ〜！例: add \"牛乳を買う\" 🥛");
            return 2;
          }
          const out = await this.deps.addTodo({ title });
          console.log(`🎉 追加したよ！ id=${out.id}`);
          return 0;
        }

        case "list": {
          const out = await this.deps.listTodos();
          if (out.items.length === 0) {
            console.log("📭 まだ何もないよ〜");
            return 0;
          }
          console.log("📋 ToDo一覧だよ〜✨");
          for (const t of out.items) {
            const mark = t.completed ? "✅" : "⬜";
            console.log(`${mark} ${t.id}  ${t.title}`);
          }
          return 0;
        }

        case "done": {
          const id = (rest[0] ?? "").trim();
          if (!id) {
            console.log("❌ id が必要だよ〜！例: done 123 ✅");
            return 2;
          }
          await this.deps.doneTodo({ id });
          console.log("✅ 完了にしたよ〜！");
          return 0;
        }

        default:
          console.log(`🤔 コマンドがわからないよ: ${command}`);
          this.printHelp();
          return 2;
      }
    } catch (e) {
      // ここは「表示に変換」だけ（ルール判断はしない）
      const msg = e instanceof Error ? e.message : String(e);
      console.log(`💥 エラー: ${msg}`);
      return 1;
    }
  }

  private printHelp() {
    console.log(`
⌨️ 使い方:
  npm run cli -- add "タイトル"
  npm run cli -- list
  npm run cli -- done <id>

📝 例:
  npm run cli -- add "牛乳を買う"
  npm run cli -- list
  npm run cli -- done 1
`.trim());
  }
}
```

### ここが「薄い」ポイントだよ🥗✨

* ルール（例：二重完了禁止）は書いてない
* 例外が来たら **表示文に変換するだけ**
* “入力の形” と “出力の形” は **DTOで閉じてる**（domain型を漏らさない🛡️）

---

## 6) `main.ts`：とりあえず動かす簡易組み立て🧩🏗️

`src/adapters/inbound/cli/main.ts`

ここは2パターン用意するね😊

* A) すでにユースケースがある人：importして差し込む✨
* B) まだ揃ってない人：**超ミニの仮ユースケース**で動かす🎉（今日の成功体験用）

### A) 既存ユースケースを差し込む版（おすすめ）🌟

```ts
import { CliAdapter } from "./CliAdapter";

// 例：あなたのプロジェクト側に合わせて読み替えてね🙏
// import { AddTodoUseCase, DoneTodoUseCase, ListTodosUseCase } from "../../../app/usecases";
// import { InMemoryTodoRepository } from "../../outbound/InMemoryTodoRepository";

async function main() {
  // ここは仮：後の章で Composition Root を綺麗に1箇所にするよ😊
  // const repo = new InMemoryTodoRepository();
  // const addTodo = new AddTodoUseCase(repo);
  // const doneTodo = new DoneTodoUseCase(repo);
  // const listTodos = new ListTodosUseCase(repo);

  // 今日の章では「cliが薄い」が主役なので、
  // 依存を渡す形だけ先に作っておこう✨
  throw new Error("ここをあなたの UseCase に差し替えてね🙂（下のB版ならそのまま動くよ）");
}

main().catch((e) => {
  console.error("💥 起動エラー:", e);
  process.exitCode = 1;
});
```

### B) 今日だけの「仮」ユースケースで動かす版（コピペ即動作）🎉

```ts
import { CliAdapter } from "./CliAdapter";

type Todo = { id: string; title: string; completed: boolean };

// 💡これは「仮」。本物のルールは中心（domain/usecase）へ移すよ🧠✨
const db: Todo[] = [];
let seq = 1;

const addTodo = async ({ title }: { title: string }) => {
  const t: Todo = { id: String(seq++), title, completed: false };
  db.push(t);
  return { id: t.id };
};

const listTodos = async () => {
  return { items: db.map((t) => ({ ...t })) };
};

const doneTodo = async ({ id }: { id: string }) => {
  const t = db.find((x) => x.id === id);
  if (!t) throw new Error("そのid、見つからないよ〜😵");
  if (t.completed) throw new Error("もう完了済みだよ〜✅");
  t.completed = true;
};

async function main() {
  const cli = new CliAdapter({ addTodo, doneTodo, listTodos });
  const exitCode = await cli.run(process.argv.slice(2));
  process.exitCode = exitCode;
}

main().catch((e) => {
  console.error("💥 起動エラー:", e);
  process.exitCode = 1;
});
```

> B版は「今日の動く体験用」だよ😊
> 次の章以降で、db（配列）じゃなく **Outbound Adapter（InMemory / File）** に差し替えていくと、ヘキサの良さがどんどん見える✨🔁

---

## 7) 実行して「動く！」を味わう🚀💖

1. 型チェック✅

```powershell
npm run typecheck
```

2. 追加🥛

```powershell
npm run cli -- add "牛乳を買う"
```

3. 一覧📋

```powershell
npm run cli -- list
```

4. 完了✅

```powershell
npm run cli -- done 1
```

---

## 8) ありがち事故と回避テク😵‍💫🧯

### ✅ npm の `--` を忘れる

`npm run cli add "..."` だと、引数がうまく渡らないことがあるよ〜
👉 **必ず `--` を挟む**：`npm run cli -- add "..."` ✨

### ✅ `tsx` は型チェックしない

動いたけど実は型がズレてた！が起きやすい😇
👉 `npm run typecheck` を先に回すのが安心だよ ([Node.js][1])

---

## 9) AI（Copilot/Codex）に頼むと良いところ🤖✨

CLI Adapterは **定型が多い**からAIが得意だよ😊
（ただし “責務の境界” は人間が握る🛡️）

そのまま投げてOKプロンプト例👇📝

* 「Nodeの `process.argv` で `add/list/done` をswitchで分岐するCLI雛形を作って。入力チェックは最小。ユースケースは関数で受け取る形にして」🤖✨
* 「CLIのhelp表示を、WindowsのPowerShellで動く例つきで整えて」📌
* 「例外をユーザー向けメッセージに変換する薄いハンドリングにして（業務ルールは書かない）」🥗

---

## 10) “薄いAdapter”セルフチェック✅🥗

最後にこれ見てOKなら勝ち🎉

* [ ] CLIが domain の型（Entity/ValueObject）を import してない🛡️
* [ ] CLIに業務ルール（例：二重完了禁止の判断）が増えてない🙅‍♀️
* [ ] CLIは「入力→DTO→ユースケース→出力整形」だけになってる🔁
* [ ] `new UseCase()` をCLIがやってない（依存は外から）🔌✨

---

## ミニ宿題🎀📝

1. `help` コマンドを追加して、usageを丁寧にしてみよ😊
2. `list` に `--all` / `--done` フィルタを付ける（ただしルールは増やさない！表示だけ✨）

---

次は **Outbound Adapter（InMemoryRepository）** で、今日の “仮db” をちゃんと差し替えていくよ〜🧠📦🔁✨

[1]: https://nodejs.org/en/learn/typescript/run?utm_source=chatgpt.com "Running TypeScript with a runner"
[2]: https://nodejs.org/en/blog/release/v24.13.0?utm_source=chatgpt.com "Node.js 24.13.0 (LTS)"
[3]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
