## 第18章：CreateTask を実装（中心の流れを固める）✅🧩

この章は **「追加系UseCaseの王道テンプレ」** を完成させる回だよ〜！🥳
CreateTask が作れたら、以降の UseCase（Complete/List）もめちゃ作りやすくなる✨

---

# 1) CreateTask の責務（ここ大事）🎯

CreateTask（UseCase）はざっくりこう👇

* 📥 **入力を受け取る**（Request）
* 🧹 **入力を整える**（trim/最小バリデーション）
* ❤️ **中心ルールで Task を作る**（Entity の factory / ルール）
* 🔌 **Port に保存を頼む**（Repository）
* 📤 **結果を返す**（Response）

ポイントはこれ👇
UseCase は **「段取り係」** 🧑‍🍳✨
ドメインのルール（例：タイトル空はダメ）は **Entity側**に寄せるのがキレイ👍

---

# 2) 今回のゴール（完成イメージ）🧠✨

データの流れはこうなるよ👇

**Controller(UI) → CreateTaskRequest → CreateTaskInteractor → TaskRepository.save → CreateTaskResponse → Controller(UI)**

UseCaseは **DBもHTTPも知らない** 🙅‍♀️
知っていいのは **Port（インターフェース）** だけ🔌

---

# 3) まずは型を揃える（Request / Response / Error）📦

ここからコードいくね！✍️
（フォルダ例：`src/usecases/createTask/`）

### 3-1. Result 型（成功/失敗を統一）🎭

```ts
// src/shared/result.ts
export type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

export const Ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
export const Err = <E>(error: E): Result<never, E> => ({ ok: false, error });
```

---

### 3-2. CreateTask の Request / Response 📨📨

```ts
// src/usecases/createTask/createTaskModels.ts
export type CreateTaskRequest = {
  title: string;
};

export type CreateTaskResponse = {
  taskId: string;
};
```

最初はこれで十分！ミニアプリだしね🗒️✨

---

### 3-3. エラー型（内側の言葉で）⚠️

「失敗」を雑に `throw` しないで、**型で表現**していくよ💪✨

```ts
// src/usecases/createTask/createTaskErrors.ts
export type CreateTaskError =
  | { type: "InvalidTitle"; message: string }
  | { type: "PersistenceFailed"; message: string };
```

* `InvalidTitle` は **ドメイン寄り**（入力がダメ）
* `PersistenceFailed` は **技術寄り**（保存が失敗）

※ DBの例外そのまま見せないのがキレイ🙆‍♀️

---

# 4) Port（Repository / Id / Clock）を用意する 🔌🆔⏰

UseCase は「能力」が欲しいだけ。なので Port を生やす🌱

```ts
// src/ports/taskRepository.ts
import { Task } from "../entities/task";

export interface TaskRepository {
  save(task: Task): Promise<void>;
}
```

IDと時間も「外側都合」になりがちだから Port にするとテストが楽😍

```ts
// src/ports/idGenerator.ts
export interface IdGenerator {
  next(): string;
}
```

```ts
// src/ports/clock.ts
export interface Clock {
  now(): Date;
}
```

---

# 5) Entity（Task）側：中心ルールで作る ❤️🧱

UseCase が Task を雑に作らず、**Entity の入口で守る**🔒

```ts
// src/entities/task.ts
export class Task {
  private constructor(
    public readonly id: string,
    public readonly title: string,
    public readonly completed: boolean,
    public readonly createdAt: Date,
  ) {}

  static create(params: { id: string; title: string; createdAt: Date }) {
    const title = params.title.trim();

    if (title.length === 0) {
      return { ok: false as const, error: { type: "InvalidTitle" as const, message: "タイトルが空だよ🥺" } };
    }
    if (title.length > 100) {
      return { ok: false as const, error: { type: "InvalidTitle" as const, message: "タイトル長すぎ！100文字までだよ🥺" } };
    }

    return {
      ok: true as const,
      value: new Task(params.id, title, false, params.createdAt),
    };
  }
}
```

Entity の `create()` が **中心ルールの門番**だよ🛡️✨
ここに「絶対守りたい条件」を置くと、外側が増えても安心😊

---

# 6) いよいよ本体：CreateTaskInteractor を実装 ✅🧩

UseCase は Port を注入して動く！💉

```ts
// src/usecases/createTask/createTaskInteractor.ts
import { TaskRepository } from "../../ports/taskRepository";
import { IdGenerator } from "../../ports/idGenerator";
import { Clock } from "../../ports/clock";
import { Task } from "../../entities/task";
import { Result, Ok, Err } from "../../shared/result";
import { CreateTaskRequest, CreateTaskResponse } from "./createTaskModels";
import { CreateTaskError } from "./createTaskErrors";

export class CreateTaskInteractor {
  constructor(
    private readonly repo: TaskRepository,
    private readonly idGen: IdGenerator,
    private readonly clock: Clock,
  ) {}

  async execute(req: CreateTaskRequest): Promise<Result<CreateTaskResponse, CreateTaskError>> {
    // ① 入力を整える（外側のクセを落とす）
    const title = req.title ?? "";

    // ② Entityに作らせる（中心ルール）
    const created = Task.create({
      id: this.idGen.next(),
      title,
      createdAt: this.clock.now(),
    });

    if (!created.ok) {
      // EntityのエラーをUseCaseのエラーに整形
      return Err({ type: "InvalidTitle", message: created.error.message });
    }

    // ③ 保存（Port経由）
    try {
      await this.repo.save(created.value);
    } catch {
      return Err({ type: "PersistenceFailed", message: "保存に失敗したよ🥺" });
    }

    // ④ Response（外側の都合に寄せない）
    return Ok({ taskId: created.value.id });
  }
}
```

