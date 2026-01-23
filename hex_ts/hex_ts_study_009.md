## 第9章 今回の題材を決める（ToDoミニ）📝🍰

（ここから「実作業」に入るよ〜！😊💻✨）

---

### 9.1 なんで “ToDoミニ” が題材にちょうどいいの？🎯💕

ヘキサゴナル（Ports & Adapters）を体験するには、題材が **小さくて、あとから育てられる** のがいちばん良いのね🌱✨
ToDoはまさにそれ！

**ToDoが強い理由💪✨**

* ルールが作れる（＝ドメインが育つ）🧠💖
  例：タイトル空NG、完了の二重適用NG…など
* 入口（CLI→HTTP）を差し替えても“中心”は変わらないを体験できる🔁😆
* DBやファイル保存に差し替えるのも分かりやすい💾📄
* テストが書きやすい（中心だけなら爆速！）🧪⚡

---

### 9.2 今日作る “ToDoミニ” の範囲を決めよう🧁📌

まずは **機能を3つだけ** に絞るよ〜（ここ大事！）✂️✨

**機能（最小セット）✅**

1. 追加（Add）➕📝
2. 一覧（List）📋👀
3. 完了（Complete）✅🎉

これだけで「ユースケース」「状態」「永続化」「差し替え」が全部練習できるのが嬉しいポイントだよ😊💕

---

### 9.3 “ルール” を先に決めるのがコツだよ🛡️✨

ToDoアプリって、ただのCRUDに見えるけど…
**ルールを入れると一気に“設計の練習”になる**の😊💖

今回のミニアプリのルールはこんな感じにしよう👇

**ルール案（ドメインの芯）🧠🧷**

* タイトルは空文字ダメ🙅‍♀️（空白だけもダメ）
* タイトルは前後の空白をトリムしてから扱う✂️
* 完了は二重適用できない（同じToDoを2回完了にしない）🚫✅✅
* IDは必ず存在する（作るときに付く）🆔✨

> この「完了の二重適用禁止」って、実は **冪等性（idempotency）** の入り口にもなるよ〜🚪✨
> （のちの章で“APIの設計”にも効いてくるやつ！）

---

### 9.4 まず “言葉” を揃えよう📚💕（地味に最重要！）

設計が混乱する一番の原因って、じつは「言葉がブレること」なんだよね😵‍💫💥
なのでこの章でミニ辞書を固定しちゃう📌✨

**このアプリの用語🗂️**

* **Todo**：やること1件（id / title / completed）
* **title**：表示する文字列（空NG）
* **completed**：完了状態（true/false）
* **completeする**：未完了 → 完了にする操作（2回目はエラー）

---

### 9.5 ユースケースの “入口” をまだ決めない理由💖（I/O後回し！）

ここがヘキサゴナルの気持ちよさの核心だよ〜😊✨

**今はこう考える：**

* 入口（CLI / HTTP / 画面）は “あとで何でも付け替えられる” 🚪🔁
* だから先に作るべきは **中心（ルール＆ユースケース）** 🧠🛡️
* 入口や保存先は、中心が決まってから “差し込み” すればOK🔌🧩

**I/O後回しのメリット🎁✨**

* 「どのUIにする？」で迷って止まらない🚫🌀
* テストが最短で書ける🧪⚡（中心だけなら外部依存ゼロ！）
* 仕様変更（たとえばWeb化）しても中心が壊れにくい🔧💕

---

### 9.6 仕様を “3つのカード” にして固定しよう🃏✨

この章の成果物は「コード」じゃなくて、**超ミニ仕様書（カード）** にしよう😊📝
（これが次章以降の設計の地図になるよ🗺️✨）

#### 🃏カード1：AddTodo（追加）➕

* 入力：title（文字列）
* 成功：新しいTodoができる（idが付く）
* 失敗：titleが空（または空白だけ）ならエラー

#### 🃏カード2：ListTodos（一覧）📋

