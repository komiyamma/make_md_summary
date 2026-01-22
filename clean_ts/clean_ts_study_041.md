# 第41章：設定（Config）の境界 ― どこで読み、どこへ渡す？🧾✨

この章はね、**「環境ごとに変わる情報（Port番号、DBパス、APIキー…）が、内側（UseCase/Entity）に侵入して事故るのを防ぐ」**ための回だよ〜😊🛡️

---

## この章のゴール🎯✨

* `process.env` とか `.env` の存在を、**UseCase/Entityから消せる**🌪️➡️🧼
* 設定を **“外側で読む→型チェック→必要最小限だけ注入”** できる💉✨
* テストで **設定のせいでつまづかない**（＝差し替えが楽）🧪🎉

---

## まず結論：Configの鉄則3つ🧠📌

1. **Configは外側で読む**（起動時・Composition Root）🚪
2. **内側はConfigを知らない**（`process.env`禁止！）🙅‍♀️
3. **渡すのは必要最小限**（Config丸ごと注入しない）🍱✨

「環境差」をコードに混ぜると壊れやすいから、**境界で止める**のが勝ち筋だよ😊🧱

---

## なんで危ないの？よくある事故集😇💥

### 事故①：UseCaseが `process.env` を直読みする

* UseCaseが「外側（実行環境）」に依存しちゃう
* テストで `process.env` を整えないと落ちる
* 依存が“見えない”から、後で地獄👻

### 事故②：Configを “どこでもimportできるSingleton” にする

* いろんな層がこっそり使い始めて、いつの間にか中心が汚れる🫠
* 「何が必要な依存なのか」が隠れてレビューでも気づきにくい🙈

---

## Configって何が入るの？仕分けが超大事🧺✨

### ✅ 外側のConfig（内側に入れない寄り）

* サーバーの `PORT`、DB接続情報、外部サービスURL、APIキー、ログ設定など
* これは「インフラ都合」だから、外側で完結させたい💡
  （12-factorでも「設定は環境変数に置く」が推奨されてるよ）([12-Factor App][1])

### ✅ 内側に渡してもOKな“方針”っぽい値（ただし最小限！）

* 例：`TASK_TITLE_MAX_LENGTH`（運用で変えたい上限）みたいなもの
* **Config丸ごとじゃなくて、数値1個だけ渡す**のがコツ🍬

---

## 2026的：.envはNodeが“標準で”読めるよ📦✨

最近のNodeは `.env` を **CLIオプションで読み込める**よ〜！
`--env-file` / `--env-file-if-exists` が公式に案内されてる👏([Node.js][2])
しかも `.env` サポートは Node 20.6.0 から入った流れ（リリースノートにもある）だよ🆕([Node.js][3])

* `--env-file`：ファイルが無いとエラーになりやすい
* `--env-file-if-exists`：無くても続行してくれる（本番で便利）💡([Node.js][2])

※ `dotenv` も今も普通に使える（npmにある）から、チーム方針で選んでOKだよ😊([npmjs.com][4])

---

## 目標の形：データの流れ（Config版）🔁✨

**外側（起動）**
`.env/環境変数` を読む → **型チェック** → `AppConfig` を作る
↓
**外側（組み立て）**
必要な値だけ取り出して、AdapterやUseCaseへ注入💉
↓
**内側（UseCase/Entity）**
「ただの値」として受け取って使う（出どころは知らない）😌

---

## 実装：Configを“外側で読む→検証→注入”してみよう🛠️💕

### 1) `.env`（ローカル用）を用意🗒️

```ini
PORT=3000
DB_PATH=./data/tasks.sqlite
TASK_TITLE_MAX_LENGTH=100
NODE_ENV=development
```

### 2) Node起動で `.env` を読み込む（標準機能）🚀

```json
{
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "start": "node dist/main/index.js",
    "start:dev": "node --env-file-if-exists=.env dist/main/index.js"
  }
}
```

`--env-file-if-exists` は「ローカルは.env、クラウドは環境変数」みたいな切り替えに強いよ😊🧩([Node.js][2])

---

## 3) 外側でConfigを“型チェック”する（Zodで安心）🧪✨

