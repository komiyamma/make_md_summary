# 第21章 Inbound Port：UseCaseの入口を決める 🚪🔌✨

（ちょい最新メモ🔎）いま npm 上の `typescript` 最新は **5.9.3** になってるよ〜📦✨ ([NPM][1])
TypeScript は **6.0→7.0** に向けて大きく変わる流れ（6.0が“橋渡し”で、7.0はネイティブ版）って公式も言ってる！🧠⚡ ([Microsoft for Developers][2])
（Node も **v24 が Active LTS** って書かれてるよ〜🟢） ([Node.js][3])

---

## 1. この章でできるようになること 🎯💖

* 「Inbound Portって何？」を**一言で説明**できるようになる🔌✨
* UseCaseの**入口（引数/戻り値/失敗の形）**をキレイに決められる📮📤
* CLI や HTTP など入口が増えても、**中心（UseCase/ドメイン）がブレない**状態を作れる🛡️😊

---

## 2. Inbound Portってなに？（一言で）🗣️🔌

**Inbound Port = “中心（UseCase）を呼ぶための約束（契約）”** だよ〜😊✨

* 外側（CLI/HTTP/GUIなど）「これ呼びたいんだけど！」
* 中心（UseCase）「OK！その代わり **この形で渡して**、返すのは **この形** ね！」

この「**呼び出しの約束の形**」が Inbound Port 💡
TypeScript でいうと、だいたい **`interface`** or **関数型 `type`** で表現することが多いよ〜✍️
（公式ハンドブックでも “interface も type alias も object type を名付けできる”って説明されてる👍） ([typescriptlang.org][4])

---

## 3. Inbound Portが決める3点セット 🍱✨

Inbound Port では、最低この3つを決めるよ〜👇

### ① 入力（Input）📮

* 何を受け取る？
* どの型で受け取る？
* **外側の都合（HTTPのRequestとか）を混ぜない！** 🙅‍♀️

### ② 出力（Output）📤

* 何を返す？（作成したTodo？ 一覧？）
* 返す型は何？
* **ドメイン型をそのまま返さず、DTOにする**（将来守れる🛡️）

### ③ 失敗（Failure）😵‍💫

* どう失敗を表現する？

  * 例外で投げる？
  * `Result` で返す？（おすすめ寄り✨）
* **外側が困らない形**にするのが大事！

---

## 4. 入口の“入力チェック”はどこでやる？📌😊

ここ、設計で迷いがちポイント〜〜😵‍💫💥
結論からいくね👇

### ✅ 入口（Adapter）でやるチェック（境界チェック）🚪🧼

* 受け取ったものが **型として正しいか**（文字列？数値？）
* 必須が **存在するか**
* 文字列の **trim** とか、形式（長さ・正規表現）
* **HTTPのステータスに変換しやすい**やつ

### ✅ ドメインでやるチェック（不変条件）🧠🧷

* 「タイトル空は禁止」みたいな **ルールそのもの**
* 「完了の二重適用禁止」みたいな **状態遷移のルール**

### ✅ UseCaseでやること（手順と判断）🧠➡️🧠

* 入力を受け取る
* ドメインを作る/操作する
* Repository（Outbound Port）呼ぶ
* 結果をDTOにして返す

> つまり：**“入口で形を整えて、中心でルールを守る”** 💖🛡️

---

## 5. 今回のミニアプリで作る Inbound Port（3つ）📝✅

Todoミニで、UseCaseはこの3つだったよね（第19章あたりのやつ）👇

* `AddTodo`（追加）
* `CompleteTodo`（完了）
* `ListTodos`（一覧）

この3つそれぞれに **Inbound Port** を作るよ〜🔌✨
（1ユースケース=1ポート、が初心者には超わかりやすい😊）

---

## 6. ファイル配置（迷子防止）📁🧭

例：こんな感じに置くのがスッキリ〜✨

