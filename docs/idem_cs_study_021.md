# 第21章：非同期の冪等性②（処理済み記録で重複を潰す）✅🧾

## 今日のゴール🎯✨

* 同じメッセージ（MessageId）が **2回以上届いても、処理が1回だけ適用される** ようにする🔁➡️✅
* 「処理済み記録テーブル（Inbox / Idempotent Consumer）」の **定番フロー** を C# で実装する💪🧠
* **並行（同時）に届いても壊れない** ところまで守る🛡️⚡

---

## まず前提：非同期は“重複が普通”📬🌧️

非同期メッセージは、ネットワークや実行環境の都合で「同じものがもう一回届く」が起きます😇
たとえば Azure Service Bus だと、処理中にロック期限が切れたり、Abandon（放棄）されたりすると **同じメッセージが再び受信可能** になります🔁 ([Microsoft Learn][1])
RabbitMQ でも ACK の仕組み上「少なくとも1回（at-least-once）」になりやすいので、**コンシューマは冪等に作るのが推奨** されています🐰✅ ([RabbitMQ][2])

---

## 解決策：Idempotent Consumer（Inbox）パターン📮✅

発想はシンプルです✨

> **「MessageId を DB に記録して、2回目以降は“もう処理した”として捨てる」**

この「処理済み記録」が **Inbox（受信箱）** みたいに働きます📥🧾

---

## いちばん大事な“鉄の3ルール”🧱🔒

### ルール①：メッセージに一意な MessageId を持たせる🔑

* 「このメッセージは同じものだよ」を識別できないと、重複判定できません😵‍💫
* GUID でOKです✨

### ルール②：処理の最初に「処理済みテーブルへ INSERT」を試みる🧾

* **ユニーク制約**で「同じ MessageId は1回だけ」になるようにする💥➡️✅
* ここで弾かれたら **重複なので即終了**（でもメッセージは “完了扱い” にする）🎉

### ルール③：業務処理と「処理済み記録」は同じトランザクションでまとめる🧠🧷

* 途中で落ちても整合性が崩れないようにするためです⚡

---

## ミニドメイン（教材用）🛒💳

**PaymentConfirmed（支払い確定）** メッセージを受け取ったら…

* Orders の状態を `Paid` にする✅
* 同じ MessageId がもう一回来ても、**Paid が増えたり二重反映したりしない** 🔁🚫

---

## DB設計：ProcessedMessages（処理済み記録）🧾🗃️

### テーブル設計の例（最小）✨

* `MessageId`：重複判定キー🔑
* `Consumer`：どのハンドラで処理したか（複数ハンドラがあると便利）🏷️
* `ProcessedAt`：いつ処理したか🕒

### SQL（イメージ）

```sql
CREATE TABLE ProcessedMessages (
    Id           INTEGER PRIMARY KEY AUTOINCREMENT,
    MessageId    TEXT    NOT NULL,
    Consumer     TEXT    NOT NULL,
    ProcessedAt  TEXT    NOT NULL
);

-- 同じメッセージを同じコンシューマで2回処理させない
CREATE UNIQUE INDEX UX_ProcessedMessages_MessageId_Consumer
ON ProcessedMessages (MessageId, Consumer);
```

> ✅ **ポイント**：ユニーク制約が“最後の砦”です🛡️
> アプリの if 文だけだと、同時実行で負けます（レースで突破される）🏎️💥

---

## 実装（EF Core 10 / .NET 10）で作るよ🧑‍💻✨

2026年1月時点だと、.NET 10 と C# 14 が最新ラインで、EF Core 10 は LTS です📌 ([Microsoft Learn][3])

---

## コード：エンティティ＆DbContext🧩🧾

### Order

```csharp
public enum OrderStatus
{
    Pending = 0,
    Paid = 1
}

public sealed class Order
{
    public Guid Id { get; set; }
    public OrderStatus Status { get; set; } = OrderStatus.Pending;
    public DateTimeOffset? PaidAt { get; set; }
}
```

### ProcessedMessage

```csharp
public sealed class ProcessedMessage
{
    public long Id { get; set; }
    public string MessageId { get; set; } = default!;
    public string Consumer { get; set; } = default!;
    public DateTimeOffset ProcessedAt { get; set; }
}
```

### DbContext（ユニーク制約🔥）

```csharp
using Microsoft.EntityFrameworkCore;

public sealed class AppDbContext : DbContext
{
    public DbSet<Order> Orders => Set<Order>();
    public DbSet<ProcessedMessage> ProcessedMessages => Set<ProcessedMessage>();

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Order>()
            .HasKey(x => x.Id);

        modelBuilder.Entity<ProcessedMessage>()
            .HasIndex(x => new { x.MessageId, x.Consumer })
            .IsUnique(); // ✅ ここが命！

        base.OnModelCreating(modelBuilder);
    }
}
```

