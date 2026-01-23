# 第25章：Inbound Adapter② CLIの入力→DTO変換 🔁⌨️✨

前の章（第24章）で「CLIからユースケースを呼べた！🎉」ところまで行ったので、今回は **“人間の入力（コマンド）” を “中心が食べられる形（DTO）” に翻訳**していくよ〜😊💕

---

## 1. 今日のゴール 🎯💖

この章の終わりに、こうなってたら勝ち！✨

* CLIの入力（`process.argv`）を **安全にパース**できる 🧠🔍
* 文字列だらけの入力を **DTOに変換**できる 📮✨
* 変換やバリデーションは **Adapter側に閉じ込め**、中心（UseCase/Domain）を汚さない 🛡️🏰
* 入力ミスのときに **ユーザーに優しいエラー表示**ができる 😌🫶

---

## 2. なぜ「CLI入力→DTO変換」を Adapter に置くの？🧩

CLI入力って、だいたいこんな “外側都合” のかたまりだよね👇😵‍💫

* 文字列しか来ない（`"123"` とか `"true"` とか）🧻
* `"--title"` の書き方、引用符、スペース、OSの癖…🪟💥
* 入力ミスが日常茶飯事（`--titlle` とか）🙃

これを中心（UseCase/Domain）に持ち込むと…

* 中心が文字列処理まみれで汚れる 😱
* テストがしんどくなる 😵
* 入口が増えたとき（HTTP化とか）に地獄 🔥

だから、**Adapterが翻訳係🧩**になって、中心に渡すのは **綺麗なDTOだけ📮** にするのが気持ちいいの✨

---

## 3. 今回のCLI仕様（例）を決めよう 📝🍰

ToDoミニアプリのコマンドを、こんな感じにするよ😊

* 追加：`todo add --title "牛乳を買う"` 🥛
* 完了：`todo complete --id 123` ✅
* 一覧：`todo list` 📋

> ここで大事なのは「仕様を決めたら、中心じゃなく入口で頑張る」ってことだよ〜🛡️✨

---

## 4. パースの道具：Node標準 `parseArgs` を使う 🔧✨

Nodeには **コマンドライン引数を構造化してくれる** `util.parseArgs` があるよ！
`options / short / strict / positionals` など、欲しい機能がまとまってる🧠✨ ([Node.js][1])

「外部ライブラリ（commander等）でもOK」だけど、まずは **依存を増やさず**に行けるこの方法でいこ〜😊

---

## 5. DTOってどこに置く？（置き場所のおすすめ）📁🧭

DTOは「中心が食べる形」だから、**app層（ユースケース寄り）**に置くのが扱いやすいよ✨

例：

* `src/app/dto/AddTodoDto.ts`
* `src/app/dto/CompleteTodoDto.ts`

---

## 6. 実装ステップ（ここから手を動かすよ〜！）💻🎀

### 6-1. DTOを作る 📮✨

```ts
// src/app/dto/AddTodoDto.ts
export type AddTodoDto = {
  title: string;
};
```

```ts
// src/app/dto/CompleteTodoDto.ts
export type CompleteTodoDto = {
  id: string;
};
```

> `id` を string にしてるのは、CLI入力がまず文字列だからだよ😊
> 数値にしたいなら「入口で変換」してからDTOにしてね🧩✨

---

### 6-2. バリデーション：Zod で「入口チェック」する 🧪✨

Zodは **スキーマ（型＋制約）**を作って、入力を検証できるよ😊
`z.object(...)` みたいに書けるのが特徴✨ ([Zod][2])
さらに最近は Zod v4 の情報も出てるから、プロジェクトの採用バージョンは固定しておくと安心だよ🧷✨ ([Zod][3])

```ts
// src/adapters/cli/validation/addTodoSchema.ts
import { z } from "zod";

export const addTodoSchema = z.object({
  title: z.string().trim().min(1, "title は空にできません😢"),
});

export type AddTodoInput = z.infer<typeof addTodoSchema>;
```

ポイント💡

