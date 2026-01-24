短く言うと、第9章（フォーマット統一）を、2026年時点のTS/VS Code周辺（Prettier/EditorConfig/ESLint連携など）に合わせて、手順→例→課題→AI活用まで“教材ページ”としてまとめます。最新の設定推奨はWebで確認して反映します。


# 第9章 フォーマット統一（読みやすさの土台）🎀🧹

## ねらい🎯

* **見た目の揺れ（インデント・改行・クォートなど）をゼロにする**🧼✨
* **保存したら自動で整う状態**を作って、リファクタの差分を読みやすくする👀📉
* “整形の議論”を卒業して、**中身（設計・ロジック）に集中**できるようにする🧠💡

---

## 学ぶこと🧠✨

* フォーマッター（Prettier）で、コード見た目を自動で統一する🪄

  * Prettierは「意見のあるフォーマッター」で、解析→再出力で一貫したスタイルにします。 ([Visual Studio Marketplace][1])
* `.prettierrc` / `.prettierignore` / `.editorconfig` を用意して、チームでも同じ見た目にする📁🧷

  * Prettierは複数の設定ファイル形式に対応しています。 ([Prettier][2])
  * EditorConfigは「エディタやIDEが違ってもコーディングスタイルを揃える」ための仕組みです。 ([EditorConfig][3])
* VS Codeで「保存＝整形」にして、日々の整形作業を消す💾✨

  * VS Codeには「Format Document」などの整形機能があります。 ([Visual Studio Code][4])
* コマンドで **整形（write）** と **確認（check）** を使い分ける✅🔍

  * `--check` は「書き換えずに、整形されてるか確認する」ためのオプションです。 ([Prettier][5])

---

## まず知っておくミニ知識📌🧁

### フォーマッターとLintは別もの👭

* **フォーマッター**：見た目（空白、改行、カッコの並べ方）を揃える🎀
* **Lint**：危ない書き方・バグりやすい書き方を注意する👮‍♀️⚠️
* ここではまず **見た目の統一** に集中！次章でLintに進みやすくなるよ🚶‍♀️➡️

---

## コード例（ビフォー/アフター）🧩➡️✨

### Before 😵‍💫（見た目がガタガタ）

```ts
export  function calcTotal (items:{price:number, qty:number}[]){
let total=0
for(const it of items){
total += it.price*it.qty
}
return  total
}
```

### After 😌✨（読むのがラク）

```ts
export function calcTotal(items: { price: number; qty: number }[]) {
  let total = 0;
  for (const it of items) {
    total += it.price * it.qty;
  }
  return total;
}
```

ポイント🌸

* 余計な空白が消える🧹
* インデントが揃う📏
* たったそれだけで、差分の“意味”が見やすくなる👀✨

---

## 手順（小さく刻む）👣🧷

### 0) 今日の作戦🗺️✨

* **プロジェクトにPrettierを入れる**
* **設定ファイルを置く**
* **保存時に自動整形**
* **整形だけのコミット**で区切る💾🧷

---

### 1) Prettierを追加する📦✨

```bash
npm i -D prettier
```

---

### 2) Prettier設定ファイルを作る📝🎀

#### いちばんシンプル（`.prettierrc`）

```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "endOfLine": "lf"
}
```

メモ🧁

* `endOfLine: "lf"` は、Windowsでも改行差分が増えにくくて安心🪟➡️📉

  * Prettierは `endOfLine` オプションを持っていて、デフォルトが `lf` になっている旨が説明されています。 ([Prettier][6])

---

### 3) 整形したくないものを除外する🙅‍♀️📄

`.prettierignore`

```txt
node_modules
dist
build
coverage
*.min.*
```

---

### 4) EditorConfigで“最低限の約束”を固定する📏🧷

`.editorconfig`

```ini
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.md]
trim_trailing_whitespace = false
```

* EditorConfigは、複数エディタ間でスタイルを揃えるための仕様＆仕組みです。 ([EditorConfig][3])

---

### 5) VS Codeを「保存したら整形」にする💾🪄

#### ワークスペース設定に入れる（おすすめ）📁✨

`.vscode/settings.json`

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

* VS Codeには「Format Document」など整形機能があり、保存時整形も設定できます。 ([Visual Studio Code][4])
* 拡張機能は **`esbenp.prettier-vscode` が公式**と明記されています。 ([Visual Studio Marketplace][7])

  * 似た名前の **`Prettier.prettier-vscode` はDeprecated**（非推奨）なので避けよう⚠️ ([Visual Studio Marketplace][7])

#### すぐ整形したいときの操作（覚えておくと便利）⌨️✨

* **Format Document**：`Shift + Alt + F`（Windows）🪄

  * VS Code公式の「Formatting」説明に載っています。 ([Visual Studio Code][4])

