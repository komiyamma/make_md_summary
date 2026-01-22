# 第33章：ViewModel設計（画面向けの形を固定）📦✨

この章は「Presenterを作ったけど、**じゃあ“画面が欲しい形”ってどう決めるの？**」を、ちゃんと型で固定していく回だよ〜😊🧩
（UIが変わっても中心が無傷でいられるようにする作戦✨）

---

## 1) ViewModelってなに？Responseと何が違うの？🤔💡

* **UseCaseのResponse**：アプリの中心が返す「内側基準の結果」📤

  * 例：`completed: boolean`、`createdAt: Date` みたいな“意味”中心
* **ViewModel**：画面がそのまま使える「外側基準のデータ」🖥️🎀

  * 例：`statusLabel: "完了"`、`createdAtText: "2026/01/23"` みたいな“表示”中心

この「表示に都合いい形に変換する」って考え方は、Presentation Model / MVVM でも同じ発想だよ〜📚✨ ([martinfowler.com][1])
そしてクリーンアーキの文脈だと、それをやるのが **Presenter**（Response→Viewに便利な形へ変換する人）って感じ🧑‍🍳✨ ([Stack Overflow][2])

---

## 2) ViewModel設計のコツ（これ守ると強い）💪✨

### ✅ ルール1：ViewModelは“画面の契約”📜

UI側は ViewModel だけ見れば描画できるのが理想！
「Entityをそのまま渡す」は、あとで高確率で泣く😭

### ✅ ルール2：文字列はViewModelで完成させる📝✨

* 日付フォーマット
* 表示用ラベル（例：完了/未完了）
* 画面用のメッセージ（空表示など）

→ UIに散らすと、画面が増えた瞬間に同じロジックが増殖するよ〜🌀

### ✅ ルール3：画面の“判断”に必要なフラグを入れる🚦

例：

* `canComplete: boolean`
* `showEmptyState: boolean`
* `errorMessage?: string`

UIは **if文ちょっとで済む** ようにしてあげると平和☺️🌸

### ✅ ルール4：ViewModelは“外側なので”外側都合OK🙆‍♀️

CSSクラス名とか、UI用の区分値とか、入れてOK！
（だからこそ、ここに隔離するのが価値💎）

---

## 3) まずは画面の要件を1枚にする🗒️👀

例：タスク一覧画面で表示したいのはこんな感じ👇

* 上に「未完了が何件」みたいなサマリ📊
* 各行に

  * タイトル
  * 状態ラベル（未完了 / 完了）
  * 作成日（表示用文字列）
  * 完了ボタンを出すかどうか

この“欲しい形”を **ViewModelで固定** するよ😊✨

---

## 4) ViewModelの型を定義しよう（Task一覧）🧱✨

```ts
// src/interface-adapters/view-models/taskListViewModel.ts

export type TaskListItemViewModel = Readonly<{
  id: string;
  title: string;

  // 表示用（UIがそのまま出せる）
  statusLabel: "未完了" | "完了";
  createdAtText: string;

  // UIの判断をラクにする
  canComplete: boolean;
}>;

export type TaskListViewModel = Readonly<{
  summaryText: string;          // 例: "未完了 2件"
  items: TaskListItemViewModel[];

  // 空表示などの状態
  emptyMessage?: string;        // 例: "タスクがまだないよ〜🗒️"
}>;
```

ポイントはこれ👇😊

* `createdAtText` みたいに **表示に直結する形** にしてる✨
* `canComplete` で **UIのif地獄を防止** 🙅‍♀️
* `Readonly` で「画面が勝手に書き換えない」雰囲気を作る🔒

---

## 5) Presenterで Response → ViewModel に変換する🎨➡️📦

ここでは例として `ListTasksResponse` を受け取って変換するよ〜！

