## 第42章：外部サービス（通知など）もDriverとして外側へ📣✨

「通知したい！」ってなった瞬間、クリーンアーキが一番ありがたくなる章だよ〜😊
Slack / Discord / メール / Push / SMS…みたいな**外部サービス**は、ぜんぶ「外側」！🌍
内側（UseCaseやEntity）にSDKやHTTPの匂いを持ち込まないで、**Port → Adapter → 注入**の流れでキレイに包むよ🧼💕

（ちなみに本日時点だと TypeScript は 5.9 系が安定ラインで、6.0/7.0 の話も進んでるよ📌） ([typescriptlang.org][1])
（Node は v24 が Active LTS で、v22 は Maintenance LTS という状況だよ〜） ([Node.js][2])

---

## 今日やること（ゴール）🎯💪

今回のミニTaskアプリに、こんな機能を足すよ👇

* ✅ **タスクを完了したら通知する**
* ✅ 通知のやり方は後で差し替えられる（Console → Slack Webhook とか）🔁
* ✅ UseCaseは外部サービスを1ミリも知らない😎✨

---

## まず結論：外部サービス連携の“型”はこれだけ🧩

**内側**（UseCase）
→ 「通知してね」という **Port**（インターフェース）だけ知ってる

**外側**（Driver/Adapter）
→ Slack Webhook にHTTPで投げる、メール送る、などを実装する

```text
UseCase(CompleteTask)
   └─ calls NotifierPort  ←（ここが境界！）
          ├─ ConsoleNotifierAdapter
          └─ SlackWebhookNotifierAdapter
```

---

## ステップ1：Portを定義する（内側の言葉で）🔌📘

ポイントはこれ👇
**「Slackに投稿する」じゃなくて「完了を通知する」**って表現にすること💡

```ts
// src/ports/NotifierPort.ts
export type TaskCompletedNotification = {
  taskId: string;
  title: string;
  completedAtIso: string;
};

export interface NotifierPort {
  notifyTaskCompleted(note: TaskCompletedNotification): Promise<void>;
}
```

* ✅ `TaskCompletedNotification` は **内側都合のデータ**（Slackのpayloadにしない！）
* ✅ `Promise<void>` でOK（返り値でUI都合を混ぜない）✨

---

## ステップ2：UseCaseからPortを呼ぶ（外部APIは絶対に触らない）🚫🌐

「CompleteTaskInteractor」の成功時に通知するイメージだよ😊

```ts
// src/usecases/CompleteTask/CompleteTaskInteractor.ts
import { NotifierPort } from "../../ports/NotifierPort";
import { ClockPort } from "../../ports/ClockPort";
import { TaskRepositoryPort } from "../../ports/TaskRepositoryPort";

export class CompleteTaskInteractor {
  constructor(
    private readonly taskRepo: TaskRepositoryPort,
    private readonly clock: ClockPort,
    private readonly notifier: NotifierPort
  ) {}

  async execute(taskId: string): Promise<void> {
    const task = await this.taskRepo.findById(taskId);
    if (!task) throw new Error("TaskNotFound"); // ここは前章までの方針に合わせてね😊

    task.complete(this.clock.now());

    await this.taskRepo.save(task);

    // ✅ 外部サービスの詳細は知らない。ただ「通知して」と言うだけ
    await this.notifier.notifyTaskCompleted({
      taskId: task.id,
      title: task.title,
      completedAtIso: this.clock.now().toISOString(),
    });
  }
}
```

### ここ、超大事💥

* UseCaseは `fetch()` も Slack SDK も知らない
* 知っていいのは **NotifierPortだけ** 🔌✨

---

## ステップ3：まずはConsoleで通知するAdapter（最小で体感）🖥️🎉

外側に実装するよ〜！

```ts
// src/adapters/notifiers/ConsoleNotifier.ts
import { NotifierPort, TaskCompletedNotification } from "../../ports/NotifierPort";

export class ConsoleNotifier implements NotifierPort {
  async notifyTaskCompleted(note: TaskCompletedNotification): Promise<void> {
    console.log(`✅ Task completed! id=${note.taskId} title="${note.title}" at=${note.completedAtIso}`);
  }
}
```

これで「差し替えできる」感が一気に出る😆✨

---

## ステップ4：Slack Incoming Webhook で通知するAdapter（外側だけで完結）💬🔔

Slack の Incoming Webhooks は「Webhook URL に JSON をPOSTする」仕組みだよ📮 ([Slack開発者ドキュメント][3])
なので Adapter は、Webhook URL を受け取って `fetch` で投げるだけ！

> Node の `fetch` は Node 18 でデフォルト有効（当初はexperimental）になって、Node 21 では stable fetch に言及があるよ〜🧠 ([Node.js][4])