---

### 6) コマンドで「整形」と「確認」を分ける🧪✅

`package.json` の scripts に追加するとラク🎀

```json
{
  "scripts": {
    "format": "prettier . --write",
    "format:check": "prettier . --check"
  }
}
```

* `--check` は「整形されてるか確認だけ」なので、CIや“整形漏れ検知”に向いています✅ ([Prettier][5])

---

### 7) “整形だけのコミット”を作る🧷💾

**コツはこれだけ👇**

1. 設定ファイル追加（Prettier/EditorConfig/VS Code設定）📁
2. `npm run format` で整形🪄
3. 差分を見て、**整形しか起きてない**のを確認👀
4. **整形だけ**でコミット✅💾

整形コミットは「中身を変えてない」から、レビューも安心して進むよ🌸

---

## よくあるつまづき🧯😵‍💫（すぐ直る）

### ① 保存しても整形されない💥

チェック✅

* `.vscode/settings.json` に `editor.formatOnSave: true` がある？
* `editor.defaultFormatter` が Prettier になってる？
* 他のフォーマッター拡張が同じ言語を奪ってない？（複数入れると起きがち）🎭

---

### ② 「Prettierの拡張がどれ？」問題🤔

* Marketplaceには似た名前があるけど、**公式は `esbenp.prettier-vscode`** と明記されています。 ([Visual Studio Marketplace][7])
* **Deprecated表示のものは避ける**⚠️ ([Visual Studio Marketplace][7])

---

### ③ ESLint導入後に整形が二重に走る🌀

* これは“次章あるある”！
* 解決の基本は「Prettierで整形」「ESLintは品質チェック」って役割分担すること👭
* `eslint-config-prettier` は **Prettierと衝突しやすいルールをオフ**にします。 ([GitHub][8])

---

## ミニ課題✍️🎀

### 課題A：整形だけコミットを作ろう🧷💾

1. `.prettierrc` / `.prettierignore` / `.editorconfig` / `.vscode/settings.json` を追加
2. `npm run format`
3. 差分を見て「空白・改行・クォート」しか変わってないのを確認👀
4. 整形だけコミット✅

### 課題B：整形漏れを見つけよう🔍

1. どこか1ファイルをわざと崩す（インデントぐちゃぐちゃ）😈
2. `npm run format:check` を実行
3. ちゃんと検知されるか確認✅

---

## AI活用ポイント🤖✨（お願い方＋チェック観点✅）

### 1) 設定の意味を“やさしく翻訳”してもらう📝

お願い例💬

* 「この `.prettierrc` の各項目を、初心者向けに1行ずつ説明して」
  チェック観点✅
* 説明が“見た目の話”に留まっているか（挙動を変える話を混ぜない）🧼

---

### 2) 「整形コミットとしてOK？」を判定してもらう👀🤖

お願い例💬

* 「このdiff、整形だけに見える？ロジック変化が混ざってないかチェックして」
  チェック観点✅
* 変数名・条件式・戻り値などが変わってないか
* 変更が“空白/改行/クォート/カンマ”中心か

---

### 3) “チームで揉めない設定”案を3つ出してもらう🎛️🤖

お願い例💬

* 「printWidthを80/100/120にした場合のメリット・デメリットを並べて」
  チェック観点✅
* 最終決定は **Prettierの自動整形で一貫すること**（人間が手整形しない）🎀

---

## 章末チェックリスト🧿✅

* 保存したら自動で整形される？💾🪄
* `format` と `format:check` が動く？🧪✅
* `.prettierrc` と `.editorconfig` が入ってる？📁🧷
* 整形だけのコミットを作れた？🧷💾
* 似た名前のDeprecated拡張を入れてない？⚠️ ([Visual Studio Marketplace][7])

[1]: https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode&utm_source=chatgpt.com "Prettier - Code formatter"
[2]: https://prettier.io/docs/configuration?utm_source=chatgpt.com "Configuration File"
[3]: https://editorconfig.org/?utm_source=chatgpt.com "EditorConfig"
[4]: https://code.visualstudio.com/docs/editing/codebasics?utm_source=chatgpt.com "Basic editing"
[5]: https://prettier.io/docs/cli?utm_source=chatgpt.com "CLI"
[6]: https://prettier.io/docs/options?utm_source=chatgpt.com "Options"
[7]: https://marketplace.visualstudio.com/items?itemName=Prettier.prettier-vscode "
        Prettier - Code formatter - Visual Studio Marketplace
    "
[8]: https://github.com/prettier/eslint-config-prettier?utm_source=chatgpt.com "prettier/eslint-config-prettier: Turns off all rules that ..."