* 入力：なし（まずは全部返す）
* 成功：Todoの配列（id/title/completed）
* 並び順：とりあえず追加順でOK（あとで変えられる）

#### 🃏カード3：CompleteTodo（完了）✅

* 入力：id
* 成功：completedがtrueになる
* 失敗：

  * 対象が無い → エラー
  * すでに完了 → エラー（ルール違反）

---

### 9.7 そのまま貼れる「README用ミニ仕様」📝🎀

次の章でプロジェクト作るとき、最初にREADMEに貼ると迷子にならないよ😊✨
（このままコピペOK！）

```text
# Todoミニ（Hexagonal体験用）

## 機能
- AddTodo: タイトルを指定してTodoを追加する
- ListTodos: Todoの一覧を取得する
- CompleteTodo: 指定したTodoを完了にする

## ルール（ドメイン）
- titleは空文字/空白だけ禁止（trim後に判定）
- 完了は二重適用禁止（完了済みにもう一度Completeしない）
- Todoは必ずidを持つ

## 期待するエラー
- ValidationError: titleが不正
- NotFoundError: idが見つからない
- DomainError: 完了二重適用などルール違反
```

---

### 9.8 AI拡張の “安全な使い方” だけ先に決めよ🤖🧠✨

AIはめっちゃ便利だけど、**この章でAIに任せていいのは「文章化」まで**が安全だよ⚠️😊
「何を作るか」「ルールは何か」は、あなたの頭で決めるのが勝ち🏆✨

**おすすめプロンプト（そのまま使ってOK）📝🤖**

* 「上の仕様をGiven-When-Then形式の受け入れ条件にして」
* 「エラーケースを漏れなく列挙して」
* 「用語集を短く整理して」

---

### 9.9 2026年の“いま”の道具メモ🧰✨（安全運用の小ネタ付き）

* Nodeは **v24系がLTS** で、2026-01-13に **24.13.0（セキュリティリリース）** が出てるよ🔐✨ ([Node.js][1])
* npmは **11.8.0** が最新（2026-01-21公開）だよ📦🚀 ([NPM][2])
* TypeScriptは npm上だと **5.9.3** が最新扱い（直近の安定ライン）🟦✨ ([NPM][3])
* TypeScript公式は「6.0は5.9→7.0の橋渡し」と説明してるよ🌉 ([Microsoft for Developers][4])
* VS Codeは「1.108が利用可能」と案内されてて、Updatesページで追えるよ🧩✨ ([Visual Studio Code][5])
* ついでに注意⚠️：最近は“怪しいリポジトリを開かせる攻撃”も話題になってるから、**知らないrepoは信頼（Trust）する前に中身チェック**が安心だよ🕵️‍♀️🔍 ([TechRadar][6])

---

### 9.10 まとめ：この章でできたこと🎁💖

* 題材を “ToDoミニ” に固定した📝🍰
* 機能を3つに絞った（Add / List / Complete）✅
* ルール（中心の芯）を先に決めた🛡️✨
* READMEに貼れるミニ仕様まで用意した📌🎀

次の章から、いよいよプロジェクト作って「動く！」まで持っていくよ〜🚀😊

[1]: https://nodejs.org/en/blog/release/v24.13.0?utm_source=chatgpt.com "Node.js 24.13.0 (LTS)"
[2]: https://www.npmjs.com/package/npm?activeTab=versions&utm_source=chatgpt.com "11.8.0"
[3]: https://www.npmjs.com/package/typescript?activeTab=versions&utm_source=chatgpt.com "typescript"
[4]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[5]: https://code.visualstudio.com/updates/v1_109?utm_source=chatgpt.com "January 2026 Insiders (version 1.109)"
[6]: https://www.techradar.com/pro/security/north-korean-hackers-target-microsoft-virtual-studio-code?utm_source=chatgpt.com "North Korean hackers target Microsoft Virtual Studio Code"
