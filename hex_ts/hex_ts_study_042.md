# 42. 直し方テンプレ：分解の手順書 🔧📌


# 第42章：直し方テンプレ📌🔧「混ざったコード」をヘキサゴナルに分解する手順書 🏰🔌🧩✨

この章は、「動いてるけど、直すのが怖いコード😵‍💫」を **少しずつ安全に** ほどいて、**中心（ルール）を守れる形**にしていくための “分解レシピ” だよ〜😊💖
（2026年1月時点だと、Node は 24 系が Active LTS、TS は 5.9 系が最新安定版として案内されてるよ〜🧠✨。 ([Node.js][1])）

---

## 1) この章のゴール 🎯💞

この章の最後に、あなたはこうなれる！✨

* 「この関数、責務が混ざってる😱」を **見つけられる** 👀🔍
* それを **Port（約束）に切り出して** 🔌
* **Adapter（変換・呼び出し係）へ移動して** 🧩
* **テストで守りながら** 🧪🛡️
* “中心が外を知らない”形に直せるようになる！🏰✨

---

## 2) 分解の前に：いちばん大事な作戦 🗺️🛡️

いきなり大改造しないよ！🙅‍♀️💦
ヘキサゴナルのリファクタは **「一口サイズ🍰」で進める**のが勝ち✨

### ✅ 絶対ルール（安全装備）🧯✨

* 1ステップごとに **必ず動く状態に戻す** 🔁
* 変更が小さいうちに **コミット**（“小刻み保存”）📌
* **テストが無いなら、先に薄いテスト（動作保証）を作る** 🧪

---

## 3) 今日の題材：よくある「混ぜこぜ」地獄 😵‍💫💥

例えばこんなの（HTTP handler が全部やってる）👇

```ts
// ❌ あるある：入力チェック・ルール・DB・レスポンスが全部ここ
export async function postTodo(req: any, res: any) {
  const title = (req.body?.title ?? "").trim();
  if (!title) return res.status(400).json({ message: "title required" });

  // ルール（本当は中心に置きたい）
  if (title.length > 50) return res.status(400).json({ message: "too long" });

  // DB（外側）
  const saved = await prisma.todo.create({
    data: { title, completed: false },
  });

  // 表示（外側）
  return res.status(201).json({
    id: saved.id,
    title: saved.title,
    completed: saved.completed,
  });
}
```

これ、動くけど…

* ルール変更が怖い😱
* DB変えたら壊れる😱
* テストしにくい😱
  が揃ってるやつ！

---

## 4) 直し方テンプレ🔧📌（この順でやれば迷子になりにくい！）

ここからが本題✨
**①→②→③→④** の順でやるよ😊💕

---

# ✅ ① 混ざってる責務を発見する 👀🎨

まずは “何が混ざってる？” を見える化しよ！

### 🎨 色分け4分類（超使える✨）

* 🟦 **入力**：パース、バリデーション、トリム、型変換
* 🟥 **ルール**：業務判断、不変条件、状態遷移
* 🟩 **外部I/O**：DB/ファイル/外部API/時間/UUID
* 🟨 **出力**：レスポンス整形、画面表示、ステータスコード

さっきのコードで言うと👇

* 🟦 `trim()` と `空チェック`
* 🟥 `50文字制限`
* 🟩 `prisma.todo.create`
* 🟨 `res.status().json(...)`

### ✅ ここでのゴール

「この関数、中心（🟥）と外側（🟩🟨）が混ざってる！」って言える状態にする😊✨

---

# ✅ ② Port（約束）を “最小” で決める 🔌✂️

次にやるのはこれ👇
**「中心が欲しいものだけ」をインターフェースにする**✨

ポイントは **最小**！
「DBの都合」じゃなくて「ユースケースの言葉」にするよ😊

## ②-1) まず UseCase を言語化する 🧠📝

今回なら：

* ユースケース名：`AddTodo`
* 入力：`title`
* 出力：`id/title/completed`

