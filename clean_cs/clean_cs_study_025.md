# 第25章：トランザクション境界はUseCaseに置く💳🧩

> 今日の前提としては、**.NET 10（LTS）**が最新の安定版で、EF Core も **EF Core 10** が現行世代だよ〜🧡（サポート期間も長めで安心） ([Microsoft Dev Blogs][1])

---

## 1) そもそも「トランザクション境界」ってなに？🤔💡

トランザクションは、ざっくり言うと…

* ✅ **全部成功したら確定（commit）**
* ✅ **途中で失敗したら全部なかったことに（rollback）**

っていう **“まとめて一発”** の仕組みだよ〜💪✨ ([Microsoft Learn][2])

で、クリーンアーキ的に大事なのはここ👇

### 🎯 「整合性の単位」はビジネスが決める

「どこまでを “一回の成功” とみなすか？」は **UIでもDBでもなく、アプリのルール側（UseCase）が決める**のが自然なんだよね😊✨
だから、

## ✅ 1ユースケース ＝ 1トランザクション（の感覚）

を基本にするのがスッキリする！🎮📦

---

## 2) まず安心ポイント：EF Coreは `SaveChanges` が自動でトランザクションだよ😌🫶

EF Core（リレーショナルDBの場合）は基本的に、

* `SaveChanges()` / `SaveChangesAsync()` **1回** の中は
* ✅ 自動でトランザクションになって
* ❌ 失敗したらロールバック

してくれるよ〜！✨ ([Microsoft Learn][2])

なので、**最初の最適解**はコレ👇

### 🌟 「UseCaseの最後にSaveChangesを1回だけ」

* 途中で `SaveChanges` を何度も呼ばない
* 1ユースケースの確定は最後にまとめる

---

## 3) じゃあ「手動トランザクション」が必要なのはいつ？🧯💥

EF Coreの自動トランザクションで足りないのは、例えばこんな時👇

### (A) `SaveChanges` を2回以上したい時

例：途中でDB採番IDが必要で、一回保存してから続きやりたい…など

→ そのままやると、**1回目だけ確定して2回目で失敗**みたいな事故が起きる😱

### (B) 複数のDB操作を「まとめて原子化」したい時

* 更新 → 監査ログ → 関連テーブル更新 を“一発で成功”にしたい

### (C) リトライ（耐障害）設定と併用する時（Azure SQLとか）☁️

リトライ実行戦略を有効にしてるのに、手動トランザクションを張ると例外になるケースがあるよ〜
その場合は **ExecutionStrategy で “トランザクション全体を一塊として実行”**が必要！ ([Microsoft Learn][3])

---

## 4) 置き場所ルール：UseCaseが「境界」を決め、外側が「実行」する🧼🔌

ここがクリーンアーキのキモ🧠✨

* ✅ UseCase：**「この処理は原子的にやる」**を決める（境界の宣言）
* ✅ Infrastructure（外側）：**DBトランザクションを実際に開始/commit/rollback**する

UseCaseがEF Coreの `DbContext` を直接触り始めると、だんだん外側依存が混ざりやすいからね🥺💦

---

## 5) 実装パターン①：UseCaseは `IUnitOfWork.SaveChanges()` を最後に1回だけ🧁✨

「自動トランザクション（SaveChanges単位）」を活かす、いちばん素直な形だよ〜😊

### ✅ Core（UseCases側）に置く（インターフェース）

```csharp
public interface IUnitOfWork
{
    Task SaveChangesAsync(CancellationToken ct = default);
}
```

### ✅ UseCase（Interactor）

（例：メモ作成＋監査ログも一緒に保存）

```csharp
public sealed class CreateMemoInteractor : ICreateMemoInputPort
{
    private readonly IMemoRepository _memos;
    private readonly IAuditLogRepository _audit;
    private readonly IUnitOfWork _uow;
    private readonly ICreateMemoOutputPort _output;

    public CreateMemoInteractor(
        IMemoRepository memos,
        IAuditLogRepository audit,
        IUnitOfWork uow,
        ICreateMemoOutputPort output)
    {
        _memos = memos;
        _audit = audit;
        _uow = uow;
        _output = output;
    }

    public async Task Handle(CreateMemoRequest request, CancellationToken ct)
    {
        // Domain側で不変条件が守られる想定🛡️
        var memo = Memo.Create(request.Title, request.Body, request.AuthorId);

        await _memos.AddAsync(memo, ct);
        await _audit.AddAsync(AuditLog.MemoCreated(memo.Id, request.AuthorId), ct);

        // 🌟 ここが「UseCaseのトランザクション境界（確定点）」✨
        await _uow.SaveChangesAsync(ct);

        await _output.Ok(new CreateMemoResponse(memo.Id), ct);
    }
}
```

### ✅ Infrastructure側（EF Core実装）

```csharp
public sealed class EfUnitOfWork : IUnitOfWork
{
    private readonly AppDbContext _db;

    public EfUnitOfWork(AppDbContext db) => _db = db;

    public Task SaveChangesAsync(CancellationToken ct = default)
        => _db.SaveChangesAsync(ct);
}
```

> `SaveChanges` はそれ自体がトランザクションなので、これで「1ユースケース＝1トランザクション」が成立するよ〜🫶 ([Microsoft Learn][2])

---

## 6) 実装パターン②：どうしても複数 `SaveChanges` が必要なら「トランザクション実行役」を外側に置く🎁🧱

UseCaseが「複数段階の保存」をしたい時に、UseCaseへ `BeginTransaction` を直書きしたくない…！ってなるよね🥺

そこで便利なのが **トランザクション・ランナー（外側が実行）**🧙‍♀️✨

### ✅ Coreに置く（宣言だけ）

