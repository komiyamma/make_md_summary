# 第43章：Composition Rootとは（依存を一箇所で組む）🧩🏗️✨

## 1) 今日のゴール 🎯😊

この章が終わったら、こんな状態になってればOKだよ〜！✨

* **Composition Rootをひと言で説明できる**📣
* 「このアプリの依存って何が何に必要？」を**木（ツリー）で描ける**🌳
* “組み立てコード”を**1か所に閉じ込める理由**が腹落ちする💡
* **やりがちな地雷（Service Locator化など）**を回避できる🧨🛡️

---

## 2) Composition Rootってなに？🤔🧩

超ざっくり言うと…

> **アプリの部品（UseCase/Adapter/Driver…）を、最後に“組み立てる場所”**だよ🏗️✨

Mark Seemann（DIの有名な人）が「Composition Rootは、モジュールを組み立てる（compose）**なるべく唯一の場所**」って説明してるよ📌 ([Ploeh Blog][1])

そして超重要なルールがこれ👇

* **組み立てはComposition Rootだけでやる**🧩
* **それ以外のコードは“組み立てない”**（＝newやコンテナ参照を散らさない）🙅‍♀️
* **DIコンテナを使うなら、参照するのはComposition Rootだけ**📦🔒 ([Stack Overflow][2])

---

## 3) なんで「1か所」に閉じ込めるの？💡😆

理由はシンプルに、**設計の事故が激減する**から！🚑💥

### ✅ いいこと①：差し替えが“そこだけ”で済む🔁✨

たとえば TaskRepository を…

* InMemory版 🧺
* SQLite版 🗃️

に切り替えたい時、**組み立てが散ってる**と「どこでnewしてたっけ😇」ってなって地獄…
Composition Rootに閉じ込めておくと、**差し替えは1か所**で終わる🎉

### ✅ いいこと②：依存関係が見える👀🌳

「このUseCaseは何を必要としてる？」がツリーで追えるから、迷子になりにくい🧭

### ✅ いいこと③：中身（中心）が“汚れにくい”🧼💖

UseCaseやEntityが「DBの作り方」「フレームワークの初期化」を知り始めた瞬間に、クリーンアーキが崩れやすい⚠️
組み立てを外に追い出して守るよ🛡️

---

## 4) Composition Rootに「置くもの／置かないもの」📦🚫

### ✅ 置くもの（やっていい）🧩

* DBクライアント生成（例：SQLite接続）🗄️
* Repository/Adapterの生成 🧺🗃️
* UseCaseの生成 🎬
* Controller/Presenterの生成 🚪🎨
* それらをつなぐ“配線” 🔌
* ルーティング登録・サーバ起動（エントリポイント付近）🚀

### ❌ 置かないもの（やっちゃダメ寄り）🙅‍♀️

* ドメインルール（Entityのルール）❤️
* ユースケースの処理そのもの 🎬
* 変換ロジックが肥大化したもの（Mapper/Presenterの本体まで全部）😵‍💫
  → それはAdapters側に置いて、Composition Rootは「つなぐだけ」に寄せたい✨

---

## 5) ミニTaskアプリで「依存の木」を描こう🌳✍️

まずは頭の中を“木”にしてスッキリさせるよ〜！😊✨

「CreateTask」を例にすると、こんな感じ👇

```text
[Web Server / Router]  ← Frameworks & Drivers（外側）
        │
   [Controller]        ← Inbound Adapter（入口）
        │  (Requestに変換)
        v
 [CreateTask UseCase]  ← Use Cases（中心）
        │  (Portに依存)
        v
 [TaskRepository Port] ← Ports（差し替え口）
        │
        v
[SQLiteTaskRepository] ← Outbound Adapter（外側実装）
        │
        v
  [SQLite Driver]      ← Driver（外側）
```

ポイントはここだよ👇😊

* 中心（UseCase）は **Portしか知らない**🔌
* SQLiteの詳細は **外側に押し出す**🗃️
* それらを **最終的に接続するのがComposition Root**🏗️

---

## 6) 「依存ツリー」を作る手順（超実践）🛠️✨

### ステップA：部品を“層ごと”に棚卸しする🧺🧱

最低限、紙でもメモでもOK！📝
このアプリだと、だいたいこんな部品があるよね👇

* UseCase：CreateTask / CompleteTask / ListTasks 🎬
* Ports：TaskRepository / IdGenerator / Clock 🔌🆔⏰
* Outbound Adapter：InMemoryTaskRepository / SQLiteTaskRepository 🧺🗃️
* Inbound Adapter：TaskController（3つのUseCaseを呼ぶ）🚪
* Presenter：Response → ViewModel 🎨📦
* Driver：Webサーバ、DBドライバ ⚙️🗄️

