# 第27章：Outbound Adapter②：FileRepository（JSON保存）📄💾✨

この章は「**InMemoryRepository を FileRepository に差し替えるだけで永続化できる**」って体験を作る回だよ〜😊🔁
（ちなみに今の Node は **v24 が LTS**、TypeScript は **5.9 系が安定版**って状況だよ📌 ([Node.js][1])）

---

## 1) 今日のゴール 🎯✨

できるようになることはこれ👇

* JSONファイル（`todos.json`）に ToDo を保存・読み込みできる📄💾
* **中心（ドメイン/ユースケース）を1行も触らずに**永続化できる🔁🧠
* ファイルI/O失敗（壊れたJSON、権限、読み込み不可）を「外側の責務」として扱える😵‍💫➡️🧩

---

## 2) まず大事な考え方（超短く）🛡️🔌🧩

* **Port（Repository interface）**：中心が「こうしてね」ってお願いする約束🔌
* **Adapter（FileRepository）**：その約束を「ファイルI/Oで実現」する変換器🧩
* Adapterの仕事は **変換＆呼び出し**まで！
  ルール（例：空タイトル禁止、二重完了禁止…）を入れたら太りすぎで負け🥗⚠️

---

## 3) 保存形式を決める（シンプルが最強）📄✨

今回はこうしよ👇

* 保存先：`./data/todos.json`
* 形式：配列でOK `[{ id, title, completed, createdAt, completedAt? }, ...]`

> ポイント：**保存形式は “外の都合”** だから、domainの型そのまま保存しないで、**Record（保存用の形）** を用意して変換するよ🧩🔁

---

## 4) 実装：FileRepository を作るよ〜😊💻

### 4-1) Outbound Port（再掲：最小の約束）🔌

`src/app/ports/TodoRepository.ts`

```ts
export type TodoRecord = {
  id: string;
  title: string;
  completed: boolean;
  createdAt: string;      // ISO文字列で保存
  completedAt?: string;   // 完了してたら
};

export interface TodoRepository {
  list(): Promise<TodoRecord[]>;
  saveAll(todos: TodoRecord[]): Promise<void>;
}
```

> ここでは「domainのTodoを直接返さない」設計に寄せて、Recordでやってるよ📦✨
> （もし前の章で domain の `Todo` を返す形にしてるなら、**Adapter側で Todo⇄Record を変換**すればOK🙆‍♀️）

---

### 4-2) FileRepository 本体（JSON読み書き＋安全対策）📄💾🧩

`src/adapters/out/file/FileTodoRepository.ts`

```ts
import { promises as fs } from "node:fs";
import path from "node:path";
import type { TodoRecord, TodoRepository } from "../../../app/ports/TodoRepository.js";

type FileTodoRepositoryOptions = {
  dataDir: string;     // 例: path.resolve("data")
  fileName?: string;   // 例: "todos.json"
};

/**
 * JSONファイルで永続化する Outbound Adapter 🧩
 * - 変換＆I/Oに徹する（ルールは入れない！）🥗
 */
export class FileTodoRepository implements TodoRepository {
  private readonly filePath: string;

  // “同一プロセス内の同時save”で壊れないよう、保存を直列化するキュー🔒
  private writeQueue: Promise<void> = Promise.resolve();

  constructor(opts: FileTodoRepositoryOptions) {
    const fileName = opts.fileName ?? "todos.json";
    this.filePath = path.join(opts.dataDir, fileName);
  }

  async list(): Promise<TodoRecord[]> {
    try {
      const text = await fs.readFile(this.filePath, "utf8");
      const raw = JSON.parse(text);

      if (!Array.isArray(raw)) return []; // 壊れてたら空扱い（方針は好みでOK）
      // 超軽量バリデ（ガチでやるなら zod 等でもOK）
      return raw
        .filter(isTodoRecordLike)
        .map((x) => ({
          id: x.id,
          title: x.title,
          completed: x.completed,
          createdAt: x.createdAt,
          completedAt: x.completedAt,
        }));
    } catch (e: any) {
      if (e?.code === "ENOENT") return []; // 初回はファイル無し＝空
      // JSON壊れてる、権限ない、などは「外の失敗」
      throw new InfrastructureError("Failed to read todos.json", e);
    }
  }

  async saveAll(todos: TodoRecord[]): Promise<void> {
    // 同時に呼ばれても壊れないよう “直列化” するよ🔒
    this.writeQueue = this.writeQueue.then(() => this.saveAllInternal(todos));
    return this.writeQueue;
  }

  private async saveAllInternal(todos: TodoRecord[]): Promise<void> {
    try {
      await fs.mkdir(path.dirname(this.filePath), { recursive: true });

      const json = JSON.stringify(todos, null, 2) + "\n";

      // 途中で落ちても壊れにくい “テンポラリ書き込み→リネーム” 🧯
      const tmpPath = this.filePath + ".tmp";
      await fs.writeFile(tmpPath, json, "utf8");
      await fs.rename(tmpPath, this.filePath);
    } catch (e: any) {
      throw new InfrastructureError("Failed to write todos.json", e);
    }
  }
}

function isTodoRecordLike(x: any): x is TodoRecord {
  return (
    x &&
    typeof x === "object" &&
    typeof x.id === "string" &&
    typeof x.title === "string" &&
    typeof x.completed === "boolean" &&
    typeof x.createdAt === "string" &&
    (x.completedAt === undefined || typeof x.completedAt === "string")
  );
}

export class InfrastructureError extends Error {
  override name = "InfrastructureError";
  constructor(message: string, public readonly cause?: unknown) {
    super(message);
  }
}
```

