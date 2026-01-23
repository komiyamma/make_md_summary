# 37. AI活用①：雛形生成の安全な頼り方 🤖🧰


## 第37章：AI活用①：雛形生成の安全な頼り方 🤖🧰✨

この章はひとことで言うと、**「AIに“雑務（雛形）”を任せて、設計の芯は自分で守る」**練習だよ〜😊💖
AIって便利なんだけど、放っておくと **Ports & Adapters の“依存の向き”を平気で壊しがち**だから、ここで安全運転の型を身につけよっ🚗💨

---

## 1) 今日のゴール 🎯✨

できるようになることはコレ👇

* **AIに任せてOKな範囲 / ダメな範囲**を、迷わず切り分けられる✅
* **安全な頼み方テンプレ**で、雛形をサクッと量産できる✅
* 生成物を**チェックリストで検査**して、中心（ドメイン/ユースケース）を守れる🛡️✨

ついでに、最近のAIコーディング機能（エージェント系）って「勝手に編集してテストまで回す」モードもあるから、そこも安全に使えるようにしよ〜🤖🔧
（例：CopilotのAgent modeは、タスク達成のために自律的に複数ファイルを編集したり、コマンドを提案して繰り返したりする感じだよ。）([GitHub Docs][1])

---

## 2) まず大前提：AIの得意/不得意（超大事）🧠✨

### AIが得意（任せてOK）💪🤖

**「繰り返し」「雛形」「単純な変換」「テストの土台」**が強い！

* Adapterの雛形（ファイル/DB/HTTP/CLIなど）🧩
* DTO変換のボイラープレート（変換関数の骨組み）🔁
* テストの雛形（describe/it、モック、データ準備）🧪
* 既存コードの説明、影響範囲の洗い出し（コード理解）🔎

  * ワークスペース全体を前提に答えやすくする仕組みもあるよ（workspace context的なやつ）([Visual Studio Code][2])

### AIが苦手（ここは任せない）🙅‍♀️💥

ここをAIに丸投げすると、ヘキサゴナルが崩れる率が一気に上がる😱

* **Port設計（どの約束を、どの粒度で切るか）**🔌
* **依存の向き（中心→外側参照の禁止）**🧭🔥
* **ドメインルール（不変条件・状態遷移・業務判断）**🏰
* “便利だから”で **巨大Port / 太いAdapter**にする判断🐘🍔

> まとめると：
> **AIは「工事の人」👷‍♀️、あなたは「設計士」👩‍💻**
> 設計図（Ports/依存/ルール）はあなたが握る！🛡️✨

---

## 3) 安全運転の「3ステップ」🚦✨（これだけ守れば事故激減）

### Step A：AIに“最初に”やらせるのは「計画」📝

いきなりコード生成じゃなくて、まず計画を出させるとミスが減るよ😊

* どのファイルを作る？
* どのPortを使う？（※新規Port追加は原則しない、するなら理由を書く）
* 中心（domain/app）には触らない？触るなら最小？

### Step B：生成は「差分前提」にする🧩

AIにはこう言うのが強い👇

* 「**新規ファイルだけ作って**」
* 「**既存ファイルは変更しないで**」
* 「変更するなら **diff形式で出して**」

### Step C：人間が“検査”する🧪🔎

* `git diff` を見る👀
* テスト回す🧪
* “中心が汚れてないか”チェックリストで確認🛡️

---

## 4) 便利な最新機能：Agent mode を安全に使うコツ 🤖🧯

最近は「エージェント」が強い！
CopilotのAgent modeは、タスクを受けると **どのファイルを変えるか判断して編集**し、**必要なターミナルコマンド（例：テスト）も提案**して反復する感じだよ。([GitHub Docs][1])

ただし！強いぶん事故も起きるので、コツはこれ👇

* ✅ **タスクを小さく**（Adapter雛形1つ、テスト追加1つ、みたいに）
* ✅ **“触っていい場所”を明示**（例：`src/adapters/**` のみ）
* ✅ **ターミナル実行は必ず内容を読んでから**（VS Code側でも確認導線がある）([Visual Studio Code][3])
* ✅ 最後は **diffレビュー + テスト**（ここ省略しない！）

---

## 5) 最強の安全装置：`copilot-instructions.md` を置こう 🧷✨

AIに毎回「中心を汚すな」って言うの、めんどいよね？😵‍💫
そこで **リポジトリに“指示書ファイル”を置く**と、毎回の会話が安定するよ〜📌✨

VS Codeのドキュメントでも、`.github/copilot-instructions.md` を使う流れが案内されてるよ。([Visual Studio Code][4])
しかも最近は、設定ベースの古いやり方（codeGeneration/testGenerationの指示）は **VS Code 1.102 でdeprecated**扱いで、**instructionsファイル推奨**になってるよ。([Visual Studio Code][5])

### 置き場所（基本）📁

* `.github/copilot-instructions.md`

### まずはコピペでOKなテンプレ 🎀

（あなたのToDoミニ前提で、ヘキサゴナルを守る指示だけ入れてあるよ）

