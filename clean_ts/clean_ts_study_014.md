# 第14章：Use Case Interactorの「型」を決める📐🎬✨

ここでやるのは超シンプルで、でも超効くやつです💪💖
**「Use Caseは毎回この形で書く！」**を決めて、迷いとブレを消します🧹✨
テンプレが決まると、あとが爆速になるよ〜🚀😊

---

## 1) まず結論：この講座のInteractor“標準形”✅🧩

この先ずっと使う「型」はこれ👇✨

* Use Caseは **1目的 = 1Interactor** 🎯
* 入口は **Request**（外側の言葉を入れない）📥
* 出口は **Response**（表示都合を入れない）📤
* 実行メソッド名は **execute** に統一🧠
* 戻り値は **Promise** に統一（同期でも）⏳
* 成功/失敗は **Result型** で返す（例外ドカーンを減らす）🧯

---

## 2) 最新事情もちょい確認👀🆕（型設計に効くところだけ）

* TypeScript は **5.9系のリリースノート**で Node 向け設定（`--module node20` など）を安定オプションとして用意していて、TSの“Node運用”まわりがより整理されてきてるよ🧠✨ ([typescriptlang.org][1])
* Node は **v24 が Active LTS**、**v25 が Current** といった枝の動き（更新日含む）が公式でまとまってるよ📦 ([nodejs.org][2])
* テストは Vitest 側のドキュメントが **2026年1月更新**になってて、普通に“今の前提”でOK🧪✨ ([vitest.dev][3])
  （※さらに Vitest 4 系で Browser Mode が安定化、みたいな流れもあるよ〜🌐🧪 ([InfoQ][4])）

> で、何が言いたいかというと…
> **「Use Case を Promise 前提にしておくと、IOやテスト戦略と噛み合ってめっちゃ楽」**ってこと🥳

---

## 3) Result型を1つ決めよう🧯✨（失敗の戻し方を統一）

第21章で「失敗の扱い」を本格的にやるけど、ここでは“器”だけ作るよ🍱✨

```ts
// usecases/_shared/Result.ts
export type Ok<T> = { ok: true; value: T };
export type Err<E> = { ok: false; error: E };
export type Result<T, E> = Ok<T> | Err<E>;

export const ok = <T>(value: T): Ok<T> => ({ ok: true, value });
export const err = <E>(error: E): Err<E> => ({ ok: false, error });
```

これで、Use Caseはいつもこう返せる👇😊

* 成功：`return ok(response)`
* 失敗：`return err(error)`

---

## 4) Use Case の“型”テンプレ（これが本体）🧱✨

### 4-1. 「UseCaseインターフェース」を統一する🎛️

```ts
// usecases/_shared/UseCase.ts
import type { Result } from "./Result";

export interface UseCase<Request, Response, Failure> {
  execute(request: Request): Promise<Result<Response, Failure>>;
}
```

この1枚があるだけで、プロジェクト全体がスッキリします😌✨
「どのUseCaseも execute で呼べる」って強い💪

---

## 5) Chapter 14の実作業：CreateTask のInteractor骨格を作る🗒️✨

ここでは「形だけ」をちゃんと作るよ🎯
（中身の実装は第18章でガッツリやる想定🧩）

### 5-1. Request / Response / Failure を分けて置く📦📌

```ts
// usecases/create-task/CreateTaskModels.ts
export type CreateTaskRequest = {
  title: string;
};

export type CreateTaskResponse = {
  taskId: string;
};
```

Failure（失敗）は“内側の言葉”でね⚠️💭

```ts
// usecases/create-task/CreateTaskErrors.ts
export type CreateTaskFailure =
  | { type: "InvalidTitle"; message: string }
  | { type: "Unexpected"; message: string };
```

> ここでのポイント💡
>
> * HTTP 400 とか 500 とかは **まだ絶対入れない**🙅‍♀️
> * “内側の失敗”として言語化する🗣️✨

---

### 5-2. Port（必要な能力）だけ差し込む🔌✨

Interactorは **Portにだけ依存**するんだったね😊

```ts
// usecases/ports/TaskRepository.ts
export interface TaskRepository {
  save(task: { id: string; title: string; completed: boolean }): Promise<void>;
}
```

