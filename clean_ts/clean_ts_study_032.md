# 第32章：Output Boundary：Presenter（出力変換口）を作る🎨✨

ここから一気に「クリーンアーキっぽさ」が出てくるよ〜！😊
**Presenter**はね、UseCaseが返した **Response（内側の都合のよいデータ）** を、画面やAPIが使いやすい **ViewModel（外側の都合のよい形）** に“整形”する係だよ🎀

> クリーンアーキでは Controller → UseCase → Presenter の順で“実行の流れ”が動く例が示されていて、**コード依存は内側（UseCase）へ向く**のがポイントだよ📌 ([クリーンコーダーブログ][1])

---

## 1) Presenterって何をする人？🧑‍🍳🍽️

イメージは「盛り付け担当」🍱✨

* UseCase：栄養バランスの良い料理（ビジネスルール）を作る🥦
* Presenter：お皿にきれいに盛って、食べやすくする🍽️
* View/UI：それを出す（表示する）🖥️

Presenterがやることはだいたいこれ👇

* Response → ViewModel への変換（名前変更・形変換・並び替え）🔁
* 表示用の加工（例：boolean → “完了/未完了”、日付フォーマット）🗓️
* UIを楽にする“ちょい足し”情報の生成（例：`badgeText`）🏷️

逆にやらないこと🙅‍♀️

* **ビジネスルール**（例：「タイトルが空ならダメ」はEntity/UseCaseでやる）
* DBアクセスやHTTPの知識（外側の話）
  Presenterは「表示の都合だけ」に集中するのが王道だよ🍀 ([Stack Overflow][2])

---

## 2) どこに置く？どう繋ぐ？🧭🔌

今回の“出力の道”はこうするよ👇

**UseCase（内側）**
→ OutputBoundary（インターフェース）
→ **Presenter（Interface Adapters）**
→ ViewModel（Interface Adapters）
→ View / APIレスポンス（外側）

> OutputBoundaryを通してPresenterへ渡して、Presenterが「見せやすい形」に詰め替える…という説明がよく使われるよ📦 ([GitHub][3])

そしてWeb開発だと、フレームワーク都合で「Controllerっぽいところが増えがち」だけど、**“変換の責務”をPresenterに閉じ込める**のが狙いだよ🧼 ([Zenn][4])

---

## 3) 実装してみよう：Presenterの“入口”を作る🚪🎨

### 3-1. UseCase側：OutputBoundary（インターフェース）を用意🧩

例：ListTasks の出力境界を作るよ📤

```ts
// src/usecases/listTasks/ListTasksOutputBoundary.ts
import type { ListTasksResponse } from "./ListTasksResponse";

export interface ListTasksOutputBoundary {
  present(response: ListTasksResponse): void;
}
```

ポイント💡

* UseCaseは **OutputBoundaryしか知らない**（Presenterの実体は知らない）✨
* `present()` は **Responseを受け取るだけ**（戻り値を無理に返さない）🙆‍♀️

---

### 3-2. Presenter側：ViewModel型を用意（最小でOK）📦✨

この章では“最小で”いくよ（次の章でViewModelをちゃんと育てる🌱）

```ts
// src/interfaceAdapters/viewModels/TaskListViewModel.ts
export type TaskItemViewModel = {
  id: string;
  title: string;
  statusText: "完了✅" | "未完了🕒";
};

export type TaskListViewModel = {
  items: TaskItemViewModel[];
  total: number;
  completedCount: number;
};
```

---

### 3-3. Presenter実装：Response → ViewModel に変換🎨🔁

```ts
// src/interfaceAdapters/presenters/ListTasksPresenter.ts
import type { ListTasksOutputBoundary } from "../../usecases/listTasks/ListTasksOutputBoundary";
import type { ListTasksResponse } from "../../usecases/listTasks/ListTasksResponse";
import type { TaskListViewModel } from "../viewModels/TaskListViewModel";

export class ListTasksPresenter implements ListTasksOutputBoundary {
  private _viewModel: TaskListViewModel | null = null;

  present(response: ListTasksResponse): void {
    const items = response.tasks.map((t) => ({
      id: t.id,
      title: t.title,
      statusText: t.completed ? "完了✅" : "未完了🕒",
    }));

    const completedCount = response.tasks.filter((t) => t.completed).length;

    this._viewModel = {
      items,
      total: items.length,
      completedCount,
    };
  }

  // ControllerやViewが取り出す用👀
  get viewModel(): TaskListViewModel {
    if (!this._viewModel) {
      // presentが呼ばれる前に見に来た場合の保険🛟
      return { items: [], total: 0, completedCount: 0 };
    }
    return this._viewModel;
  }
}
```

