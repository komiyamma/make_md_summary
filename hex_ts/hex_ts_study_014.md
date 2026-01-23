# 第14章：品質の土台（Lint / Format / Test）🧹🧪✨

## この章のゴール🎯

* **コードの見た目**を自動でそろえられる（Format）✨
* **バグっぽい書き方**を早めに止められる（Lint）🚨
* **壊してないか**を秒速で確認できる（Test）🧪
* さらに、`npm run check` みたいな“安心ボタン”を作る🔘💕

---

## まず結論：2026の鉄板3点セット🧰✨

* **ESLint**：Lint担当（今の安定は v9 系。v10 はRCが出てる）🕵️‍♀️ ([ESLint][1])
* **Prettier**：Format担当（3.8 が 2026/01/14 に出てるよ）🎀 ([Prettier][2])
* **Vitest**：Test担当（v4 移行が本格化）⚡

TypeScript自体は、現時点の最新安定が **5.9.3**（GitHubのrelease tag基準）だよ📌
（TS 5.9系のドキュメント更新も 2026/01/21 で動いてるのが確認できる✨） ([GitHub][3])

---

## 14.1 「機械に任せる」と何が嬉しいの？🤖💖

* **PRの差分が小さくなる**（見た目の差分が消える）👀✨
* **“うっかり”を先に怒ってくれる**（未使用変数、型の取り違え…）😵‍💫➡️😌
* **怖くなく直せる**（テストが盾🛡️）
* **AIの提案が安定する**（フォーマットが一貫してると、修正の精度が上がる）🤝✨

---

## 14.2 セットアップ手順（この通りでOK）🚀🪟

### ✅ Step 1：必要パッケージを入れる📦

PowerShell でもOKだよ🎶

```bash
npm i -D eslint @eslint/js typescript typescript-eslint prettier vitest @vitest/coverage-v8
```

---

### ✅ Step 2：ESLint（Lint）を設定する🕵️‍♀️✨

ESLint v9 以降の基本は **Flat Config**（`eslint.config.*`）だよ📌
`eslint.config.mjs` をプロジェクト直下に作ってね📝

```js
// eslint.config.mjs
import eslint from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    ignores: ["dist/**", "coverage/**", "node_modules/**"],
  },
  {
    rules: {
      // 初心者でも効き目が大きい＆うるさすぎないライン✨
      "@typescript-eslint/no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
    },
  }
);
```

この書き方（`tseslint.config(...)` と `configs.recommended`）は typescript-eslint 側の “Flat Config” 推奨スタイルだよ🧩 ([typescript-eslint.io][4])

---

### ✅ Step 3：Prettier（Format）を設定する🎀✨

`.prettierrc.json` を作るよ〜（シンプルでOK）😊

```json
{
  "printWidth": 100,
  "singleQuote": true,
  "semi": true
}
```

ついでに `.prettierignore` も置いとくと気持ちいい🧼

```txt
dist
coverage
node_modules
```

---

### ✅ Step 4：Vitest（Test）を設定する🧪⚡

`vitest.config.ts` を作るよ〜！

```ts
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      include: ["src/**/*.ts"]
    }
  }
});
```

Vitestの設定は公式ドキュメントの `defineConfig` 形式が基本だよ📌
（v4でカバレッジまわりの挙動が変わる話もあるから、`include` を明示しておくのが安心✨）

---

### ✅ Step 5：動作確認用のミニコードを置く🍰

`src/sum.ts`

```ts
export const sum = (a: number, b: number) => a + b;
```

`src/sum.test.ts`

```ts
import { describe, it, expect } from "vitest";
import { sum } from "./sum";

describe("sum", () => {
  it("adds numbers", () => {
    expect(sum(1, 2)).toBe(3);
  });
});
```

---

### ✅ Step 6：npm scripts を整える🔧✨

`package.json` の `scripts` をこうしてね👇

```json
{
  "scripts": {
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "format": "prettier . --write",
    "format:check": "prettier . --check",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "check": "npm run format:check && npm run lint && npm run test"
  }
}
```

