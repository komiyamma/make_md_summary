本日時点のGit/VS Code/AI拡張の最新事情を軽くリサーチしてから、「第6章（Git超基本①）」をTypeScript学習者向けに、ビフォー/アフター例・手順・課題・AI活用まで丸ごと教材ページとして作ります。


## 第6章 Gitの超基本①（コミット＝セーブ）💾🧷

### ねらい🎯

* **「戻れる安心感」**を手に入れる（コミット＝セーブポイント🎮みたいなもの）💾✨
* まずは最低限の4つだけできるようにする👉 **add / commit / log / diff** 👣
* 「壊さずに直す」ための、毎回の小さな手順が身につく🛟✅

---

### 今日のゴール🎁

この章の最後に、こんな状態になってたらOKだよ〜！🌸

* 変更したら **差分(diff)を見て**👀
* 必要なものだけ **ステージ(add)して**🧺
* **コミット(commit)してセーブ**💾
* **履歴(log)を見てニヤける**😏✨

---

## まずはコレだけ！Gitの3つの場所📦🧺🗃️

Gitは「箱」が3つあると思うと分かりやすいよ〜！🧠✨

1. **作業中（Working Tree）**📝

* ファイルを編集してる状態（まだセーブしてない変更）

2. **ステージ（Staging Area）**🧺

* 「この変更をセーブに入れるよ！」って選んだ変更だけ置く場所

3. **コミット履歴（Repository）**🗃️

* セーブデータ置き場（コミットが積み上がる）💾💾💾

イメージ図👇

```text
編集した！✍️ →（作業中）→ add で選ぶ🧺 →（ステージ）→ commit で保存💾 →（履歴）📚
```

---

## VS Codeでやる場所🧑‍💻🧭

* 左のメニューの **ソース管理（Source Control）** アイコン（枝分かれっぽいマーク）を開く🌿
* そこに「変更」「ステージ済み変更」「コミット入力欄」がまとまってるよ✅
* 最近のVS Codeでは、**コミットメッセージをエディタで書く時の操作ボタンが見つけやすく改善**されてるよ📝✨ ([Visual Studio Code][1])

---

## 最小コマンドセット（これだけで戦える）💪💻

VS Code操作がメインでも、**意味を理解するため**にコマンドも最小だけ覚えよ〜🙌

```bash
git status        # 今どうなってる？（最重要）👀
git diff          # 何が変わった？（ステージ前）🧩
git add .         # 変更を全部ステージへ🧺（最初はこれでOK）
git commit -m "..."  # セーブ💾
git log --oneline --decorate  # セーブ履歴を短く見る📚
git diff --staged # 何をセーブに入れる？（ステージ後）🔍
```

> ✅コツ：困ったらまず `git status` だけ打てば、次に何すればいいかだいたい書いてあるよ👀✨

---

# ハンズオン：3回コミットして差分を見る👀💾💾💾

## 0) 準備（状態確認）🧰

ターミナルを開いて👇

```bash
git status
```

* `On branch main` とか出たらOK🌿
* もし「not a git repository」って出たら、どこか別フォルダにいる可能性大！📁💦（プロジェクトのルートへ移動しよ〜）

---

## 1) 変更①：1行だけ変えてコミット（超ミニセーブ）🧷

例として `src/greet.ts` を用意したことにするね👇（すでにあってもOK）

```ts
export function greet(name: string) {
  return "Hello, " + name;
}
```

### ✅1行だけ変える

`"Hello, "` をテンプレート文字列にする（見やすくするだけ）✨

**After**👇

```ts
export function greet(name: string) {
  return `Hello, ${name}`;
}
```

### 差分を見る👀

```bash
git diff
```

### ステージしてコミット💾

```bash
git add .
git commit -m "refactor: use template string in greet"
```

### 履歴を見る📚

```bash
git log --oneline --decorate -5
```

---

## 2) 変更②：小さな関数を足してコミット（意味が伝わるセーブ）➕💾

`src/greet.ts` に「空文字を弾く」だけ追加してみるよ〜🚦

**Before**👇

```ts
export function greet(name: string) {
  return `Hello, ${name}`;
}
```

**After**👇

```ts
function normalizeName(name: string) {
  return name.trim();
}

export function greet(name: string) {
  const normalized = normalizeName(name);
  return normalized ? `Hello, ${normalized}` : "Hello";
}
```

### 差分確認👀

```bash
git diff
```

### ステージ→コミット🧺💾