* `.trim().min(1)` みたいな “入力の見た目チェック” は **入口の責務** だよ🧩✨
* これ、中心に入れると「HTTPでも同じこと書く」羽目になるから、入口で統一しておくと最高😊💕

---

### 6-3. コマンドをパースする（`parseArgs`）🔍⌨️

`util.parseArgs` は Node公式のドキュメントに仕様がまとまってるよ✨
`options` を定義して、戻り値の `values / positionals` を使う感じ😊 ([Node.js][1])

今回は「サブコマンド方式」だから、

* `positionals[0]` → `add / complete / list`
* それ以外を `options` で受け取る

って分けるよ〜！

```ts
// src/adapters/cli/parse/parseCli.ts
import { parseArgs } from "node:util";
import { addTodoSchema } from "../validation/addTodoSchema";
import type { AddTodoDto } from "../../../app/dto/AddTodoDto";
import type { CompleteTodoDto } from "../../../app/dto/CompleteTodoDto";

export type CliCommand =
  | { kind: "add"; dto: AddTodoDto }
  | { kind: "complete"; dto: CompleteTodoDto }
  | { kind: "list" };

export function parseCli(argv: string[]): CliCommand {
  // argv は `process.argv.slice(2)` が入ってくる想定だよ😊
  const { positionals } = parseArgs({
    args: argv,
    allowPositionals: true,
    strict: false, // まずは学習用に false（慣れたら true 推奨✨）
  });

  const sub = positionals[0];

  if (sub === "add") return parseAdd(argv);
  if (sub === "complete") return parseComplete(argv);
  if (sub === "list") return { kind: "list" };

  throw new Error(`不明なコマンドです😢: ${String(sub)}\n例: todo add --title "xxx"`);
}

function parseAdd(argv: string[]): CliCommand {
  // add の後ろだけを parseArgs に渡す（subcommand を取り除く）
  const args = argv.slice(1);

  const { values } = parseArgs({
    args,
    options: {
      title: { type: "string", short: "t" },
    },
    strict: true,
  });

  const result = addTodoSchema.safeParse({
    title: values.title,
  });

  if (!result.success) {
    const msg = result.error.issues.map((i) => `- ${i.message}`).join("\n");
    throw new Error(`入力が変だよ〜😢\n${msg}`);
  }

  return { kind: "add", dto: { title: result.data.title } };
}

function parseComplete(argv: string[]): CliCommand {
  const args = argv.slice(1);

  const { values } = parseArgs({
    args,
    options: {
      id: { type: "string" },
    },
    strict: true,
  });

  const id = String(values.id ?? "").trim();
  if (!id) throw new Error("id が必要だよ〜😢 例: todo complete --id 123");

  return { kind: "complete", dto: { id } };
}
```

ここ、超重要ポイント3つ🧠🧷✨

1. **「翻訳」は adapter 内で完結**

   * `values` は未信用（`unknown` みたいなもん）
   * スキーマで検証してから DTO を作る🧩

2. **中心は `process.argv` を一切知らない** 🙅‍♀️

   * これが “中心を守る” 🛡️🏰

3. `parseArgs` は `options` 定義に従って構造化して返してくれる

   * `values` と `positionals` が基本セットだよ✨ ([Node.js][1])

---

### 6-4. CLI Runner 側で使う（ユースケースに渡す）🚀✨

第24章で作った “CLI入口” で、DTOを作ってユースケースに渡す形へ進化させよう😊

```ts
// src/adapters/cli/cliRunner.ts
import { parseCli } from "./parse/parseCli";

export async function runCli(argv: string[]) {
  try {
    const cmd = parseCli(argv);

    if (cmd.kind === "add") {
      // 例: addTodoUseCase.execute(cmd.dto)
      console.log("ADD DTO:", cmd.dto);
      return;
    }

    if (cmd.kind === "complete") {
      console.log("COMPLETE DTO:", cmd.dto);
      return;
    }

    if (cmd.kind === "list") {
      console.log("LIST!");
      return;
    }
  } catch (e) {
    // Nodeのエラー文字列は変わることがあるので、識別は code 等が推奨だよ〜という話もあるよ🧯
    // （ここでは学習用に message 表示でOK😊）
    // Node公式でも error.message は変更され得るので識別子には code 推奨って書かれてるよ :contentReference[oaicite:5]{index=5}
    const msg = e instanceof Error ? e.message : String(e);
    console.error(msg);
    process.exitCode = 1;
  }
}
```

