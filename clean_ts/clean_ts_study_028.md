第28章：Portの境界線チェック（命名・責務）🧼🔌✨
〜「Portが“技術用語まみれ”になってない？」「責務がデカすぎない？」を、ここで一回ピカピカにする回だよ〜😊🌟

---

## 1) この章のゴール 🎯💖

この章が終わったら、あなたはこうなれるよ👇✨

* Port名を見ただけで「内側（業務）っぽい？外側（技術）っぽい？」が判定できる👀✅
* Portのメソッドを見て「UseCaseに必要な分だけ？」って言えるようになる✂️✨
* Portが“境界”として正しく機能してるか、チェックリストで監査できる🧾🛡️

---

## 2) まず大事な前提：Portは“契約”📜🤝

Hexagonal（Ports & Adapters）では、Portは「アプリ中心が外界に求める契約」で、外側はそれを満たす（実装する）側だよ〜って考え方が基本😊🔌
この発想があるから、DBやフレームワークを差し替えやすくなるんだ✨ ([AWS Documentation][1])

---

## 3) Portが汚れてると起きる“あるある”😇🧨

Portが境界として微妙になると、こんな症状が出るよ👇

* `SqlTaskRepository` とか `HttpTaskClient` とか、名前が技術直球⚙️😵
* メソッドが `insert` / `select` / `update` で、DB操作の言葉が内側に侵入🗄️➡️❤️
* `TaskRow` / `DbTaskRecord` みたいな“DB都合の型”がPortの入出力に混ざる📦💥
* いつの間にかPortが巨大化して「何でも屋Repository」になる（CRUD全部入り）🍱🐘

ここを直すのが第28章だよ🧼✨

---

## 4) 命名チェック：Port名は“能力”か“目的”で言う🗣️💎

Portの名前は **技術じゃなくて、アプリが欲しい能力** を表すのがコツ😊🔌
「アプリ語で表現する」っていうのが超重要✨ ([DEV Community][2])

### ✅ 良いPort名（業務寄り）🥰

* `TaskStore`（タスクを保存/取得できる場所）
* `TaskReader` / `TaskWriter`（読み/書きを分ける）
* `IdGenerator`（IDを作れる能力）
* `Clock`（今の時刻が取れる能力）

### ❌ 微妙Port名（技術寄り）😵‍💫

* `SqlTaskRepository`（SQLが前面に出すぎ）
* `TaskDao`（“DAO”は技術用語寄り）
* `PrismaTaskRepo`（具体技術が名前に混ざる）
* `HttpNotifierClient`（HTTPが内側に見えてる）

### 判定の超かんたんルール✨

Port名を見て、こう言える？👇

* 「DBのことは忘れて説明できる」→ ✅内側っぽい
* 「SQL/HTTP/フレームワークを言わないと説明できない」→ ❌外側っぽい

---

## 5) 責務チェック：Portのメソッドは“UseCaseから逆算”✂️🎬

Portは **UseCaseが必要な分だけ** を持つのが基本だよ😊
（巨大な“万能Repository”は、境界を溶かしがち…🫠）

### ✅ 良い例：最小の能力に絞る✨

```ts
import { Task } from "../../entities/task/Task";

export interface TaskStore {
  save(task: Task): Promise<void>;
  findById(id: string): Promise<Task | null>;
  list(): Promise<Task[]>;
}
```

### ❌ 悪い例：DB都合のCRUDが露出😇

```ts
export interface SqlTaskRepository {
  insertTaskRow(row: { id: string; title: string; completed: 0 | 1 }): Promise<number>;
  updateTaskRow(row: any): Promise<void>;
  selectTaskRows(where: string): Promise<any[]>;
}
```

**ポイント**：`where: string` とか来た瞬間に「SQLの匂い」すごいよね😂🧄

---

## 6) “Portの入出力”チェック：DBの型を入れない📦🚫

Portの入出力は、基本こう考えると事故りにくいよ👇😊

### パターンA：Entityをそのまま使う（今回のミニアプリ向け）🧱✨

* `Task` を渡す / `Task` を返す
* シンプルで学習向き😊

### パターンB：Port専用DTO（Snapshot）を使う📸

* Entityを直接出したくないときに便利
* でも今はやりすぎ注意⚠️（第29章の「増やしすぎない運用」にも繋がるよ🌱）

---

## 7) エラー表現チェック：Portのエラーが“技術語”になってない？⚠️🧯

Portが返す失敗が `SqlError` とか `AxiosError` とかだと、中心が外側に引っ張られるよ😵‍💫

