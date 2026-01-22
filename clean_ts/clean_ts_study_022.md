# 第22章：UseCaseテスト：Port差し替えで検証🧪🎭✨

この章は「外側（DB/HTTP/UI）が無くても、UseCaseが正しいって証明できる！」を体で覚える回だよ〜😊💖
ポイントは **Portを“テスト用に差し替える”** こと！🔌🔁

---

## 1) この章のゴール🎯✨

* UseCaseを **外部なし（DBなし/HTTPなし）** でテストできるようになる🙌
* Portを **Fake/Stub/Spy** に差し替えて、成功/失敗を全部検証できる✅
* 「中心が壊れてない」安心感を **テストで常設** できるようになる🛡️💕

---

## 2) まず“差し替え”の意味を一言で📌

**UseCaseが依存するのはPortだけ**だから、テストではそのPortを
🧠 本物（SQLiteなど） → 🎭 偽物（Fakeなど）
に置き換えればOK！

これがクリーンアーキの“勝ち筋”の1つだよ💘

---

## 3) テストダブル（偽物）3兄弟👯‍♀️✨

* **Stub**：決まった値を返すだけ（例：findByIdが必ずTaskを返す）📦
* **Fake**：簡易だけど動く実装（例：Mapで保存できるRepository）🗃️
* **Spy**：呼ばれた回数・引数を記録する（例：saveが呼ばれた？）👀

Vitestなら `vi.fn()` や `vi.spyOn()` でSpyが作れるよ〜🕵️‍♀️✨ ([Vitest][1])

---

## 4) この章で使うテスト環境（2026時点の定番寄り）🧰✨

ここでは **Vitest** でいくよ！軽くて速くて、TSでも扱いやすい🙆‍♀️💨
（VitestはViteベースの“次世代テスト”って位置づけだよ） ([Vitest][2])

### インストール（例）

```powershell
npm i -D vitest typescript @types/node
```

### `vitest.config.ts`（最小）

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'node',
    include: ['test/**/*.test.ts'],
    clearMocks: true,
  },
})
```

設定の考え方は公式のConfig説明に沿ってるよ🧩 ([Vitest][3])

### `package.json`（例）

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run"
  }
}
```

---

## 5) テスト対象の前提（最低限だけ）🧱✨

この章では、UseCaseがこんなPortを使う想定にするね👇

* `TaskRepository`（保存/取得/一覧）
* `IdGenerator`（ID生成）
* `Clock`（現在時刻）

---

## 6) テスト用の差し替えPortを作ろう🎭🔧

### 6-1) Port定義（例）

```ts
// src/ports/TaskRepository.ts
import { Task } from '../entities/Task'

export interface TaskRepository {
  save(task: Task): Promise<void>
  findById(id: string): Promise<Task | null>
  list(): Promise<Task[]>
}

// src/ports/IdGenerator.ts
export interface IdGenerator {
  newId(): string
}

// src/ports/Clock.ts
export interface Clock {
  now(): Date
}
```

### 6-2) Fake Repository（Mapで保存できるやつ）🗃️✨

```ts
// test/doubles/FakeTaskRepository.ts
import { TaskRepository } from '../../src/ports/TaskRepository'
import { Task } from '../../src/entities/Task'

export class FakeTaskRepository implements TaskRepository {
  private store = new Map<string, Task>()

  async save(task: Task): Promise<void> {
    this.store.set(task.id, task)
  }

  async findById(id: string): Promise<Task | null> {
    return this.store.get(id) ?? null
  }

  async list(): Promise<Task[]> {
    return [...this.store.values()]
  }

  seed(tasks: Task[]) {
    for (const t of tasks) this.store.set(t.id, t)
  }
}
```

### 6-3) 固定IdGenerator / 固定Clock（テストを安定させる）🆔⏰✨