### ステップB：ライフタイム（寿命）を決める🧬

ここ、地味に大事！😳

* **Singleton（1個だけ）**：DB接続、Repository、UseCase（多くはこれ）🗄️
* **Requestごと**：HTTPリクエスト文脈が必要なもの（今回はほぼ無しでもOK）📨
* **毎回生成**：軽いMapper/Presenter（好み）🔁

この判断が曖昧だと「なんか毎回DBつないで遅い😇」みたいな事故が起きる💥

### ステップC：入口（Entry Point）を決める🚪

Composition Rootは「入口の近く」って考えるのが基本だよ📍 ([Ploeh Blog][3])
Webアプリなら、だいたい **main.ts / server.ts / index.ts** あたりが入口になりがち！

---

## 7) フォルダ配置例（迷子防止）📁🧭

「配線」を分離しておくと、気持ちいいよ〜✨

```text
src/
  entities/
  usecases/
  ports/
  adapters/
    inbound/
    outbound/
    presenters/
  frameworks/
    web/
    db/
  composition/
    root.ts        ← ★ここがComposition Root本体
  main.ts          ← ★起動（entry point）
```

* `composition/root.ts`：**依存を組み立てて、アプリを返す**🧩
* `main.ts`：**root.tsを呼んで起動するだけ**🚀

---

## 8) Composition Rootの“形”を作る（雛形）🧩🏗️

ここでは「配線の骨組み」を作るよ！✨（全部つなぐのは次章でガッツリ💉）

### ✅ 例：buildして起動できる形にする

```ts
// src/composition/root.ts
import { createTaskInteractor } from "../usecases/createTask/CreateTaskInteractor";
import { completeTaskInteractor } from "../usecases/completeTask/CompleteTaskInteractor";
import { listTasksInteractor } from "../usecases/listTasks/ListTasksInteractor";

import { createTaskController } from "../adapters/inbound/createTaskController";
import { completeTaskController } from "../adapters/inbound/completeTaskController";
import { listTasksController } from "../adapters/inbound/listTasksController";

import { createTaskPresenter } from "../adapters/presenters/createTaskPresenter";
import { listTasksPresenter } from "../adapters/presenters/listTasksPresenter";

// Outbound adapters
import { createInMemoryTaskRepository } from "../adapters/outbound/inMemoryTaskRepository";
// import { createSQLiteTaskRepository } from "../adapters/outbound/sqliteTaskRepository";

import { systemClock } from "../frameworks/time/systemClock";
import { uuidGenerator } from "../frameworks/id/uuidGenerator";

export type App = {
  controllers: {
    createTask: ReturnType<typeof createTaskController>;
    completeTask: ReturnType<typeof completeTaskController>;
    listTasks: ReturnType<typeof listTasksController>;
  };
};

export function buildApp(): App {
  // 1) Drivers / low-level
  const clock = systemClock();
  const idGen = uuidGenerator();

  // 2) Outbound adapters (Portsの実装)
  const taskRepo = createInMemoryTaskRepository();
  // const taskRepo = createSQLiteTaskRepository({ file: "tasks.db" });

  // 3) Presenters
  const createPresenter = createTaskPresenter();
  const listPresenter = listTasksPresenter();

  // 4) UseCases（Portだけ知ってる状態）
  const createTask = createTaskInteractor({ taskRepo, idGen, clock, presenter: createPresenter });
  const completeTask = completeTaskInteractor({ taskRepo, clock });
  const listTasks = listTasksInteractor({ taskRepo, presenter: listPresenter });

  // 5) Controllers（薄い入口）
  return {
    controllers: {
      createTask: createTaskController({ createTask }),
      completeTask: completeTaskController({ completeTask }),
      listTasks: listTasksController({ listTasks }),
    },
  };
}
```

### ✅ 入口はもっと薄く！🚀

```ts
// src/main.ts
import { buildApp } from "./composition/root";
import { startWebServer } from "./frameworks/web/server";

const app = buildApp();
startWebServer({ controllers: app.controllers });
```

この形にしておくと…

* 組み立ては `buildApp()` だけ🏗️
* サーバ起動は `main.ts` だけ🚀
* UseCase/Entityは配線を知らない💖

…っていう、かなり綺麗な状態になるよ😊✨

---

## 9) よくある地雷 💣😇（これ踏むと一気に汚れる）

### 地雷①：UseCaseの中で `new SQLiteTaskRepository()` しちゃう🗃️💥

→ それ、中心が外側を知ってしまうパターン😇
差し替え不能になるよ〜！