## ②-2) DTO を作る（外に漏らす形）📮✨

```ts
export type AddTodoInput = { title: string };
export type AddTodoOutput = { id: string; title: string; completed: boolean };
```

## ②-3) Outbound Port（保存の約束）を最小で作る 💾🔌

```ts
export interface TodoRepositoryPort {
  create(todo: { title: string; completed: boolean }): Promise<{ id: string; title: string; completed: boolean }>;
}
```

> ✅ ここが大事：Port は「中心が必要なことだけ」！
> `findByFooAndBarAndBaz()` みたいな巨大化はあとで地獄になるよ🐘💥

---

# ✅ ③ Adapter に移動（変換と呼び出しだけ残す）🧩🏃‍♀️

ここで「混ぜこぜ関数」をほどいていくよ✨
順番としては **中心→外側** がラク😊

## ③-1) 中心（UseCase）を作る 🏰❤️

```ts
export class AddTodoUseCase {
  constructor(private readonly repo: TodoRepositoryPort) {}

  async execute(input: AddTodoInput): Promise<AddTodoOutput> {
    const title = input.title.trim();

    // 🟥 ルールは中心！
    if (!title) throw new Error("title required");
    if (title.length > 50) throw new Error("too long");

    return await this.repo.create({ title, completed: false });
  }
}
```

## ③-2) Outbound Adapter（DB実装）を作る 🧩💾

```ts
export class PrismaTodoRepositoryAdapter implements TodoRepositoryPort {
  async create(todo: { title: string; completed: boolean }) {
    const saved = await prisma.todo.create({ data: todo });
    return { id: saved.id, title: saved.title, completed: saved.completed };
  }
}
```

## ③-3) Inbound Adapter（HTTP handler）を “薄く” する 🌐🧩

```ts
export async function postTodo(req: any, res: any) {
  try {
    const usecase = new AddTodoUseCase(new PrismaTodoRepositoryAdapter());

    // 🟦 入力はここで（中心に文字列処理を持ち込まない意識！）
    const input = { title: String(req.body?.title ?? "") };

    const out = await usecase.execute(input);

    // 🟨 出力もここで
    return res.status(201).json(out);
  } catch (e: any) {
    return res.status(400).json({ message: e.message ?? "bad request" });
  }
}
```

### ✅ Adapter が薄いかチェック（超重要🥗⚠️）

* Adapter に **業務ルール** が居たらアウト🙅‍♀️
* Adapter の仕事はだいたい

  * 変換🔁
  * 呼び出し📞
  * 例外を外のエラーへ変換🎭
    だけでOK！

---

# ✅ ④ テストで守る（分解の成功を固定する）🧪🛡️

分解のゴールは「綺麗」じゃなくて **壊れない** だよ😊💕

## ④-1) InMemory を作って UseCase を単体テストする 🧠🧪

```ts
import { describe, it, expect } from "vitest";

class InMemoryRepo implements TodoRepositoryPort {
  private seq = 1;
  async create(todo: { title: string; completed: boolean }) {
    return { id: String(this.seq++), title: todo.title, completed: todo.completed };
  }
}

describe("AddTodoUseCase", () => {
  it("タイトルが空ならエラー", async () => {
    const uc = new AddTodoUseCase(new InMemoryRepo());
    await expect(() => uc.execute({ title: "   " })).rejects.toThrow("title required");
  });

  it("正常に追加できる", async () => {
    const uc = new AddTodoUseCase(new InMemoryRepo());
    const out = await uc.execute({ title: "buy milk" });
    expect(out.title).toBe("buy milk");
    expect(out.completed).toBe(false);
  });
});
```

### ✅ これがヘキサゴナルの快感ポイント💖

* DBなしで速い🧠⚡
* ルールが文章みたいに読める📖✨
* 外側を変えても中心のテストは守られる🛡️

---

## 5) “分解できてる？”セルフ診断チェックリスト ✅🔍✨

