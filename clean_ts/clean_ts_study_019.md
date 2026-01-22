# 第19章：CompleteTask を実装（更新系UseCaseの基本形）🔁✅✨

この章は「**更新系ユースケースの黄金パターン**」を、ミニTaskアプリでちゃんと体に入れる回だよ〜！💪😊
（Create が「追加」なら、Complete は「状態を変える」＝更新だね🗒️✅）

---

## まずは“今どきの前提”メモ（2026/01 時点）📌🧠

* TypeScript は npm の最新が **5.9.3**（現行の安定ライン）だよ✨ ([npm][1])
* TypeScript 6/7 は“これから”の大きな流れ（6は橋渡し、7はネイティブ化の流れが進行中）🛣️ ([Microsoft for Developers][2])
* テストは **Vitest 4 系**が主流の一角（4.0アナウンスあり）🧪✨ ([Vitest][3])
* Node は 24 系が Active LTS として動いてる（リリース一覧で確認できる）🟩 ([nodejs.org][4])

---

## この章のゴール🎯✨

CompleteTask を「中心を汚さず」に実装できるようになること！😊
具体的にはこの流れ👇を **迷わず**書けたら勝ち〜！🏆

1. **取得**（Repository Port）🔎
2. **Entity のメソッドで更新**（ルールは中心）🧠✅
3. **保存**（Repository Port）💾
4. **Response を返す**（表示都合はまだ持ち込まない）📦

---

## 更新系UseCaseの“あるある落とし穴”先に言うね⚠️😇

* 「完了済みをもう一回完了」ってどう扱う？（二重クリック問題）🖱️🖱️
* 「IDが存在しない」時に、どこで何を返す？🫥
* 「保存失敗（DB落ちた等）」をドメインエラーと混ぜない？🌩️
* 「UseCaseがDate生成しちゃう」問題（テストしづらい）⏰💦

この章では **“決め方”**ごと整理していくよ〜！🧡

---

## 1) Request / Response を用意する📥📤

更新系は入力がシンプルになりがち！今回は「完了したいTaskのID」だけでOK🙆‍♀️✨

```ts
// usecases/completeTask/CompleteTaskRequest.ts
export type CompleteTaskRequest = {
  taskId: string;
};
```

戻り値は、成功/失敗が分かる形にしておくと後がラク😊
（第21章の“境界で扱う”にも繋がるよ〜！）

```ts
// usecases/completeTask/CompleteTaskResponse.ts
import { Task } from "../../entities/Task";

export type CompleteTaskResponse =
  | { ok: true; task: Task }
  | { ok: false; error: CompleteTaskError };

export type CompleteTaskError =
  | { type: "TaskNotFound"; taskId: string }
  | { type: "AlreadyCompleted"; taskId: string }
  | { type: "InvalidTaskId"; taskId: string };
```

---

## 2) UseCase が触っていいのは Port だけ🔌✨

Repository と Clock（時間）を Port として受け取るよ〜⏰😊
（`new Date()` をUseCaseで直書きしないのがコツ！🧪💕

```ts
// usecases/ports/TaskRepository.ts
import { Task } from "../../entities/Task";

export interface TaskRepository {
  findById(id: string): Promise<Task | null>;
  save(task: Task): Promise<void>;
}
```

```ts
// usecases/ports/Clock.ts
export interface Clock {
  now(): Date;
}
```

---

## 3) Entity 側に「完了する」ルールがある前提にする🧠✅

Task エンティティは「外から直接 completed を書き換えさせない」スタイルが理想だよ🔒✨
ここでは最小イメージだけ置くね（すでに作ってるなら読み替えてOK！）

```ts
// entities/Task.ts
export class Task {
  constructor(
    public readonly id: string,
    public readonly title: string,
    public readonly completedAt: Date | null,
  ) {}

  complete(at: Date): { ok: true; task: Task } | { ok: false; error: "AlreadyCompleted" } {
    if (this.completedAt) return { ok: false, error: "AlreadyCompleted" };
    return { ok: true, task: new Task(this.id, this.title, at) };
  }
}
```

---

## 4) いよいよ CompleteTaskInteractor を実装する！🔁✅✨

ここが本番〜！💪😊
更新系は「取得→更新→保存」の順番を崩さないのが超大事だよ🧡

```ts
// usecases/completeTask/CompleteTaskInteractor.ts
import { TaskRepository } from "../ports/TaskRepository";
import { Clock } from "../ports/Clock";
import { CompleteTaskRequest } from "./CompleteTaskRequest";
import { CompleteTaskResponse } from "./CompleteTaskResponse";

export class CompleteTaskInteractor {
  constructor(
    private readonly repo: TaskRepository,
    private readonly clock: Clock,
  ) {}

  async execute(request: CompleteTaskRequest): Promise<CompleteTaskResponse> {
    // 1) 入力の最低限チェック（境界ほど厳密じゃなくてOK、でも安全にね😊）
    if (!request.taskId || request.taskId.trim().length === 0) {
      return { ok: false, error: { type: "InvalidTaskId", taskId: request.taskId } };
    }

    // 2) 取得
    const task = await this.repo.findById(request.taskId);
    if (!task) {
      return { ok: false, error: { type: "TaskNotFound", taskId: request.taskId } };
    }

    // 3) Entityで更新（ルールは中心！）
    const completed = task.complete(this.clock.now());
    if (!completed.ok) {
      return { ok: false, error: { type: "AlreadyCompleted", taskId: request.taskId } };
    }

    // 4) 保存
    await this.repo.save(completed.task);

    // 5) 応答
    return { ok: true, task: completed.task };
  }
}
```

