# 第39章：Webフレームワークは“外側”として置くだけ🧱⚙️🌍

この章はね、**「Express/FastifyみたいなWebフレームワークを、中心（Entities / UseCases）に“混ぜない”」**のがテーマだよ😊✨
フレームワークは便利だけど、便利さの代償として「依存」が強いの。だから **いちばん外側（Frameworks & Drivers）に押し出して使う**のがクリーンアーキのコツ🫶

---

## 0. 2026/01/23 時点の“前提になる最新”だけサクッと把握🧠✨

* Node.jsは **v24がActive LTS**、v25がCurrent という扱いになってるよ📦🟢 ([Node.js][1])
* TypeScript は **npmのlatestが 5.9.3**（今の安定ライン）だよ🧩 ([npm][2])
* Expressは **v5系が正式リリース済み**で、5.1.0 も出てる（v5が“今の本道”）🚀 ([Express][3])

  * v5は「Promise/asyncの扱い」などがより現代的になってるのがポイントだよ✍️ ([GitHub][4])

---

## 1. ここで言う「Webフレームワークは外側」ってどういう意味？🤔💡

### ✅ 外側に置く＝こうする

* ルーティング（`GET /tasks` とか）🛣️
* ミドルウェア（JSONパース、CORS、ログ、認証など）🧴
* リクエスト/レスポンスの“生の型”（`Request/Response`）📨
* HTTPステータス（200/400/500…）🔢

↑これ全部、**Frameworks & Drivers 層**に置くイメージだよ🌍✨

### ❌ やっちゃダメ（中心が汚れるパターン）🙅‍♀️💥

* UseCaseの引数が `express.Request` とかになってる
* Entityが「400を返す」とか言い出す
* “DBやHTTPの都合の言葉”が内側の命名に入り込む（例：`TaskTableRow`, `HttpTaskDto` がEntitiesにいる）

---

## 2. 依存の向きを固定するミニ図🧭✨

* 外側（Web） → 内側（Controller） → UseCase → Entity
* **逆向きは禁止**（UseCaseがExpressをimportした瞬間アウト😇）

イメージ👇

* 🌍 Express（外）
  → 🚪 Controller（変換するだけ）
  → 🎬 UseCase（アプリの方針）
  → ❤️ Entity（ルール）

---

## 3. “置き場ルール”の結論（超大事）📌🧡

### ルールA：Express/Fastifyをimportしていいのは「外側だけ」🧱

* `src/frameworks/...` だけがOK🙆‍♀️
* `src/interface-adapters`, `src/usecases`, `src/entities` はNG🙅‍♀️

### ルールB：HTTPの情報は「変換」してから内側へ📦➡️

内側はこういう**自分たちの型**で話すのが理想だよ✨
（HTTPの匂いを最小限にするの🧼）

---

## 4. 具体例：Express v5で “外側だけ” に閉じ込める実装🧪✨

ここからは「Taskミニアプリ」を想定して、**外側にExpressを置く**形を見せるね😊

### 4-1. まずは内側に寄せたHTTP共通型（Framework非依存）を作る📦

置き場：`src/interface-adapters/http/`

```ts
// src/interface-adapters/http/HttpTypes.ts
export type HttpRequest = {
  method: string;
  path: string;
  params: Record<string, string>;
  query: Record<string, string | string[]>;
  headers: Record<string, string | string[] | undefined>;
  body: unknown;
};

export type HttpResponse = {
  statusCode: number;
  body?: unknown;
  headers?: Record<string, string>;
};
```

ポイント💡

* **ここにはExpressの型を一切入れない**よ🚫
* これでControllerが“Webフレームワーク非依存”になれる✨

---

### 4-2. Controllerは「受け取って→UseCase呼んで→返す」だけ🚪🎬

置き場：`src/interface-adapters/controllers/`

（※UseCaseやPresenterは既にある前提の形で雰囲気を見せるね）

```ts
// src/interface-adapters/controllers/createTaskController.ts
import type { HttpRequest, HttpResponse } from "../http/HttpTypes";
import type { CreateTaskUseCase } from "../../usecases/create/CreateTaskUseCase";

export const createTaskController =
  (useCase: CreateTaskUseCase) =>
  async (req: HttpRequest): Promise<HttpResponse> => {
    // 1) HTTPのbodyから “内側のRequest” を作る（ここが境界の変換）
    const title = (req.body as any)?.title;

    // 2) UseCase呼び出し（UseCaseはHTTPを知らない）
    const result = await useCase.execute({ title });

    // 3) “内側の結果” を HttpResponse に変換して返す（表示都合は外に寄せる）
    if (result.ok) {
      return { statusCode: 201, body: { task: result.value } };
    }

    // エラー変換の本格版は第34章で作ったテーブルを使う想定
    return { statusCode: 400, body: { error: result.error.type } };
  };
```