### ✅ 方針例：Portの失敗は“意味”でまとめる

```ts
export type TaskStoreError =
  | { type: "Unavailable" }        // 一時的に使えない
  | { type: "Conflict" }           // 競合（更新衝突など）
  | { type: "Unknown"; message: string };

export interface TaskStore {
  save(task: Task): Promise<void>; // まずはthrow運用でもOK
}
```

ミニアプリなら「まずは throw → Adapter側でログ → 境界で変換」でも全然OKだよ😊✨
（大事なのは“エラー名にSQLとかHTTPを混ぜない”こと！）

---

## 8) 実戦：いまあるPortを“境界線チェック”して直す🧼🔧✨

ここから手を動かすよ〜！🖐️💕

### ステップ1：Port一覧を紙に書く（またはメモ）📝

例：

* `TaskRepository`
* `Clock`
* `IdGenerator`

### ステップ2：各Portに「説明文」を1行でつける💬

例：

* `TaskRepository`：タスクを保存/取得できる
* `Clock`：現在時刻を返す
* `IdGenerator`：新しいIDを作る

### ステップ3：その説明に“技術単語”が必要か判定👀

* 「SQLiteが…」って言わないと説明できる → **命名修正候補**⚠️
* 「保存できる」だけで説明できる → **OK**✅

### ステップ4：メソッドごとに「どのUseCaseの何行目？」って紐付け🎬🔗

Portの各メソッドに対して👇をやる：

* このメソッドは **Create/Complete/List** のどれで使う？
* どれでも使わないなら、今は要らないかも✂️

---

## 9) チェックリスト：Port境界線監査🧾🛡️（コピペ用）

Portごとに✅を付けてね😊✨

* □ 名前にSQL/HTTP/ORM/SDKなどの技術語が入ってない
* □ 1行説明が“業務語”だけで言える
* □ メソッドはUseCaseから逆算で必要最小限
* □ CRUD全部入りの“何でも屋”になってない
* □ 入出力に `Row/Record/DTO(外側)` が混ざってない
* □ 失敗（エラー）が技術語で漏れてない
* □ 同じ概念のPortが乱立してない（似た名前が増殖してない）
* □ Portの責務が「能力1つ」になってる（雑に言うと“1芸”🎭）

---

## 10) AI相棒の使い方 🤖✨（プロンプトテンプレ）

### ① Port名の診断

```txt
次のPort定義を、クリーンアーキテクチャ観点でレビューして。
- Port名が技術寄り/業務寄りか判定
- もし技術寄りなら、業務寄りの代替名を3案
- メソッドがUseCase（Create/Complete/List）から見て過剰か不足かも指摘
コード:
(ここに interface を貼る)
```

### ② “巨大Repository化”してないかチェック

```txt
このPortが「何でも屋Repository」になっていないか診断して。
もし分割するなら、分割後のinterface案を提示して。
条件：UseCaseは Create / Complete / List のみ。
(ここに interface を貼る)
```

---

## 11) 理解チェック問題（1問）🧠🎀

次のうち「Portとして命名が一番よい」ものはどれ？😊

A. `SQLiteTaskDao`
B. `TaskTableGateway`
C. `TaskStore`
D. `PrismaTaskRepository`

👉答え：**C**（技術なしで能力を言えてるから）✨

---

## 12) この章の提出物（成果物）📦🎁

* Port境界線監査チェックリスト（✅付き）🧾
* Port名と責務のリファクタ結果（差分が分かる形）🔧✨
* 「変更した理由」を各Port1行メモ💬

---

## ちょい最新ネタ：TypeScript側の“境界を汚さない助け”も増えてるよ🧼🧠

TypeScript 5.9 では `tsc --init` の生成内容が見直されて、モジュール境界を意識しやすい設定（例：`verbatimModuleSyntax` や `noUncheckedSideEffectImports` など）も最初から入りやすくなったよ✨ ([Microsoft for Developers][3])
（“うっかり副作用importで内側が汚れる”みたいな事故の芽を減らせる方向性🌱）

---

次の第29章は、この章で綺麗にしたPortを「増やしすぎないための運用ルール」に落とし込むよ〜😊🔌🌱✨

[1]: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html?utm_source=chatgpt.com "Hexagonal architecture pattern - AWS Prescriptive Guidance"
[2]: https://dev.to/xoubaman/understanding-hexagonal-architecture-3gk?utm_source=chatgpt.com "Understanding Hexagonal Architecture"
[3]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9-beta/ "Announcing TypeScript 5.9 Beta - TypeScript"