---

## コード：メッセージとハンドラ本体📬➡️🛠️

### メッセージ（受信側が読む形）

```csharp
public sealed record PaymentConfirmed(
    string MessageId,
    Guid OrderId,
    DateTimeOffset PaidAt
);
```

### “重複なら即終了”ハンドラ✅🧾

```csharp
using Microsoft.EntityFrameworkCore;

public sealed class PaymentConfirmedHandler
{
    private const string ConsumerName = nameof(PaymentConfirmedHandler);
    private readonly AppDbContext _db;

    public PaymentConfirmedHandler(AppDbContext db) => _db = db;

    public async Task<bool> HandleAsync(PaymentConfirmed msg, CancellationToken ct)
    {
        // true: 今回は処理した / false: 重複でスキップした
        await using var tx = await _db.Database.BeginTransactionAsync(ct);

        _db.ProcessedMessages.Add(new ProcessedMessage
        {
            MessageId = msg.MessageId,
            Consumer = ConsumerName,
            ProcessedAt = DateTimeOffset.UtcNow
        });

        try
        {
            // ✅ まず「処理済み記録」を確保しにいく
            await _db.SaveChangesAsync(ct);
        }
        catch (DbUpdateException ex) when (ex.IsUniqueConstraintViolation())
        {
            // 🔁 すでに処理済み（ユニーク制約に負けた）
            await tx.RollbackAsync(ct);
            return false;
        }

        var order = await _db.Orders.SingleAsync(x => x.Id == msg.OrderId, ct);

        // ✅ “状態を指定する”感じで安全に（すでにPaidなら何もしない）
        if (order.Status != OrderStatus.Paid)
        {
            order.Status = OrderStatus.Paid;
            order.PaidAt = msg.PaidAt;
            await _db.SaveChangesAsync(ct);
        }

        await tx.CommitAsync(ct);
        return true;
    }
}
```

### ユニーク制約違反の判定（DB別に軽く吸収）🧯

SQLite / SQL Server などで例外の中身が違うので、最低限の吸収をします😊
（教材では “雰囲気” でOK！本番はプロジェクトDBに合わせて調整します✨）

```csharp
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;

public static class EfCoreExceptionExtensions
{
    public static bool IsUniqueConstraintViolation(this DbUpdateException ex)
    {
        // SQLite: SqliteException.SqliteErrorCode == 19 が UNIQUE constraint failed
        if (ex.InnerException is SqliteException sqliteEx)
            return sqliteEx.SqliteErrorCode == 19;

        // SQL Serverなどはプロバイダ別の例外型を見る（ここでは簡略）
        return false;
    }
}
```

---

## ミニ演習：同じ MessageId を2回流して確認🔁✅

「同じ MessageId の PaymentConfirmed を2回処理」して、Orders が増えない・状態が壊れないのを確認します🧪✨

### 擬似テスト（超ミニ）

```csharp
var orderId = Guid.NewGuid();
db.Orders.Add(new Order { Id = orderId });
await db.SaveChangesAsync();

var handler = new PaymentConfirmedHandler(db);

var msg = new PaymentConfirmed(
    MessageId: Guid.NewGuid().ToString("N"),
    OrderId: orderId,
    PaidAt: DateTimeOffset.UtcNow
);

var first = await handler.HandleAsync(msg, CancellationToken.None);
var second = await handler.HandleAsync(msg, CancellationToken.None);

Console.WriteLine($"1回目={first}, 2回目={second}"); // 期待: true, false ✅
```

---

## 実運用っぽく：Azure Service Bus（エミュレータ）で重複を体験🚌💨

Azure Service Bus はローカル用エミュレータがあり、Docker で動かせます🐳✨
2026-01-16 にエミュレータ v2.0.0 がリリースされています📌 ([Microsoft Learn][4])

### エミュレータ接続文字列（ローカル実行の例）

Microsoft Learn の手順だと、ローカル実行アプリからはこんな接続文字列になります🧾

```text
Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;
```

（管理操作は `:5300` が必要なケースもあります） ([Microsoft Learn][5])

> ⚠️ エミュレータは **開発・テスト用** です（本番利用はしない） ([Microsoft Learn][4])

---

## “ブローカー側の重複排除”もあるけど、アプリ側は必須だよ🧠🛡️