---

## 7. Windowsで詰まりやすいポイント🪟😵‍💫（あるある救急箱🚑✨）

### 7-1. ダブルクォート忘れ問題 `"..."` 😇

PowerShellだとスペース入りは引用符が必要！

* ✅ `--title "牛乳を買う"`
* ❌ `--title 牛乳を買う`（途中で分裂する💥）

### 7-2. `--title=xxx` と `--title xxx` の差

`parseArgs` はどっちも扱えることが多いけど、まず教材では **`--title "xxx"`** に寄せると混乱が少ないよ😊

---

## 8. 「Adapterが太ってない？」チェック🥗⚠️

この章の CLI Adapter は **薄いほど正義**✨

OK ✅

* parse（引数を読む）
* validate（入力の形を検査）
* DTOへ変換（翻訳）
* エラーを人間向けに整形（表示）

NG ❌

* 「タイトルが重複したらダメ」みたいな業務ルールをここで判断
* “完了の二重適用禁止” をここでやる
  → それは中心（Domain/UseCase）の仕事だよ〜🛡️🏰💦

---

## 9. AI拡張の使いどころ🤖💖（安全にズルしよ♪）

AIに頼むと強いところ✨

* `parseArgs` の `options` 設計の下書き
* Zodスキーマの雛形
* エラーメッセージの改善案
* CLIヘルプ文の生成

そのまま使えるプロンプト例📝✨

* 「このCLI仕様で `node:util parseArgs` の options 定義を作って。subcommand は add/complete/list。短縮オプションも提案して」
* 「次の DTO に対して Zod スキーマを書いて。trim/min も入れて。エラーメッセージは日本語で」
* 「この CLI の入力ミスに対する help 表示を、初心者向けに短くして」

AIに任せちゃダメなところ⚠️

* 「中心が何を責務に持つべきか」
* 「Port/Adapterの境界」
  ここはあなたの設計の芯なので、主導権は握ってね🛡️✨

---

## 10. 動作チェック（ミニ確認リスト）✅🎉

手元でこんな感じに試してOKなら完成だよ😊

* `todo add --title "牛乳を買う"` → DTOが出る
* `todo add --title ""` → やさしいエラーが出る😢
* `todo complete --id 123` → DTOが出る
* `todo unknown` → 例の使い方が出る

---

## 11. 自主課題📝🎀（ちょい楽しい）

1. `add` に `-t` を追加して、`todo add -t "xxx"` でも動くようにしてみて✨
   （もうコードに `short: "t"` 入れてるから成功体験しやすいよ😊） ([Node.js][1])

2. `list` に `--completed` フラグを追加して、完了だけ表示できるようにする（DTOを作る練習）✅

3. エラーメッセージに「例」を必ず付ける（ユーザー体験UP）💕

---

## まとめ 🎁💖

* CLIの入力は **外側都合のぐちゃぐちゃ** 😵‍💫
* Adapterが **parse + validate + DTO変換** までやって、中心を守る🛡️🏰
* Node標準の `util.parseArgs` で、引数パースはかなり楽できるよ🔧✨ ([Node.js][1])
* スキーマで入口チェックして、**中心には綺麗なDTOだけ** 渡そう📮✨ ([Zod][2])

---

次の第26章では、Outbound Adapter（InMemoryRepository）を作って「差し替えできる〜！🔁✨」を体感していくよ😊🧠

[1]: https://nodejs.org/api/util.html "Util | Node.js v25.4.0 Documentation"
[2]: https://zod.dev/api?utm_source=chatgpt.com "Defining schemas"
[3]: https://zod.dev/v4?utm_source=chatgpt.com "Release notes"
