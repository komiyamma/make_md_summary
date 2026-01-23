# 第18章：ドメイン入門③：ミニ不変条件（Invariants）🧷✨

この章はね、**「どんな入口（CLI/HTTP/将来のGUI）が増えても、アプリのルールが絶対に壊れない」**ようにする回だよ〜😊💖
ヘキサゴナルでいう「中心を守る🛡️」の**いちばん地味で、いちばん強い武器**が“不変条件”なのです✨

---

## 0. まず今日のゴール🎯✨

今日できるようになること👇😊

* **不変条件（Invariants）って何か**を、自分の言葉で説明できる📣✨
* **Todoドメインの不変条件を2つ**、中心（domain）で守れる🛡️

  * ✅ タイトル空はNG
  * ✅ 完了の二重適用はNG（もう完了してるのにまた完了…はダメ🙅‍♀️）
* **入口が増えてもルールが崩れない**理由がわかる🔌🧩

---

## 1. 不変条件（Invariants）ってなに？🧷

超かんたんに言うと👇

> **「この世界（ドメイン）では、絶対にこうでなきゃダメ！」**
> っていう“ルールの骨格”💀✨

たとえば Todo なら…

* タイトルが空の Todo は存在してほしくない😵‍💫
* 「完了」って1回だけでいいのに、2回目以降も通ったら変だよね？😱

これが **不変条件**だよ🧷✨

---

## 2. なんで“不変条件”をドメインに置くの？🏰🛡️

ここがヘキサゴナルの気持ちよさポイント😍✨

### ✅ 入口（Adapter）は増える前提

最初はCLIだけでも、あとからHTTP APIが増えたり、管理画面が増えたりするよね🌐📱

もし不変条件を入口側に散らすと…

* CLIではチェックしてたのに、HTTP側でチェック忘れて事故💥
* 入口が増えるたび、同じチェックをコピペ地獄😵‍💫📄📄📄

だから👇

### ✅ “中心（domain）”で守れば、全部の入口が安全になる🛡️✨

入口がどれだけ増えても、**中心が最後の砦**になってくれるの💪🔥

---

## 3. “入力チェック”と“不変条件”のちがい🧠✨

ここ、混ざりがちだから整理するね😊📌

### 入力チェック（入口でやりがち）🚪

* 文字列か？数値か？
* 必須項目が来てるか？
* JSONの形が正しいか？

👉 これは **入口（Inbound Adapter）** が得意✨

### 不変条件（ドメインが守る）🏰

* **正しいTodoとして存在できるか？**
* **状態遷移が変じゃないか？**（例：完了の二重適用）

👉 これは **domain** の責任🛡️✨

※入口で軽く弾いてもOKだけど、**最終的にdomainでも必ず守る**のが安心だよ😊

---

## 4. 実装しよう：Todoの“不変条件2つ”📝✨

ここから、コードで「中心を守る🛡️」体験いくよ〜！💻🎉
（ファイル場所は、例として `src/domain/todo/` に置く想定📁）

---

### 4.1 ドメイン側の最小コード（Todo + 不変条件）🧩🧷

ポイントはこれ👇😊

* **生成時**に「タイトル空NG」を守る
* **完了処理**で「二重完了NG」を守る
* 外から勝手に壊されないように、`Readonly` と “更新は関数で返す” を使う✨

```ts
// src/domain/todo/Todo.ts

export type TodoId = string;

export type Todo = Readonly<{
  id: TodoId;
  title: string;
  completed: boolean;
}>;

// いったん最小のドメインエラー（後の章で整備するよ😊）
export class DomainError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "DomainError";
  }
}

function normalizeTitle(raw: string): string {
  // 「空っぽ」「空白だけ」をまとめて弾きたいので trim() するよ✂️
  return raw.trim();
}

/**
 * ✅ 不変条件：タイトル空NG を守りながら Todo を作る
 */
export function createTodo(params: { id: TodoId; title: string }): Todo {
  const title = normalizeTitle(params.title);

  if (title.length === 0) {
    throw new DomainError("Todoのタイトルは空にできません🥺");
  }

  return {
    id: params.id,
    title,
    completed: false,
  } as const;
}

/**
 * ✅ 不変条件：完了の二重適用NG を守りながら完了にする
 */
export function completeTodo(todo: Todo): Todo {
  if (todo.completed) {
    throw new DomainError("このTodoは既に完了しています（二重完了NG）🙅‍♀️");
  }

  return {
    ...todo,
    completed: true,
  } as const;
}
```