Azure Service Bus には Duplicate Detection（重複検出）があり、一定時間ウィンドウ内は **同じ MessageId を落とす** ことができます🔁🚫 ([Microsoft Learn][6])
でも、こういう理由で「アプリ側の冪等（Inbox）」はやっぱり必要になりがちです😇

* 時間ウィンドウ外の重複は防げない⌛
* 受信側の処理中に再配達が起きる（ロック期限など）📬🔁 ([Microsoft Learn][1])
* 技術や設定が変わっても壊れない“最後の砦”が欲しい🛡️

---

## 重要なお知らせ：古い Service Bus SDK は移行が必要📦⚠️

Azure Service Bus の古い SDK（`WindowsAzure.ServiceBus` / `Microsoft.Azure.ServiceBus` など）は **2026-09-30 にリタイア予定** と案内されています📌
なので、今から触るなら **最新の Azure SDK 系（`Azure.Messaging.ServiceBus`）** に寄せるのが安心です✅ ([Microsoft Learn][6])

---

## よくある落とし穴集😵‍💫🧯（ここ超大事）

### 落とし穴①：処理済みテーブルに永遠に溜まる🗄️💥

* 対策：TTL（何日保持するか）を決めて掃除🧹⏳
  （第14章の話と合流するやつ！）

### 落とし穴②：メール送信みたいな“外部副作用”が二重になる📧💣

* 対策：

  * メール送信も「処理済み記録」の内側で管理する
  * もしくは送信自体を別イベントに分け、そこにも Inbox を入れる📬✅

### 落とし穴③：ACK（Complete）を先にやっちゃう✅➡️😱

* **DBコミット前に ACK すると、失敗時に二度とリトライできない**
* 対策：**コミット成功 → ACK** の順で✨

---

## AI活用コーナー🤖✨（Copilot/Codex向けプロンプト例）

### 1) DB設計を出してもらう🧾

* 「Inbox（Idempotent Consumer）用の ProcessedMessages テーブル設計を、SQL Server と SQLite の両方で提案して。ユニーク制約も必須で。」

### 2) 例外判定ヘルパを整えてもらう🧯

* 「EF Core の DbUpdateException から UNIQUE 制約違反を判定する拡張メソッドを、SQLite と SQL Server の両方対応で書いて。」

### 3) レビュー観点をチェックリスト化✅

* 「このメッセージハンドラが冪等になっているか、チェック項目を10個作って。」

---

## ミニ演習📝✨

1. `ProcessedMessages` に `PayloadHash`（本文ハッシュ）カラムを追加してみよう🔐

   * **同じ MessageId なのに本文が違う** ときはどう扱う？（怖いよね😱）

2. `Consumer` を変えて、**同じ MessageId でも別ハンドラなら処理できる** 設計にしてみよう🏷️

3. 並行テスト💥

   * 同じ MessageId を **同時に2本** で処理しても、必ず片方が重複扱いになるのを確認🏎️✅

---

## 小テスト🎓💖（3問）

**Q1.** Inbox パターンで一番強い“守り”はどれ？
A. if文で「処理済みならreturn」
B. ログに MessageId を出す
C. DB のユニーク制約で弾く

**Q2.** 「処理済み記録」と「業務更新」を同一トランザクションにする理由は？
A. 速くなるから
B. 途中失敗で整合性が崩れないようにするため
C. コードが短くなるから

**Q3.** Service Bus などで重複が起きる代表例として正しいのは？
A. ロック期限切れで再配達される
B. 必ず1回しか届かない
C. MessageId は自動で常に同じになる

> ✅答え：Q1=C / Q2=B / Q3=A（ロック期限の話） ([Microsoft Learn][1])

---

## まとめ📌✨

* 非同期は重複が起きる前提📬🌧️
* **Inbox（処理済み記録 + ユニーク制約 + トランザクション）** が王道の守り🧾🛡️
* ブローカーの重複排除機能があっても、アプリ側の冪等は“最後の砦”として超重要✅🔁

[1]: https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-queues-topics-subscriptions?utm_source=chatgpt.com "queues, topics, and subscriptions - Azure Service Bus"
[2]: https://www.rabbitmq.com/docs/reliability?utm_source=chatgpt.com "Reliability Guide"
[3]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[4]: https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-emulator-whats-new "What's new with Service Bus emulator - Azure Service Bus | Microsoft Learn"
[5]: https://learn.microsoft.com/en-us/azure/service-bus-messaging/test-locally-with-service-bus-emulator "Test locally by using the Azure Service Bus emulator - Azure Service Bus | Microsoft Learn"
[6]: https://learn.microsoft.com/en-us/azure/service-bus-messaging/duplicate-detection?utm_source=chatgpt.com "Azure Service Bus duplicate message detection"
