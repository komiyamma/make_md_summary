## 第38章：Adapters層の依存監査（中心を汚さない）🛡️✨

### 🎯 到達目標（1文）

Adapters（Controller/Presenter/Repository/Mapper）が“便利だから”で中心（UseCases/Entities）を汚してないか、**ルール＋自動チェックで即発見できる状態**にするよ✅🧹

---

## 1) まず超ざっくり：Adaptersって何する場所？🧩

Adaptersは「翻訳係」だよ📚✨

* 外側の入力（HTTP/CLI/UIなど）→ **UseCaseが食べやすいRequestに翻訳**🍽️
* UseCaseのResponse → 外側（画面/HTTP）に**見せやすい形に翻訳**🎨
* DB/外部サービス → Portを満たす形で**つなぎこむ**🔌

✅ 逆に、Adaptersがやっちゃダメなのはこれ👇

* **ビジネスルールを決める**（＝中心の仕事）🚫
* **中心の型に外部ライブラリの都合を混ぜる**（例：SQLiteのRow型がPortを侵食）🚫
* **依存の向きを逆転させる**（UseCasesがAdaptersをimportしちゃう等）🚫

---

## 2) “中心が汚れる”あるある事故 💥😇

次のどれかが起きてたら黄色信号だよ⚠️

### 🧨事故A：Presenterが「仕様」を決め始める

* 例：画面表示のための整形を超えて「未完了は作成日が古い順に並べるのが正しい仕様！」みたいに決める
  ➡️ **それが“業務ルール”ならUseCaseへ**、ただの見た目都合ならPresenterでOK（境界の線引きが大事）🎀

### 🧨事故B：ControllerがUseCaseを飛び越えてEntityを直接いじる

* 「UseCase呼ぶのめんどい」→ `task.complete()` をControllerで直呼び
  ➡️ **中心の手続き（取得→更新→保存→レスポンス）が壊れやすい**💔

### 🧨事故C：PortやUseCaseの入出力に“外部ライブラリ型”が混ざる

* `TaskRepositoryPort.save(row: SqliteRow)` みたいなの
  ➡️ これやると、中心がDB都合に染まる🧟‍♂️

---

## 3) Adapters依存監査チェックリスト ✅🧾（コピペで使えるよ）

### 3-1. 依存（import）の監査 👀⬅️

* ✅ UseCases/Entitiesが `src/adapters/**` をimportしてない
* ✅ Entitiesが `src/usecases/**` や外部都合（HTTP/DB）をimportしてない
* ✅ Portの型が **業務語彙**で、外部ライブラリ型が出てこない
* ✅ Adaptersは「翻訳」だけで、中心のルール判断がない（if文の意味を読む！）🧠

### 3-2. 責務（ロジック）の監査 🧼

* ✅ Controllerは **受け取る→変換→UseCase呼ぶ** の3つだけ🚪
* ✅ Presenterは **Response→ViewModel** の整形だけ🎨
* ✅ Repository/Mapperは **保存/取得と変換** だけ🔄
* ✅ 例外（DB/ネットワーク）は **技術エラー**として境界で変換され、中心に漏れない⚠️➡️🚧

---

## 4) 自動化で“違反したら落とす”を作る 🤖🔧

ここからが第38章のメインだよ〜！🎉
2026の現場だと、**ESLint（Flat Config）＋ dependency-cruiser ＋ madge** の組み合わせがめっちゃ強い💪✨

---

# 4-1) ESLintで「禁止import」をガチガチにする 🧱

ESLintは今どき **Flat Config（eslint.config.*）** が基本だよ🧹
TypeScript向けの推奨セットも公式で案内されてる（typescript-eslintのGetting Started）📘✨ ([TypeScript ESLint][1])
ESLint自体も設定ファイルの仕組みを公式ドキュメントで案内してるよ📄 ([ESLint][2])

例：`eslint.config.mjs`（まずこれでOK）👇

```js
// eslint.config.mjs
// @ts-check

import eslint from "@eslint/js";
import { defineConfig } from "eslint/config";
import tseslint from "typescript-eslint";

export default defineConfig(
  eslint.configs.recommended,
  tseslint.configs.recommended,

  // ✅ Entities：中心の中心。外側を見ない！
  {
    files: ["src/entities/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["src/usecases/**", "src/adapters/**", "src/frameworks/**"],
              message: "Entitiesは外側に依存しないよ🛡️（中心のルールだけ！）",
            },
          ],
        },
      ],
    },
  },

  // ✅ UseCases：Adapters/Frameworksを見ない！（Port経由にする）
  {
    files: ["src/usecases/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["src/adapters/**", "src/frameworks/**"],
              message: "UseCases→外側依存は禁止🚫（Portで受け取ろう🔌）",
            },
          ],
        },
      ],
    },
  },

  // ✅ Adapters：ここは“翻訳係”。中心を呼ぶのはOK、でも中心の判断はしない！
  // （必要なら inbound/outbound の相互import禁止なども追加できるよ）
);
```

💡ワンポイント

* `tseslint.configs.recommended` を使う構成は公式案内に沿ってるよ📘 ([TypeScript ESLint][1])
* ESLintの設定ファイル仕様は公式ドキュメントが基準📄 ([ESLint][2])