（※ここは第24〜29章で洗練するけど、今は最小でOK🙆‍♀️）

---

### 5-3. Interactor（実行役）の型を完成させる🎬✅

```ts
// usecases/create-task/CreateTaskInteractor.ts
import type { UseCase } from "../_shared/UseCase";
import { err, ok, type Result } from "../_shared/Result";
import type { TaskRepository } from "../ports/TaskRepository";
import type { CreateTaskRequest, CreateTaskResponse } from "./CreateTaskModels";
import type { CreateTaskFailure } from "./CreateTaskErrors";

export class CreateTaskInteractor
  implements UseCase<CreateTaskRequest, CreateTaskResponse, CreateTaskFailure>
{
  constructor(private readonly repo: TaskRepository) {}

  async execute(
    request: CreateTaskRequest
  ): Promise<Result<CreateTaskResponse, CreateTaskFailure>> {
    // ここでは「形」だけ。中身は第18章で完成させるよ🧩✨

    const title = request.title?.trim();
    if (!title) {
      return err({ type: "InvalidTitle", message: "タイトルが空だよ😢" });
    }

    const taskId = crypto.randomUUID(); // 外側に逃がす場合は後でPort化🆔✨
    await this.repo.save({ id: taskId, title, completed: false });

    return ok({ taskId });
  }
}
```

> `crypto.randomUUID()` は「便利だけど差し替えたい」気持ちが出てくるやつ😆
> それを **第26章（Id/ClockのPort化）**で“綺麗に”する流れになるよ🆔⏰✨

---

## 6) クラス？関数？どっちがいいの？🤔✨

この講座のおすすめは👇

* **基本：クラスInteractor**（依存をconstructorで見せられて分かりやすい）🏗️✨
* ただし、依存が少ない・状態がないなら **関数Interactor** でもOK🙆‍♀️

初心者のうちは **「依存が見える」＝理解が早い**ので、まずクラスで統一が安全だよ😊💕

---

## 7) 命名と配置ルール（迷子ゼロのため）🗺️🧭

おすすめルール📌✨

* フォルダ名：`create-task` / `complete-task` / `list-tasks` みたいに **動詞＋目的**📝
* ファイル分割：

  * `XxxModels.ts`（Request/Response）📦
  * `XxxErrors.ts`（Failure）⚠️
  * `XxxInteractor.ts`（実行役）🎬
* `execute()` 以外の名前を増やさない（迷いが増えるから）🧠💥

---

## 8) AI相棒🤖✨（コピペ用プロンプト）

### テンプレ生成🧱

```text
CreateTask の UseCase テンプレを TypeScript で作って。
条件：
- execute(request): Promise<Result<response, failure>> 形式
- Request/Response/Failure を別ファイルに分ける
- 外側の言葉（HTTP/SQL/Express等）を一切出さない
- repo は Port(interface) として注入する
```

### “混ざり”チェック🧼

```text
この UseCase 実装に「外側の都合（HTTP/DB/フレームワーク）」が混ざってないか監査して。
混ざってる行を指摘して、分離案も出して。
```

---

## 9) 理解チェック✅💡（1問だけ）

**Q.** Use Case の `execute()` の戻り値を `Promise` に統一しておくと、何が嬉しい？🧠✨
（ヒント：テスト、IO、差し替え、のどれか🎯）

---

## 10) 提出物（成果物）📦🎁

* `Result.ts` / `UseCase.ts` を `_shared` に作る✅
* `CreateTask` の

  * `Models` / `Errors` / `Interactor` を作って **コンパイル通る状態**にする✅
* ついでに（余裕あれば）`CompleteTask` / `ListTasks` も “型だけ” 作ると最高🥳🎉

---

次の第15章では、この型にピッタリはまる **Requestモデル（Input Boundary）**を作っていくよ📥✨
「外側の入力を内側に入れる“整形口”」ってやつね😊🧼💕

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://vitest.dev/api/expect.html?utm_source=chatgpt.com "expect"
[4]: https://www.infoq.com/news/2025/12/vitest-4-browser-mode/?utm_source=chatgpt.com "Vitest Team Releases Version 4.0 with Stable Browser ..."
