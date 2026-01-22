# 第36章：Outbound Adapter：永続化Repository（SQLite）🗃️✅

この章は「InMemory の TaskRepository を、SQLite で永続化する Repository に差し替える」回だよ〜！🎉
ポイントはただ1つ👇

**UseCase も Entity も一切変えずに、外側（Repository 実装）だけ差し替える**🔁✨
これができると「クリーンアーキ、ほんとに効くじゃん…！」って体感できるやつ😊💕

---

## 0) まず“どのSQLite”でやる？🤔🧩

SQLite を TypeScript/Node で触る方法、今どきは主にこの3つ👇

* **A：Node 組み込みの「node:sqlite」**
  追加インストール不要で楽ちんだけど、まだ “実験中” 扱いだよ〜（ドキュメント上も安定度が低め）📌 ([Node.js][1])
* **B：better-sqlite3（人気・速い・シンプル）**
  いまも定番。最新版は 12.6.2 になってるよ🧠✨ ([npm][2])
* **C：sqlite3（非同期寄り・昔からある）**
  Windows など向けに prebuilt binary が用意される方針が明記されてるよ🪟👍 ([GitHub][3])

この講座では **B：better-sqlite3** で実装していくね！
（A の node:sqlite は「あとで試す用のおまけ」として最後にちょこっと載せるよ😊）

---

## 1) 永続化Repositoryの責務って何？🎯

Outbound Adapter（SQLiteTaskRepository）の責務はシンプル👇

* Port（TaskRepository interface）を満たす ✅
* SQL を叩いて保存/取得する ✅
* “DBの都合” を内側に漏らさない（SQLやRow形式を内側に持ち込まない）✅

逆に、**ここでやっちゃダメ**な例👇💥

* 業務ルール（タイトルの長さ制限とか）を Repository が判断する
* UseCase の流れ（Create/Complete の手順）を Repository が持つ
* 「HTTPのエラー」みたいな外側表現を返す

---

## 2) つくるDBテーブル（最小）🧱

Taskアプリ（Create / Complete / List）なら、最小はこれでOK👌✨

```sql
CREATE TABLE IF NOT EXISTS tasks (
  id           TEXT PRIMARY KEY,
  title        TEXT NOT NULL,
  completed    INTEGER NOT NULL DEFAULT 0,
  created_at   TEXT NOT NULL,
  completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
```

* 日時は扱いやすいので **ISO文字列（例：2026-01-23T12:34:56.789Z）**で保存にしちゃうのが楽だよ🕒✨
* completed は SQLite 的に INTEGER（0/1）で持つのが定番👍

---

## 3) ファイル配置（おすすめ）📁✨

「SQLiteの詳細は外側に」って意識で、こんな感じがわかりやすいよ〜！

* src

  * entities
  * usecases
  * ports
  * adapters

    * outbound

      * sqlite

        * SQLiteTaskRepository.ts
        * schema.ts

※ DB接続の生成（どこにファイル作るか等）は、あとで “外側” に寄せやすい形にしておくのがコツだよ🧼✨

---

## 4) 実装：schema の適用（起動時に1回）🧾

まず schema.ts を作って「テーブルがなければ作る」だけやるよ〜！

