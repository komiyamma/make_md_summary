# 第4章：VS Codeの基本セット（拡張＋快適化）🧰✨

この章のゴールはシンプル！👇
**「保存した瞬間に、コードが自動で整って、ミスにすぐ気づける」状態**を作ります😆💖
（モジュラーモノリスは“長期戦”なので、ここで快適さを作ると後半がめっちゃ楽になります🧩✨）

---

## 1) まずは拡張機能を入れる（最小で勝つ💪✨）

VS Codeの拡張は入れすぎると逆に混乱しがち😵‍💫
なので「必須セット」＋「あると助かる」を分けます🎯

### ✅ 必須セット（この章の主役👑）

* **ESLint**（コードのルール違反を見つけて直す係🕵️‍♀️）

  * `editor.codeActionsOnSave` の `source.fixAll.eslint` に対応していて、保存時にまとめて直せます✨ ([Visual Studio Marketplace][1])
* **Prettier - Code formatter**（見た目を整える係💅）

  * 競合を防ぐために「デフォルトのフォーマッタ」に指定するのが推奨です🧠✨ ([Visual Studio Marketplace][2])

### 👍 あると助かる（快適さUP🌈）

* **EditorConfig for VS Code**（改行・インデント等の統一🧼）
* **Error Lens**（エラーが目立って気づきやすい👀💥）
* **Path Intellisense**（パス補完で迷子を減らす🧭）

> ポイント：まずは「ESLint＋Prettier」で完成にして、足りない時に追加が安全だよ☺️✨

---

## 2) “保存したら自動で整う”を作る（ここが本丸🏰✨）

VS Codeの保存時自動処理は主に2つあります👇

* **Format on Save**：フォーマッタ（Prettierなど）で整形🧽
* **Code Actions on Save**：ESLintなどで修正アクション実行🔧

`editor.codeActionsOnSave` は最近のVS Codeでは **`"explicit" / "always" / "never"`** で指定する流れが明確です（`explicit` は“手動保存したときだけ”） ([Visual Studio Code][3])

### ✅ オススメ設定（迷ったらこれでOK💯）

プロジェクト直下に `.vscode/settings.json` を作って👇を入れます（プロジェクトごとに効くので安全🧸）

```json
{
  // ① 保存時にフォーマット（Prettier）
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",

  // ② 保存時にESLintの修正（Fix）も走らせる
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },

  // ③ TypeScriptは“プロジェクトの”TypeScriptを見る（後述）
  "typescript.tsdk": "./node_modules/typescript/lib"
}
```

* Prettier をデフォルトフォーマッタにするのが推奨です🧼 ([Visual Studio Marketplace][2])
* `source.fixAll.eslint` は ESLint 拡張が対応している保存時アクションです🔧 ([Visual Studio Marketplace][1])
* `explicit/always/never` の説明はVS Code側の公式にあります📘 ([Visual Studio Code][3])

---

## 3) よくあるハマりポイント回避😵‍💫🧯（ここ読むだけで事故減る）

### 🧨 罠1：Prettierが効かない／別の拡張が勝つ

✅ 対策：**defaultFormatterをPrettierに固定**（上の設定の通り） ([Visual Studio Marketplace][2])

### 🧨 罠2：ESLintが「保存しても直らない」

✅ 対策：`editor.codeActionsOnSave` に `source.fixAll.eslint` を入れる（上の通り） ([Visual Studio Marketplace][1])

### 🧨 罠3：ESLint v9以降で設定形式（Flat Config）まわりがややこしい

ESLint v9 系では **Flat Config（`eslint.config.*`）前提の挙動**が絡んで、VS Code拡張側の期待とズレることがあります🌀
その場合、プロジェクト設定として `.vscode/settings.json` に **`eslint.useFlatConfig`** を明示すると安定することがあるよ🧩 ([GitHub][4])

例：Flat Config を使うなら👇

```json
{
  "eslint.useFlatConfig": true
}
```

例：従来の `.eslintrc` を使っていて挙動が怪しいなら👇（状況次第）

```json
{
  "eslint.useFlatConfig": false
}
```

> ここは“プロジェクトごと”に置くのが安全、という実務アドバイスもあります🧠 ([Wantedly][5])

---

## 4) TypeScriptの「VS Code内のバージョン」をプロジェクトと揃える🧠🧩

VS Codeは内部にTypeScriptを持っていて、プロジェクトのTypeScriptと違うと「型の挙動が違う😱」が起きます。
なので **ワークスペースのTypeScriptを使う**のが定番です✨

### ✅ 2ステップでOK

1. `.vscode/settings.json` にこれ（さっき入れたやつ）

```json
{
  "typescript.tsdk": "./node_modules/typescript/lib"
}
```

2. コマンドパレットで **TypeScript: Select TypeScript Version** → ワークスペース版を選ぶ
   この流れはVS Codeの公式ドキュメントにもあります📘 ([Visual Studio Code][6])

---

## 5) チーム（未来の自分👩‍💻💕）のための“おすすめ拡張”共有📦✨

`.vscode/extensions.json` を置いておくと、開いた人に「この拡張おすすめだよ」って出せます🎁

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "editorconfig.editorconfig"
  ]
}
```

---

## 6) 章末ミニ課題🧩✅（10分でOK！）

### 🎯 ミニ課題A：保存で勝手に整うのを確認しよう

1. わざとインデントぐちゃぐちゃにする😈
2. 保存（Ctrl+S）
3. **Prettierで整形される**＆**ESLintが直せるところ直す**のを確認✨

### 🎯 ミニ課題B：TSのバージョン差事故を防ぐ

1. `typescript.tsdk` を入れる
2. **TypeScript: Select TypeScript Version** で切り替える
3. 型エラー表示が安定するのを体感👀✨ ([Visual Studio Code][6])

---

## 7) AIに頼るときの“勝ちパターン”プロンプト🤖📝✨

（コピペして使ってOKだよ💖）

* 「このリポジトリは TypeScript + ESLint + Prettier を使う。VS Code の `.vscode/settings.json` を、保存時に Prettier整形＋ESLint fix が走る構成で提案して。競合しやすい点も教えて」
* 「ESLint v9 / Flat Config を使う予定。VS Code拡張側で詰まりやすい設定（`eslint.useFlatConfig` など）を整理して、プロジェクト単位のおすすめを書いて」
* 「この設定で“保存してもESLintが直らない”時に見るべきチェックリストを作って」

---

## 次章の予告👀💡

次の第5章は、ここで整えた環境を使って **AI拡張の“使い方の型”** を作ります🤖✨
「AIに任せてOK／ダメ」の線引きができると、設計学習が爆速になるよ〜🚀💖

[1]: https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint&utm_source=chatgpt.com "VS Code ESLint extension"
[2]: https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode&utm_source=chatgpt.com "Prettier - Code formatter"
[3]: https://code.visualstudio.com/updates/v1_83?utm_source=chatgpt.com "September 2023 (version 1.83)"
[4]: https://github.com/microsoft/vscode-eslint/issues/1879?utm_source=chatgpt.com "Document behavior and defaults of useFlatConfig across ..."
[5]: https://en-jp.wantedly.com/companies/wantedly/post_articles/939693?utm_source=chatgpt.com "ESLint v9 対応奮闘記 | Wantedly Engineer Blog"
[6]: https://code.visualstudio.com/docs/typescript/typescript-compiling?utm_source=chatgpt.com "Compiling TypeScript"
