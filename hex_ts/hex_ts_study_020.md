# 第20章：ユースケース入門②：入力・出力の形（DTO）📮📤✨

この章は「ユースケースが、外の世界（CLI/HTTP/画面/DB）とどう会話するか」を、**DTO（Data Transfer Object）**でスッキリさせる回だよ〜😊✨
ここが決まると、あとで入口（CLI→HTTP）を差し替えても中心が揺れない💖

---

## 1) DTOってなに？ざっくり言うと「受け渡し用の伝票」🧾✨

DTOは、ユースケースが受け取る＆返す**“ただのデータ”**だよ📦
ポイントはこれ👇

* ✅ **薄い**（余計なメソッドや複雑さなし）
* ✅ **外に見せても安全**（内部事情を隠せる🛡️）
* ✅ **JSONにしやすい**（HTTPと相性◎🌐）

たとえば Todo を「追加する」なら、

* 入力DTO：`{ title: "牛乳買う" }` 🥛
* 出力DTO：`{ todo: { id, title, completed } }` ✅

みたいな感じ😊

---

## 2) なぜ domain の型を外に漏らさないの？😱🧨

もしユースケースが `Todo` クラス（ドメイン）そのまま返すと、外側がこうなる👇

* 外側（HTTP/CLI）が **Todoの内部構造に依存**しちゃう
* ドメインを変更したら、外側も巻き込まれて壊れがち💥
* JSON化で想定外の形になったり、テストが読みづらくなったり😵‍💫

DTOにしておくと…

* 中心（ドメイン）の変更が外に漏れにくい🛡️
* 入口（CLI→HTTP）を変えてもユースケースが安定する🔁✨
* テストが「仕様の文章」みたいに読める🧪📖

---

## 3) DTOの設計ルール（これだけ守ればOK）✅✨

DTOは「外へ渡す前提」だから、だいたいこうするのが安全だよ👇

### ✅ ルールA：基本はプリミティブ中心（string/number/boolean）🧱

* `Date` は避けて **ISO文字列**にしよ（`"2026-01-23T..."`）🕒
* クラスインスタンスは渡さない🙅‍♀️

### ✅ ルールB：DTOは “ただの箱” 📦

* メソッドなし
* ロジックなし（判断や状態遷移はドメインへ🧠）

### ✅ ルールC：名前は「外に見せたい言葉」💬

* ドメインの内部用語（濃い言葉）をそのまま出さなくていい🙆‍♀️

---

## 4) TodoミニアプリのDTOを作ろう📝🍰

フォルダ例（迷子防止）📁🧭

* `src/app/dtos/` … DTO置き場📮
* `src/app/usecases/` … ユースケース🎮
* `src/domain/` … ルール（ドメイン）🧠

まずは DTO を作るよ✨

```ts
// src/app/dtos/todo.dto.ts

export type TodoDto = Readonly<{
  id: string;
  title: string;
  completed: boolean;
}>;

export type AddTodoInputDto = Readonly<{
  title: string;
}>;

export type AddTodoOutputDto = Readonly<{
  todo: TodoDto;
}>;

export type CompleteTodoInputDto = Readonly<{
  id: string;
}>;

export type CompleteTodoOutputDto = Readonly<{
  todo: TodoDto;
}>;

export type ListTodosOutputDto = Readonly<{
  todos: readonly TodoDto[];
}>;
```

`Readonly` を付けるのは「外に渡すデータは基本いじらない」って気持ちになるからおすすめ😊🛡️

---

## 5) ドメイン → DTO への変換（Mapper）🔁🧩

ここが**超大事**✨
**変換は中心じゃなくて“アプリ層（ユースケース寄り）”か“アダプタ”**でやるとキレイだよ🧼

例：`Todo` ドメインがクラスだとして…

```ts
// src/app/dtos/todo.mapper.ts
import { Todo } from "../../domain/todo/Todo.js";
import { TodoDto } from "./todo.dto.js";

export function toTodoDto(todo: Todo): TodoDto {
  return {
    id: todo.id,              // getterでもOK
    title: todo.title,
    completed: todo.completed,
  };
}
```

> ✅ “外に渡す形”は、この `toTodoDto` が責任もつ感じ💖

---

## 6) ユースケースの「入口と出口」をDTOで固定する🚪📤✨

ユースケースは、外側の都合（HTTPのRequestとか）を知らない🙅‍♀️
なので、**DTOだけ**知ってればOKにするよ！

