# 第26章：副作用Port（Clock/Idなど）の最小抽象 ⏰🆔✨

## 0. 今日のゴール 🎯

この章が終わると…👇

* 「時間」と「ID」を **UseCaseの外に追い出す** 理由がわかる😳
* **Clock / IdGenerator という最小Port** を作れる🧩
* テストで **日付もIDも固定** できて、テストが安定する🧪✨

---

## 1. なんで “時間” と “ID” が問題になるの？😵‍💫

時間とIDって、ついこう書いちゃうよね👇

```ts
const now = new Date();
const id = crypto.randomUUID();
```

でもこれ、UseCaseの中に入ると地味に困るの…😭💦

### 困りポイント①：テストが不安定になる🧪💣

* `new Date()` は実行するたび違う
* `randomUUID()` も毎回違う
  → 期待値が固定できなくて、テストが「運ゲー」になりがち🎰😇

### 困りポイント②：UseCaseが “外側の都合” を抱える🌪️

時間・乱数・環境依存って、**副作用（side effect）** の代表格。
クリーンアーキ的には、UseCaseは **外側の都合を知らない** のが理想だよね🧼✨

---

## 2. “最小抽象” の考え方 🌱

ここ超大事〜！📌
抽象化ってやりすぎると、逆にわけわかめになる🍜😇

だから今回はこうする👇

* **必要な能力だけ** をPortにする
* メソッドは **1個でOK**
* 型も **迷わない形** にする

---

## 3. Portの設計：Clock と IdGenerator を作る🧩✨

### 3.1 Clock Port ⏰

「今の時刻ちょうだい」だけ言えればOK👍

```ts
// src/ports/Clock.ts
export interface Clock {
  now(): Date;
}
```

> `Date` を返すのがわかりやすい版ね😊
> （あとで「numberで返す版」も紹介するよ〜）

---

### 3.2 IdGenerator Port 🆔

「新しいIDちょうだい」だけでOK👍

```ts
// src/ports/IdGenerator.ts
export interface IdGenerator {
  newId(): string;
}
```

ここで `string` にしておくと超ラク😌✨
（Entity側で `TaskId` をちゃんとした型にしたくなったら、あとで強化できるよ💪）

---

## 4. “外側” の実装例（Adapter/Driver側）⚙️✨

### 4.1 SystemClock（本物の時間）🕰️

```ts
// src/drivers/SystemClock.ts
import type { Clock } from "../ports/Clock";

export class SystemClock implements Clock {
  now(): Date {
    return new Date();
  }
}
```

---

### 4.2 UUIDの生成（randomUUID）🆔✨

UUID v4 を作るなら `crypto.randomUUID()` が超お手軽🙌
ブラウザの Web Crypto としても使えるし、Nodeでも使える場面が多いよ〜😊
MDNでも `Crypto.randomUUID()` は v4 UUID 生成って説明されてるよ📚✨ ([MDNウェブドキュメント][1])

#### Node向け（`node:crypto` を使う版）🧰

```ts
// src/drivers/UuidGenerator.node.ts
import type { IdGenerator } from "../ports/IdGenerator";
import { randomUUID } from "node:crypto";

export class UuidGenerator implements IdGenerator {
  newId(): string {
    return randomUUID();
  }
}
```

> Nodeのリリース状況は変わりやすいけど、2026-01-12時点で v24 が Active LTS になってるのが公式一覧で確認できるよ📌 ([Node.js][2])

#### ブラウザ向け（`globalThis.crypto` を使う版）🌐

```ts
// src/drivers/UuidGenerator.browser.ts
import type { IdGenerator } from "../ports/IdGenerator";

export class UuidGenerator implements IdGenerator {
  newId(): string {
    return globalThis.crypto.randomUUID();
  }
}
```

`Crypto.randomUUID()` は幅広く使える機能として整理されてるよ🧡（対応状況の目安も確認できる） ([Can I Use][3])

---

## 5. UseCaseに注入して使う（ここがキモ！）💉✨

例：CreateTask で「作成日時」と「ID」を使うケース🎀

```ts
// src/usecases/CreateTaskInteractor.ts
import type { Clock } from "../ports/Clock";
import type { IdGenerator } from "../ports/IdGenerator";
import type { TaskRepository } from "../ports/TaskRepository"; // 25章で作った想定

export class CreateTaskInteractor {
  constructor(
    private readonly repo: TaskRepository,
    private readonly clock: Clock,
    private readonly ids: IdGenerator,
  ) {}

  async execute(title: string) {
    const id = this.ids.newId();
    const createdAt = this.clock.now();

    const task = { id, title, completed: false, createdAt }; // Entity化しててもOK👌
    await this.repo.save(task);

    return { id };
  }
}
```

UseCaseが **時計もUUIDも直接知らない** 状態になったね🥳🎉

