## 第37章：Mapper：DBレコード↔内側モデル変換を隔離🔄🧹

### 1) この章でできるようになること🎯✨

* DBの行（Row/Record）と、内側のEntity（Task）を**混ぜない**で変換できるようになる😌🧼
* 変換ロジックを**1か所に閉じ込めて**、修正をラクにする💪💛
* 「カラム名変更」「型変更」「NULL増えた」みたいなDBの揺れでも、中心が壊れにくくする🏛️🛡️

---

### 2) Mapperってなに？🤔🔄

Mapperは「外側のデータ（DBの行）」を「内側のモデル（Entity）」に変換する担当だよ🧑‍🍳✨
逆（Entity → DB用の形）もやるよ🔁

* DBの行：`completed_at` みたいな **snake_case**、`0/1` のboolean、`TEXT`の日時…ありがち🫠
* 内側のEntity：`completedAt: Date | null`、`completed: boolean`、命名は **業務の言葉**…がうれしい😊💕

つまりMapperは、**「ズレの吸収材」**🧽✨

---

### 3) なんで隔離が大事？（放置すると起きる悲劇）😱💥

Mapperがない（or いろんな場所に散ってる）と…

* UseCaseやEntityに `completed_at` とかSQL語彙が侵入する🐍➡️🏛️❌
* 画面やAPIが増えるたびに、変換がコピペ地獄になる📎📎📎
* DBの変更が入ると、あちこちでバグる（しかも見落とす）🧨😇

隔離すると…

* DB変更は **Mapperだけ直せばOK** になりやすい✅✨
* 変換の「正解」が1つになる（迷子にならない）🧭😊

---

### 4) 置き場所（おすすめ）📁✨

Interface Adapters層（Adapter側）にまとめるのがコツだよ🧼🔁

例（雰囲気）：

* `src/adapters/outbound/sqlite/TaskRecordMapper.ts`
* `src/adapters/outbound/sqlite/TaskRecord.ts`（型だけ分けてもOK）

---

### 5) まず「変換前・変換後の形」を固定しよ🧱📌

#### DB側（Record）の例🗃️

* `id`：TEXT（例：UUID文字列）
* `title`：TEXT
* `completed`：INTEGER（0/1）
* `created_at`：TEXT（ISO文字列）
* `completed_at`：TEXT or NULL

#### 内側（Entity）の例🏛️

* `id: TaskId`
* `title: string`（本当はTitleのVOでもOK）
* `completed: boolean`
* `createdAt: Date`
* `completedAt: Date | null`

---

### 6) Mapperの鉄則3つ✅✅✅

1. **純粋関数にする**（DBアクセスしない、状態持たない）🧼✨
2. **両方向を必ず用意**（Record→Entity / Entity→Record）🔁
3. **変換のクセを1か所に集約**（boolean・Date・NULL・命名）🧷📌

---

### 7) 実装例（TaskRecordMapper）✍️🔄

```ts
// src/adapters/outbound/sqlite/TaskRecord.ts
export type TaskRecord = {
  id: string;              // DBはTEXT
  title: string;
  completed: 0 | 1;        // DBはINTEGER(0/1)
  created_at: string;      // ISO文字列
  completed_at: string | null;
};
```

```ts
// src/adapters/outbound/sqlite/TaskRecordMapper.ts
import type { TaskRecord } from "./TaskRecord";

// 例：内側のTask（Entity）型（すでにある想定だけど、雰囲気のために型だけ）
export type Task = {
  id: string;
  title: string;
  completed: boolean;
  createdAt: Date;
  completedAt: Date | null;
};

const toIso = (d: Date) => d.toISOString();
const fromIso = (s: string) => {
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) throw new Error(`Invalid date: ${s}`);
  return d;
};

export const TaskRecordMapper = {
  toDomain(record: TaskRecord): Task {
    return {
      id: record.id,
      title: record.title,
      completed: record.completed === 1,
      createdAt: fromIso(record.created_at),
      completedAt: record.completed_at ? fromIso(record.completed_at) : null,
    };
  },

  toRecord(task: Task): TaskRecord {
    return {
      id: task.id,
      title: task.title,
      completed: task.completed ? 1 : 0,
      created_at: toIso(task.createdAt),
      completed_at: task.completedAt ? toIso(task.completedAt) : null,
    };
  },
};
```

ここでのポイント💡😍