---

## 5. いまのコード、どこが“ヘキサゴナル的に良い”の？🔌🧩✨

### ✅ 入口が何であれ、domainが最後に守る🛡️

CLIでもHTTPでも、最終的に `createTodo` / `completeTodo` を通る限り、ルールは破れない💖

### ✅ 状態遷移の芽がある🌱

`completed: false → true` の変化は、のちの章で「状態機械っぽい考え方🚦」にも繋げられるよ😊✨

---

## 6. すぐ試せる！ミニテスト（Vitest）🧪✨

不変条件は **テストで守ると超つよい**💪💖
Vitestは今も活発に更新されてて、移行ガイドも整備されてるよ📘✨ ([Vitest][1])

```ts
// src/domain/todo/Todo.test.ts

import { describe, it, expect } from "vitest";
import { createTodo, completeTodo, DomainError } from "./Todo";

describe("Todo invariants 🧷", () => {
  it("タイトル空はNG", () => {
    expect(() => createTodo({ id: "1", title: "   " })).toThrow(DomainError);
  });

  it("完了の二重適用はNG", () => {
    const todo = createTodo({ id: "1", title: "Buy milk" });
    const done = completeTodo(todo);

    expect(done.completed).toBe(true);
    expect(() => completeTodo(done)).toThrow(DomainError);
  });

  it("タイトルは前後の空白を落として保存される", () => {
    const todo = createTodo({ id: "1", title: "  Hello  " });
    expect(todo.title).toBe("Hello");
  });
});
```

---

## 7. よくある事故パターン😱💥（先に潰す！）

### ❌ 入口にしかチェックがない

HTTPでは弾けてたのに、バッチ処理から直に保存して壊れる…みたいな事故が起きる💥

### ❌ “どこでもif”で散らかる

あちこちに `if (title === "")` が出てきたら黄色信号🚥😵‍💫
→ **domainに寄せていこう**✨

### ❌ 「とりあえずany」で通す

不変条件があっても、型が雑だと穴が増える🕳️
→ “中心ほど型を丁寧に” が安定するよ😊

---

## 8. AI活用コーナー🤖💖（この章に効く使い方）

### ✅ 不変条件の洗い出しを手伝ってもらう

コピペで使えるよ👇📝✨

* 「Todoドメインの不変条件を10個提案して。初心者向けに理由も」
* 「この `createTodo/completeTodo` に抜けてる不変条件がないかレビューして」
* 「不変条件ごとに、Vitestのテストケースを提案して」

### ⚠️ でもここは自分で決める！

**何が“ルール”か**は、アプリの意図そのものだからね😊🛡️

---

## 9. 自主ミニ課題📝🎀

できそうなのを1個だけでOKだよ〜😊✨

### 課題A：タイトル最大50文字ルールを追加✂️

* `title.length > 50` をドメインで弾く
* テストも追加🧪

### 課題B：「未完了に戻す」を作ってみる🔁

* ただしルールを自分で決めてね（戻せる？戻せない？）😊

---

## 10. まとめ🎁✨（今日の合言葉）

* 不変条件は **「絶対に守りたいルール」** 🧷
* 入口が増えても壊れないように、**domainが最後に守る** 🏰🛡️
* 「タイトル空NG」「二重完了NG」みたいな **小さいルールから**始めるのがコツ🌱

---

## 2026年1月の“いま”メモ🗓️✨（最新版チェック）

* TypeScript の最新リリースノート（5.9）が公式ドキュメントで更新されてるよ🧠✨ ([typescriptlang.org][2])
* Node.js は v24 が Active LTS として案内されてるよ🔒✨ ([Node.js][3])

（バージョンは今後も動くから、迷ったら公式のリリースページを見るのが安全だよ😊）

---

次の章（第19章）では、このドメインを使って **ユースケース（Add / Complete / List）** を作って「手順」と「判断」を中心に置くよ〜🎮➡️🧠✨

[1]: https://vitest.dev/guide/?utm_source=chatgpt.com "Getting Started | Guide"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
