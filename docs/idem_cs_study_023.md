# 第23章：外部APIの冪等性②（相手が冪等じゃない時の守り）🛡️😵

## この章でできるようになること🎯✨

* 「外部APIに同じリクエストが2回飛ぶ」事故を、こちら側の設計で止める🔁🚫
* タイムアウト時に「成功してるかも…」を前提に、冷静に設計できる😇⏳
* 決済みたいな“やり直したら致命傷”の処理を安全に扱う💳🧯

---

# 23.1 まず現実：外部APIは「成功したのに失敗っぽく見える」🌧️

外部APIあるある👇💥

* 外部は処理を完了したのに、通信が切れてこちらはタイムアウト扱い😵‍💫
* 再送すると、外部側が“もう1回”処理して二重課金・二重登録…💸💸
* しかもネットワークは普通に不安定（リトライは日常）📶

だから結論はこれ👇
**「タイムアウト＝失敗」じゃなくて、むしろ“成功してるかも”** を前提に守るのが大人の設計です🧠✨

---

# 23.2 最初に確認：相手が冪等化をサポートしてない？🤝🔍

ここが超重要ポイント💡
**相手が冪等キー（Idempotency Key）をサポートしてるなら、まずそれを使う**のが最短ルートです🔑✨

代表例（超よく見るやつ）👇

* **Stripe**：`Idempotency-Key` ヘッダー。キーは最大255文字で、最低24時間経過後に自動で削除でき、削除後に同じキーを使うと“新規扱い”になります。 ([Stripe Docs][1])
* **PayPal**：`PayPal-Request-Id` ヘッダー。API呼び出し種別ごとにユニークである必要があり、サーバーが一定期間IDを保持して冪等性を提供します。 ([PayPal Developer][2])
* **Adyen**：`idempotency-key` ヘッダー（最大64文字）。タイムアウトしても同じキーで安全に再送でき、既に処理済みなら最初のレスポンスが返ります。 ([Adyen Docs][3])
* **Square**：多くのAPIで `idempotency_key` を要求（重複呼び出し対策の基本）。 ([Square][4])

また最近は「標準のHTTPヘッダーとして `Idempotency-Key` を定義しよう」というIETFの仕様ドラフトも進んでます📜✨（まだドラフト段階）。 ([IETF Datatracker][5])

---

# 23.3 でも現実：相手が冪等じゃない時、どう守る？🧱🔥

ここからが本題です💪😵
相手が冪等じゃない（または冪等の仕様が弱い）ときは、**こちら側で「外部呼び出しの防波堤」を作る**のが王道です🛡️

## 防波堤の基本パターン：Call Journal（呼び出し台帳）🧾🔒

イメージ👇

1. 外部APIを呼ぶ前に、DBに「呼ぶ予定」を記録する✍️
2. その記録が **1回しか作れない** ように一意制約で守る🧱
3. 記録作成に成功した人だけが外部APIを呼ぶ📞
4. 結果（成功/失敗/不明）をDBに保存して、次の同一要求はそれを返す🔁

## ここで守れる事故✅

* 二重送信が来ても「外部APIに2回は行かない」🚫
* タイムアウトで再送されても「台帳を見て判断」できる🧠
* “同じ注文の支払い”を、**最大1回の外部実行**に抑えられる💳🧯

---

# 23.4 「リトライしていい？」の判断はHTTPの性質から🌐🧠

HTTPには「冪等なメソッド」の考え方があります👇
**PUT/DELETE と “安全なメソッド（GETなど）” は冪等**とされています。 ([IETF Datatracker][6])

だから基本ルールはこう👇

* **GET（状態確認）**：リトライしやすい✅
* **POST（作成・課金）**：リトライは危険⚠️（相手が冪等を提供してる場合だけ安全寄り🔑）

---

# 23.5 3つの守り方セット（実務の鉄板）🥋✨

## 守り①：外部呼び出し前に「一意なキーで台帳を作る」🧾🔒