* `0/1 ↔ boolean` を**ここだけ**でやってる✅
* `created_at` のsnake_caseは**外側の都合**なので、内側に持ち込まない✅
* Dateのパース失敗も、まずMapperで止められる（バグの早期発見）✅

---

### 8) RepositoryではMapperだけを頼る🔌✨（超だいじ！）

Repositoryがやることはコレだけに寄せたい👇😊

* SQL実行 → Row取得 → **Mapper.toDomain**
* Entity受け取り → **Mapper.toRecord** → SQL実行

「Rowの構造」をRepositoryの奥で直に触り続けると、変換が増殖するよ🧟‍♀️📎
Mapperを**唯一の変換窓口**にするのが勝ち🏆✨

---

### 9) 変換漏れを潰すテスト🧪💖（Round-trip最強）

「片方向だけ動く」って事故が多いので、往復テストが気持ちいいよ😆✨

```ts
import { describe, it, expect } from "vitest";
import { TaskRecordMapper } from "./TaskRecordMapper";
import type { TaskRecord } from "./TaskRecord";

describe("TaskRecordMapper", () => {
  it("Record -> Domain -> Record が同じ意味になる", () => {
    const rec: TaskRecord = {
      id: "t-1",
      title: "hello",
      completed: 1,
      created_at: "2026-01-01T00:00:00.000Z",
      completed_at: "2026-01-02T00:00:00.000Z",
    };

    const task = TaskRecordMapper.toDomain(rec);
    const rec2 = TaskRecordMapper.toRecord(task);

    expect(rec2).toEqual(rec);
  });

  it("completed_at が null でも壊れない", () => {
    const rec: TaskRecord = {
      id: "t-2",
      title: "hi",
      completed: 0,
      created_at: "2026-01-01T00:00:00.000Z",
      completed_at: null,
    };

    const task = TaskRecordMapper.toDomain(rec);
    expect(task.completedAt).toBeNull();
  });
});
```

---

### 10) ありがち事故あるある😵‍💫➡️😊（先に潰そ！）

* `INTEGER`の0/1をそのままbooleanとして扱ってバグる😇
* `NULL` を `undefined` だと思い込む（DBはnull多い）🫠
* 日付文字列がローカル形式で保存されて地獄（ISOに寄せたい）🕰️💥
* カラム名が `completedAt` で返ってくると思い込む（返らない）🐍
* 「一覧用の軽い形」と「Entity」を混ぜてしまう（境界が溶ける）🫧

Mapperに寄せると、こういう事故の爆心地が1か所になるよ💣➡️🧯✨

---

### 11) 🆕 ちょい最新情報：SQLiteまわり（2026年1月時点）📣✨

* Node本体に `node:sqlite` が用意されていて、同期APIの `DatabaseSync` で扱えるよ（ただし **まだExperimental扱い**）。([Node.js][1])
* 以前は `--experimental-sqlite` が必要だった時期もあるけど、現在のドキュメントでは「フラグなしでも使えるがExperimental」と整理されてるよ。([Node.js][1])
* npmのSQLite系だと `better-sqlite3` は「同期で速い」系の定番で、直近の最新バージョン情報も追いやすいよ。([脆弱性ガイド][2])

※どれを使っても、この章の結論は同じ：**DBドライバの都合はMapperに閉じ込める**🔒💛

---

### 12) 理解チェック✅📝

1. `completed_at` をEntityにそのまま持ち込むと、何が困る？😵‍💫
2. Mapperを「純粋関数」に寄せると、何が嬉しい？✨
3. 変換テストで “往復” を見るのはなぜ強い？🔁🧪

---

### 13) AI相棒プロンプト（コピペ用）🤖✨

* 「この `TaskRecord` と `Task` の型から、`toDomain/toRecord` を作って。0/1↔boolean、ISO↔Date、null対応も入れて」🧠🔄
* 「Mapperの往復テスト（Record→Domain→Record）をVitestで書いて。nullケースも追加して」🧪💖
* 「DBカラムが `created_at` から `createdAt` に変わった想定で、影響範囲をMapper中心に説明して」🔍📌

---

次の章（38章）では、このAdapters層がちゃんと中心を汚してないか、依存監査で“仕上げの防波堤”を作るよ🛡️🌊✨

[1]: https://nodejs.org/api/sqlite.html "SQLite | Node.js v25.4.0 Documentation"
[2]: https://security.snyk.io/package/npm/better-sqlite3/12.6.0?utm_source=chatgpt.com "better-sqlite3 12.6.0 vulnerabilities"