```ts
// test/doubles/FixedIdGenerator.ts
import { IdGenerator } from '../../src/ports/IdGenerator'

export class FixedIdGenerator implements IdGenerator {
  constructor(private readonly fixed: string) {}
  newId(): string {
    return this.fixed
  }
}

// test/doubles/FixedClock.ts
import { Clock } from '../../src/ports/Clock'

export class FixedClock implements Clock {
  constructor(private readonly fixed: Date) {}
  now(): Date {
    return this.fixed
  }
}
```

---

## 7) UseCaseテスト①：CreateTask を検証🧪✅

### 7-1) Result型（成功/失敗の戻り値を統一）📦✨

```ts
// src/shared/Result.ts
export type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E }
```

### 7-2) CreateTaskInteractor（ざっくり形）

```ts
// src/usecases/createTask/CreateTaskInteractor.ts
import { TaskRepository } from '../../ports/TaskRepository'
import { IdGenerator } from '../../ports/IdGenerator'
import { Clock } from '../../ports/Clock'
import { Result } from '../../shared/Result'
import { Task } from '../../entities/Task'

export type CreateTaskError = { type: 'InvalidTitle' }
export type CreateTaskResponse = { taskId: string }

export class CreateTaskInteractor {
  constructor(
    private readonly repo: TaskRepository,
    private readonly idGen: IdGenerator,
    private readonly clock: Clock,
  ) {}

  async execute(input: { title: string }): Promise<Result<CreateTaskResponse, CreateTaskError>> {
    const title = input.title.trim()
    if (title.length === 0) return { ok: false, error: { type: 'InvalidTitle' } }

    const id = this.idGen.newId()
    const now = this.clock.now()

    const task = Task.create({ id, title, createdAt: now })
    await this.repo.save(task)

    return { ok: true, value: { taskId: id } }
  }
}
```

### 7-3) テスト：成功ケース🎉

```ts
// test/usecases/createTask.test.ts
import { describe, it, expect } from 'vitest'
import { CreateTaskInteractor } from '../../src/usecases/createTask/CreateTaskInteractor'
import { FakeTaskRepository } from '../doubles/FakeTaskRepository'
import { FixedIdGenerator } from '../doubles/FixedIdGenerator'
import { FixedClock } from '../doubles/FixedClock'

describe('CreateTaskInteractor', () => {
  it('正常：保存されてidが返る✅', async () => {
    const repo = new FakeTaskRepository()
    const idGen = new FixedIdGenerator('T-001')
    const clock = new FixedClock(new Date('2026-01-23T00:00:00.000Z'))

    const uc = new CreateTaskInteractor(repo, idGen, clock)
    const result = await uc.execute({ title: 'Buy milk' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.taskId).toBe('T-001')

    const saved = await repo.findById('T-001')
    expect(saved?.title).toBe('Buy milk')
    expect(saved?.completed).toBe(false)
  })
})
```

### 7-4) テスト：失敗ケース（タイトル不正）⚠️

```ts
import { describe, it, expect } from 'vitest'
import { CreateTaskInteractor } from '../../src/usecases/createTask/CreateTaskInteractor'
import { FakeTaskRepository } from '../doubles/FakeTaskRepository'
import { FixedIdGenerator } from '../doubles/FixedIdGenerator'
import { FixedClock } from '../doubles/FixedClock'

describe('CreateTaskInteractor (invalid)', () => {
  it('異常：空タイトルならInvalidTitle❌', async () => {
    const repo = new FakeTaskRepository()
    const uc = new CreateTaskInteractor(
      repo,
      new FixedIdGenerator('T-999'),
      new FixedClock(new Date('2026-01-23T00:00:00.000Z')),
    )

    const result = await uc.execute({ title: '   ' })

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.type).toBe('InvalidTitle')

    // ついでに「保存されてない」も確認すると強い💪✨
    const saved = await repo.findById('T-999')
    expect(saved).toBeNull()
  })
})
```

---

## 8) UseCaseテスト②：CompleteTask を検証🔁✅🧪

### 8-1) ありがち観点（ここ超大事）💡