```md
# Copilot Instructions (Hexagonal / Ports & Adapters)

## Architecture rules
- Domain/App (center) must not import from adapters, frameworks, Node APIs, or HTTP/DB libraries.
- Adapters can import from center, not the other way around.
- Keep adapters thin: mapping, calling ports, wrapping errors. No business rules.

## Naming rules
- Ports: *Port / *Repository / *Gateway
- Adapters: *Adapter / *RepositoryAdapter

## Changes policy
- Prefer adding new files over editing many files.
- When editing, keep diffs small and explain why.

## Testing
- When adding behavior, also add or update tests.
```

---

## 6) 「頼み方テンプレ」：この形で投げると強い 📨🤖✨

### テンプレ①：Adapter雛形を作らせる（超よく使う）🧩

```text
目的：Outbound Adapterの雛形を作って

制約：
- 触っていいのは src/adapters/ 以下だけ
- domain/app には一切触らない
- 既存の Port インターフェースを実装するだけ
- Adapter は薄く（変換・呼び出し・エラー包みのみ）
- まずは計画 → 次にコード（新規ファイルのみ）

前提（Port）：
<ここに Port のコードを貼る>
```

### テンプレ②：テスト雛形を作らせる 🧪

GitHub Copilot Chatには `/tests` みたいなスラッシュコマンドもあるから、雛形作りが早いよ〜✨([GitHub Docs][6])

```text
目的：UseCaseの単体テスト雛形を追加して

制約：
- テスト対象は src/app/usecases/AddTodo.ts
- OutboundはInMemoryで差し替え（モックでもOK）
- 仕様（期待動作）を文章コメントで先に箇条書き
- まずは失敗ケース（タイトル空など）から

出力：
- 追加/変更ファイル一覧
- テストコード
```

### テンプレ③：AIに“レビュー目線”で自己検査させる 🔍

```text
いま出した変更について、次をチェックしてNGがあれば直して：
- 中心が外部(Node/HTTP/DB)をimportしてない？
- Portが肥大化してない？
- Adapterに業務ルールが入ってない？
- DTO/変換は境界に寄ってる？
- テストは仕様を守れてる？
```

---

## 7) 実演：File保存Adapterの“雛形”をAIに作らせる 🧩📄💾

ここからは、あなたのToDoミニでよくある **JSONファイル保存**のAdapterを例にするね😊

### 7-1) まずPort（約束）を人間が提示する🔌

（例：最低限の保存・取得だけ、っていう発想）

```ts
export type TodoDTO = {
  id: string;
  title: string;
  completed: boolean;
};

export interface TodoRepositoryPort {
  findAll(): Promise<TodoDTO[]>;
  save(todo: TodoDTO): Promise<void>;
  saveAll(todos: TodoDTO[]): Promise<void>;
}
```

### 7-2) AIに投げるプロンプト例 📨🤖

```text
目的：TodoRepositoryPort を実装する FileTodoRepositoryAdapter を新規作成して

制約：
- 新規ファイルのみ（既存ファイルは編集しない）
- 保存先は data/todos.json（存在しなければ空配列で開始）
- Node の fs/promises を使ってOK（Adapterなので）
- Adapterは薄く：読み書き、JSON parse/stringify、エラーをわかりやすく投げ直すだけ
- domain/app には触らない

出力：
- 作るファイルのパス
- コード
- 例外時の挙動メモ
Port：
（ここに TodoRepositoryPort を貼る）
```

### 7-3) 生成されがちな“良い雛形”のイメージ 🧩✨

（こういうのが出たら、だいたい当たり🎯）

```ts
// src/adapters/outbound/file/FileTodoRepositoryAdapter.ts
import { promises as fs } from "node:fs";
import path from "node:path";
import type { TodoDTO, TodoRepositoryPort } from "../../../app/ports/TodoRepositoryPort";

export class FileTodoRepositoryAdapter implements TodoRepositoryPort {
  constructor(private readonly filePath: string = path.join("data", "todos.json")) {}

  async findAll(): Promise<TodoDTO[]> {
    const raw = await this.readFileOrEmpty();
    return raw;
  }

  async save(todo: TodoDTO): Promise<void> {
    const todos = await this.readFileOrEmpty();
    const next = [...todos.filter(t => t.id !== todo.id), todo];
    await this.writeAll(next);
  }

  async saveAll(todos: TodoDTO[]): Promise<void> {
    await this.writeAll(todos);
  }

  private async readFileOrEmpty(): Promise<TodoDTO[]> {
    try {
      const text = await fs.readFile(this.filePath, "utf8");
      const data = JSON.parse(text) as unknown;
      if (!Array.isArray(data)) return [];
      return data as TodoDTO[];
    } catch (e: any) {
      if (e?.code === "ENOENT") return [];
      throw new Error(`Failed to read todos file: ${this.filePath}`);
    }
  }

  private async writeAll(todos: TodoDTO[]): Promise<void> {
    try {
      await fs.mkdir(path.dirname(this.filePath), { recursive: true });
      const text = JSON.stringify(todos, null, 2);
      await fs.writeFile(this.filePath, text, "utf8");
    } catch {
      throw new Error(`Failed to write todos file: ${this.filePath}`);
    }
  }
}
```