ここまでできたら、まずはこれ叩いてみてね🎉

```bash
npm run check
```

---

## 14.3 VS Code を“気持ちよく”する設定🧠✨

拡張機能は **ESLint** と **Prettier** を入れて、`.vscode/settings.json` を作るのがおすすめ💕

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "eslint.useFlatConfig": true
}
```

### もし「Prettierがフォーマッタに出てこない😭」ってなったら…

Prettier拡張の一部バージョンで「フォーマッタとして選べなくなる」系の不具合報告が出てるよ💦（例：12.1.0 など） ([GitHub][5])
そのときは一旦、拡張機能を**ひとつ前の安定版に戻す**か、CLI（`npm run format`）で回避すると落ち着く👍✨

---

## 14.4 ⚠️【超重要】Windows向け：依存パッケージの事故を避ける🛡️

過去に **eslint-config-prettier / eslint-plugin-prettier** などがサプライチェーン攻撃で悪性コードを含んだ件があるよ（Windowsでの実行に絡む内容）😱 ([GitHub][6])

今回の章の構成は、**ESLintとPrettierを“役割分担”して、ESLint側にPrettier連携プラグインを必須にしない**ので安全寄り🍀
もし将来それらを入れるなら、影響バージョンを避けてね（例：`eslint-config-prettier` は 10.1.6〜10.1.7 が影響、修正版あり）📌 ([GitHub][6])

確認コマンド例👇

```bash
npm ls eslint-config-prettier eslint-plugin-prettier
```

---

## 14.5 AI拡張に頼むと強いところ🤖✨（丸投げNGゾーンも）

### 👍頼ってOK

* `eslint.config.mjs` の“たたき台”生成
* テストケースの追加案（境界値、異常系）🧪
* 命名の相談（`sum` → もう少し意図が出る名前…とか）📝

### ⚠️丸投げしない

* 「どのルールを採用するか」の最終判断（チームの快適さに直結）😌
* “怒られすぎて辛い設定”にしない調整（ここが学びどころ💡）

コピペで使える質問テンプレも置いとくね👇

* 「このESLint設定、初心者が辛くならない程度に“バグ検出寄り”で整えて」
* 「この章の目的（見た目統一/事故防止/テスト）に対して、過剰なルールがあったら指摘して」
* 「formatとlintの責務が混ざってないかチェックして」✅

---

## 14.6 ミニ課題📝🎀

1. わざと `src/sum.ts` に未使用変数を作る（例：`const x = 1;`）😈
2. `npm run lint` で警告が出るのを確認👀
3. `npm run lint:fix` で直るもの／直らないものを観察🔍
4. 最後に `npm run check` で“安心ボタン”が機能するのを確認🎉

---

次の章では、この“品質の土台”の上に **迷子にならないフォルダ構成**を固定して、ヘキサゴナルの形が一気に見やすくなるよ📁🧭✨

[1]: https://eslint.org/blog/2026/01/eslint-v10.0.0-rc.0-released/ "ESLint v10.0.0-rc.0 released - ESLint - Pluggable JavaScript Linter"
[2]: https://prettier.io/blog/2026/01/14/3.8.0 "Prettier 3.8: Support for Angular v21.1 · Prettier"
[3]: https://github.com/prettier/prettier-vscode/issues/3908 "No longer respects editor.defaultFormatter and editor.formatOnSave · Issue #3908 · prettier/prettier-vscode · GitHub"
[4]: https://typescript-eslint.io/packages/typescript-eslint "typescript-eslint | typescript-eslint"
[5]: https://github.com/prettier/prettier-vscode/issues/3906 "No longer eligible as formatter for many types of files · Issue #3906 · prettier/prettier-vscode · GitHub"
[6]: https://github.com/advisories/GHSA-f29h-pxvx-f335 "eslint-config-prettier, eslint-plugin-prettier, synckit, @pkgr/core, napi-postinstall have embedded malicious code · CVE-2025-54313 · GitHub Advisory Database · GitHub"
