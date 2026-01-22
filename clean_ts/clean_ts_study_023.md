# 第23章：UseCases層の依存監査（外側参照ゼロ）🛡️🔍✨

この章でできるようになること👇😊

* UseCases が **Entities と Ports 以外を import してたら即わかる**ようにする💡
* 目視じゃなくて **ツールで自動チェック**して、壊れたら止める🚨
* 「うっかり外側を触っちゃった🥲」を **最短で直す型**を身につける🧹✨

（いま安定版の TypeScript は 5.9.3（5.9系）で、ESLint は v10 RC が出てる流れだよ〜🧩✨） ([GitHub][1])
（Node は v24 が Active LTS、v25 が Current だよ🟩） ([Node.js][2])

---

## 1) 依存ルールを“1枚の表”に固定しよっ🧠📌

まずは「何がOKで何がNGか」を迷わないようにするよ😊✨

| 置き場          | importしてOK                            | importしちゃダメ                                                      |
| ------------ | ------------------------------------- | ---------------------------------------------------------------- |
| **Entities** | Entities（自分の中）                        | UseCases / Adapters / Frameworks / 外部ライブラリ直呼び（基本NG）❌             |
| **Ports**    | Entities / Ports                      | UseCases / Adapters / Frameworks（できれば）❌                          |
| **UseCases** | **Entities / Ports / UseCases（同層内）**✅ | **Adapters / Frameworks / UI / DBクライアント / dotenv / express など**❌ |
| Adapters     | Entities / Ports / UseCases           | Frameworks の内部実装を内側に漏らすのは注意⚠️                                    |
| Frameworks   | なんでも（外側）                              | —                                                                |

ここがこの章の“合格ライン”だよ🎯✨
UseCases で **外側を 1回でも import したらアウト**にする💥

---

## 2) あるある破壊パターン集（超重要）🥲🧨

### ❌ 破壊パターンA：UseCaseがDBクライアントを直に呼ぶ

* `import { db } from "...sqlite..."`
* `import { PrismaClient } from "@prisma/client"`
  → それ、Frameworks & Drivers の仕事〜！😵‍💫

✅直し方：UseCases は **TaskRepository Port** にだけ話す🔌✨

### ❌ 破壊パターンB：UseCaseがWebフレームワークに寄りかかる

* `import type { Request } from "express"`
* `import { Hono } from "hono"`
  → HTTP の言葉は外側に置こうね🚧💕

✅直し方：Controller（Inbound Adapter）で Request を **Requestモデル**に変換📦

### ❌ 破壊パターンC：UseCaseが `process.env` / `dotenv` を見る

→ 設定は外側で読むのが鉄則🧾🌍

✅直し方：必要な値だけ引数で渡す or Config Port にする✨

---

## 3) 依存監査は「目視→Lint→依存解析」の3段階が最強💪🧪✨

おすすめは **Lintで毎回自動チェック**（VS Codeで赤線が出るやつ）→ 仕上げに dependency-cruiser で全体監査、って流れ😊

---

# 4) まずはESLintで「UseCasesから外側import禁止」🚫📦✨

ESLintのルールで「このフォルダから、あのフォルダを import したらダメ」を固定するよ〜！
候補は2つ👇

* シンプルに禁止する：ESLintコアの `no-restricted-imports`（静的importだけ対象） ([ESLint][3])
* フォルダ境界で禁止する：`eslint-plugin-import` の `import/no-restricted-paths` ([GitHub][4])

ここでは **フォルダ境界に強い** `import/no-restricted-paths` を使うね😊✨

## 4-1) インストール（npm）📦✨

（TypeScript×ESLintは `typescript-eslint` が定番だよ🧩） ([npm][5])

```bash
npm i -D eslint typescript-eslint eslint-plugin-import eslint-import-resolver-typescript
```

## 4-2) 例：eslint.config.js（Flat Config）🧷✨

UseCases が `src/adapters` と `src/frameworks` を import したらアウトにするよ🚫

```js
// eslint.config.js
import importPlugin from "eslint-plugin-import";
import tseslint from "typescript-eslint";

export default [
  ...tseslint.configs.recommended,
  {
    files: ["src/**/*.ts"],
    plugins: {
      import: importPlugin,
    },
    settings: {
      "import/resolver": {
        typescript: true,
      },
    },
    rules: {
      // ✅ UseCases -> Adapters/Frameworks を禁止（フォルダ境界）
      "import/no-restricted-paths": [
        "error",
        {
          zones: [
            {
              target: "./src/usecases",
              from: "./src/adapters",
              message:
                "UseCasesはAdaptersをimportしないよ🚫（Port経由にしよ🧩）",
            },
            {
              target: "./src/usecases",
              from: "./src/frameworks",
              message:
                "UseCasesはFrameworksをimportしないよ🚫（Driver詳細は外側へ🌍）",
            },
            {
              target: "./src/usecases",
              from: "./src/ui",
              message:
                "UseCasesはUIをimportしないよ🚫（Controller/Presenterで変換してね🎨）",
            },
          ],
        },
      ],

      // おまけ：うっかり禁止モジュールを直importしたら止める（例）
      // "no-restricted-imports": ["error", { patterns: ["dotenv", "express"] }],
    },
  },
];
```