```ts
// src/adapters/outbound/sqlite/schema.ts
import type Database from "better-sqlite3";

export function applySchema(db: Database) {
  db.exec(`
    PRAGMA foreign_keys = ON;
    PRAGMA journal_mode = WAL;
    PRAGMA synchronous = NORMAL;

    CREATE TABLE IF NOT EXISTS tasks (
      id           TEXT PRIMARY KEY,
      title        TEXT NOT NULL,
      completed    INTEGER NOT NULL DEFAULT 0,
      created_at   TEXT NOT NULL,
      completed_at TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
  `);
}
```

* WAL を入れると読み書きが安定しやすいよ〜（小規模でも体感できることある）✨
* こういう “DB運用の都合” は外側に押し出してOK👍

---

## 5) 実装：SQLiteTaskRepository（Portを満たす）🔌🧩

ここが本丸だよ！🗡️✨
ポイントは👇

* **SQLは全部ここに閉じ込める**🧼
* **Row ⇄ 内側モデルの変換**をここでやる（次章で Mapper として分離する）🔄
* **例外は “Repository由来” って分かる形に包む**⚠️

```ts
// src/adapters/outbound/sqlite/SQLiteTaskRepository.ts
import Database from "better-sqlite3";
import { applySchema } from "./schema";

// 例：内側の Port（あなたの既存定義に合わせてね）
import type { TaskRepository } from "../../..//ports/TaskRepository";

// 例：内側の Entity（あなたの既存定義に合わせてね）
import type { Task } from "../../../entities/Task";

export class RepositoryError extends Error {
  constructor(message: string, public readonly cause?: unknown) {
    super(message);
    this.name = "RepositoryError";
  }
}

type TaskRow = {
  id: string;
  title: string;
  completed: number; // 0/1
  created_at: string;
  completed_at: string | null;
};

export class SQLiteTaskRepository implements TaskRepository {
  constructor(private readonly db: Database) {
    applySchema(this.db);
  }

  async save(task: Task): Promise<void> {
    try {
      const stmt = this.db.prepare(`
        INSERT INTO tasks (id, title, completed, created_at, completed_at)
        VALUES (@id, @title, @completed, @created_at, @completed_at)
        ON CONFLICT(id) DO UPDATE SET
          title = excluded.title,
          completed = excluded.completed,
          created_at = excluded.created_at,
          completed_at = excluded.completed_at
      `);

      stmt.run(this.toRowParams(task));
    } catch (e) {
      throw new RepositoryError("SQLite save failed", e);
    }
  }

  async findById(id: string): Promise<Task | null> {
    try {
      const stmt = this.db.prepare(`
        SELECT id, title, completed, created_at, completed_at
        FROM tasks
        WHERE id = ?
      `);

      const row = stmt.get(id) as TaskRow | undefined;
      if (!row) return null;

      return this.fromRow(row);
    } catch (e) {
      throw new RepositoryError("SQLite findById failed", e);
    }
  }

  async findAll(): Promise<Task[]> {
    try {
      const stmt = this.db.prepare(`
        SELECT id, title, completed, created_at, completed_at
        FROM tasks
        ORDER BY created_at DESC
      `);

      const rows = stmt.all() as TaskRow[];
      return rows.map((r) => this.fromRow(r));
    } catch (e) {
      throw new RepositoryError("SQLite findAll failed", e);
    }
  }

  // ----- 変換（次章で Mapper に分離するとキレイ✨） -----

  private toRowParams(task: Task) {
    return {
      id: task.id,
      title: task.title,
      completed: task.completed ? 1 : 0,
      created_at: task.createdAt.toISOString(),
      completed_at: task.completedAt ? task.completedAt.toISOString() : null,
    };
  }

  private fromRow(row: TaskRow): Task {
    // ここはあなたの Task Entity の作りに合わせて組み立ててね😊
    // 例：Task.restore(...) があるならそれを使うのが綺麗✨
    return {
      id: row.id,
      title: row.title,
      completed: row.completed === 1,
      createdAt: new Date(row.created_at),
      completedAt: row.completed_at ? new Date(row.completed_at) : null,
    } as Task;
  }
}
```

> 📝「Task の生成方法（create / restore）がどうなってるか」で、fromRow の書き方は変わるよ〜！
> “外側の値を内側のルールに通す” って意味でも、Entityの復元メソッドがあると強い💪✨

---

## 6) トランザクションっていつ要るの？💳🔒

**1SQLだけなら基本いらない**ことが多いよ🙂
でも👇みたいに「複数SQLをまとめて成功させたい」なら使う！

* タスク保存＋別テーブルにログ保存
* まとめて更新（バッチ）
* “中途半端に保存” を絶対避けたい処理

better-sqlite3 はトランザクションが書きやすいよ✨

```ts
const tx = db.transaction((taskParams: any, logParams: any) => {
  db.prepare("INSERT INTO tasks (...) VALUES (...)").run(taskParams);
  db.prepare("INSERT INTO task_logs (...) VALUES (...)").run(logParams);
});

tx(taskParams, logParams);
```

---

## 7) よくある落とし穴（ここ超だいじ）💥🧯

* **SQLを文字列結合で作らない**（値は必ずバインド）🧷
  → 事故りやすいし、あとで泣く😭
* **Row形式を UseCase に返さない**（Entity/内側DTOに直す）🔄
* **例外を丸投げしない**
  → 「RepositoryError」みたいに包むとデバッグが楽🕵️‍♀️✨
* **“完了判定” をDBでやらない**
  → completed のルールは内側（Entity/UseCase）に寄せるのが基本❤️

---

## 8) 簡単な結線（差し替えの瞬間）🏗️✨

InMemory から SQLite に変えるのは、理想はここだけ👇

```ts
import Database from "better-sqlite3";
import { SQLiteTaskRepository } from "./adapters/outbound/sqlite/SQLiteTaskRepository";

const db = new Database("./data/tasks.sqlite");
const taskRepo = new SQLiteTaskRepository(db);

// あとは taskRepo を UseCase に注入するだけ🎯
```

「差し替えってこういうことかぁ〜！」ってなる瞬間だよ😆🎉

---

## 9) AI相棒に頼むと強いプロンプト集🤖✨

* 「tasks テーブルのスキーマを、将来の拡張（タグ/期限）も見据えて提案して。最小案と拡張案で」🧠
* 「SQLiteTaskRepository の findAll を、ページング対応できる形に拡張する設計案を出して」📄
* 「Repository の例外設計を、原因追跡しやすい形（cause保持）で整えて」🧯
* 「Row⇄Entity 変換が増えても破綻しないように、Mapper分離の形にリファクタして」🔄✨

---

## 10) おまけ：node:sqlite を試すなら（超ミニ）🍬

Node には組み込みの SQLite が入ってて、import だけで触れるよ〜！ただし **まだ実験中扱い**だよ📌 ([Node.js][1])

```ts
import { DatabaseSync } from "node:sqlite";

const db = new DatabaseSync("./data/tasks.sqlite");
db.exec("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, title TEXT NOT NULL)");
```

「追加インストールなし」は魅力だけど、安定度が上がるまでは様子見が安心かも🙂‍↕️✨

---

## まとめ（この章で手に入る力）🎁✨

* 「Port はそのまま、Repository 実装だけ差し替え」ができる🎭✅
* SQL/DB都合を Adapter に閉じ込められる🧼🗃️
* トランザクション・例外・変換の“外側あるある”を安全に扱える🛡️

次の第37章で、この章の「fromRow / toRow」が増えて地獄にならないように **Mapper に分離**して、もっとキレイにするよ〜！🔄✨

[1]: https://nodejs.org/api/sqlite.html?utm_source=chatgpt.com "SQLite | Node.js v25.4.0 Documentation"
[2]: https://www.npmjs.com/package/better-sqlite3?utm_source=chatgpt.com "better-sqlite3"
[3]: https://github.com/TryGhost/node-sqlite3?utm_source=chatgpt.com "TryGhost/node-sqlite3: SQLite3 bindings for Node.js"