✅ここが気持ちいいところ

* UseCaseは「表示用の文字列（完了✅）」なんて知らない😌
* Presenterは“変換だけ”だからテストが超ラク🧪✨

---

## 4) TypeScriptの最新寄りテク：`satisfies`で“型の安心”を盛る🧁🛡️

Presenterって「変換ミス（プロパティ名間違い）」が起きやすいのね🥺
そこで `satisfies` を使うと、**オブジェクトの形が合ってるかチェック**しつつ、推論も保てるよ✨（TS公式でも説明されてるよ）([TypeScript][5])

```ts
import type { TaskListViewModel } from "../viewModels/TaskListViewModel";

const vm = {
  items,
  total: items.length,
  completedCount,
} satisfies TaskListViewModel;

// vm はそのまま使えるし、型チェックも強い💪
this._viewModel = vm;
```

---

## 5) Controllerからどう使うの？（超ミニ例）🚪➡️🎨➡️🖥️

Controllerは「受け取る→呼ぶ→返す」だけに薄くするよ🧻✨

```ts
// 疑似コード：src/interfaceAdapters/controllers/ListTasksController.ts
export async function listTasksController(req: unknown) {
  const presenter = new ListTasksPresenter();
  const useCase = new ListTasksInteractor(/* ports... */, presenter);

  await useCase.execute(/* request */);

  return presenter.viewModel; // これをJSONにして返す、とかね📦
}
```

> WebだとControllerとPresenterが一体っぽく見えることがあるけど、**“変換だけはPresenterに閉じ込める”**のが崩れにくいよ🧼 ([Zenn][4])

---

## 6) よくあるミス集（先に潰す💣➡️🧯）

### ❌ UseCaseで `statusText: "完了✅"` を作り始める

→ UI都合が内側に侵入してジワジワ腐る🥲
✅ 文字や表示用ラベルはPresenterへ！

### ❌ Presenterに「並び替えルール（業務ルール）」を入れる

例：「重要タスクを最上位」みたいなのが“業務上の意味”なら…
✅ UseCase側に寄せた方が安全（Presenterは“見せ方の都合”だけ）

### ❌ Presenterが外部I/Oし始める（DB/HTTP/ファイル）

✅ Presenterは基本“純粋関数”っぽく保つ（変換だけ）🎀

---

## 7) ミニ課題（手を動かす✍️✨）

### 課題A：ViewModelに「フィルタ表示用」情報を追加🔎

* `hasCompleted: boolean` を追加して
* 一件でも完了があれば `true` にする

### 課題B：並び替え（見た目の都合）をPresenterでやる🔁

* 未完了を上、完了を下に並べる（これは表示都合なのでPresenterでOK🙆‍♀️）

---

## 8) 理解チェック（1問）✅📝

**Q.** 「`completed` が true のとき `"完了✅"` にする処理」は、UseCaseとPresenterどっちに置く？理由も一言で！💡

---

## 9) 提出物（成果物）📦🎁

* `ListTasksOutputBoundary`（interface）
* `TaskListViewModel`（type）
* `ListTasksPresenter`（Response→ViewModel変換）

---

## 10) AI相棒プロンプト（コピペ用🤖✨）

```txt
あなたはクリーンアーキのPresenter担当です。
ListTasksResponse から TaskListViewModel へ変換する Presenter をTypeScriptで実装してください。

条件:
- Presenterは変換のみ（ビジネスロジック禁止）
- statusText は completed に応じて "完了✅" / "未完了🕒"
- satisfies を使って型安全に
- viewModel を getter で取り出せる形に
- 変換漏れが起きないように小さな工夫も提案して
```

---

次の第33章で、**ViewModelを「UI変更に強い形」にきれいに設計**していくよ〜！📦✨
Presenterで作ったViewModelを「どんな項目にするのが筋いいか」って話、めちゃ楽しいやつ😊💖

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "Clean Architecture by Uncle Bob - The Clean Code Blog"
[2]: https://stackoverflow.com/questions/59505110/do-i-need-presenter-in-clean-architecture?utm_source=chatgpt.com "Do I need presenter in Clean Architecture?"
[3]: https://github.com/serodriguez68/clean-architecture/blob/master/part-5-2-architecture.md?utm_source=chatgpt.com "clean-architecture/part-5-2-architecture.md at master"
[4]: https://zenn.dev/sre_holdings/articles/a57f088e9ca07d?utm_source=chatgpt.com "やさしいクリーンアーキテクチャ"
[5]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html?utm_source=chatgpt.com "Documentation - TypeScript 4.9"