Controllerの責務は“薄い”ほど勝ち🏆✨

* 変換（HTTP→内側入力）
* UseCase呼び出し
* 変換（内側出力→HTTP用）

だけ！😊

---

### 4-3. ExpressはFrameworks & Driversに隔離して、Controllerを呼ぶだけ🧱🌍

置き場：`src/frameworks/web/express/`

```ts
// src/frameworks/web/express/adaptExpress.ts
import type { Request } from "express";
import type { HttpRequest } from "../../../interface-adapters/http/HttpTypes";

export const adaptExpressRequest = (req: Request): HttpRequest => ({
  method: req.method,
  path: req.path,
  params: req.params as Record<string, string>,
  query: req.query as any,
  headers: req.headers as any,
  body: req.body,
});
```

そしてルーティング👇

```ts
// src/frameworks/web/express/routes.ts
import type { Express, Request, Response } from "express";
import { adaptExpressRequest } from "./adaptExpress";
import type { HttpResponse } from "../../../interface-adapters/http/HttpTypes";

type Controller = (req: any) => Promise<HttpResponse>;

export const registerRoutes = (app: Express, deps: { createTask: Controller }) => {
  app.post("/tasks", async (req: Request, res: Response) => {
    const httpReq = adaptExpressRequest(req);
    const httpRes = await deps.createTask(httpReq);

    if (httpRes.headers) {
      for (const [k, v] of Object.entries(httpRes.headers)) res.setHeader(k, v);
    }
    res.status(httpRes.statusCode).json(httpRes.body ?? {});
  });
};
```

ここが最高に重要💖

* Expressの`Request/Response`は **外側にだけ存在**する
* 内側へ渡すときは **必ず変換**する📦✨

---

### 4-4. Express v5の“asyncがより素直”なところも味方にする🍀

Express v5は、Promise/async系の扱いがより現代的になってるよ（ミドルウェアがrejected promiseを返したときの扱いなど）✨ ([GitHub][4])
なのでルートは基本 `async` で書いてOKに寄ってきてるのが嬉しいポイント😊

---

## 5. よくある事故と、秒速で治すコツ🧯💨

### 事故①：UseCaseが `req.body` を直接読む

* 症状：UseCaseにHTTPの匂いがつく😇
* 治し方：UseCaseの入力は `{ title: string }` みたいな**内側のRequest型**に固定🎁

### 事故②：Controllerが肥大化して“アプリのルール”を書き始める

* 症状：Controllerが賢くなりすぎる🧠💥
* 治し方：判断やルールはUseCase/Entityへ戻す🎬❤️

### 事故③：Expressのエラーハンドリング都合で、内側のエラー設計が崩れる

* 症状：Entityが「404」とか言い出す
* 治し方：**エラーは内側の言葉（DomainError）**、HTTP化は外側（第34章の変換テーブル）⚠️➡️🌐

---

## 6. この章のミニ課題（手を動かすやつ）✍️🧪

### 課題A：ListTasksのルートを追加しよう👀🗒️

* `GET /tasks`
* Controllerは `listTasksController(useCase)` 形式で作る
* Express側は同じように `adaptExpressRequest` して呼ぶだけ

### 課題B：CompleteTaskを `PATCH /tasks/:id/complete` にしよう✅🔁

* paramsから `id` を取り出す（外側で取り出して、内側のRequestに詰める）
* UseCaseはHTTPを知らないまま！

---

## 7. AI相棒（Copilot/Codex）に投げると強いプロンプト例🤖✨

* 「ExpressのRequest/Responseを内側に漏らさず、HttpRequest/HttpResponseに変換するadapter関数を書いて。型安全にしたい」
* 「Controllerを薄く保って、UseCaseのexecuteだけ呼ぶ構造にリファクタして。責務が混ざってたら指摘して」
* 「registerRoutesを増やしても読みやすいように、ルート定義を分割する提案をして」

---

## 8. できたら合格ライン✅🎉（セルフチェック）

* Expressをimportしてるのが `frameworks/` だけになってる？🧱
* UseCase/EntityがHTTP用語（statusCodeとか）を一切知らない？🧼
* ルートは「変換してController呼ぶだけ」になってる？🚪✨
* 後からExpress→別フレームワークに替えても、内側が無傷でいけそう？🔁💖

---

次の第40章では、**DBドライバ/接続設定を“外側に隔離”**して、同じノリで「外側の詳細は全部外へ」って完成度を上げていくよ🗄️➡️🌍✨

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[3]: https://expressjs.com/2025/03/31/v5-1-latest-release.html?utm_source=chatgpt.com "Express@5.1.0: Now the Default on npm with LTS Timeline"
[4]: https://github.com/expressjs/express/releases?utm_source=chatgpt.com "Releases · expressjs/express"
