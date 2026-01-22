# 第35章：Outbound Adapter：InMemory Repository実装🧺✅

この章は「Port（TaskRepository）を満たす、最小の“外側実装”」を作って、**差し替えの気持ちよさ**を最速で体験する回だよ〜！😊✨
DBなしで動くから、まずはここで “クリーンアーキの型” を体に入れちゃおう💪🧠

※参考：2026/01/23時点の周辺最新情報として、TypeScriptはnpm上で 5.9.3 が最新、Node.jsは v24 がLTS（Active LTS）で、Node v20で組み込みテストランナーが stable 扱いになってるよ〜。([npm][1])

---

## 1) InMemory Repositoryってなに？🧺💡

**Repository Port（内側が欲しい能力）**を、**メモリ上のMap**で実現する “外側の実装（Adapter）” だよ😊

### うれしいこと😍

* DBがなくてもアプリが動く✅
* テストや動作確認がめちゃ速い⚡
* 「差し替え」デモが簡単（次章のSQLite実装と交換できる）🔁✨

### 注意点⚠️

* プロセスが落ちたらデータは消える（永続化しない）🫥
* 複数台/複数プロセスでは共有できない（メモリは別々）🧩

---

## 2) まず“Port”を確認しよう🔌👀

すでに作ってある想定だけど、章が単体で読めるように最小例を置くね😊
（メソッド名はあなたのPortに合わせて読み替えてOKだよ！）

```ts
// src/usecases/ports/TaskRepository.ts
import { Task } from "../../entities/Task";

export interface TaskRepository {
  save(task: Task): Promise<void>;
  findById(id: string): Promise<Task | null>;
  list(): Promise<Task[]>;
}
```

ポイントはこれだけ🎯

* UseCaseは **この interface しか知らない**
* InMemory / SQLite は **同じ interface を実装**
  → だから差し替えできる🔁✨

---

## 3) 実装方針：Mapで持つのが一番ラク🗺️✨

JSの `Map` は **挿入順で反復できる**から、`list()` を作るのがラクだよ😊
（`values()` が挿入順で回る）([MDNウェブドキュメント][2])

ここでは、

* `Map<string, Task>` に入れる（最小版）
* 返り値は配列にして返す（`Array.from(...)`）

って作るよ〜🧺✅

---

## 4) InMemoryTaskRepository（最小版）🧺✅

置き場所の例：`src/adapters/outbound/inmemory/InMemoryTaskRepository.ts`

```ts
// src/adapters/outbound/inmemory/InMemoryTaskRepository.ts
import { TaskRepository } from "../../../usecases/ports/TaskRepository";
import { Task } from "../../../entities/Task";

export class InMemoryTaskRepository implements TaskRepository {
  private readonly store = new Map<string, Task>();

  async save(task: Task): Promise<void> {
    this.store.set(task.id, task);
  }

  async findById(id: string): Promise<Task | null> {
    return this.store.get(id) ?? null;
  }

  async list(): Promise<Task[]> {
    return Array.from(this.store.values());
  }

  // あると便利（テスト/デモ用）🧪✨
  async clear(): Promise<void> {
    this.store.clear();
  }
}
```

### できた！🎉 これで「外側の実装」が1個できたよ😊✨

---

## 5) でも“落とし穴”があるよ⚠️🕳️（めっちゃ大事）

この最小版は、**同じTaskインスタンスをそのまま保持して、そのまま返す**よね。

つまり…

* 取得した側が `task.complete()` とかして変更すると
  → Repository内にある同じインスタンスも変わる😳

これは「EntityがミュータブルでもOK」な設計なら問題にならないことも多いけど、
テストで「いつ変更されたっけ？」が分かりづらくなることがあるよ〜🌀

---

## 6) 安全寄りの改良：Snapshotを保存して“復元”する📸🔁

「共有参照がイヤ！」ってときは、**プリミティブのSnapshotを保存**して、取り出すときに復元するのが安定だよ😊✨

例（Taskが `toSnapshot()` / `rehydrate()` を持てる想定）：

```ts
// 例：Entities側（イメージ）
export type TaskSnapshot = {
  id: string;
  title: string;
  completed: boolean;
  createdAt: string; // ISO
};

export class Task {
  constructor(
    public readonly id: string,
    private _title: string,
    private _completed: boolean,
    private _createdAt: Date
  ) {}

  get title() { return this._title; }
  get completed() { return this._completed; }
  get createdAt() { return this._createdAt; }

  complete() { this._completed = true; }

  toSnapshot(): TaskSnapshot {
    return {
      id: this.id,
      title: this._title,
      completed: this._completed,
      createdAt: this._createdAt.toISOString(),
    };
  }

  static rehydrate(s: TaskSnapshot): Task {
    return new Task(s.id, s.title, s.completed, new Date(s.createdAt));
  }
}
```

この形ならRepositoryはこうできる👇