```ts
// src/interface-adapters/presenters/taskListPresenter.ts
import type { TaskListViewModel } from "../view-models/taskListViewModel";

// UseCaseのResponse（例）
export type ListTasksResponse = Readonly<{
  tasks: ReadonlyArray<{
    id: string;
    title: string;
    completed: boolean;
    createdAt: Date;
  }>;
}>;

export function presentTaskList(response: ListTasksResponse): TaskListViewModel {
  const formatter = new Intl.DateTimeFormat("ja-JP", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });

  const items = response.tasks.map((t) => {
    const statusLabel = t.completed ? "完了" : "未完了";

    return {
      id: t.id,
      title: t.title,
      statusLabel,
      createdAtText: formatter.format(t.createdAt),
      canComplete: !t.completed,
    } as const;
  });

  const remaining = items.filter((i) => i.statusLabel === "未完了").length;

  return {
    summaryText: `未完了 ${remaining}件`,
    items,
    emptyMessage: items.length === 0 ? "タスクがまだないよ〜🗒️✨" : undefined,
  };
}
```

### ✅ このPresenterが守ってること💎

* UseCaseは「表示」を知らない（Dateの整形とか言わない）🧼
* UIは ViewModel だけ見れば描画できる🎉

---

## 6) Presenterのテストを書こう（画面が変わっても安心）🧪✨

「表示用の変換」は壊れやすいから、ここはテスト相性よすぎる😳💕

```ts
// src/interface-adapters/presenters/taskListPresenter.test.ts
import { describe, it, expect } from "vitest";
import { presentTaskList } from "./taskListPresenter";

describe("presentTaskList", () => {
  it("completed を statusLabel に変換し、canComplete を付ける", () => {
    const res = {
      tasks: [
        { id: "1", title: "買い物", completed: false, createdAt: new Date("2026-01-23") },
        { id: "2", title: "提出", completed: true, createdAt: new Date("2026-01-20") },
      ],
    } as const;

    const vm = presentTaskList(res);

    expect(vm.summaryText).toBe("未完了 1件");
    expect(vm.items[0].statusLabel).toBe("未完了");
    expect(vm.items[0].canComplete).toBe(true);
    expect(vm.items[1].statusLabel).toBe("完了");
    expect(vm.items[1].canComplete).toBe(false);
  });

  it("空のとき emptyMessage を出す", () => {
    const vm = presentTaskList({ tasks: [] });
    expect(vm.emptyMessage).toBeDefined();
  });
});
```

---

## 7) ありがちな事故集（先に潰そ〜）🚑💦

* ❌ **EntityをそのままViewに渡す**
  → UI都合が中心に逆流して、変更が地獄に😱
* ❌ **日付整形が画面ごとにバラバラ**
  → 表示の統一ができず、直す箇所が増える🌀
* ❌ **UIのifが増えすぎる**
  → `canComplete` とか `emptyMessage` とか、Presenter側で整えてあげよ😊

---

## 8) AI相棒に投げると強いプロンプト集🤖✨

コピペでOKだよ〜🧁

* 「この画面（タスク一覧）に必要な ViewModel の項目を、UI都合で提案して。文字列整形も含めて！」
* 「ListTasksResponse から TaskListViewModel に変換する Presenter を TypeScript で書いて。UIのifが少なくなるようにフラグも提案して」
* 「Presenterのテスト観点を5個出して、Vitestでテストコードも作って」

---

## 9) この章のミニ課題🎒✨

### ✅ 課題A

「完了」のタスクにはタイトルの前に `✅` を付けて表示したい！
→ ViewModelに `titleText` を追加して Presenterで加工してみて😊

### ✅ 課題B

「未完了が0件のとき」サマリを `ぜんぶ完了〜🎉` にしたい！
→ `summaryText` の組み立てをPresenterで分岐してみて✨

---

## 10) 最新メモ（本日時点のTypeScript）📰✨

GitHubの公式リリース一覧では **TypeScript 5.9.3** が “Latest” として表示されてるよ（2026年1月時点）🔎✨ ([GitHub][3])
（この章で使った型・`as const`・`Intl.DateTimeFormat` みたいなやり方はそのままOKだよ😊）

---

必要なら次は、第34章の「エラー変換（内側→外側の表現）」で、**ドメインエラーを“画面に優しい形”にする設計**を繋げていこ〜⚠️➡️🌈✨

[1]: https://martinfowler.com/eaaDev/PresentationModel.html?utm_source=chatgpt.com "Presentation Model"
[2]: https://stackoverflow.com/questions/59505110/do-i-need-presenter-in-clean-architecture?utm_source=chatgpt.com "Do I need presenter in Clean Architecture?"
[3]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