### 🔌 Port 最小化チェック

* Port のメソッド名が **ユースケースの言葉**になってる？🗣️
* DB都合の引数（`transaction`, `where`, `include`）が混ざってない？😵
* “便利だから”で何でも入れてない？🐘💥

### 🧩 Adapter 薄さチェック

* Adapter に if/for が増えすぎてない？（増えたら🟥が混入してるサイン）🚨
* 変換・呼び出し・例外変換以外をしてない？🥗
* 中心の型（domain）を汚してない？🛡️

---

## 6) AI（Copilot/Codex）を使うと速いところ 🤖⚡（でも任せすぎ注意⚠️）

AIは「手作業がだるいところ」を任せると最強😊✨
（Portの向きとか “設計の芯” は人間が握ろうね🛡️）

### 🤖 コピペで使えるプロンプト集📝

**①責務の棚卸し（色分け）**

```text
この関数を「入力」「業務ルール」「外部I/O」「出力」に分類して箇条書きにして。
業務ルールっぽい行を最優先で抽出して。
```

**②Port案を最小で出す**

```text
このユースケース（AddTodo）に必要なRepositoryのインターフェースを「最小」で提案して。
DB都合の引数は入れないで、ユースケース視点の名前にして。
```

**③Adapterが太ってないかレビュー**

```text
このAdapterのコードを見て、「業務ルールが混ざっていないか」「変換と呼び出しだけになっているか」観点で指摘して。
もし混ざっていたら、中心へ移動する候補を列挙して。
```

---

## 7) ちょい最新トピック（2026年1月時点）🧠✨

* TypeScript は 5.9 のリリースノートが公開されていて、5.9.3 などの 5.9 系が配布されてるよ📦✨ ([typescriptlang.org][2])
* Node は 24 系が Active LTS（25 系は Current）という整理になってるよ🟢 ([Node.js][1])
* ESLint は v10 の RC が出ていて、設定まわり（flat config 移行など）の変更が進んでるよ⚠️ ([eslint.org][3])
* VS Code は “Workspace Trust” を前提に「信頼できない作業フォルダでは意図しないコード実行を避ける」仕組みがあるよ🔒（怪しいリポジトリを開く時は特に意識！） ([Visual Studio Code][4])
* npm は `npm audit` で依存関係の脆弱性チェックができるよ🧯 ([docs.npmjs.com][5])

---

## 8) ミニ演習🎀📝（この章の手順を体に入れる！）

次のどれか1つを選んでやってみて😊✨
（選ぶなら、まずは「1つのAPI/1つのユースケース」だけ🍰）

* ✅ **課題A**：既存の “混ぜこぜ handler” を、①〜④のテンプレ通りに分解
* ✅ **課題B**：Outbound Port を増やしてみる（例：UUID/Clock を Port 化⏰🔌）
* ✅ **課題C**：Adapter をわざと太らせてから、テンプレで救出してみる（比較で理解が爆上がり📈✨）

---

## まとめ🎁💖（第42章の合言葉）

* ①混ざりを見つける👀
* ②約束を最小にする🔌✂️
* ③外の都合はAdapterへ🧩
* ④テストで固定🧪🛡️

---

もし、今あなたが「実際に直したい混ぜこぜ関数」があるなら、そのコード貼ってくれたら、**このテンプレ①〜④で“どこをどう切るか”を一緒にマーキングして分解案を作るよ😊🔧✨**

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[3]: https://eslint.org/blog/2026/01/eslint-v10.0.0-rc.0-released/?utm_source=chatgpt.com "ESLint v10.0.0-rc.0 released"
[4]: https://code.visualstudio.com/docs/editing/workspaces/workspace-trust?utm_source=chatgpt.com "Workspace Trust"
[5]: https://docs.npmjs.com/auditing-package-dependencies-for-security-vulnerabilities/?utm_source=chatgpt.com "Auditing package dependencies for security vulnerabilities"