`import/no-restricted-paths` は「target（監視される側）」「from（禁止したい側）」でゾーンを作って守るルールだよ🧼✨ ([GitHub][4])

---

## 4-3) VS Codeで“赤線即出し”にする👀🚨

* `npm run lint` で止まる
* エディタ上でも即エラー表示✨

package.json に追加しよ😊

```json
{
  "scripts": {
    "lint": "eslint ."
  }
}
```

---

# 5) もっと強くする：境界専用の eslint-plugin-boundaries 🧱✨

「層」を“名前付き”で管理したいなら、これが超わかりやすい〜！
境界を定義して、層同士の許可関係をルール化できるよ🧸💘 ([GitHub][6])

（この章の必須じゃないけど、将来の拡張でめちゃ効く🧠✨）

---

# 6) 仕上げ：dependency-cruiserで“全体の依存”を監査＆可視化🗺️🧨✨

dependency-cruiser は「依存を解析して、ルール違反をレポート」できる道具だよ📣
JS/TSの依存を **ルールで検証**できて、必要なら **グラフ出力**もできる🖼️ ([GitHub][7])

## 6-1) インストール📦

```bash
npm i -D dependency-cruiser
```

## 6-2) 最小ルール例（UseCasesから外側禁止）🚫

```js
// .dependency-cruiser.cjs
module.exports = {
  forbidden: [
    {
      name: "usecases-no-adapters",
      comment: "UseCasesはAdaptersを参照しない🚫",
      from: { path: "^src/usecases" },
      to: { path: "^src/adapters" },
    },
    {
      name: "usecases-no-frameworks",
      comment: "UseCasesはFrameworksを参照しない🚫",
      from: { path: "^src/usecases" },
      to: { path: "^src/frameworks" },
    },
    {
      name: "usecases-no-ui",
      comment: "UseCasesはUIを参照しない🚫",
      from: { path: "^src/usecases" },
      to: { path: "^src/ui" },
    },
  ],
};
```

## 6-3) 実行コマンド🧪

```bash
npx depcruise --config .dependency-cruiser.cjs src
```

（ここまでやると「人の注意力」じゃなく「仕組み」で守れるよ〜🥳✨）

---

## 7) “違反したとき”の直し方テンプレ🧯🧼

UseCasesで外側を触ってたら、だいたい直し方は3択だよ😊✨

1. **Portを生やす**（能力として抽象化）🔌
2. 外側の詳細を **Adapterに移す**（UseCaseはPortだけ呼ぶ）🧩
3. その情報、そもそも **UseCaseの責務じゃない** → Controller/Presenterへ🚪🎨

---

## 8) ミニ演習（5分）⏱️🧪✨

1. わざと UseCase に `src/frameworks/db` を import してみる😈
2. `npm run lint`（または depcruise）で怒られるのを見る👀💥
3. `TaskRepository` Port を経由する形に直す🔌✨
4. もう一回 lint → 通ったら勝ち🏆🎉

---

## 9) 理解チェック問題（1問）✅📝

**Q. UseCases が `express` の `Request` 型だけを `import type` するのはアリ？ナシ？理由も一言で！** 🧠💬

（目安：この講座では基本“ナシ”寄りにして、HTTP語彙は外に閉じ込めるのがおすすめだよ🚧💕）

---

## 10) 提出物（成果物）📦✨

* `eslint.config.js` に **UseCases→Adapters/Frameworks禁止**が入ってる✅
* `.dependency-cruiser.cjs`（任意だけど超良い👏）
* “違反例を直したコミット”が1つある🧹✨

---

## 11) AI相棒プロンプト（コピペ用）🤖💖

* 「`src/usecases` が `src/adapters` と `src/frameworks` を import できない ESLint 設定（flat config）を作って。コメントも付けて」
* 「このUseCaseが直接触ってる外側依存を列挙して、Port化するならどんな interface が良いか提案して」
* 「dependency-cruiser のルールで “UseCasesはEntitiesとPorts以外参照禁止” を表現して」

---

必要なら次は、この章で作った監査を **GitHub ActionsでPR時に自動で落とす**ところまで一気に繋げるよ〜😆✨

[1]: https://github.com/microsoft/typescript/releases?utm_source=chatgpt.com "Releases · microsoft/TypeScript"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://eslint.org/docs/latest/rules/no-restricted-imports?utm_source=chatgpt.com "no-restricted-imports - ESLint - Pluggable JavaScript Linter"
[4]: https://github.com/import-js/eslint-plugin-import/blob/main/docs/rules/no-restricted-paths.md?utm_source=chatgpt.com "eslint-plugin-import/docs/rules/no-restricted-paths.md at main"
[5]: https://www.npmjs.com/package/typescript-eslint?utm_source=chatgpt.com "typescript-eslint"
[6]: https://github.com/javierbrea/eslint-plugin-boundaries?utm_source=chatgpt.com "javierbrea/eslint-plugin-boundaries"
[7]: https://github.com/sverweij/dependency-cruiser?utm_source=chatgpt.com "sverweij/dependency-cruiser: Validate and visualize ..."