* キー例：`OrderId` / `PaymentAttemptId`（ビジネス的に“一度きり”の単位）
* DBの一意制約：`(Provider, AttemptId)` で **重複INSERTを不可能にする**

## 守り②：タイムアウト時は「失敗」じゃなく「不明」にする😇⏳

* `Failed` と `Unknown` を分けるの超大事🔥
* `Unknown` のときは👇

  * 外部の「照会API」があるなら照会する（GETで確認）🔍
  * 照会できないなら「保留」にして、後で照合（リコンシリエーション）🧾

## 守り③：補償（キャンセル/返金）へ“逃げ道”を用意する🧯💸

相手が冪等じゃない世界では、100%事故ゼロは難しいこともあるので
**「もし二重になったら戻す」導線**があると強いです✨
（返金API、取消API、管理画面での手動対応など）

---

# 23.6 C#実装：外部APIが冪等じゃなくても安全に呼ぶ（台帳方式）🧑‍💻🛡️

## 今回のゴール🎯

* 同じ `PaymentAttemptId` で何回呼ばれても、外部APIは最大1回しか呼ばない
* 2回目以降は **保存した結果** を返す🔁

---

## ① DBに保存する「外部呼び出し台帳」エンティティ🧾

```csharp
public enum ExternalCallStatus
{
    InProgress = 0,
    Succeeded = 1,
    Failed = 2,
    Unknown = 3, // タイムアウトなど「成功したか不明」
}

public sealed class ExternalCallJournal
{
    public long Id { get; set; }

    public required string Provider { get; set; } // "PaymentX" など
    public required string AttemptId { get; set; } // PaymentAttemptId（冪等単位）
    public required string RequestHash { get; set; } // パラメータ相違検出用（任意）

    public ExternalCallStatus Status { get; set; }
    public string? ExternalReference { get; set; } // 外部側のID
    public string? ResponseJson { get; set; }       // 成功レスポンスの保存（必要な範囲で）
    public string? ErrorCode { get; set; }
    public string? ErrorMessage { get; set; }

    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}
```

> ポイント💡
>
> * `AttemptId` は「この支払い（またはこの操作）は一回だけ」の単位にするのがコツ✨
> * `RequestHash` を入れておくと「同じAttemptIdなのに中身が違う！」を検出できて事故を防げます🧠

---

## ② 一意制約（ここが命）🧱🔥

EF Core 例：

```csharp
using Microsoft.EntityFrameworkCore;

public sealed class AppDbContext : DbContext
{
    public DbSet<ExternalCallJournal> ExternalCallJournals => Set<ExternalCallJournal>();

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) {}

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<ExternalCallJournal>()
            .HasIndex(x => new { x.Provider, x.AttemptId })
            .IsUnique();

        base.OnModelCreating(modelBuilder);
    }
}
```

---

## ③ 外部API呼び出しの“安全ラッパー”実装🛡️📞

流れはこれ👇
**「台帳INSERT → 成功した1人だけ外部へ → 結果保存」** 🔁