### 地雷②：どこでも `container.resolve()` し始める📦💀

DIコンテナを“便利なグローバル辞書”にすると、実質 **Service Locator** になりやすい⚠️
「コンテナはComposition Rootだけ」ルールで守るのが安全だよ🔒 ([Stack Overflow][2])

### 地雷③：Composition Rootが肥大化して“神ファイル”化👑😵‍💫

対策：

* `buildUseCases()` / `buildAdapters()` みたいに **小さな関数に分割**🧩
* でも「再利用部品化」しすぎると逆に読みにくくなるのでほどほどに✨（Composition Root自体はアプリ専用になりがち、という考え方もあるよ） ([Ploeh Blog][4])

---

## 10) 依存が崩れてないか“見える化”する方法👀🕵️‍♀️

### ✅ 依存グラフをチェック（ルール検証もできる）🛡️

* **dependency-cruiser**：依存の可視化＆「層をまたいだimport禁止」みたいなルールも作れるよ📈 ([GitHub][5])

例（イメージ）：

```bash
npx depcruise src --output-type err-html > reports/deps.html
```

### ✅ 循環参照（サークル）検出🔁😵

* **madge**：循環importの検出＆グラフ化ができる🌀 ([waonpad.github.io][6])

例（イメージ）：

```bash
npx madge --circular src
```

### ✅ ESLintで循環importを警告する🚨

* `eslint-plugin-import` の `import/no-cycle` が有名だよ📌 ([GitHub][7])

---

## 11) 理解チェック✅🧠（ミニ問題だよ〜）

1. Composition Rootに置いていい処理を **3つ**言ってみて😊
2. 「UseCaseからDIコンテナを参照」って、何がヤバい？😇
3. InMemory→SQLiteに差し替える時、**どこが変わるのが理想**？🔁

---

## 12) 今日の提出物（成果物）📦✨

* 🌳 **依存ツリー（手書きでもOK）**：Create/Complete/List の3本
* 🏗️ `composition/root.ts`（buildAppの骨組み）
* 🚀 `main.ts`（薄い起動コード）

---

## 13) AI相棒プロンプト集 🤖💬（コピペOK）

### 依存ツリー作り🌳

```text
このプロジェクト構造（Entities/UseCases/Ports/Adapters/Frameworks）で、
CreateTaskの依存ツリーを「入口→中心→外側実装」方向にASCIIツリーで描いて。
循環参照になりそうなポイントも指摘して。
```

### Composition Rootの肥大化チェック🧹

```text
このbuildApp()が肥大化しそう。読みやすくするための分割案を、
「責務が増えすぎない範囲」で提案して。分割後の関数名も出して。
```

### “コンテナ参照が漏れてないか”監査🔍

```text
DIコンテナ（またはbuildApp）が参照されるべき場所／されてはいけない場所を、
この構成に合わせてチェックリスト化して。
```

---

## まとめ 🎉😊

Composition Rootは、クリーンアーキの「最後の砦」🏰✨
**配線を1か所に集めるだけ**で、差し替え・テスト・保守が一気にラクになるよ〜！🧩💖

次の章（第44章）では、この `buildApp()` を **手動DIで“ちゃんと全部つなぐ”**ところを、気持ちよく完成させようね💉✨

（もし「Web側（server.ts）ってどこまで外側に押し出すのがベスト？」みたいな悩みが出たら、その前提で例を出して整理するよ〜😊📦）

[1]: https://blog.ploeh.dk/2011/07/28/CompositionRoot/?utm_source=chatgpt.com "Composition Root - ploeh blog"
[2]: https://stackoverflow.com/questions/6277771/what-is-a-composition-root-in-the-context-of-dependency-injection?utm_source=chatgpt.com "What is a composition root in the context of dependency ..."
[3]: https://blog.ploeh.dk/2019/06/17/composition-root-location/?utm_source=chatgpt.com "Composition Root location by Mark Seemann - ploeh blog"
[4]: https://blog.ploeh.dk/2015/01/06/composition-root-reuse/?utm_source=chatgpt.com "Composition Root Reuse"
[5]: https://github.com/sverweij/dependency-cruiser?utm_source=chatgpt.com "sverweij/dependency-cruiser: Validate and visualize ..."
[6]: https://waonpad.github.io/blog/articles/49/?utm_source=chatgpt.com "MadgeでTypeScriptプロジェクトの循環参照を検出して予防する"
[7]: https://github.com/import-js/eslint-plugin-import/blob/main/docs/rules/no-cycle.md?utm_source=chatgpt.com "eslint-plugin-import/docs/rules/no-cycle.md at main"
