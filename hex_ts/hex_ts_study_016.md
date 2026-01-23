# 第16章 ドメイン入門①：ドメイン＝ルール置き場 🏠📌✨

この章はね、「Todoアプリの“法律”をどこに置くか？」を体で覚える回だよ〜😊💖
ドメインは **データ置き場じゃなくて、ルール置き場** です🛡️✨

---

## 0) 2026の前提メモ（ちょい最新）🗓️✨

いまのTypeScriptは **5.9系** が出ていて、`tsc --init` の生成内容も「最初からそこそこ良い感じ」になってるよ（`strict: true` などが最初から入りやすい）✨ ([Microsoft for Developers][1])
Node.jsは **v24がActive LTS**、v22はMaintenance LTS…みたいに世代が進んでるので、なるべくLTSを使うのが安全だよ🧯 ([Node.js][2])
（あと、TypeScriptは将来的に“ネイティブ化”で爆速化する流れも進行中👀） ([Microsoft Developer][3])

---

## 1) ドメインってなに？🧠💡

**ドメイン＝アプリの「ルール」と「意味」** を置く場所だよ😊✨

Todoでいうと…

* 「タイトルが空なら作れない」🚫
* 「完了済みを、もう一回完了にできない」🚫
* 「一覧に出すときはこの形にしたい」📌（※ただし“見せ方”は外側寄りになることもある）

こういう **業務ルール（アプリの都合）** を、UIやDBから守ってあげるのがドメインの役目🛡️

---

## 2) “データ”と“ドメイン”は別モノだよ😳

ありがちな勘違いはこれ👇

* ❌ ドメイン＝ただの `type Todo = { ... }`（データ袋）
* ✅ ドメイン＝**不正を作らない仕組み**（ルールがある）

**ポイント：ドメインは「状態」より「振る舞い」や「制約」が主役**だよ🏠✨

---

## 3) ルールをControllerに置くと何が起きる？😱💥

最初は動くんだけど、すぐ地獄になるやつ…🥺

* CLIとHTTPの両方に同じチェックがコピペされる📎📎
* 片方だけ修正して **ルールがズレる**（バグる）🧨
* テストが「HTTP叩かないと確認できない」みたいに重くなる😵‍💫
* “どこが仕様なの？”が迷子になる🌀

---

## 4) 悪い例：入口（Controller/Handler）にルールが散らばる ☠️

「とりあえずここでチェックしよ〜」が積み重なるパターン😇

```ts
// ❌ adapters/http/addTodoHandler.ts とかに書いちゃう例（悪い例）
export function addTodoHandler(req: any) {
  const title = String(req.body.title ?? "").trim();

  if (title.length === 0) {
    return { status: 400, body: { message: "title is required" } };
  }

  // さらに別の入口(CLI)にも同じチェックが増える…
  // さらに「完了は二重適用NG」も別ファイルに散らばる…

  // 保存して返す…
}
```

これ、入口が増えた瞬間に **“ルールの複製”が始まる**のがヤバい😱

---

## 5) 良い例：ドメインが「不正を作らせない」🛡️✨

ドメイン側に「空タイトルは禁止」を入れると、入口が何個あっても安全になるよ💖

### ✅ ドメインの考え方（超ざっくり）

* **作るときに守る**（コンストラクタ／ファクトリで検査）🧷
* **操作するときに守る**（メソッドで検査）🔒
* 破ったら **ドメインエラー** として返す📌

---

## 6) まずはTodoの“法律”をドメインに置こう 🏛️📝

ここからは「最小セット」でいくよ😊✨
（この章は “ユースケース” じゃなくて “ドメインの置き方” に集中！）

### 📁 置き場所イメージ

* `src/domain/todo/` … Todoの世界（ルール）🏠

  * `Todo.ts`
  * `TodoError.ts`（エラー定義）

---

## 7) 実装：ドメインエラーを作る 🧯

```ts
// src/domain/todo/TodoError.ts
export class TodoError extends Error {
  override name = "TodoError";
}

export class ValidationError extends TodoError {
  override name = "ValidationError";
}

export class StateError extends TodoError {
  override name = "StateError";
}
```

---

## 8) 実装：Todoは「ルール込みの存在」にする 🧩✨

```ts
// src/domain/todo/Todo.ts
import { StateError, ValidationError } from "./TodoError";

export type TodoId = string;

export class Todo {
  private constructor(
    public readonly id: TodoId,
    public readonly title: string,
    public readonly completed: boolean,
  ) {}

  // ✅ “作る” の入口をここに寄せる（不正を作らない）
  static create(params: { id: TodoId; title: string }): Todo {
    const title = params.title.trim();
    if (title.length === 0) throw new ValidationError("タイトルは必須だよ📝");
    return new Todo(params.id, title, false);
  }

  // ✅ “操作” の入口もここ（不正な遷移を止める）
  complete(): Todo {
    if (this.completed) throw new StateError("もう完了してるよ✅（二重適用NG）");
    return new Todo(this.id, this.title, true);
  }
}
```

### ここが気持ちいいポイント😊💕

* 入口（CLI/HTTP/GUI）が増えても、**ルールは1か所**📌
* テストが「Todoだけ」でできるようになる🧪✨
* “仕様”が `Todo.create()` と `todo.complete()` を見れば分かる👀

---

## 9) ドメインに入れてOK / ダメ 🙆‍♀️🙅‍♀️

### ✅ 入れてOK（ルール系）

* Entity（Todoみたいな存在）🧩
* Value Object（タイトル専用型とか）🎀
* 不変条件（空禁止、二重完了禁止）🧷
* ドメインエラー（仕様としての失敗）📌

### ❌ 入れない（外側の都合）

* `fs`（ファイル保存）📄
* HTTPの `Request/Response` 🌐
* DBのORMモデル🗄️
* UIのフォーム状態🖥️

**ドメインは“外の型”を知らない**が最強ルールだよ🛡️

---

## 10) ミニ演習（5分）📝🎀

次のルールを1つだけ追加してみてね😊

* ルール案A：タイトルは **50文字まで** ✂️
* ルール案B：タイトルは **連続スペースだけ禁止** 🚫
* ルール案C：完了後はタイトル変更できない（将来用）🔒

追加場所はここ👇

* `Todo.create()`（作成時の検査）
* `Todo.complete()`（状態遷移の検査）

---

## 11) AIの使いどころ（安全運転🤖🧰）

AIにはこう頼むとめっちゃ強いよ💖

* 「このドメインルール、テストケースにするとしたら何パターン？」🧪
* 「例外クラス名、もっと読みやすい案ある？」📝
* 「`Todo.create` のバリデーションを増やしたい。破壊的変更にならない方法は？」🔧

でもこれは任せすぎ注意⚠️

* 「ルールそのもの（何を禁止するか）」は自分で決めよ🛡️✨

---

## 12) まとめ 🎁💖

* ドメインは **データ袋じゃなくてルール置き場** 🏠📌
* ルールを入口に置くと、入口が増えた瞬間にコピペ地獄😱
* `create()` と `complete()` にルールを入れると、中心が強くなる🛡️✨

---

## 次章チラ見せ👀✨

次は **「最小モデル（Todo）をもう少し整える」** に進むよ〜🧩📝
idやtitleを、もっと“事故りにくい形”にしていく感じ😊💕

[1]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/ "Announcing TypeScript 5.9 - TypeScript"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://developer.microsoft.com/blog/typescript-7-native-preview-in-visual-studio-2026?utm_source=chatgpt.com "TypeScript 7 native preview in Visual Studio 2026"