```csharp
using System.Security.Cryptography;
using System.Text;
using Microsoft.EntityFrameworkCore;

public sealed class PaymentGatewaySafeClient
{
    private readonly AppDbContext _db;
    private readonly HttpClient _http; // 外部API用

    public PaymentGatewaySafeClient(AppDbContext db, HttpClient http)
    {
        _db = db;
        _http = http;
    }

    public async Task<PaymentResult> ChargeAsync(
        string attemptId,
        ChargeRequest request,
        CancellationToken ct)
    {
        string provider = "PaymentX";
        string requestHash = ComputeHash($"{request.Amount}:{request.Currency}:{request.CustomerId}");

        // 1) まず台帳を作る（最小トランザクション）
        ExternalCallJournal journal;
        try
        {
            journal = new ExternalCallJournal
            {
                Provider = provider,
                AttemptId = attemptId,
                RequestHash = requestHash,
                Status = ExternalCallStatus.InProgress,
            };

            _db.ExternalCallJournals.Add(journal);
            await _db.SaveChangesAsync(ct);
        }
        catch (DbUpdateException)
        {
            // 一意制約に引っかかった＝誰かが先に処理中/処理済み
            journal = await _db.ExternalCallJournals
                .SingleAsync(x => x.Provider == provider && x.AttemptId == attemptId, ct);

            // パラメータ違いは危険なので止める
            if (journal.RequestHash != requestHash)
            {
                return PaymentResult.Conflict("同じAttemptIdで内容が違うよ⚠️（事故防止で停止）");
            }

            return journal.Status switch
            {
                ExternalCallStatus.Succeeded => PaymentResult.FromSaved(journal.ResponseJson!, journal.ExternalReference),
                ExternalCallStatus.InProgress => PaymentResult.Processing("処理中だよ⏳（あとでもう一回見に来てね）"),
                ExternalCallStatus.Unknown => PaymentResult.Unknown("成功したか不明だよ😵（照会 or 後で確認が必要）"),
                ExternalCallStatus.Failed => PaymentResult.Failed(journal.ErrorCode, journal.ErrorMessage),
                _ => PaymentResult.Unknown("状態が不明だよ😵"),
            };
        }

        // 2) ここに来るのは「台帳を作れた1人」だけ✅
        try
        {
            // ⚠️ 相手が冪等じゃない前提なので、POSTの自動リトライはしないのが基本
            using var httpReq = new HttpRequestMessage(HttpMethod.Post, "/charge")
            {
                Content = JsonContent.Create(request),
            };

            using var resp = await _http.SendAsync(httpReq, ct);
            resp.EnsureSuccessStatusCode();

            var body = await resp.Content.ReadAsStringAsync(ct);

            journal.Status = ExternalCallStatus.Succeeded;
            journal.ResponseJson = body;
            journal.ExternalReference = resp.Headers.TryGetValues("X-External-Id", out var values)
                ? values.FirstOrDefault()
                : null;
            journal.UpdatedAt = DateTimeOffset.UtcNow;

            await _db.SaveChangesAsync(ct);
            return PaymentResult.Success(body, journal.ExternalReference);
        }
        catch (TaskCanceledException ex) when (!ct.IsCancellationRequested)
        {
            // タイムアウト系：成功してるかもなので Unknown
            journal.Status = ExternalCallStatus.Unknown;
            journal.ErrorCode = "TIMEOUT";
            journal.ErrorMessage = ex.Message;
            journal.UpdatedAt = DateTimeOffset.UtcNow;

            await _db.SaveChangesAsync(CancellationToken.None);
            return PaymentResult.Unknown("タイムアウト😵‍💫 成功した可能性があるから照会が必要だよ");
        }
        catch (Exception ex)
        {
            journal.Status = ExternalCallStatus.Failed;
            journal.ErrorCode = "EX";
            journal.ErrorMessage = ex.Message;
            journal.UpdatedAt = DateTimeOffset.UtcNow;

            await _db.SaveChangesAsync(CancellationToken.None);
            return PaymentResult.Failed(journal.ErrorCode, journal.ErrorMessage);
        }
    }

    private static string ComputeHash(string s)
    {
        var bytes = SHA256.HashData(Encoding.UTF8.GetBytes(s));
        return Convert.ToHexString(bytes);
    }
}

// 例：返り値モデル（教材用に軽量化）
public sealed record ChargeRequest(decimal Amount, string Currency, string CustomerId);

public sealed record PaymentResult(string Kind, string Message, string? RawJson = null, string? ExternalRef = null)
{
    public static PaymentResult Success(string json, string? extRef) => new("Success", "成功だよ✅", json, extRef);
    public static PaymentResult FromSaved(string json, string? extRef) => new("Success", "前回の結果を返すよ🔁✅", json, extRef);
    public static PaymentResult Processing(string msg) => new("Processing", msg);
    public static PaymentResult Unknown(string msg) => new("Unknown", msg);
    public static PaymentResult Failed(string? code, string? msg) => new("Failed", $"失敗だよ⚠️ {code}: {msg}");
    public static PaymentResult Conflict(string msg) => new("Conflict", msg);
}
```