これが **「入力→ルール→保存→出力」** の基本形だよ✅✨

---

# 7) テストで「差し替え可能」を体感しよ🧪🎭

最近は **Vitest 4** が大きくアップデートされてるよ〜（2025年後半に v4 リリース）🧪✨ ([Vitest][1])
（TypeScript 5.9 が “最新” として案内されてるのもここで確認できるよ） ([TypeScript][2])

## 7-1. Fake を作る（Repository / Id / Clock）🧸

```ts
// src/usecases/createTask/createTaskInteractor.test.ts
import { describe, it, expect } from "vitest";
import { CreateTaskInteractor } from "./createTaskInteractor";
import { TaskRepository } from "../../ports/taskRepository";
import { IdGenerator } from "../../ports/idGenerator";
import { Clock } from "../../ports/clock";
import { Task } from "../../entities/task";

class FakeRepo implements TaskRepository {
  saved: Task[] = [];
  shouldFail = false;

  async save(task: Task): Promise<void> {
    if (this.shouldFail) throw new Error("boom");
    this.saved.push(task);
  }
}

class FixedId implements IdGenerator {
  constructor(private readonly id: string) {}
  next() { return this.id; }
}

class FixedClock implements Clock {
  constructor(private readonly date: Date) {}
  now() { return this.date; }
}

describe("CreateTaskInteractor", () => {
  it("成功：Taskを保存してtaskIdを返す✅", async () => {
    const repo = new FakeRepo();
    const uc = new CreateTaskInteractor(
      repo,
      new FixedId("task-001"),
      new FixedClock(new Date("2026-01-01T00:00:00.000Z")),
    );

    const res = await uc.execute({ title: "  buy milk  " });

    expect(res.ok).toBe(true);
    if (res.ok) {
      expect(res.value.taskId).toBe("task-001");
    }
    expect(repo.saved.length).toBe(1);
    expect(repo.saved[0].title).toBe("buy milk"); // trimされてる✨
  });

  it("失敗：タイトル空はInvalidTitle⚠️", async () => {
    const repo = new FakeRepo();
    const uc = new CreateTaskInteractor(repo, new FixedId("x"), new FixedClock(new Date()));

    const res = await uc.execute({ title: "   " });

    expect(res.ok).toBe(false);
    if (!res.ok) {
      expect(res.error.type).toBe("InvalidTitle");
    }
    expect(repo.saved.length).toBe(0); // 保存されない👍
  });

  it("失敗：保存に失敗したらPersistenceFailed⚠️", async () => {
    const repo = new FakeRepo();
    repo.shouldFail = true;

    const uc = new CreateTaskInteractor(repo, new FixedId("x"), new FixedClock(new Date()));

    const res = await uc.execute({ title: "ok" });

    expect(res.ok).toBe(false);
    if (!res.ok) {
      expect(res.error.type).toBe("PersistenceFailed");
    }
  });
});
```

これで「外側（repo）を差し替えても中心（UseCase）がテストできる」って体感できるはず😍✨

---

# 8) よくある落とし穴（先に潰す）🧯💥

* ❌ UseCase が `req.title` をそのまま DBに投げる
  → ✅ **Entityでtrim/ルールを守る**（中心の一貫性）
* ❌ UseCase が DB例外文をそのまま返す
  → ✅ **PersistenceFailed みたいな型に包む**
* ❌ Response に `Task` 丸ごと返す
  → ✅ **必要最低限の Response**（今回は taskId だけでOK）

---

# 9) AI相棒🤖✨に投げると強いプロンプト（コピペOK）

* 🤖「CreateTaskInteractor を Clean Architecture 的に実装して。依存は TaskRepository/IdGenerator/Clock の Port だけ。戻り値は Result 型で」
* 🤖「CreateTask の Vitest テストを3本（成功/入力失敗/保存失敗）で書いて。FakeRepo を使って」
* 🤖「Task Entity の create() に入れるべき不変条件を提案して。初心者向けに理由も添えて」

---

# 10) ミニ理解チェック✅📚

1. CreateTask が直接DBを触っちゃダメなのはなぜ？🔌
2. タイトル空のルールは UseCase と Entity、どっちに置くのが自然？❤️
3. `PersistenceFailed` みたいな「技術失敗」を型にするメリットは？⚠️

---

## ちょい最新メモ📰✨（今どきの周辺事情）

* TypeScript は公式ダウンロード案内で **5.9 が “currently”** 扱いになってるよ ([TypeScript][2])
* Node.js は **v24 が Active LTS**（2026年1月時点）で、v22 は Maintenance LTS だよ ([nodejs.org][3])

---

次の第19章（CompleteTask）に進むと、「取得→Entity更新→保存」の更新系テンプレも完成するよ🔁✅
同じ型（Result/Port）を使ってキレイに揃えていこ〜！🥰🎉

[1]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[2]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
