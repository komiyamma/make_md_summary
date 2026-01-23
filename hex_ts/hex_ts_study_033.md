# 33. エラー設計①：中心のエラー（仕様）📌😌

この章はね、めちゃ大事なことをやります✨
**「エラーも仕様の一部」**として、ヘキサゴナルの**中心（domain/app）に“きれいに置く”**練習だよ〜😊🔌🧩

---

## 1) 今日のゴール🎯✨

できるようになること👇

* **「仕様として起きるエラー」と「事故（I/O失敗）」を分けて説明**できる🧠✨
* 中心のエラーを **型（判別可能ユニオン）で表現**できる🔖
* ユースケースが **例外を投げ散らかさず**、`Result`で返せる🧯✨
* Adapter側で「中心エラー→表示/HTTPレスポンス」に変換できるイメージが持てる🌈

判別可能ユニオン（タグ付きユニオン）で安全に分岐できるのがTSの強みだよ〜🔀✨
（TypeScript公式でも “Discriminating Unions” は定番テクとして紹介されてるよ） ([typescriptlang.org][1])

---

## 2) まず分けよう！エラーは2種類だけでOK😊✌️

### A. 仕様エラー（中心のエラー）📌

**ルールにより「できません」**ってなるやつ。
例：

* タイトル空はダメ🚫
* 完了済みをもう一回完了はダメ🚫

✅ これは **アプリの仕様そのもの**だから、中心に置く🛡️

### B. 事故エラー（外側のエラー）😵‍💫

**I/Oや外部都合で「失敗しました」**ってなるやつ。
例：

* ファイル読めない📄💥
* DB落ちた💾💥
* ネット落ちた🌐💥

✅ これは **Adapterの世界**で扱う（次章の領域）🧩

---

## 3) 方針：中心は「Resultで返す」🧯✨（投げ散らかさない）

中心でおすすめはこれ👇

* ✅ **成功**：`ok(value)`
* ✅ **仕様エラー**：`err(error)`
* ✅ **事故エラー**：中心では原則作らない（Adapterでラップする）

JS/TSは例外も使えるけど、**中心でthrow多用**すると

* 呼び出し側が毎回 try/catch 地獄😇
* 「どんなエラーが起きるか」が型で見えない🙈
  ってなりがち。

だからこの教材では **Result推し**で行くよ〜💖

---

## 4) 実装：`Result` 型を用意しよう📦✨

`src/app/result.ts`

```ts
export type Ok<T> = { ok: true; value: T };
export type Err<E> = { ok: false; error: E };
export type Result<T, E> = Ok<T> | Err<E>;

export const ok = <T>(value: T): Ok<T> => ({ ok: true, value });
export const err = <E>(error: E): Err<E> => ({ ok: false, error });
```

これだけで、中心の戻り値が **「成功 or 仕様エラー」**って型で読めるようになるよ😊✨

---

## 5) 実装：中心のエラーを「判別可能ユニオン」で作る🔖✨

ポイントはこれ👇

* **共通の識別子フィールド（例：`type`）**を持つ
* `switch`で分岐すると、TSが賢く絞り込んでくれる🔍✨ ([typescriptlang.org][1])

`src/app/errors.ts`

```ts
// 仕様エラー（中心）だけを定義するよ🛡️

export type DomainError =
  | { type: "TodoTitleEmpty" }
  | { type: "TodoAlreadyCompleted"; id: string };

export type ValidationError =
  | { type: "TodoIdInvalid"; raw: string };

// 章の範囲ではこの2つを「中心エラー」として扱うよ📌
export type AppError = DomainError | ValidationError;

// 分岐漏れをコンパイル時に潰すお守り🧿
export const assertNever = (x: never): never => {
  throw new Error(`Unexpected: ${JSON.stringify(x)}`);
};
```

> `DomainError` と `ValidationError` を分けるの、地味に効くよ〜✨
>
> * DomainError：ドメインのルール違反（中心の心臓❤️）
> * ValidationError：入力の形や変換の失敗（境界寄り🚪）

---

## 6) 例：ドメイン側で「仕様エラー」を返す🧠📝

`src/domain/todo.ts`（超ミニ例）

```ts
import { Result, ok, err } from "../app/result";
import { DomainError } from "../app/errors";

export type Todo = {
  id: string;
  title: string;
  completed: boolean;
};

export const createTodo = (id: string, title: string): Result<Todo, DomainError> => {
  if (title.trim().length === 0) return err({ type: "TodoTitleEmpty" });

  return ok({
    id,
    title: title.trim(),
    completed: false,
  });
};

export const completeTodo = (todo: Todo): Result<Todo, DomainError> => {
  if (todo.completed) return err({ type: "TodoAlreadyCompleted", id: todo.id });

  return ok({ ...todo, completed: true });
};
```

ここが気持ちいいポイント😍

* **例外じゃない**からテストが読みやすい🧪✨
* `Result`で **成功/失敗が必ず返る**（抜け道が減る）🛡️

---

## 7) 例：ユースケースが「中心エラー」を束ねて返す🎮➡️🧠

今回は “CompleteTodo” を例にするね✅

`src/app/usecases/completeTodo.ts`