* `src/app/ports/in/` … Inbound Port置き場🔌
* `src/app/usecases/` … UseCase本体🧠
* `src/app/dto/` … 入出力DTO📮📤

---

## 7. まずDTOを用意（Input/Output）📮📤✨

（もう作ってある想定でもOKだけど、章の中で形を固定しちゃうね😊）

### AddTodo DTO 📝

```ts
// src/app/dto/add-todo.dto.ts
export type AddTodoInput = Readonly<{
  title: string; // 入口で trim 済み想定✨
}>;

export type AddTodoOutput = Readonly<{
  id: string;
  title: string;
  completed: boolean;
}>;
```

### CompleteTodo DTO ✅

```ts
// src/app/dto/complete-todo.dto.ts
export type CompleteTodoInput = Readonly<{
  id: string;
}>;

export type CompleteTodoOutput = Readonly<{
  id: string;
  completed: true;
}>;
```

### ListTodos DTO 📃

```ts
// src/app/dto/list-todos.dto.ts
export type ListTodosInput = Readonly<{
  // 今回は空でもOK（将来 filter/sort が入るかも✨）
}>;

export type ListTodosOutput = Readonly<{
  items: ReadonlyArray<Readonly<{
    id: string;
    title: string;
    completed: boolean;
  }>>;
}>;
```

> `Readonly` を軽く付けておくと「入口DTOは基本いじらない」感が出て良いよ〜🧊✨
> （TypeScript の object type と `readonly` は公式でも基本として紹介されてるよ） ([typescriptlang.org][4])

---

## 8. Inbound Port を定義しよう（本題）🚪🔌🔥

ここで大事なのは👇

* **外側が依存するのは“Port”だけ**
* Adapter は UseCase の実体（クラス）を知らなくていい
* **Promise に統一**すると後で楽（DB/HTTP混ざっても揺れない）😊

### AddTodo Inbound Port 📝🔌

```ts
// src/app/ports/in/add-todo.port.ts
import type { AddTodoInput, AddTodoOutput } from "../../dto/add-todo.dto";

export interface AddTodoPort {
  execute(input: AddTodoInput): Promise<AddTodoOutput>;
}
```

### CompleteTodo Inbound Port ✅🔌

```ts
// src/app/ports/in/complete-todo.port.ts
import type { CompleteTodoInput, CompleteTodoOutput } from "../../dto/complete-todo.dto";

export interface CompleteTodoPort {
  execute(input: CompleteTodoInput): Promise<CompleteTodoOutput>;
}
```

### ListTodos Inbound Port 📃🔌

```ts
// src/app/ports/in/list-todos.port.ts
import type { ListTodosInput, ListTodosOutput } from "../../dto/list-todos.dto";

export interface ListTodosPort {
  execute(input: ListTodosInput): Promise<ListTodosOutput>;
}
```

> `execute` って名前にしておくと「入口は常に execute」になって迷いにくいよ〜😊✨
> もちろん `handle` とか `run` でもOKだけど、プロジェクトで統一が大事🧁

---

## 9. Port を “小さく保つ”コツ ✂️✨（増やしすぎ防止）

Inbound Port がダメになりやすいのはこの2つ👇

### ❌ でかいポート（何でも屋）🐘💥

* `TodoAppService` に全部詰め込む
* 100メソッドになって地獄😇

### ✅ 小さいポート（ユースケース単位）🍰✨

* 「追加」「完了」「一覧」で別々
* 変更理由が分離される
* テストもしやすい🧪💖

---

## 10. 入口チェック（境界チェック）の“方針”を Port に反映する📌😊

ここ、めちゃ大事〜！✨

Port の `input` は、できればこうしたい👇

* **`unknown` を受け取らない**（解析/バリデーションはAdapterの仕事）
* **「UseCase が理解できる最小の形」**に整えて渡す
* つまり `AddTodoInput` みたいな DTO にする💖

**だから Port のシグネチャは “キレイな入力” を前提にしてOK**✨
（ただし、ドメインの不変条件はドメインで守るよ🛡️）

