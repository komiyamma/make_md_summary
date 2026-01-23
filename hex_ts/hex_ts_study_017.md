# 第17章 ドメイン入門②：最小モデル（Todo）を作る 🧩📝✨

この章は「**Todoって何者？**」を、**小さく・安全に**つくる回だよ😊
このあとユースケースやAdapterを足していくけど、**まず中心（ドメイン）に “しっかりした芯”** を作るのが勝ちパターン🏰🛡️

---

## 1) 今日作る “最小モデル” はこれだけ 🎯

Todoは、まず **3つの情報**があれば成立するよ👇

* `id`：識別子（同じタイトルでも区別できる）🪪
* `title`：やること（空文字はダメ！）📝
* `completed`：完了した？（true/false）✅

この3つを **ドメイン層（中心）** に置く✨
そして一番大事なのが👇

> ❌ **不正なTodoを作れない**ようにする（生成時チェック）
> ✅ つまり「空タイトルTodo」を物理的に生まれなくする👶🚫

---

## 2) まずはファイルを作ろう 📁✨

おすすめ配置（第15章の `domain / app / adapters` に合わせる形）👇

* `src/domain/errors/DomainError.ts`
* `src/domain/todo/Todo.ts`

---

## 3) まず “ドメインのエラー” を1個だけ用意 🧯✨

ドメイン層で「ルール違反だよ！」って言いたいときの、専用エラーだよ😊

```ts
// src/domain/errors/DomainError.ts
export class DomainError extends Error {
  constructor(
    public readonly code: string,
    message: string
  ) {
    super(message);
    this.name = "DomainError";
  }
}
```

ポイント👇

* `code` を付けると、あとでログやHTTPのエラー変換が超ラクになる💡✨（第33章にも効いてくる）

---

## 4) Todoモデル（超シンプル版）を作る 🧩📝

「**private constructor + static create**」で、**必ずチェックを通す**形にするよ🛡️

```ts
// src/domain/todo/Todo.ts
import { DomainError } from "../errors/DomainError";

export type TodoId = string;

export type Todo = Readonly<{
  id: TodoId;
  title: string;
  completed: boolean;
}>;

function normalizeTitle(input: string): string {
  // 前後スペースを削って、見た目の事故を減らす✨
  return input.trim();
}

export function createTodo(params: { id: TodoId; title: string }): Todo {
  const title = normalizeTitle(params.title);

  if (title.length === 0) {
    throw new DomainError("TODO_TITLE_EMPTY", "タイトルは空にできません🙅‍♀️");
  }

  return Object.freeze({
    id: params.id,
    title,
    completed: false,
  });
}
```

いいところ😎✨

* **Todoは createTodo を通さないと作れない**（＝ルールが守られる）🛡️
* `Object.freeze()`で実行時にも「うっかり書き換え」を防ぎやすい🔒
* ドメイン層は **DBもHTTPもファイルも知らない**（超きれい✨）

> ここで「idをどう作るの？」って思うよね🙂
> それは後で **Outbound Port（UUID生成）**に逃がすのがヘキサゴナル的に気持ちいい💖
> いったん今章は「idは外から渡す」でOK！

---

## 5) 動作チェック（ミニ）✅✨

試しに一瞬だけ使ってみる（あとで消してOK）🧪

```ts
// src/domain/todo/_demo.ts（一時ファイルでOK）
import { createTodo } from "./Todo";

const ok = createTodo({ id: "demo-1", title: "  牛乳を買う  " });
console.log(ok); // title が trim されるよ✨

const ng = createTodo({ id: "demo-2", title: "   " }); // ここでDomainError
console.log(ng);
```

---

## 6) “ちょい背伸び版（任意）”：titleを型で守る 🧠✨

「titleはstringだけど、空は禁止！」を **型で表現**したい人向け🎀
（この発想、あとでValue Objectにもつながるよ！）

```ts
// src/domain/todo/TodoTitle.ts
import { DomainError } from "../errors/DomainError";

declare const todoTitleBrand: unique symbol;
export type TodoTitle = string & { readonly [todoTitleBrand]: true };

export function createTodoTitle(input: string): TodoTitle {
  const v = input.trim();
  if (v.length === 0) {
    throw new DomainError("TODO_TITLE_EMPTY", "タイトルは空にできません🙅‍♀️");
  }
  return v as TodoTitle;
}
```

こうすると👇

* `TodoTitle` を持ってる時点で「空じゃない」前提で扱いやすい✨
* ただし初心者さんは **超シンプル版だけで全然OK**だよ😊💕

---

## 7) よくある事故あるある 😵‍💫💥（先に潰す）

* **Todoをただのinterfaceで作るだけ**
  → どこでも `title: ""` のTodoが作れちゃう😱
* **trimしない**
  → `"   "` が通ってしまう＆画面表示が微妙になる🌀
* **completedを外から自由に書き換えられる**
  → 状態のルールが守れなくなる（次章で対策するよ🚦）

---

## 8) AIに頼るならここが安全 🤖✨

この章でAIに頼ってOKなもの👇

* `DomainError` の雛形生成🧯
* `createTodo` のテストケース案🧪
* 命名案（normalizeTitle とか）📝

逆に注意⚠️

* 「id生成をdomain内でcrypto.randomUUIDしよう！」みたいな提案
  → それ、中心が外側（環境）を知っちゃう方向なので後で辛くなる🥲
  ちなみに `crypto.randomUUID()` はNodeに用意されてて、Node v14.17.0 / v15.6.0で追加、RFC 4122 v4 UUIDを暗号学的PRNGで生成するよ📌 ([Node.js][1])
  でも **使う場所はAdapter/Composition Root側** がキレイ✨

---

## 9) 章末ミニ課題 📝🎀

### 課題A：タイトルの最大長を追加してみよう ✂️📏

例：100文字まで（超えたらDomainError）

### 課題B：titleの正規化を強化してみよう 🧽

* 連続スペースを1個にする（`"a   b"` → `"a b"`）など✨

### 課題C：Todoを “不変” にしてるか確認 🔒

* `Object.freeze` を外したらどうなる？
* `Readonly` を外したらどうなる？
  差分で体感してみて😊

---

## 10) まとめ 🎁✨

* Todoの最小モデルは **id / title / completed** 🧩
* **生成時チェック**で「不正状態」を生ませない🛡️
* domainは外側（DB/HTTP/Node機能）を知らない方が強い🏰✨

（おまけ：TypeScriptは今だと 5.9 系が最新で、`tsc --init` がかなり “今っぽい最小構成” を吐くようになってるよ🧰✨ ([typescriptlang.org][2])）

---

## 次章チラ見せ 👀✨（第18章）

次は **不変条件（Invariants）** をもう少し増やして、
「完了の二重適用禁止」みたいな **状態遷移のルール**に入っていくよ🚦💖

[1]: https://nodejs.org/api/crypto.html "Crypto | Node.js v25.4.0 Documentation"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html "TypeScript: Documentation - TypeScript 5.9"