**ここでのポイント**👇

* `fs` とか `path` は **Adapter側だけ**で使ってる（中心に漏れてない）🛡️✨
* やってることは **読み書き + JSON変換**だけ（業務ルールなし）🥗
* `data/todos.json` が無い時は空で始める（I/Oの都合吸収）👍

---

## 8) 生成物チェックリスト（5秒で検査）✅🔎

AIが出したコードを見たら、まずこれだけ確認して〜😊

### ✅ ヘキサゴナル検査

* [ ] domain/app が **Node/HTTP/DB** を import してない？（してたら即アウト🙅‍♀️）
* [ ] Adapter に **業務ルール**（禁止/二重完了/状態遷移）が入ってない？
* [ ] Port が **でかすぎ**ない？（メソッド増やしすぎ注意⚠️）
* [ ] 変換（DTO/外部型）は **境界に寄ってる**？

### ✅ エージェント系（Agent mode）検査

* [ ] 変更ファイルが増えすぎてない？（まずは小さく！）
* [ ] 提案されたターミナルコマンドを理解してOK押した？([Visual Studio Code][3])
* [ ] 最後に `git diff` 見た？🫣
* [ ] テスト回した？🧪

---

## 9) ちょい最新：Copilot Memory（プレビュー）って何？🧠✨

最近、Copilotがリポジトリの理解を溜めていく **Copilot memory** が話題だよ〜📌
「リポジトリ単位で記憶が育つ」感じで、プレビューとして案内されてるよ。([The GitHub Blog][7])
しかも **メモリは“ユーザー単位”じゃなく“リポジトリ単位”**って明記されてる！([GitHub Docs][8])

**使いどころ**はね👇

* 命名規則、フォルダ構成、テスト方針を覚えてくれて、雛形の精度が上がりやすい💖
  **注意**は👇
* チーム/共有リポだと “みんなで同じ記憶” を使う感じになるので、指示書（instructions）を整備してからが安全🎀

---

## 10) ついでに：OpenAI Codex（VS Code拡張）派の人へ 🤖🔧

OpenAI側も **Codex IDE extension** を案内してて、IDEの横で使ったり、タスクを“クラウド側に委任”する方向もあるよ〜。([OpenAI Developers][9])
（どっち派でも、この章の「安全運転ルール」は同じで効くよ😊🛡️）

---

## 11) ミニ演習（手を動かすと定着するよ）📝🎀

### 演習A：Adapter雛形をAIに作らせる（Outbound）🧩

* `FileTodoRepositoryAdapter` をAIに作らせる
* 条件：**新規ファイルのみ**、**Adapter薄く**

### 演習B：テスト雛形をAIに作らせる（UseCase）🧪

* `AddTodo` の失敗ケース（タイトル空）からテスト追加
* 条件：**InMemory差し替え**、仕様が読めるテストにする

### 演習C：AIに自己レビューさせて直させる 🔍

* チェックリスト（中心汚染/太いAdapter/巨大Port）を投げて修正させる

---

## 12) 今日のまとめ 🎁💖

* AIに任せるのは **雛形・繰り返し・テストの土台**🤖✨
* 任せないのは **Port設計・依存の向き・ドメインルール**🛡️🔥
* 安全運転は **計画→差分→検査**🚦
* 指示書ファイル（`copilot-instructions.md`）はマジで効く🎀✨([Visual Studio Code][4])

---

おまけ（超安心材料）📌
TypeScriptは公式の最新リリースノートが **5.9（2026-01-21更新）**として出てるので、この章も「2026年最新前提」で組んでOKだよ〜😊✨([typescriptlang.org][10])

[1]: https://docs.github.com/en/copilot/get-started/features?utm_source=chatgpt.com "GitHub Copilot features"
[2]: https://code.visualstudio.com/docs/copilot/reference/workspace-context?utm_source=chatgpt.com "Make chat an expert in your workspace"
[3]: https://code.visualstudio.com/docs/copilot/chat/getting-started-chat?utm_source=chatgpt.com "Getting started with chat in VS Code"
[4]: https://code.visualstudio.com/docs/copilot/getting-started?utm_source=chatgpt.com "Get started with GitHub Copilot in VS Code"
[5]: https://code.visualstudio.com/docs/copilot/customization/custom-instructions?utm_source=chatgpt.com "Use custom instructions in VS Code"
[6]: https://docs.github.com/en/copilot/reference/cheat-sheet?utm_source=chatgpt.com "GitHub Copilot Chat cheat sheet"
[7]: https://github.blog/changelog/2026-01-15-agentic-memory-for-github-copilot-is-in-public-preview/?utm_source=chatgpt.com "Agentic memory for GitHub Copilot is in public preview"
[8]: https://docs.github.com/en/copilot/concepts/agents/copilot-memory?utm_source=chatgpt.com "About agentic memory for GitHub Copilot"
[9]: https://developers.openai.com/codex/ide/?utm_source=chatgpt.com "Codex IDE extension"
[10]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"