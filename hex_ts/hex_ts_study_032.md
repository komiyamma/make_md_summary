# 32. テスト①：ユースケース単体テスト（最優先）🧪💪

([Past chat][1])([Past chat][2])([Past chat][3])([Past chat][4])([Past chat][5])

## 1) 今日やること（ざっくり）🎯

この章で作るのは「**ユースケースの単体テスト**」だよ😊
ポイントはこれだけ👇

* ✅ **DBもHTTPも触らない**（中心だけを試す🧠❤️）
* ✅ **Portは差し替える**（InMemoryでOK🔁）
* ✅ テストが **仕様書みたいに読める** ようにする📖✨

---

## 2) なんで“ユースケース”からテストするの？🧐💡

ユースケース（AddTodo / CompleteTodo / ListTodos）は、アプリの「判断」と「手順」が集まる場所だよね✨
ここをテストすると…

* 🔥 仕様が崩れてもすぐ気づける
* 🔁 入口（CLI→HTTP）を変えても安心
* 🧪 外側（DB/ファイル/ネット）が不安定でも、中心は安定して検証できる

つまり「中心を守る🛡️」が、**テストでも実現できる**ってこと😊💕

---

## 3) 今日のテスト戦略（結論）🧩

ユースケース単体テストの定番セットはこれ👇

* 🧠 **InMemoryRepository**（配列で保存するやつ）
* ⏰ **FakeClock**（固定時刻を返す）
* 🆔（必要なら）**FakeIdGenerator**（固定IDを返す）

外の都合をぜんぶ固定すると、テストが **爆速＆安定** になるよ🚀✨

---

## 4) テスト基盤（2026の定番寄り）⚙️✨

いま「爆速・TS相性よし」で選ばれがちなのが **Vitest** だよ🧪⚡
Vitest 4 系が現行メジャーで、VS Code連携も強い✨ ([Vitest][6])

> ちなみに Jest も現役で、Jest 30 が “Stable” 側にいるよ（好みで選んでOK）🧪 ([Jest][7])

### インストール（Vitest）

```bash
npm i -D vitest
```

### ついでにカバレッジ（あとで使う）

Vitest は起動時に必要パッケージのインストールを促してくれるけど、手で入れてもOK😊
V8 カバレッジならこれ👇 ([Vitest][8])

```bash
npm i -D @vitest/coverage-v8
```

### package.json にスクリプト追加（例）

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "coverage": "vitest run --coverage"
  }
}
```

### vitest.config.ts（最小）

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    // 迷ったらまずこれだけでOK😊
    globals: true
  }
})
```

---

## 5) テスト対象（今回はここだけ）🧠❤️

第32章で狙うのはこれ👇

* ✅ AddTodoUseCase：追加できる／できない
* ✅ CompleteTodoUseCase：完了できる／二重完了できない
* ✅ ListTodosUseCase：一覧がDTOで返る

そして重要なのが…
**ユースケースはI/Oを知らない**ので、テストでは **Outbound Port を差し替える**だけで動くはず✨

---

## 6) テスト用の“差し替え部品”を用意しよう🧰✨

### InMemoryTodoRepository（例）

（すでに Chapter 26 のを持ってるならそれを使ってOKだよ😊）

```ts
// src/adapters/outbound/InMemoryTodoRepository.ts
import type { TodoRepositoryPort } from '../../app/ports/TodoRepositoryPort'
import type { Todo } from '../../domain/Todo'

export class InMemoryTodoRepository implements TodoRepositoryPort {
  private todos: Todo[] = []

  async save(todo: Todo): Promise<void> {
    const i = this.todos.findIndex(t => t.id === todo.id)
    if (i >= 0) this.todos[i] = todo
    else this.todos.push(todo)
  }

  async findById(id: string): Promise<Todo | null> {
    return this.todos.find(t => t.id === id) ?? null
  }

  async findAll(): Promise<Todo[]> {
    return [...this.todos]
  }
}
```

### FakeClock（例）

```ts
// test/fakes/FakeClock.ts
import type { ClockPort } from '../../src/app/ports/ClockPort'

export class FakeClock implements ClockPort {
  constructor(private readonly fixed: Date) {}

  now(): Date {
    return this.fixed
  }
}
```

> 「時間」をPortにしておくと、**テストで一生ラク**だよ⏰✨（固定できるのが強すぎる）

---

## 7) まず1本！AddTodo の “成功テスト” を書く 🎉🧪

### テストの型（Arrange → Act → Assert）🧁

* 🍳 Arrange：準備
* ▶️ Act：実行
* ✅ Assert：確認