#### ここ、めっちゃ大事ポイントだよ〜📌✨

* `ENOENT`（ファイル無い）は **初回あるある** → 空配列にするのがやさしい😊
* JSON壊れた、権限ない、などは **I/O失敗** → `InfrastructureError` で包む🧯
* 保存は **tmpに書いてから rename** → 途中クラッシュ時に壊れにくい💪✨
* `writeQueue` で **同時保存を直列化** → 競合でJSON破損しにくい🔒

---

## 5) Composition Root で差し替える 🧩🏗️✨

「InMemory から File に変える」のはここだけにしてね👇

例：`src/main.ts` とか `src/compositionRoot.ts` みたいな場所

```ts
import path from "node:path";
import { FileTodoRepository } from "./adapters/out/file/FileTodoRepository.js";
// import { InMemoryTodoRepository } from "./adapters/out/memory/InMemoryTodoRepository.js";

const repo = new FileTodoRepository({
  dataDir: path.resolve("data"),
});

// あとはユースケースに repo を渡すだけ（中心は変更なし）🧠✨
```

> 「差し替え戦略」が気持ちいい瞬間きた〜！🔁💖
> ここがヘキサゴナルの快感ポイントだよ😊✨

---

## 6) 動作確認（超かんたん）🧪🎉

CLIを作ってる前提だと、こんな流れ👇

* `add` したら `data/todos.json` が増える📄
* もう一回 `list` したら復元される🔁

確認のコツ👀✨

* `data/todos.json` を **わざと壊す**（カンマ消すとか）→ 読み込み失敗の挙動を見る😳
* フォルダを読み取り専用にして保存 → `InfrastructureError` が出るか見る🔐

---

## 7) Adapter が “太ってない？”チェック 🥗⚠️✅

**NG（太る）**😱

* 「空タイトル禁止」みたいな業務ルールが FileRepo にある
* 「完了二重適用禁止」みたいな状態遷移がある
* 巨大 if/for が増えて「ドメインっぽい」判断がある

**OK（薄い）**😊

* JSON ⇄ Record 変換
* read/write/rename と例外ラップ
* 「壊れてた時どうする？」みたいな I/O方針（外側の判断）

---

## 8) AI拡張に頼むときのプロンプト例 🤖📝✨

コピペで使えるやつ置いとくね👇

* 「この FileRepository が **業務ルールを持ってないか**レビューして。変換とI/O以外があったら指摘して」
* 「`saveAll` を **壊れにくい保存**（tmp→rename）にしたい。Windowsでも動く形で提案して」
* 「`list()` で JSON が壊れてる時の方針を3案（空扱い/エラー/バックアップ復旧）で比較して」

---

## 9) ミニ課題 🎀📝

できたら強いよ〜💪✨

1. `todos.json.bak` を作る（保存前に旧ファイルをコピー）📄📄
2. JSON壊れてたら `InfrastructureError` の `cause` をログに出す📊
3. `saveAll` じゃなく `upsert(todo)` にしたくなった時、Portをどう最小化するか考える🔌✨

---

## まとめ 🎁💖

* FileRepository は **Outbound Adapter**：中心の約束（Port）を **ファイルI/Oで実現**する係🧩
* **変換＆I/Oに徹する**のが正義🥗✨（ルールは中心へ！）
* tmp→rename と 直列化で、JSON保存でもわりと堅くできる🧯🔒

次の章（28章）は「Adapterが薄いかチェック（太ったら負け）🥗⚠️」だから、今日の実装は最高の前フリだよ〜😊🔥

[1]: https://nodejs.org/en/blog/release/v24.13.0?utm_source=chatgpt.com "Node.js 24.13.0 (LTS)"