```ts
import { TaskRepository } from "../../../usecases/ports/TaskRepository";
import { Task, TaskSnapshot } from "../../../entities/Task";

export class InMemoryTaskRepository implements TaskRepository {
  private readonly store = new Map<string, TaskSnapshot>();

  async save(task: Task): Promise<void> {
    this.store.set(task.id, task.toSnapshot());
  }

  async findById(id: string): Promise<Task | null> {
    const snap = this.store.get(id);
    return snap ? Task.rehydrate(snap) : null;
  }

  async list(): Promise<Task[]> {
    return Array.from(this.store.values()).map(Task.rehydrate);
  }

  async clear(): Promise<void> {
    this.store.clear();
  }
}
```

どっちを採用する？🤔

* **最小版**：ラク！学習向き！🧺
* **Snapshot版**：テスト安定・事故りにくい！📸✨

この講座的には、まず最小版→余裕が出たらSnapshot版がオススメだよ😊

---

## 7) 使い方（Composition Rootで注入）💉🏗️

「UseCaseはPortしか知らない」ので、組み立て側で注入するよ✨

```ts
import { InMemoryTaskRepository } from "./adapters/outbound/inmemory/InMemoryTaskRepository";
import { CreateTaskInteractor } from "./usecases/CreateTaskInteractor";

const taskRepo = new InMemoryTaskRepository();

const createTask = new CreateTaskInteractor(taskRepo /*, 他のPort */);
```

この状態でアプリは **DBなしで動く**✅
次章でSQLite版を作ったら、ここを差し替えるだけでOKになるよ🔁😊

---

## 8) テスト（Vitestでサクッと）🧪✨

Vitestは 2025/10 に v4 が出ていて、移行ガイドも整ってるよ。([Vitest][3])
（もちろんJestでもOKだけど、速くて気軽なのが嬉しいやつ😊）

### テスト観点🎯

* saveしたらfindByIdで取れる✅
* listで保存した順に並ぶ✅（Mapは挿入順で反復される）([MDNウェブドキュメント][2])

```ts
// test/InMemoryTaskRepository.test.ts
import { describe, it, expect, beforeEach } from "vitest";
import { InMemoryTaskRepository } from "../src/adapters/outbound/inmemory/InMemoryTaskRepository";
import { Task } from "../src/entities/Task";

describe("InMemoryTaskRepository", () => {
  let repo: InMemoryTaskRepository;

  beforeEach(async () => {
    repo = new InMemoryTaskRepository();
    await repo.clear();
  });

  it("save -> findById で取得できる", async () => {
    const task = new Task("t1", "Buy milk", false, new Date());
    await repo.save(task);

    const found = await repo.findById("t1");
    expect(found).not.toBeNull();
    expect(found?.id).toBe("t1");
    expect(found?.title).toBe("Buy milk");
  });

  it("list は保存順に並ぶ", async () => {
    await repo.save(new Task("t1", "A", false, new Date()));
    await repo.save(new Task("t2", "B", false, new Date()));

    const list = await repo.list();
    expect(list.map(t => t.id)).toEqual(["t1", "t2"]);
  });
});
```

※あなたのTaskのconstructor形が違うなら、そこだけ合わせてね😊✨

---

## 9) この章の“設計のコツ”まとめ🧠✨

### ✅守れてたら勝ち🎉

* UseCaseはRepositoryの **実体（InMemory/SQLite）を知らない**
* AdapterはPortを **ちゃんと実装**してる
* Composition Rootで **差し替え**できる

### 💥ありがちな事故😵

* UseCase内で `new InMemoryTaskRepository()` しちゃう
  → 差し替え不能！依存ルール的にもアウト寄り💦
* Adapterの都合でPortを変えちゃう
  → 内側が外側に引っ張られる🌀

---

## 10) 到達目標・チェック問題・提出物・AIプロンプト🎁🤖✨

### 🎯 到達目標（1文）

InMemoryで `TaskRepository` を実装し、UseCaseへ注入して動かせる😊✅

### ✅ 理解チェック（1問）

「UseCaseがRepositoryの具体クラスを知らない」状態って、コードのどこを見ると確認できる？👀🔎

### 📦 提出物（成果物）

* `InMemoryTaskRepository` の実装（最小版 or Snapshot版）🧺
* `save/findById/list` のテスト2本以上🧪✨

### 🤖 AIプロンプト（コピペ用）

```text
TaskRepository interface を満たす InMemoryTaskRepository を TypeScript で実装して。
要件：
- Map を使って保存
- save/findById/list を実装
- list は保存順
- 可能なら共有参照を避ける設計（snapshot保存→復元案）も提案して
```

---

次の第36章でSQLite版を作ると、**「外側だけ交換して中心は無傷」**が完成するよ〜！🎉🔁✨

[1]: https://www.npmjs.com/package/typescript?activeTab=versions&utm_source=chatgpt.com "typescript"
[2]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map?utm_source=chatgpt.com "Map - JavaScript - MDN Web Docs - Mozilla"
[3]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