🔎 ちなみにESLintは「TypeScriptの設定ファイル（eslint.config.ts/mts/cts）」もサポートを進めてきてるよ（公式ブログ）📰 ([ESLint][3])
（でもまずは `.mjs` で安定運用がラク✨）

---

# 4-2) dependency-cruiserで「アーキ違反」をテスト化する 🧪🚨

dependency-cruiserは **依存ルールを自分で書いて違反を検出**できるやつだよ🛡️

* `depcruise --init` で設定ファイルを作れる
* ルール例（from/toで禁止）もREADMEに載ってる📌 ([GitHub][4])

### 📦 インストール＆初期化

```bash
npm i -D dependency-cruiser
npx depcruise --init
```

### ✅ 例：クリーンアーキの“最低限”ルールを追加

`.dependency-cruiser.js` に forbidden を足すイメージ👇
（READMEのルール形をそのまま使えるよ） ([GitHub][4])

```js
// .dependency-cruiser.js （抜粋イメージ）
module.exports = {
  forbidden: [
    // UseCasesはAdaptersを見ない
    {
      name: "no-usecases-to-adapters",
      severity: "error",
      from: { path: "^src/usecases" },
      to: { path: "^src/adapters" },
    },

    // UseCasesはFrameworksも見ない
    {
      name: "no-usecases-to-frameworks",
      severity: "error",
      from: { path: "^src/usecases" },
      to: { path: "^src/frameworks" },
    },

    // Entitiesは外側を見ない（超重要）
    {
      name: "no-entities-outward",
      severity: "error",
      from: { path: "^src/entities" },
      to: { path: "^src/(usecases|adapters|frameworks)" },
    },
  ],
};
```

### ▶ 実行

```bash
npx depcruise src
```

---

# 4-3) madgeで「循環依存」をあぶり出す 🌀👻

循環依存って、設計がにごると増えがち😇
madgeは **循環依存を探す**のが得意だよ💡（npm公式にも説明あり） ([npm][5])

```bash
npx madge --circular --extensions ts,tsx src
```

---

## 5) “Adapters層”の監査ポイントをもっと具体化 💎

ここ、超大事だからもう一段かみくだくね🫶✨

### ✅ Adaptersに置いていいロジック（OK）🟢

* 変換：`HTTP body → CreateTaskRequest`
* 整形：`ListTasksResponse → TaskListViewModel`
* エラー変換：`DomainError → { status, message }`
* マッピング：`DB row ↔ Task(Entity)`

### ❌ Adaptersに置いちゃダメなロジック（NG）🔴

* 「タイトルは20文字以内が正しい」みたいな**業務ルール確定**
* 「完了できるのは◯◯の場合だけ」みたいな**状態遷移ルール確定**
* 「DBがこういう制約だから、中心の型もこうして」みたいな**外部都合の押し込み**

---

## 6) ミニ演習（10分）⌛🎒

### 🧪 わざと違反して、ツールに怒らせよう😈➡️😇

1. UseCaseからAdapterをimportしてみる（わざと！）

   * `src/usecases/CreateTaskInteractor.ts` で `src/adapters/...` をimport
2. ESLintを走らせる

```bash
npx eslint .
```

3. 「UseCases→外側依存は禁止🚫」って怒られたら成功🎉
4. 修正：**Port（interface）をUseCases側に置いて**、Adapterはそれを実装する形に戻す🔌✨

---

## 7) 提出物（成果物）📦✨

* ✅ `eslint.config.mjs`（禁止importルール入り）
* ✅ `.dependency-cruiser.js`（Clean Architecture最低限ルール入り）
* ✅ `package.json` に監査スクリプト（任意だけどあると最高）

例：

```json
{
  "scripts": {
    "lint": "eslint .",
    "lint:deps": "depcruise src",
    "lint:cycles": "madge --circular --extensions ts,tsx src"
  }
}
```

---

## 8) AI相棒🤖💬（コピペ用プロンプト）

### 🩺 Adapter診断

```text
次のファイルはAdapterです。中心（Entities/UseCases）に責務が漏れてないか診断して、
(1)怪しい行
(2)なぜNGか
(3)修正案（どの層に移すべきか）
を箇条書きで出して。
```

### 🧱 依存ルール生成（dependency-cruiser）

```text
このフォルダ構成でClean Architectureの依存ルールをdependency-cruiserのforbiddenで作って。
最低限：Entitiesは外側を見ない / UseCasesはAdaptersとFrameworksを見ない。
```

---

必要なら次は、第38章の内容に合わせて
「✅ 監査に落ちたときの“直し方パターン集”（典型10個）」も作れるよ📚✨
（“Controllerがnewしてる問題”とか、“Portに外部型が漏れてる問題”とかを、テンプレで直せるやつ💪😆）

[1]: https://typescript-eslint.io/getting-started/ "Getting Started | typescript-eslint"
[2]: https://eslint.org/docs/latest/use/configure/configuration-files "Configuration Files - ESLint - Pluggable JavaScript Linter"
[3]: https://eslint.org/blog/2025/01/eslint-v9.18.0-released/?utm_source=chatgpt.com "ESLint v9.18.0 released"
[4]: https://github.com/sverweij/dependency-cruiser "GitHub - sverweij/dependency-cruiser: Validate and visualize dependencies. Your rules. JavaScript, TypeScript, CoffeeScript. ES6, CommonJS, AMD."
[5]: https://www.npmjs.com/package/madge?utm_source=chatgpt.com "madge"