---

## 6. テストがめっちゃ楽になる（FixedClock / FixedId）🧪🎭✨

### 6.1 固定Clock ⏰🧊

```ts
// test/fakes/FixedClock.ts
import type { Clock } from "../../src/ports/Clock";

export class FixedClock implements Clock {
  constructor(private readonly fixed: Date) {}
  now(): Date {
    return this.fixed;
  }
}
```

### 6.2 連番IdGenerator 🆔📦

```ts
// test/fakes/SequenceIdGenerator.ts
import type { IdGenerator } from "../../src/ports/IdGenerator";

export class SequenceIdGenerator implements IdGenerator {
  private i = 0;
  constructor(private readonly ids: string[]) {}
  newId(): string {
    const v = this.ids[this.i];
    this.i++;
    if (!v) throw new Error("No more ids!");
    return v;
  }
}
```

### 6.3 テスト例（期待値が固定できる🥰）

```ts
import { CreateTaskInteractor } from "../src/usecases/CreateTaskInteractor";
import { FixedClock } from "./fakes/FixedClock";
import { SequenceIdGenerator } from "./fakes/SequenceIdGenerator";

test("CreateTask sets id and createdAt deterministically", async () => {
  const repo = /* InMemoryTaskRepository を用意（35章あたり） */;
  const clock = new FixedClock(new Date("2026-01-01T00:00:00.000Z"));
  const ids = new SequenceIdGenerator(["task-001"]);

  const uc = new CreateTaskInteractor(repo, clock, ids);
  const res = await uc.execute("Buy milk");

  expect(res.id).toBe("task-001");

  const saved = await repo.findById("task-001");
  expect(saved.createdAt.toISOString()).toBe("2026-01-01T00:00:00.000Z");
});
```

これでテストが **安定・爆速・気持ちいい** 🥹💖

---

## 7. よくある落とし穴あるある🚧😇

### 7.1 抽象化しすぎて “Port地獄” 🕳️

「文字列整形Port」「配列ソートPort」…みたいに増やすと破綻しがち😂
✅ 目安：**環境依存／非決定（毎回変わる）／テストで困る** ならPort候補！

### 7.2 Clockが `Date` を返すとミューテーション事故😵

`Date` は変更可能だから、心配ならこういう設計もアリ👇

* `now(): number`（epoch ms）にする
* `return new Date(this.fixed.getTime())` みたいにコピーして返す

初心者のうちは `Date` でOK、慣れたら強化で十分だよ😊✨

---

## 8. 章末チェックリスト ✅✨

* [ ] UseCase内に `new Date()` が出てこない👀
* [ ] UseCase内に `randomUUID()` / `Math.random()` が出てこない👀
* [ ] `Clock` は `now()` だけ（増やしすぎない）
* [ ] `IdGenerator` は `newId()` だけ（増やしすぎない）
* [ ] テストで Clock/Id を差し替えて固定できる🧪🎭

---

## 9. ミニ課題 📝💖

1. `CompleteTaskInteractor` に `completedAt` を付けたくなったとして、Clockを注入して保存してみてね⏰✅
2. テストで「完了時刻が固定」になるのを確認してみてね🧪✨
3. `IdGenerator` を「キューが空なら例外」の仕様にして、テストも1本追加してみてね🆔💥

---

## 10. AI相棒プロンプト（コピペ用）🤖✨

* 🧠 **概念理解**：
  「クリーンアーキで、Clock と Id を Port 化する理由を、初心者に3行で説明して。例も1つつけて」

* 🧩 **最小設計レビュー**：
  「この Clock/IdGenerator interface、抽象化しすぎてない？最小に削るならどうする？」

* 🧪 **テスト改善**：
  「UseCaseテストで new Date() と randomUUID() を排除したい。FixedClock と SequenceIdGenerator を使う形に書き換えて」

---

## ちょい最新メモ 📰✨（2026/01/23 時点）

* TypeScript は npm 上で 5.9.3 が latest として表示されてるよ📌 ([npmjs.com][4])
* TypeScript 6.0/7.0 に向けた動き（Go移植など）も公式ブログで進捗が出てるよ🚀 ([Microsoft for Developers][5])

---

次の章（27章）は、このPortたちの **入出力モデル** を「外側都合にしない」って話に入っていくよ📦✨
必要なら、ここまでの `Clock/Id` を組み込んだ “最小フォルダ構成” もセットで作るよ〜📁🥳

[1]: https://developer.mozilla.org/en-US/docs/Web/API/Crypto/randomUUID?utm_source=chatgpt.com "Crypto: randomUUID() method - Web APIs | MDN"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://caniuse.com/mdn-api_crypto_randomuuid?utm_source=chatgpt.com "Crypto API: `randomUUID()` | Can I use... Support tables for ..."
[4]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[5]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