```ts
// src/app/usecases/AddTodoUseCase.ts
import { AddTodoInputDto, AddTodoOutputDto } from "../dtos/todo.dto.js";
import { toTodoDto } from "../dtos/todo.mapper.js";
import { Todo } from "../../domain/todo/Todo.js";
import { TodoRepositoryPort } from "../ports/TodoRepositoryPort.js";

export class AddTodoUseCase {
  constructor(private readonly repo: TodoRepositoryPort) {}

  async execute(input: AddTodoInputDto): Promise<AddTodoOutputDto> {
    // 入力チェック（軽いのはここでもOKだけど、方針は後の章で整理するよ😊）
    const todo = Todo.create(input.title);

    await this.repo.save(todo);

    return { todo: toTodoDto(todo) };
  }
}
```

ここでの気持ち👉

* **入力はDTO**（外から来る伝票📮）
* **内部はドメイン**（ルールで作る🧠）
* **出力はDTO**（外へ返す伝票📤）

---

## 7) DTOを使うとテストがめっちゃ読みやすい🧪✨

返ってくるのが DTO だと、テストがこうなる👇（読みやすい〜！😍）

```ts
const out = await addTodo.execute({ title: "牛乳買う" });

expect(out.todo.title).toBe("牛乳買う");
expect(out.todo.completed).toBe(false);
```

ドメインの複雑さ（メソッドとか）をテストが知らなくて済むのが最高💖

---

## 8) 「DTOが薄いか」セルフチェック✅🥗

DTOが太り始めると事故るので、これで点検しよ〜🚨

* ❌ DTOに `validate()` とか `complete()` とかメソッド生えてる
* ❌ DTOの中にドメインクラス入ってる（`todo: Todo` とか）
* ❌ DTOがDBの形そのまま（`created_at` とか外部都合が混入）
* ✅ DTOは “外に見せたい言葉” だけになってる
* ✅ JSONにしても自然な形になってる

---

## 9) AIに頼むならこの聞き方が安全🤖📝✨

### 雛形生成（OK）🧰

```text
TodoアプリのUseCase用DTOを作りたいです。
AddTodo / CompleteTodo / ListTodos の input/output DTO を
「プリミティブ中心」「Readonly」「JSON化しやすい」形でTypeScriptで提案して。
```

### レビュー（めっちゃおすすめ）🔍

```text
このDTO設計で「ドメインが外に漏れてないか」「DTOが太ってないか」
「将来HTTP/CLIに差し替えても中心が変わらないか」を観点にチェックして。
```

---

## 10) 最新のTSまわり小ネタ（DTO設計がラクになるやつ）✨

* npm の `typescript` 最新は **5.9.3**（2026年1月時点）だよ📌 ([NPM][1])
* TypeScript 5.9 では、Node向けの設定として **`--module node20`** みたいな「安定ターゲット」も用意されてるよ（挙動がブレにくい方針）🧭 ([typescriptlang.org][2])
* DTOの入力検証をライブラリでやるなら、Zod は **v4系が安定**していて（例：v4.3.0）、DTOと相性がいいよ✅ ([GitHub][3])

  * 軽量派なら Valibot も選択肢だよ🪶 ([valibot.dev][4])

（※検証の置き場所は次の章以降で「境界でやる」方針に寄せていくよ😊）

---

## 11) ミニ課題🎀📝（5〜10分でOK）

### 課題A：`ListTodosOutputDto` を整える✨

* `todos` を `readonly` 配列にしたまま
* `TodoDto` の形が崩れないことを確認してね✅

### 課題B：将来用フィールドを入れてみる🕒

* `createdAt: string`（ISO文字列）を `TodoDto` に追加
* **ドメインの Date をそのまま出さない**ことがポイントだよ🙅‍♀️💡

---

## この章のまとめ🎁💖

* DTOは「伝票」📮📤
* ユースケースの入口と出口をDTOで固定すると、中心が守れる🛡️
* ドメインは濃くてOK、外に出すときはDTOで薄くする🥗✨
* 変換（Mapper）を1か所に集めると、未来がラク🔁💕

次はこのDTOが「Port（約束）」にどう繋がっていくかが気持ちいいところだよ〜🔌✨

[1]: https://www.npmjs.com/package/typescript?activeTab=versions&utm_source=chatgpt.com "typescript"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[3]: https://github.com/colinhacks/zod/releases?utm_source=chatgpt.com "Releases · colinhacks/zod"
[4]: https://valibot.dev/?utm_source=chatgpt.com "Valibot: The modular and type safe schema library"