```csharp
public interface ITransactionalRunner
{
    Task RunAsync(Func<CancellationToken, Task> action, CancellationToken ct = default);
}
```

### ✅ Infrastructure（EF Coreで実行）

```csharp
public sealed class EfTransactionalRunner : ITransactionalRunner
{
    private readonly AppDbContext _db;

    public EfTransactionalRunner(AppDbContext db) => _db = db;

    public async Task RunAsync(Func<CancellationToken, Task> action, CancellationToken ct = default)
    {
        await using var tx = await _db.Database.BeginTransactionAsync(ct);
        try
        {
            await action(ct);
            await tx.CommitAsync(ct);
        }
        catch
        {
            // Dispose時にrollbackされる設計も多いけど、明示しとくと安心🙂
            await tx.RollbackAsync(ct);
            throw;
        }
    }
}
```

### ✅ 使い方：UseCaseはそのまま、外側で“包む”🎀

たとえば **InteractorをDecoratorで包む**とキレイ！

```csharp
public sealed class TransactionalCreateMemoInputPort : ICreateMemoInputPort
{
    private readonly ICreateMemoInputPort _inner;
    private readonly ITransactionalRunner _tx;

    public TransactionalCreateMemoInputPort(ICreateMemoInputPort inner, ITransactionalRunner tx)
    {
        _inner = inner;
        _tx = tx;
    }

    public Task Handle(CreateMemoRequest request, CancellationToken ct)
        => _tx.RunAsync(innerCt => _inner.Handle(request, innerCt), ct);
}
```

これだと **「どのUseCaseをトランザクションで守るか」**をDI（Composition Root）で選べて超ラク〜🥳✨

---

## 7) 実戦注意：リトライ（接続回復）とトランザクションはセットで考えてね☁️🔁

Azure SQL とかで `EnableRetryOnFailure()` を入れてる時、**ユーザー開始のトランザクション（BeginTransaction）**を普通に使うと例外が出ることがあるよ😵‍💫

Microsoft Learnでも、

* 「リトライ戦略は“失敗した処理を丸ごと再実行”する必要がある」
* 「だからトランザクションで括るなら、ExecutionStrategyで全体を実行してね」

って説明されてるよ〜 ([Microsoft Learn][3])

（詳しいコード例も同ページに載ってる✨） ([Microsoft Learn][3])

---

## 8) `TransactionScope` は強いけど、まずは“使わない”寄りでOK🙅‍♀️💦

`TransactionScope`（アンビエントトランザクション）は便利だけど…

* async/await で使うなら `TransactionScopeAsyncFlowOption.Enabled` が必要だったり ([Microsoft Learn][4])
* 複数接続をまたぐと **分散トランザクション**の話が出たり（Windows限定でサポート等） ([Microsoft Learn][2])

…と、初心者フェーズだと事故りやすい🫠💥

なのでこの章のおすすめ優先度は👇
1️⃣ `SaveChanges 1回` に寄せる
2️⃣ どうしても必要なら `BeginTransaction` を “外側のRunner/Decorator” に隔離
3️⃣ それでも足りない最終手段として `TransactionScope`

---

## 9) ミニ課題（手を動かすやつ）📝✨

### 課題1：事故る版を作る😈（学習用）

* `SaveChanges` を2回呼ぶUseCaseを書いて
* 2回目で例外を投げてみて
* **1回目だけ確定しちゃう問題**を確認👀💥

### 課題2：修正版に直す💪

* `SaveChanges 1回` に寄せる（IDはGuid採番にする等）

  * もしくは TransactionalRunner で全体を包む

### 課題3：チェックリスト作成✅

UseCaseごとにこの3点を確認！

* 「成功の定義」は何？（どこまで成功で一回？）🎯
* `SaveChanges` は何回？（1回にできない？）🧁
* 外部API呼び出しをトランザクション内に入れてない？（ロック長引きがち）⏳

---

## 10) AI（Copilot/Codex）にやらせると捗ること🤖💖

* 「このUseCaseの成功条件を “原子性” の観点で言語化して」✍️
* 「SaveChangesが複数回になってる理由を指摘して、1回にまとめる案を3つ出して」🧠
* 「TransactionalRunner + Decorator の雛形を作って。例外時の挙動も含めて」🧩
* 「このInteractorは“境界”が守れてる？DBやHTTPの匂いがしない？」🕵️‍♀️

---

## まとめ🎀✨

* ✅ トランザクション境界（整合性の単位）は **UseCaseが決める**
* ✅ EF Coreは `SaveChanges` 1回なら基本それだけで原子的（自動トランザクション） ([Microsoft Learn][2])
* ✅ 手動トランザクションが必要なら、**外側のRunner/Decorator**に隔離するとクリーン🧼
* ✅ リトライ有効時は ExecutionStrategy とセットで考える（重要！） ([Microsoft Learn][3])
* ✅ `TransactionScope` は最後の手段でOK（async設定や分散Txで沼りやすい） ([Microsoft Learn][4])

---

次の章（第26章）の「例外/エラーの流し方（Core→外）」に繋がるように、もし今のプロジェクト題材（メモ管理）の**“失敗パターン一覧”**を一緒に作りたければ、それもすぐ出せるよ〜！😆📌

[1]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
[2]: https://learn.microsoft.com/en-us/ef/core/saving/transactions "Transactions - EF Core | Microsoft Learn"
[3]: https://learn.microsoft.com/en-us/ef/core/miscellaneous/connection-resiliency "Connection Resiliency - EF Core | Microsoft Learn"
[4]: https://learn.microsoft.com/en-us/dotnet/api/system.transactions.transactionscopeasyncflowoption?view=net-10.0&utm_source=chatgpt.com "TransactionScopeAsyncFlowOpti..."