* ないID → NotFoundになる？😵
* すでに完了 → AlreadyCompletedになる？😵‍💫
* 正常 → 完了状態が更新され保存される？🎉

Fake repoにseedしてからテストするとラクだよ〜🌱

（※ここはあなたの `CompleteTaskInteractor` の設計に合わせて、同じ要領でテストを書けばOK🙆‍♀️✨）

---

## 9) UseCaseテスト③：ListTasks を検証👀🧪✨

Listは「入ってるものが、ちゃんと返る」が基本！
Fake repoにタスクを詰めて、Responseの形だけ確認すれば十分強いよ💪💕

---

## 10) Spy（vi.fn）で“呼ばれ方”も確認したい時👀✨

「saveが呼ばれたか？」みたいな確認はSpyが便利！
Vitestの `vi.fn()` / `vi.spyOn()` を使うよ🕵️‍♀️ ([Vitest][1])

```ts
import { vi, expect } from 'vitest'

const repo = {
  save: vi.fn(async () => {}),
  findById: vi.fn(async () => null),
  list: vi.fn(async () => []),
}

expect(repo.save).toHaveBeenCalledTimes(1)
```

ただしね👇
✅ **状態で証明できるなら状態テスト（Fake）優先**
👀 **どうしても呼び出し回数/順番が大事な時だけSpy**
って覚えると、テストが“壊れにくく”なるよ〜💖

---

## 11) よくある落とし穴あるある😇💥

* **テストにSQLiteやHTTPが混ざる** → それ統合テスト側！この章は“中心だけ”🧼
* **Date.now() を直接使ってテストが不安定** → Clock差し替えで固定⏰✅
* **IDがランダムで比較できない** → IdGenerator固定🆔✅
* **エラーが文字列バラバラ** → Result＋Error型で統一📦✅

---

## 12) この章の提出物📦✨

* `FakeTaskRepository`（Map版）🗃️
* `FixedClock` / `FixedIdGenerator` ⏰🆔
* 3UseCaseそれぞれのテスト

  * 成功✅
  * 失敗（最低1つ）⚠️

---

## 13) 理解チェック（1問）📝💖

**Q.** なぜUseCaseテストでDBを立ち上げなくていいの？
（ヒント：UseCaseは何に依存してる？🔌）

---

## 14) AI相棒プロンプト（コピペ用）🤖✨

```text
あなたはクリーンアーキテクチャの講師です。
TypeScriptのUseCaseテストを書きたいです。

- 対象UseCase: {CreateTask | CompleteTask | ListTasks}
- Port: TaskRepository / Clock / IdGenerator
- テストランナー: Vitest
- 方針: PortをFake/Stubに差し替えて、外部（DB/HTTP）なしで検証したい

要件:
1) 成功ケースのテスト
2) 失敗ケースのテスト（ドメインエラー）
3) FakeTaskRepository（Map実装）
4) テストが壊れにくい観点（状態テスト優先）

コードを最小構成で提案してください。
```

---

## ちょい最新メモ（環境の安心材料）🧷✨

Nodeは2026年1月時点で **v24系(LTS)** のリリースが継続してるよ（同日にv22 LTSもセキュリティ更新あり）。 ([nodejs.org][4])
（ここは“選ぶ時の目安”ね😊）

---

次は、第22章の流れのまま **「CompleteTask / ListTasks のテストを、あなたの実装に合わせて具体コード化」** まで一気に仕上げてもいいよ〜🥳💖
（今のあなたの `Interactor` と `Port` の型を貼ってくれたら、ピタッと合わせて書くよ✍️✨）

[1]: https://vitest.dev/api/mock?utm_source=chatgpt.com "Mocks"
[2]: https://vitest.dev/?utm_source=chatgpt.com "Vitest | Next Generation testing framework"
[3]: https://vitest.dev/config/?utm_source=chatgpt.com "Configuring Vitest"
[4]: https://nodejs.org/en/blog/release/v24.13.0?utm_source=chatgpt.com "Node.js 24.13.0 (LTS)"