```ts
// src/main/config/env.ts
import { z } from "zod";

const EnvSchema = z.object({
  PORT: z.coerce.number().int().min(1).max(65535).default(3000),
  DB_PATH: z.string().min(1),
  TASK_TITLE_MAX_LENGTH: z.coerce.number().int().min(1).max(200).default(100),
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
});

export type AppConfig = z.infer<typeof EnvSchema>;

export function loadConfig(): AppConfig {
  const parsed = EnvSchema.safeParse(process.env);
  if (!parsed.success) {
    console.error("❌ Config error:", parsed.error.format());
    process.exit(1); // 起動直後に落として気づけるのが正義🛑
  }
  return parsed.data;
}
```

Zodは「スキーマ定義して検証する」ライブラリで、`parse/safeParse` でバリデーションできるよ🧷([Zod][5])

---

## 4) どこへ渡す？“必要最小限”注入の例💉🍱

```ts
// src/main/di/makeApp.ts（イメージ）
import type { AppConfig } from "../config/env";

export function makeApp(config: AppConfig) {
  // ✅ DB_PATHはSQLiteRepository（外側）へ
  const repo = new SqliteTaskRepository({ dbPath: config.DB_PATH });

  // ✅ PORTはWebサーバ起動（外側）へ
  const server = new WebServer({ port: config.PORT });

  // ✅ UseCaseへ渡すなら「値だけ」🍬
  const createTask = new CreateTaskInteractor({
    repo,
    maxTitleLength: config.TASK_TITLE_MAX_LENGTH,
  });

  return { server, createTask };
}
```

ポイントはこれ👇✨

* `DB_PATH` を **UseCaseに渡さない**（それAdapterの都合！）🧠
* UseCaseに渡すなら `maxTitleLength` みたいに **意味のある値1個**🍭
* UseCase内に `process.env` が出てきたら赤信号🚨

---

## テストが楽になる理由🧪🎉

UseCaseがConfig直読みだと、テスト前に `process.env` を整える儀式が必要になるけど…
この形なら **ただの引数**で済むよ😊

```ts
const usecase = new CreateTaskInteractor({
  repo: new FakeTaskRepository(),
  maxTitleLength: 10,
});
```

「環境の都合」が消えると、テストが気持ちよくなる〜✨🧼

---

## チェックリスト（設計監査用）✅👀

* [ ] UseCase/Entityに `process.env` / `.env` / `fs` 読み込みが無い？🚫
* [ ] Configは **起動時に一括ロード**してる？🚀
* [ ] Configは **型チェック**して、ダメなら即落ちる？🛑
* [ ] UseCaseに渡すのは **最小限の値**だけ？🍬
* [ ] DB接続文字列やAPIキーを **内側に渡してない**？🔐

---

## ミニ演習（手を動かす）📝✨

1. `.env` に `TASK_TITLE_MAX_LENGTH=5` を入れる
2. `CreateTask` でタイトル6文字を弾くようにして、ドメインエラーにする⚠️
3. テストでは `maxTitleLength: 5` を渡して同じ挙動になるのを確認🧪🎯

---

## AI相棒プロンプト（コピペ用）🤖✨

* 「`process.env` を直接読んでる箇所があれば、クリーンアーキ的にNG理由と修正案を出して」
* 「この `EnvSchema` に足りないバリデーション観点を列挙して（ポート範囲、必須、enumなど）」
* 「ConfigをUseCaseに渡しすぎてないかレビューして。渡すべき最小単位に分解して提案して」
* 「起動時にConfigが不正なら“分かりやすいエラー表示”にしたい。例を出して」

---

次の章（42）で、外部サービス（通知とか）を同じノリで **Port/Adapterで包んで注入**して完成させるよ〜📣✨

[1]: https://12factor.net/config?utm_source=chatgpt.com "Store config in the environment"
[2]: https://nodejs.org/api/environment_variables.html?utm_source=chatgpt.com "Environment Variables | Node.js v25.4.0 Documentation"
[3]: https://nodejs.org/en/blog/release/v20.6.0?utm_source=chatgpt.com "Node.js 20.6.0 (Current)"
[4]: https://www.npmjs.com/package/dotenv?utm_source=chatgpt.com "Dotenv"
[5]: https://zod.dev/api?utm_source=chatgpt.com "Defining schemas"