---

# 23.7 .NETの“賢いリトライ”はこう使う（やりすぎ注意）🧠⚡

.NET では `HttpClient` に回復性（リトライ/タイムアウト/サーキットブレーカー等）を追加する仕組みが用意されています。標準ハンドラーは `AddStandardResilienceHandler` で追加できます。 ([Microsoft Learn][7])

ただし！重要⚠️

* **POST（課金）に無条件リトライを入れると事故る**
* 入れるなら **GET（照会）** や、相手が冪等キーを提供してるPOSTだけにするのが安全寄り🔑

---

# 23.8 ミニ演習📝💳（相手が冪等じゃない決済API想定）

## 演習A：守り案を言語化しよう🧠✨

「外部決済APIが冪等じゃない」前提で、次を埋めてみよう👇

* 冪等の単位（AttemptIdに使うもの）：＿＿＿＿
* 台帳の一意制約キー：＿＿＿＿
* Unknown（タイムアウト）のときの方針：＿＿＿＿（照会／保留／手動確認など）
* 二重になった場合の補償：＿＿＿＿（返金／取消など）

## 演習B：テストして事故を再現→止める🧪💥

1. 同じ `attemptId` で `ChargeAsync` を2回呼ぶ（連打でもOK）🔁
2. 外部APIのログ（またはモック）を見て「外部が1回しか呼ばれてない」を確認✅
3. わざとタイムアウトを起こして `Unknown` になるのを確認😵‍💫

---

# 23.9 小テスト（サクッと理解チェック）🧠✅

**Q1.** 外部API呼び出しでタイムアウトしたとき、「失敗」と断定しない方がいい理由は？
A. ＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿

**Q2.** 相手が冪等じゃないときに、こちら側でまず作るべき“防波堤”は？
A. ＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿

**Q3.** POSTの自動リトライが危険になりやすいのはなぜ？
A. ＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿

**Q4.** 冪等キーを使うとき「同じキーでパラメータが違う」を許すと何が起きうる？
A. ＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿

---

# 23.10 仕上げチェックリスト🧾✨（この章のゴール）

* [ ] 外部呼び出し前に「台帳（Journal）」を作っている🧾
* [ ] 台帳は一意制約で守られている🧱
* [ ] タイムアウトは `Unknown` として扱う設計になっている😵‍💫
* [ ] 2回目以降は“保存した結果”を返せる🔁✅
* [ ] 照会（GET）や補償（返金/取消）の導線がある🔍🧯
* [ ] ログに `AttemptId` / 外部ID / 相関ID を残せる🔎

---

## AI活用🤖✨（コピペで使える）

* 「この外部API操作は再送して安全？危険？理由も含めて整理して」
* 「Unknown（タイムアウト）状態を扱う状態遷移図を作って」
* 「ExternalCallJournal のテーブル設計（PIIを避ける方針込み）を提案して」
* 「“二重課金が起きた時の補償フロー”を初心者向けに説明して」

[1]: https://docs.stripe.com/api/idempotent_requests?utm_source=chatgpt.com "Idempotent requests | Stripe API Reference"
[2]: https://developer.paypal.com/api/rest/reference/idempotency/?utm_source=chatgpt.com "Idempotency"
[3]: https://docs.adyen.com/development-resources/api-idempotency?utm_source=chatgpt.com "API idempotency"
[4]: https://developer.squareup.com/docs/sdks/dotnet/common-square-api-patterns?utm_source=chatgpt.com "Common Square API Patterns"
[5]: https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/?utm_source=chatgpt.com "The Idempotency-Key HTTP Header Field"
[6]: https://datatracker.ietf.org/doc/html/rfc9110?utm_source=chatgpt.com "RFC 9110 - HTTP Semantics"
[7]: https://learn.microsoft.com/ja-jp/dotnet/core/resilience/http-resilience "回復性がある HTTP アプリを構築する: 主要な開発パターン - .NET | Microsoft Learn"