```ts
// src/adapters/notifiers/SlackWebhookNotifier.ts
import { NotifierPort, TaskCompletedNotification } from "../../ports/NotifierPort";

export class SlackWebhookNotifier implements NotifierPort {
  constructor(private readonly webhookUrl: string) {}

  async notifyTaskCompleted(note: TaskCompletedNotification): Promise<void> {
    const text = `✅ タスク完了！\n• ${note.title}\n• id: ${note.taskId}\n• at: ${note.completedAtIso}`;

    const res = await fetch(this.webhookUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!res.ok) {
      // 外部サービス都合の失敗は「外側のエラー」だよ⚠️
      throw new Error(`SlackWebhookFailed: ${res.status}`);
    }
  }
}
```

### ここもコツ🧠✨

* Slackのpayload（blocksとか）を **Port側に漏らさない**
* Slack特有の表現は Adapter の中だけ🎁

---

## ステップ5：Composition Root で注入（差し替えスイッチはここだけ）🏗️🔁

「どのNotifierを使うか」を決めるのは外側の役目だよ😊
（環境変数の読み取りもここ側！）

```ts
// src/main/compose.ts （例）
import { CompleteTaskInteractor } from "../usecases/CompleteTask/CompleteTaskInteractor";
import { ConsoleNotifier } from "../adapters/notifiers/ConsoleNotifier";
import { SlackWebhookNotifier } from "../adapters/notifiers/SlackWebhookNotifier";

export function buildCompleteTaskInteractor(deps: {
  taskRepo: any;
  clock: any;
}) {
  const notifier =
    process.env.SLACK_WEBHOOK_URL
      ? new SlackWebhookNotifier(process.env.SLACK_WEBHOOK_URL)
      : new ConsoleNotifier();

  return new CompleteTaskInteractor(deps.taskRepo, deps.clock, notifier);
}
```

* ✅ 差し替えが **1箇所** で完結するのが気持ちいい🥹✨
* ✅ UseCase側は一切変更なし！

---

## 「通知失敗したら、タスク完了も失敗？」問題🤔⚖️

初心者がここでハマりがちなので、方針を2つだけ覚えよ〜！📝✨

### 方針A：通知は “ベストエフォート” にする（おすすめ）🌼

* タスク完了は成功✅
* 通知は失敗してもログだけ残す🪵
  → ユーザー体験が安定しやすい！

### 方針B：通知も含めて “全部成功じゃないとダメ” にする🔥

* 完了処理と通知を強く結びつける
  → 厳密だけど、外部障害でアプリが止まりやすい💦

今回のミニアプリなら、まずは **方針A** が扱いやすいよ😊✨
（本格運用の世界だと「Outbox」や「リトライキュー」とかの話に進むよ📦🚚）

---

## テストはどうする？（答え：Spy/FakeでOK）🧪🎭

外部サービスに本当に投げたらテストが遅い＆壊れやすいので、PortをFakeにするよ！

```ts
// test/SpyNotifier.ts
import { NotifierPort, TaskCompletedNotification } from "../src/ports/NotifierPort";

export class SpyNotifier implements NotifierPort {
  public calls: TaskCompletedNotification[] = [];

  async notifyTaskCompleted(note: TaskCompletedNotification): Promise<void> {
    this.calls.push(note);
  }
}
```

これをUseCaseに注入して、`calls.length === 1` とか確認すればOK😊✨

---

## よくある事故（これだけ避ければ勝ち）🚑💥

* ❌ Port名が `SlackService` になってる（外側用語が内側に侵入）
* ❌ Portの型が `{ text: string, blocks: ... }` みたいにSlack payload そのもの
* ❌ UseCaseの中で `fetch()` しちゃう
* ❌ Webhook URL を Entity や UseCase で読んでる（設定の境界が崩壊）
* ❌ 通知の例外が原因で「タスク完了」が全部失敗になる（方針未決定）

---

## ミニ理解チェック（1分）✅📝

1. 「Slackに投稿する」をPort名にしちゃダメなのはなぜ？🤔
2. NotifierPort が受け取る `TaskCompletedNotification` は、どんな言葉で作るべき？📘
3. Webhook URL を読むのはどの層？🏗️

---

## 提出物（成果物）📦🎀

* `NotifierPort` と `TaskCompletedNotification`
* `ConsoleNotifier` Adapter
* `SlackWebhookNotifier` Adapter（Webhook URLは外側から注入）
* `CompleteTaskInteractor` が通知を呼ぶようになっていること✅

---

## AI相棒に投げるプロンプト（コピペ用）🤖✨

```text
次の方針で、TypeScriptのコードを改善して！
- UseCaseは外部サービス詳細（Slack/HTTP）を知らない
- NotifierPortを定義して注入する
- Portの入出力は内側の言葉で（Slack payloadにしない）
- Adapter側でSlack Incoming WebhookにPOSTする（textだけでOK）
対象コード: （ここに貼る）
```

---

次の章（第43章）で、この「どれを注入するか問題」を **Composition Root** としてもっと気持ちよく整理していくよ〜🏗️💉✨

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks?utm_source=chatgpt.com "Sending messages using incoming webhooks - Slack API"
[4]: https://nodejs.org/en/blog/announcements/v18-release-announce?utm_source=chatgpt.com "Node.js 18 is now available!"