---

## 5) “二重完了”はどうするのが良いの？🖱️🖱️🤔

ここ、実務でもめっちゃ出るやつ！😆

### 方針A：AlreadyCompleted を「失敗」として返す⚠️

* ルールが厳密で分かりやすい
* でもUIで二重クリックするとエラーになりがち💦

### 方針B：AlreadyCompleted を「成功扱い（冪等）」にする✅

* UI/通信の揺れに強い
* “完了してるならそれでOKだよね😊”が自然な場面が多い

ミニTaskなら **方針B**も全然アリだよ〜✨
やるなら Interactor のここを変えるだけ👇

```ts
// AlreadyCompleted を success 扱いにする例（冪等にする）
const completed = task.complete(this.clock.now());
if (!completed.ok) {
  return { ok: true, task }; // すでに完了してる状態をそのまま返す
}
```

---

## 6) テスト：Port差し替えで秒速で検証🧪🎭✨

Vitest 4 系で書く例だよ〜（最近の主流の一角）🧪✨ ([Vitest][3])

### Fake Repository（メモリ実装）🧺

```ts
// tests/fakes/FakeTaskRepository.ts
import { TaskRepository } from "../../src/usecases/ports/TaskRepository";
import { Task } from "../../src/entities/Task";

export class FakeTaskRepository implements TaskRepository {
  private store = new Map<string, Task>();

  seed(task: Task) {
    this.store.set(task.id, task);
  }

  async findById(id: string): Promise<Task | null> {
    return this.store.get(id) ?? null;
  }

  async save(task: Task): Promise<void> {
    this.store.set(task.id, task);
  }
}
```

### Fake Clock（時間固定）⏰

```ts
// tests/fakes/FakeClock.ts
import { Clock } from "../../src/usecases/ports/Clock";

export class FakeClock implements Clock {
  constructor(private readonly fixed: Date) {}
  now(): Date {
    return this.fixed;
  }
}
```

### テスト本体✅

```ts
// tests/completeTask.test.ts
import { describe, it, expect } from "vitest";
import { Task } from "../src/entities/Task";
import { CompleteTaskInteractor } from "../src/usecases/completeTask/CompleteTaskInteractor";
import { FakeTaskRepository } from "./fakes/FakeTaskRepository";
import { FakeClock } from "./fakes/FakeClock";

describe("CompleteTask", () => {
  it("タスクを完了にできる✅", async () => {
    const repo = new FakeTaskRepository();
    const now = new Date("2026-01-23T00:00:00.000Z");
    const clock = new FakeClock(now);

    repo.seed(new Task("t1", "write tests", null));

    const uc = new CompleteTaskInteractor(repo, clock);
    const res = await uc.execute({ taskId: "t1" });

    expect(res.ok).toBe(true);
    if (res.ok) {
      expect(res.task.completedAt?.toISOString()).toBe(now.toISOString());
    }
  });

  it("存在しないIDは NotFound 🫥", async () => {
    const repo = new FakeTaskRepository();
    const clock = new FakeClock(new Date());

    const uc = new CompleteTaskInteractor(repo, clock);
    const res = await uc.execute({ taskId: "nope" });

    expect(res.ok).toBe(false);
    if (!res.ok) {
      expect(res.error.type).toBe("TaskNotFound");
    }
  });
});
```

---

## 7) AI相棒に頼むならこのプロンプトが強いよ🤖✨

コピペでOK〜！💕

* 「更新系UseCaseの流れ（取得→更新→保存）で、漏れやすいチェック項目を列挙して」📝
* 「CompleteTaskInteractor を、例外（DB失敗）とドメイン失敗（AlreadyCompleted）を混ぜない設計に直して」🧠
* 「冪等（idempotent）にしたい。AlreadyCompleted を成功扱いにする場合の注意点を整理して」✅

---

## 8) 理解チェック（1問）📚✨

**Q.** CompleteTask で `new Date()` をUseCaseに直書きすると何が困る？😵‍💫
（ヒント：テスト🧪と再現性🎲）

---

## 9) 提出物（この章の成果物）📦✅

* `CompleteTaskInteractor`（取得→更新→保存の形で）🔁
* FakeRepository / FakeClock を使ったテスト2本以上🧪✨
* “AlreadyCompleted を失敗にするか成功にするか”の方針メモ（1行でOK）📝💕

---

必要なら次、**CompleteTask の Presenter 側でのエラー変換のイメージ**（「AlreadyCompleted をUIではどう見せる？」みたいなやつ😆）も、ちょい先取りで例を作れるよ〜！🎨✨

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[2]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[3]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