---

## 11. Adapter から呼ぶと、こうなる（超うすいのが正義）🥗✨

例：CLI Adapter が `AddTodoPort` を呼ぶイメージ👇

```ts
// src/adapters/in/cli/add-todo.cli.ts
import type { AddTodoPort } from "../../../app/ports/in/add-todo.port";

export async function runAddTodoCli(addTodo: AddTodoPort, rawTitle: string) {
  const title = rawTitle.trim(); // ← 境界チェック（最低限）✨
  if (!title) {
    throw new Error("title is required"); // ここは後の章で整える👍
  }

  const created = await addTodo.execute({ title });

  console.log(`created: ${created.id} / ${created.title}`);
}
```

ポイントはこれ👇💡

* CLI は **Port しか知らない**（最高🧠✨）
* 文字列の trim と空チェックは **入口で**
* UseCase には「整った input」だけ渡す📮

---

## 12. “良い Inbound Port” チェックリスト ✅🔍✨

作ったらこれでセルフチェックしてね〜😊💖

* [ ] Port の input/output に **HTTP/Express/Request/Response** が混ざってない？🙅‍♀️
* [ ] **メソッド数が増えすぎてない？**（1ユースケース1つが安心🍰）
* [ ] input は **UseCaseが理解できる最小形**になってる？✂️
* [ ] output は **外側に見せるDTO**になってる？（domain直出ししてない？）🛡️
* [ ] `Promise` で統一されてる？（後でDB/外部APIが来ても平気）🔁

---

## 13. AI拡張の使いどころ（Port編）🤖💖

Portは「設計の芯」だから、AIに**丸投げは禁止**だけど…
次みたいに使うと超強いよ〜✨

### 👍 使ってOK（安全）✅

* DTO から Port の雛形を作らせる
* 命名案を10個出させる
* 「Portが大きすぎない？」のレビュー

### ⚠️ 注意（ここは人間が決める）🧠🔥

* 「UseCaseをどう分割するか」
* 「入力チェックをどこまで入口でやるか」
* 「どの失敗を Result にするか/例外にするか」

#### コピペで使える質問テンプレ📝🤖

* 「この `AddTodoInput` と `AddTodoOutput` から、ヘキサゴナルの Inbound Port を最小で提案して。外部フレームワーク型は絶対に入れないで。」
* 「この Port 設計、将来 HTTP と CLI の両方から呼ぶ前提で不自然な点ある？」
* 「Port が肥大化する兆候があるか、チェックリスト形式で指摘して。」

---

## 14. ミニ課題（5分）📝🎀

### 課題A：ListTodos を拡張してみよう✨

* `ListTodosInput` に `onlyCompleted?: boolean` を足してみて
* Port のシグネチャは変えずに、DTOだけ増やす練習😊

### 課題B：Port 名を “動詞＋名詞” に整える✨

* `AddTodoPort` / `CompleteTodoPort` / `ListTodosPort`
* 迷ったら「ユースケース名＝ポート名」でもOK🍰

---

## まとめ 🎁💖

* **Inbound Port は「UseCaseの入口の約束」** 🔌
* 決めるのは **Input / Output / Failure** の3点セット🍱
* 入力チェックは **入口（Adapter）**、ルールは **ドメイン**、手順は **UseCase** 🛡️✨
* Port は **小さく・薄く・ユースケース単位** がいちばん事故りにくい😊🍰

次の章（Outbound Port）で、今作ったUseCaseが「外へ頼む約束（Repositoryなど）」も作って、いよいよ差し替え可能性が爆上がりするよ〜🔁💾✨

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "typescript"
[2]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/ "Progress on TypeScript 7 - December 2025 - TypeScript"
[3]: https://nodejs.org/en/about/previous-releases "Node.js — Node.js Releases"
[4]: https://www.typescriptlang.org/docs/handbook/2/objects.html "TypeScript: Documentation - Object Types"