```ts
// test/usecases/AddTodoUseCase.test.ts
import { describe, it, expect } from 'vitest'
import { InMemoryTodoRepository } from '../../src/adapters/outbound/InMemoryTodoRepository'
import { FakeClock } from '../fakes/FakeClock'
import { AddTodoUseCase } from '../../src/app/usecases/AddTodoUseCase'

describe('AddTodoUseCase', () => {
  it('タイトルが正常なら Todo を追加できる ✅', async () => {
    // Arrange 🍳
    const repo = new InMemoryTodoRepository()
    const clock = new FakeClock(new Date('2026-01-23T00:00:00Z'))
    const useCase = new AddTodoUseCase(repo, clock)

    // Act ▶️
    const result = await useCase.execute({ title: '牛乳を買う' })

    // Assert ✅
    expect(result.title).toBe('牛乳を買う')
    expect(result.completed).toBe(false)

    const all = await repo.findAll()
    expect(all).toHaveLength(1)
    expect(all[0]!.title).toBe('牛乳を買う')
  })
})
```

この時点で「テストが文章っぽい」感じ出てきたでしょ？😊📖✨

---

## 8) AddTodo の “失敗テスト” を足す（仕様を守る🛡️）🚫🧪

「タイトル空は禁止」みたいなルールは、テストで固定しよ💪

```ts
import { describe, it, expect } from 'vitest'
import { InMemoryTodoRepository } from '../../src/adapters/outbound/InMemoryTodoRepository'
import { FakeClock } from '../fakes/FakeClock'
import { AddTodoUseCase } from '../../src/app/usecases/AddTodoUseCase'
import { ValidationError } from '../../src/domain/errors/ValidationError'

describe('AddTodoUseCase', () => {
  it('タイトルが空なら ValidationError 🚫', async () => {
    const repo = new InMemoryTodoRepository()
    const clock = new FakeClock(new Date('2026-01-23T00:00:00Z'))
    const useCase = new AddTodoUseCase(repo, clock)

    await expect(
      useCase.execute({ title: '' })
    ).rejects.toBeInstanceOf(ValidationError)

    const all = await repo.findAll()
    expect(all).toHaveLength(0)
  })
})
```

> ここでのコツ✨
> **失敗したときに「保存されてない」も確認**すると、事故が減るよ😊🧯

---

## 9) CompleteTodo のテスト（状態遷移の守り🧷✨）

やりたいのはこの3つ👇

* ✅ 未完了 → 完了できる
* 🚫 2回目の完了はできない
* 🚫 存在しないIDはエラー

```ts
import { describe, it, expect } from 'vitest'
import { InMemoryTodoRepository } from '../../src/adapters/outbound/InMemoryTodoRepository'
import { AddTodoUseCase } from '../../src/app/usecases/AddTodoUseCase'
import { CompleteTodoUseCase } from '../../src/app/usecases/CompleteTodoUseCase'
import { FakeClock } from '../fakes/FakeClock'
import { DomainError } from '../../src/domain/errors/DomainError'

describe('CompleteTodoUseCase', () => {
  it('未完了のTodoは完了できる ✅', async () => {
    const repo = new InMemoryTodoRepository()
    const clock = new FakeClock(new Date('2026-01-23T00:00:00Z'))

    const add = new AddTodoUseCase(repo, clock)
    const created = await add.execute({ title: 'レポート出す' })

    const complete = new CompleteTodoUseCase(repo, clock)
    const done = await complete.execute({ id: created.id })

    expect(done.completed).toBe(true)
  })

  it('完了の二重適用はエラー 🚫', async () => {
    const repo = new InMemoryTodoRepository()
    const clock = new FakeClock(new Date('2026-01-23T00:00:00Z'))

    const add = new AddTodoUseCase(repo, clock)
    const created = await add.execute({ title: '掃除する' })

    const complete = new CompleteTodoUseCase(repo, clock)
    await complete.execute({ id: created.id })

    await expect(
      complete.execute({ id: created.id })
    ).rejects.toBeInstanceOf(DomainError)
  })
})
```

---

## 10) ListTodos のテスト（DTOで返ってくるのが嬉しい📮✨）

ここで大事なのは👇

* ✅ **domain型を外に漏らさない**（DTOで返す）
* ✅ 並び順などがあるなら、テストで固定

