# 第10章：プロジェクト作成 🪟📦🚀

この章は「まず動く状態」を最短で作ります😊✨
あとでヘキサゴナルに育てていくために、**土台だけ**をきれいに作るよ〜🌱🔌

---

## 1) まずは環境チェック✅🔍

VS Codeのターミナル（PowerShell）で、これを打って確認するよ👇

```bash
node -v
npm -v
```

おすすめは **Node.js の Active LTS** を使うこと（2026年1月時点だと **v24 が Active LTS**、v25 は “Current”）だよ😊
「長く安定して使える版」を選ぶのがコツ✨ ([Node.js][1])

> ちなみに VS Code は 2026/1/8 に 1.108 が出てるよ（この章の手順はその辺りの最新VS CodeでもOK）🧰✨ ([Visual Studio Code][2])

---

## 2) Node.js が入ってない／バージョンを揃えたいとき🧑‍🔧✨

### A. いちばん簡単：Node公式の LTS を入れる🍀

Node公式サイトから **LTS** を入れるのが一番ラクだよ（インストール後はターミナルを開き直してね）😊
※LTSの状況は公式のリリース表で確認できるよ📌 ([Node.js][1])

### B. 複数プロジェクトで Node を切替えたい：nvm-windows🔁

複数バージョンを行ったり来たりするなら nvm-windows が便利✨（プロジェクトごとにNodeを揃えやすい） ([GitHub][3])

---

## 3) ToDoミニの「土台プロジェクト」を作る📝🍰

ここからが本番！コピペでOK👌✨

### 3-1. フォルダ作成 → npm初期化📁

```bash
mkdir todo-hex
cd todo-hex
npm init -y
```

### 3-2. TypeScript実行の最短セットを入れる⚡

今回は「コンパイルしてから実行」より、まず **TSをサクッと動かす** のを優先するよ😊
（後の章でビルドや品質設定をしっかり整える✨）

```bash
npm i -D typescript tsx @types/node
```

* `tsx`：TypeScriptを気持ちよく実行するランタイム的なやつ⚡（開発体験が軽い） ([GitHub][4])
* TypeScript自体は、2026/1時点でも公式リリースノートが更新され続けてる（今どきの型機能の前提にできる）🧠✨ ([TypeScript][5])

### 3-3. tsconfig を作る🛡️

```bash
npx tsc --init --rootDir src --outDir dist --module nodenext --target es2022 --strict
```

### 3-4. `src/main.ts` を作る✍️

```bash
mkdir src
code src/main.ts
```

中身👇（とりあえず動けばOK🎉）

```ts
console.log("Hello Hexagonal ToDo! 🔌✨");

const now = new Date();
console.log("Now:", now.toISOString());
```

### 3-5. `package.json` に scripts を足す🏃‍♀️💨

`package.json` を開いて、`"scripts"` をこんな感じにするよ👇

```json
{
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/main.ts",
    "start": "tsx src/main.ts",
    "build": "tsc -p tsconfig.json",
    "start:dist": "node dist/main.js"
  }
}
```

---

## 4) 起動して「動いた！」を確認🎉✅

```bash
npm run start
```

さらに監視モード（保存したら自動で再実行）✨

```bash
npm run dev
```

---

## 5) pnpm派の人向け（任意）🐿️✨

pnpmを使うなら、**Corepack** 経由が今どきでスッキリしやすいよ😊
Corepackは Node に同梱されるけど、**有効化が必要**なことがあるので👇 ([Node.js][6])

```bash
corepack enable
corepack enable pnpm
```

プロジェクト側で使うpnpmのバージョンを揃えたいなら、Corepackで固定もできるよ📌 ([pnpm.io][7])

---

## 6) よくある詰まりポイント集😵‍💫🧯

### ❌ `node` が見つからない

* インストール後に **ターミナルを開き直す**（超多い！）🔁
* それでもダメなら PATH が通ってない可能性

### ❌ PowerShellで `npm.ps1` が実行できない系

「スクリプト実行が無効」みたいなエラーが出ることがあるよ。
その場合は “CurrentUser” の範囲だけ緩める設定が定番（会社PCはルール優先ね🥺）⚠️

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### ❌ VS Code のターミナルが思ったシェルじゃない

VS Code は「既定プロファイル」を選べるよ✨（PowerShellを選び直すのもここ） ([Visual Studio Code][8])

---

## 7) AI拡張に投げると捗るプロンプト集🤖💖

コピペして使ってOKだよ👇✨

* 「このプロジェクトに `scripts`（dev/start/build）を追加して、`tsx` で動く最小構成にして。ESM前提で `type: module` も入れて」
* 「`tsconfig.json` を初心者が詰まらない範囲で安全寄りに整えて。今回の要件は “まず動くこと”」
* 「この章の構成で、コマンドを1本の手順にまとめて。失敗したときのチェック項目も箇条書きで」

---

## 章のゴール達成チェック🎯✅

* `npm run start` で **Hello が出る**🎉
* `npm run dev` で **watchが動く**👀✨
* `src/` と `tsconfig.json` と `package.json` が揃ってる📦

---

次の章では、VS Code側の設定を整えて「迷子にならない開発環境」にしていくよ〜🧭💖

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://code.visualstudio.com/updates?utm_source=chatgpt.com "December 2025 (version 1.108)"
[3]: https://github.com/coreybutler/nvm-windows/releases?utm_source=chatgpt.com "Releases · coreybutler/nvm-windows"
[4]: https://github.com/privatenumber/tsx?utm_source=chatgpt.com "privatenumber/tsx: ⚡️ TypeScript Execute | The easiest ..."
[5]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[6]: https://nodejs.org/download/release/v22.11.0/docs/api/corepack.html?utm_source=chatgpt.com "Corepack | Node.js v22.11.0 Documentation"
[7]: https://pnpm.io/installation?utm_source=chatgpt.com "Installation | pnpm"
[8]: https://code.visualstudio.com/docs/terminal/profiles?utm_source=chatgpt.com "Terminal Profiles"