```ts
import { Result, ok, err } from "../result";
import { AppError } from "../errors";
import { completeTodo } from "../../domain/todo";

// すでにある想定（第22章で作ったOutbound Portのイメージ）🔌
export type TodoRepository = {
  findById(id: string): Promise<{ id: string; title: string; completed: boolean } | null>;
  save(todo: { id: string; title: string; completed: boolean }): Promise<void>;
};

export type CompleteTodoInput = { id: string };
export type CompleteTodoOutput = { id: string; completed: true };

export const completeTodoUseCase = async (
  input: CompleteTodoInput,
  deps: { repo: TodoRepository }
): Promise<Result<CompleteTodoOutput, AppError>> => {
  // ① 入力チェック（境界寄りだけど、中心側に置くならValidationErrorとして明示）📌
  if (input.id.trim().length === 0) {
    return err({ type: "TodoIdInvalid", raw: input.id });
  }

  // ② 取得（見つからないは「仕様」にするかは設計次第）
  const found = await deps.repo.findById(input.id);
  if (!found) {
    // 今回は章のテーマ外なので「ValidationErrorに寄せる」簡易版でOKにするね🙏
    return err({ type: "TodoIdInvalid", raw: input.id });
  }

  // ③ ドメインの状態遷移（ここでDomainErrorが出るかも）🧠
  const completed = completeTodo(found);
  if (!completed.ok) return err(completed.error);

  // ④ 保存（I/O事故は次章で！この章では成功すると仮定でOK✨）
  await deps.repo.save(completed.value);

  return ok({ id: completed.value.id, completed: true });
};
```

---

## 8) 「中心エラー」を人間向けに変換する（Adapterでやる）🧩✨（チラ見せ）

中心は型でキレイだけど、そのままだとユーザーに見せにくいよね👀
なので **外側（CLI/HTTP）が翻訳**するよ🔁

`src/adapters/shared/formatError.ts`（例）

```ts
import { AppError, assertNever } from "../../app/errors";

export const formatError = (e: AppError): string => {
  switch (e.type) {
    case "TodoTitleEmpty":
      return "タイトルが空っぽだよ〜🥺 文字を入れてね📝";
    case "TodoAlreadyCompleted":
      return `そのToDo（id=${e.id}）はもう完了済みだよ✅`;
    case "TodoIdInvalid":
      return `idが変だよ〜😵 raw="${e.raw}"`;
    default:
      return assertNever(e);
  }
};
```

この `switch` が **分岐漏れをコンパイルで怒ってくれる**のが最高〜✨
（判別可能ユニオンのうまみ💖） ([typescriptlang.org][1])

---

## 9) ちょい最新トピック：`Error.cause` は“外側”で便利🧷✨

この章は「中心エラー」だけど、次章につながる豆知識ね😊
外側でI/O失敗を **ラップ**するとき、`cause` が超便利✨

* `cause` は「元の原因」を残せる仕組みだよ🧵
* ブラウザでもNodeでも広く使えるようになってるよ📌 ([MDN Web Docs][2])

例（外側でやるやつ）：

```ts
try {
  // readFileとか…
} catch (cause) {
  throw new Error("File read failed", { cause });
}
```

---

## 10) よくあるミス集😇⚠️（ここ踏む人多い）

* ❌ **中心が `Response` とか `Request` を返し始める**
  → 仕様エラーは中心の型で返して、HTTPはAdapterで翻訳🌐🧩

* ❌ **エラー文言を中心に直書き**（UI都合が混ざる）
  → 中心は `{ type: ... }`、文言は外側で😊

* ❌ **エラー型が巨大化**（なんでも1つに詰める）
  → まずは「今必要な最小」だけでOK✂️✨

---

## 11) AIに頼むときのプロンプト（そのまま使ってOK）🤖📝✨

コピペ用👇

* 「この `AppError` の `switch` に分岐漏れがないか確認して。漏れてたら追加して」
* 「このUseCaseは例外を投げてない？ `Result` に統一できる？」
* 「`DomainError` にUI文言が混ざってない？ 混ざってたら外側へ移動案を出して」
* 「`ValidationError` と `DomainError` の境界が変じゃない？分離案を提案して」

---

## 12) ミニ演習📝🎀

### 演習A：エラーを1個追加してみよ✨

* ルール：タイトルは **最大30文字**まで✂️
* `DomainError` に `TodoTitleTooLong` を追加
* `createTodo` でチェック
* `formatError` に文言追加

### 演習B：分岐漏れをわざと起こしてみよ😈

* `DomainError` に新しいtypeだけ追加
* `formatError` を直さずに保存
  → TSが怒ってくれたら勝ち🏆✨（環境によっては `assertNever` の効き方が変わるので、`switch` のdefault処理も見てね）

---

## まとめ🎁💖

* エラーは **仕様（中心）** と **事故（外側）** に分ける📌
* 中心は **`Result` + 判別可能ユニオン** が超わかりやすい🔖✨ ([typescriptlang.org][1])
* 外側（Adapter）が **表示/HTTP/ログ** に翻訳する🧩
* `Error.cause` は外側のエラー連鎖で便利🧵✨ ([MDN Web Docs][2])

次の第34章では、いよいよ **「外側の事故エラー（I/O失敗）」** をどう扱うか😵‍💫➡️🧠 をやるよ〜！

[1]: https://www.typescriptlang.org/docs/handbook/unions-and-intersections.html?utm_source=chatgpt.com "Handbook - Unions and Intersection Types"
[2]: https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/Error/cause?utm_source=chatgpt.com "Error: cause - JavaScript - MDN Web Docs - Mozilla"