```ts
import { describe, it, expect } from 'vitest'
import { InMemoryTodoRepository } from '../../src/adapters/outbound/InMemoryTodoRepository'
import { AddTodoUseCase } from '../../src/app/usecases/AddTodoUseCase'
import { ListTodosUseCase } from '../../src/app/usecases/ListTodosUseCase'
import { FakeClock } from '../fakes/FakeClock'

describe('ListTodosUseCase', () => {
  it('TodoがDTOの配列で返る 📝', async () => {
    const repo = new InMemoryTodoRepository()
    const clock = new FakeClock(new Date('2026-01-23T00:00:00Z'))

    const add = new AddTodoUseCase(repo, clock)
    await add.execute({ title: 'パン買う' })
    await add.execute({ title: 'メール返す' })

    const list = new ListTodosUseCase(repo, clock)
    const result = await list.execute({})

    expect(result.items).toHaveLength(2)
    expect(result.items[0]!).toHaveProperty('id')
    expect(result.items[0]!).toHaveProperty('title')
    expect(result.items[0]!).toHaveProperty('completed')
  })
})
```

---

## 11) テストを“仕様書っぽくする”コツ集 📖✨

テストって、読み物として強いとめちゃくちゃ価値が上がるよ😊💕

* 🏷️ `it('〜できる')` を **日本語で仕様っぽく**
* 🧁 Arrange/Act/Assert をコメントで分ける
* 🎁 期待値は「最小だけ」＋「大事な副作用（保存された）」を足す
* 🧨 バグりやすい境界値を先に書く（空文字、二重完了、存在しないID）

---

## 12) VS Codeで気持ちよく回す（実行・デバッグ）🧪🕵️‍♀️

Vitest は VS Code の拡張で、テストの実行・監視・デバッグがしやすいよ✨ ([Visual Studio Marketplace][9])

* ▶️ テスト横の再生ボタンで1本だけ実行
* 👀 watch で保存のたびに自動実行
* 🧷 ブレークポイント置いてデバッグもOK

---

## 13) ちょい足し：カバレッジ（あとで効くやつ）📊✨

「テストしてる気になってた…」を防ぐために、たまに見るのはアリ😊
Vitest は V8 / Istanbul を選べて、V8がデフォルトだよ📌 ([Vitest][8])

```bash
npm run coverage
```

Vitest 4 系ではカバレッジ周りに変更もあるから、更新時は migration をチラ見すると安心だよ👀✨ ([Vitest][10])

---

## 14) AI拡張の使い方（この章での正解🤖✨）

AIはここで超頼れるよ😆💕

### ✅ 使っていい（むしろ使うと速い）

* テストケースの洗い出し（境界値リスト化）📝
* AAAの雛形生成（describe/it の骨組み）🦴
* 失敗ケースの網羅チェック✅

### ⚠️ 注意（ここは自分で握る）

* Portの粒度を勝手に変える
* ユースケースに外側の型を混ぜる
* 例外方針を勝手に変える

### そのまま使えるお願いテンプレ🎁

* 「AddTodo/CompleteTodo/ListTodosの**仕様（成功/失敗）**を箇条書きで出して」
* 「各仕様を **it文（日本語）** にして」
* 「副作用（保存・更新）も確認するAssert案を足して」

---

## まとめ 🎁💖

* 🧪 まずは **ユースケース単体テスト** が最優先
* 🔁 Portは **InMemory/Fake** に差し替えて固定
* 📖 テストを **仕様書みたいに読む** を目指す

次の章（エラー設計）に進むと、今日書いたテストがさらに “設計のガードレール” になるよ🧯✨

[1]: https://chatgpt.com/c/6972381d-6360-8322-a0f0-bba36f098720 "設計教材のまとめ方"
[2]: https://chatgpt.com/c/6972d5db-f454-8322-bf2a-7212a0688408 "ユースケース入門①"
[3]: https://chatgpt.com/c/6972dd6c-8b24-8324-bcef-afba79d81688 "Hexagonal Ports Introduction"
[4]: https://chatgpt.com/c/6972d213-8ed8-8324-87a2-3964f9ec1c34 "ヘキサゴナル設計入門"
[5]: https://chatgpt.com/c/6972c89e-f628-8323-b961-a6c3c8dea31e "AI拡張準備ガイド"
[6]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[7]: https://jestjs.io/versions?utm_source=chatgpt.com "Jest Versions"
[8]: https://vitest.dev/guide/coverage.html "Coverage | Guide | Vitest"
[9]: https://marketplace.visualstudio.com/items?itemName=vitest.explorer&utm_source=chatgpt.com "Vitest"
[10]: https://vitest.dev/guide/migration.html?utm_source=chatgpt.com "Migration Guide"