```bash
git add .
git commit -m "refactor: add normalizeName and handle blank"
```

---

## 3) 変更③：型・意図の改善をコミット（TypeScriptっぽい）🧷✨💾

「返り値のパターンが増えた」みたいな時、軽く整理することあるよね🌸
ここでは例として、返り値の型を明示して安心感UP（超小さめ改善）👇

**After**👇

```ts
function normalizeName(name: string): string {
  return name.trim();
}

export function greet(name: string): string {
  const normalized = normalizeName(name);
  return normalized ? `Hello, ${normalized}` : "Hello";
}
```

### ステージ→コミット💾

```bash
git add .
git commit -m "chore: add explicit return types in greet module"
```

---

## VS Codeでも「差分」と「履歴」を見る👀📚

* **差分(diff)**：ソース管理でファイルをクリック→左右に差分が出る✨
* **履歴(log)**：コミット一覧（グラフ）で流れを見れる（最近の更新でもSource Controlまわりの改善が継続してるよ）🧭✨ ([Visual Studio Code][1])

---

# よくある事故あるある😇🧨（そして回避）

## あるある①：コミットしたつもりが、入ってない💦

* 原因：**addし忘れ**🧺❌
* 回避：コミット前にこれ👇

```bash
git diff --staged
```

## あるある②：関係ない変更まで混ざる🌀

* 回避：**変更を小さく刻む👣**

  * 「命名だけ」「整形だけ」「ロジックだけ」みたいに分けると最強✨

## あるある③：コミットメッセージが「update」だけ😇

* 回避：「何をしたか」が1秒で分かる文にする✍️

  * ✅ `refactor: extract normalizeName`
  * ✅ `fix: handle blank name in greet`

---

# コミットメッセージのミニ型（これで困らない）📝✨

迷ったらこの形でOKだよ〜🌷

* `refactor: ～`（動作は変えずに内部改善）🧹
* `fix: ～`（バグ修正）🩹
* `chore: ～`（雑務・設定・型注釈など）🧰

> VS Code側でもコミットメッセージ入力の体験が改善されてきてるので、エディタ入力も使いやすいよ📝✨ ([Visual Studio Code][1])

---

# AI活用ポイント🤖✅（コミット文の添削）

AIは「メッセージ案を出す係」にすると超便利だよ〜！🧁✨
（でも**最終チェックはdiffを見る👀**が絶対ルール🛟）

## お願いテンプレ（そのままコピペOK）📋

```text
次の変更差分の内容から、コミットメッセージ案を3つください。
条件：
- 1行で短く
- 何をしたかが分かる
- refactor/fix/chore のどれかで始める
- 変更が混ざってたら「分けた方がいい」も教えて

差分の要約：
（ここに git diff の内容 or 変更点を貼る）
```

## CodexみたいなIDE拡張を使う時の注意⚠️🪟

CodexはVS Code拡張として使えて、エディタの文脈で提案を出してくれるよ🤖🧑‍💻 ([Visual Studio Marketplace][2])
ただし **Windowsは“実験的”扱いで、WSL環境が推奨**になってる点は知っておくと安心だよ🪟➡️🐧 ([OpenAI Developers][3])

---

# ミニ課題✍️🌸（提出物なしでOK）

## やること✅

1. 1行だけ変えてコミット💾
2. もう1回、小さな改善をしてコミット💾
3. さらにもう1回、型 or 読みやすさ改善でコミット💾
4. 最後にこれを実行して、履歴と差分を眺める👀✨

```bash
git log --oneline --decorate -10
```

## チェックリスト🧿✨

* `git status` がキレイ（変更なし）になってる？✅
* コミットが3つ積まれてる？💾💾💾
* 各コミットのメッセージが「何したか」分かる？📝
* `git diff` を見てからコミットできた？👀

---

### まとめ🌼

* **コミット＝セーブ**💾（戻れるから怖くない）
* 毎回やるのはこれだけ👇

  * **diffで確認👀 → addで選ぶ🧺 → commitで保存💾 → logで履歴📚**
* 「小さく刻む👣」が、リファクタの安全運転そのものだよ〜🛟✨

[1]: https://code.visualstudio.com/updates "December 2025 (version 1.108)"
[2]: https://marketplace.visualstudio.com/items?itemName=openai.chatgpt "
        Codex – OpenAI’s coding agent - Visual Studio Marketplace
    "
[3]: https://developers.openai.com/codex/ide/ "Codex IDE extension"
