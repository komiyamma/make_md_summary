# 第22章：外部APIの冪等性①（リトライ/タイムアウトの落とし穴）🤝⚡

## この章のゴール🎯✨

* 外部API呼び出しで起きる「二重実行💥」の原因が説明できる
* 「リトライしていい条件／ダメな条件🙅‍♀️」を判断できる
* タイムアウト時に「成功したか不明😵‍💫」を安全に扱う設計ができる
* C#（ASP.NET Core）で“現代的な”回復性（Resilience）設定ができる

---

# 1. 外部APIが絡むと、なぜ事故が増えるの？😱📡

外部APIは、こっちのアプリの外にある世界です🌍
つまり…

* ネットワークは切れる📶💨
* 相手は遅いことがある🐢
* 相手は混んでて「429（混雑）」を返すことがある🚧
* たまに「500（相手のサーバーエラー）」もある💥

こういう“一時的エラー（transient error）”は普通に起きる前提で設計するのが今どきです。([Microsoft Learn][1])

---

# 2. いちばんヤバいのは「二重実行」💣🔁

たとえば決済API（課金）を呼ぶ場面💳

## 😇 1回押したつもり

* こっちは課金APIを呼ぶ
* でも途中でタイムアウト（待ちきれず中断）⏳

## 😵 こっちの勘違い

「失敗したっぽいから、もう一回リトライしよ！」

## 💥 でも現実は…

* 相手は“最初の課金を完了してた”
* リトライ分で“2回目の課金”が走る
  ➡️ 二重課金😇🔥

---

# 3. 外部APIの結果は3種類ある（これ超重要）🧠✨

外部API呼び出しの結果って、実はこう分かれます👇

1. **成功✅**（200/201など）
2. **失敗❌**（4xx/5xxなどで確定）
3. **不明😵‍💫**（タイムアウト／通信断／相手は処理したかも…）

この **「不明😵‍💫」** が外部APIの地雷です💣

---

# 4. そもそも「リトライしていい？」はHTTPの性質で変わる📚🌐

HTTPには「安全（safe）」「冪等（idempotent）」という考え方があります🧩
ざっくり言うと…

* **GET/HEAD**：読み取り中心で安全寄り🫶
* **POST**：何かを作る・実行することが多く危険寄り💥
* **PUT/DELETE**：冪等っぽいけど副作用があるので注意⚠️

規格としても「クライアントは、冪等でない処理を勝手にリトライすべきじゃない（除：安全にできると分かってる場合）」という方向です。([RFCエディタ][2])

---

# 5. リトライの判断ルール（初心者向けの決定版）🧭✨

## まず自問①：この呼び出しは“何回やっても同じ結果”にできる？🔁

* **できる（GETなど）** → 自動リトライOKになりやすい✅
* **できない（POSTで課金・予約作成など）** → 自動リトライは危険🙅‍♀️

## 自問②：それは“一時的エラー”っぽい？🌧️

一般に一時的エラー扱いされやすい例👇

* **HTTP 500以上**（相手の都合）
* **HTTP 408**（タイムアウト）
* **HTTP 429**（混雑）
* `HttpRequestException` など通信系の例外
  ([Microsoft Learn][1])

## 自問③：リトライ回数は「少なめ」？🧯

リトライは多いほど安全…ではなく、**過負荷を増やして炎上🔥**することがあります。
基本は **2〜3回**くらいを上限にして、指数バックオフ＋ジッター（揺らぎ）を入れるのが定番です。([Microsoft Learn][1])

---

# 6. “今どきC#”の回復性：Standard Resilience Handler を使う🛠️✨

.NETのHTTP回復性は、`Microsoft.Extensions.Http.Resilience` を使うのが素直です。([Microsoft Learn][1])
（※昔よく見た `Microsoft.Extensions.Http.Polly` は非推奨扱いです。）([Microsoft Learn][3])

さらに大事な注意点👇
**標準設定は「全HTTPメソッドをリトライ」しがち**なので、POST等をそのままにするとデータ重複が起きうる、と公式にも明記されています。([Microsoft Learn][1])

---

# 7. 実装：POSTの自動リトライを止めて、安全に“確認”へ回す🔒➡️🔎

> ねらい：
> **POSTは自動リトライしない🙅‍♀️**
> タイムアウトなど“不明😵‍💫”になったら、**ステータス照会（GET）で確認**する✅

## 7.1 Program.cs（HttpClient＋回復性を設定）🧩

```csharp
using Microsoft.Extensions.Http.Resilience;

var builder = WebApplication.CreateBuilder(args);

// 外部決済API（例）のクライアント
builder.Services.AddHttpClient<PaymentApiClient>(client =>
{
    client.BaseAddress = new Uri("https://api.example-payments.local");

    // HttpClient自身のTimeoutと、回復性のTimeoutを二重にしない方が混乱が少ないので
    // ここは無限にして、下のResilience側で制御するのがわかりやすいです☺️
    client.Timeout = Timeout.InfiniteTimeSpan;
})
.AddStandardResilienceHandler(options =>
{
    // ✅ 超重要：危険なメソッド（POSTなど）は自動リトライを無効化
    options.Retry.DisableForUnsafeHttpMethods();

    // 全体の上限（リトライ込みの合計時間）
    options.TotalRequestTimeout.Timeout = TimeSpan.FromSeconds(20);

    // 1回の試行ごとの上限
    options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(5);
});

var app = builder.Build();

app.MapPost("/orders/{orderId}/pay", async (
    string orderId,
    PayRequest body,
    PaymentApiClient payments,
    HttpContext http,
    CancellationToken ct) =>
{
    // 実務だと「クライアントが送ってくる」か「サーバーが発行してDBに保存」が多いです🔑
    var idempotencyKey =
        http.Request.Headers.TryGetValue("Idempotency-Key", out var v) && !string.IsNullOrWhiteSpace(v)
            ? v.ToString()
            : Guid.NewGuid().ToString("N");

    try
    {
        var result = await payments.ChargeAsync(orderId, body.Amount, idempotencyKey, ct);
        return Results.Ok(new { orderId, result.ChargeId, result.Status, idempotencyKey });
    }
    catch (Exception ex) when (ex is TimeoutException)
    {
        // ⏳ タイムアウト＝失敗確定ではない！
        // ここは「不明😵‍💫」として、照会APIで確認するのが安全🌱
        var status = await payments.TryGetChargeByIdempotencyKeyAsync(idempotencyKey, ct);
        if (status is not null)
        {
            return Results.Ok(new
            {
                orderId,
                status.ChargeId,
                status.Status,
                idempotencyKey,
                note = "timeoutだったけど相手側で処理済みでした✅"
            });
        }

        // まだ確定できない場合は、処理中扱いで返す（同期で粘らない）🌀
        return Results.Accepted(
            $"/orders/{orderId}/pay/status?idempotencyKey={idempotencyKey}",
            new { orderId, idempotencyKey, note = "処理中かもしれません。あとでstatusを見てね🫶" }
        );
    }
});

app.MapGet("/orders/{orderId}/pay/status", async (
    string orderId,
    string idempotencyKey,
    PaymentApiClient payments,
    CancellationToken ct) =>
{
    var status = await payments.TryGetChargeByIdempotencyKeyAsync(idempotencyKey, ct);
    return status is null ? Results.NotFound(new { orderId, idempotencyKey }) : Results.Ok(status);
});

app.Run();

public sealed record PayRequest(decimal Amount);
```

## 7.2 PaymentApiClient（Idempotency-Key を付けて呼ぶ）🔑📨

```csharp
using System.Net;
using System.Net.Http.Json;

public sealed class PaymentApiClient(HttpClient http)
{
    public async Task<ChargeResult> ChargeAsync(
        string orderId,
        decimal amount,
        string idempotencyKey,
        CancellationToken ct)
    {
        using var req = new HttpRequestMessage(HttpMethod.Post, "/charges");
        req.Headers.Add("Idempotency-Key", idempotencyKey);

        req.Content = JsonContent.Create(new { orderId, amount });

        using var res = await http.SendAsync(req, ct);
        res.EnsureSuccessStatusCode();

        return (await res.Content.ReadFromJsonAsync<ChargeResult>(cancellationToken: ct))!;
    }

    public async Task<ChargeResult?> TryGetChargeByIdempotencyKeyAsync(
        string idempotencyKey,
        CancellationToken ct)
    {
        using var req = new HttpRequestMessage(
            HttpMethod.Get,
            $"/charges/by-idempotency-key/{idempotencyKey}");

        using var res = await http.SendAsync(req, ct);

        if (res.StatusCode == HttpStatusCode.NotFound)
            return null;

        res.EnsureSuccessStatusCode();
        return await res.Content.ReadFromJsonAsync<ChargeResult>(cancellationToken: ct);
    }
}

public sealed record ChargeResult(string ChargeId, string Status);
```

---

# 8. 「Idempotency-Key」って実在するの？あるよ！✨🔑

実務の外部APIは、**同じ要求の再送を“1回扱い”にするためのキー**をヘッダーで受け付けることが多いです。
例：Stripe は `Idempotency-Key` を使って「最初の結果（ステータスコード＋ボディ）を保存し、同じキーなら同じ結果を返す」方式を説明しています。([Stripe Docs][4])
PayPal も `PayPal-Request-Id` で同様の考え方をガイドしています。([PayPal Developer][5])

さらに、HTTPの標準化として `Idempotency-Key` ヘッダーを提案するIETFドラフトも進んでいます（※ドラフト段階）。([IETF Datatracker][6])

---

# 9. ありがちなNG集（これやると爆発しがち）💥😇

* ❌ **POST課金を「失敗っぽいから」無限リトライ**
* ❌ タイムアウトを「失敗確定」と決めつけて再送🔁
* ❌ リトライ回数が多すぎて相手APIをさらに混雑させる🚧
* ❌ 429が来てるのに即リトライ連打（相手の指示を無視）
* ❌ ログに「idempotencyKey / requestId」が残ってなくて調査不能🔍💦

---

# 10. ミニ演習📝🌸

## 演習1：リトライ可否を判定しよう🧠

次の操作に「自動リトライOK？🙆‍♀️ / 危険？🙅‍♀️」をつけて、理由を1行で📝

1. GETで商品一覧取得
2. POSTで注文作成
3. PUTで住所更新
4. POSTで決済確定

## 演習2：タイムアウト時の挙動を決めよう⏳

「タイムアウト＝不明😵‍💫」として、次のどれにする？

* A: 202 Accepted（あとでstatus照会）🌀
* B: status照会で確認して、分かれば確定レスポンス✅
* C: その場で再送（※やるなら条件を超厳しく）⚠️

---

# 11. 小テスト（サクッと5問）✅🧠

1. 外部APIの結果が「成功/失敗/不明」の3つになる理由は？
2. POSTの自動リトライが危険な典型例を1つ
3. 429が返ってきた時にまず疑うべきことは？
4. タイムアウトを“失敗確定”にすると何が起きる？
5. .NETの標準回復性で、POSTのリトライを止める方法は？

---

# 12. 実務チェックリスト🧾✨

* ✅ 「この外部呼び出しはリトライして良い操作？」を分類した
* ✅ POST系は **自動リトライ無効**にしている（またはIdempotency-Keyで安全化）([Microsoft Learn][1])
* ✅ タイムアウト時は「不明」として、照会 or 非同期に逃がす
* ✅ リトライ回数は少なめ＆バックオフ（過負荷回避）([Microsoft Learn][1])
* ✅ idempotencyKey / 相関IDをログに残す🔍
* ✅ HttpClientのTimeout設計（デフォルトは100秒）を理解している([Microsoft Learn][7])

---

# 13. AI活用（Copilot/Codex向け）🤖💡

* 「この外部API呼び出し、リトライ条件を“安全寄り”にするとしたら？HTTPステータス別に方針を書いて」
* 「Standard Resilience HandlerでPOSTのリトライを止めつつ、GETだけリトライする設定例をC#で」([Microsoft Learn][1])
* 「タイムアウト時に“成功か不明”を扱うフローを、状態遷移図っぽく」

---

## 次章の予告🎈

次の章では、**「相手が冪等じゃない😵」**（Idempotency-Keyも無い）ときに、どう守るかをやります🛡️✨

[1]: https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience "Build resilient HTTP apps: Key development patterns - .NET | Microsoft Learn"
[2]: https://www.rfc-editor.org/rfc/rfc9110.html "RFC 9110: HTTP Semantics"
[3]: https://learn.microsoft.com/ja-jp/dotnet/core/resilience/ "回復性のあるアプリ開発の概要 - .NET | Microsoft Learn"
[4]: https://docs.stripe.com/api/idempotent_requests?utm_source=chatgpt.com "Idempotent requests | Stripe API Reference"
[5]: https://developer.paypal.com/api/rest/reference/idempotency/?utm_source=chatgpt.com "Idempotency - PayPal API reference"
[6]: https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/?utm_source=chatgpt.com "The Idempotency-Key HTTP Header Field - Datatracker - IETF"
[7]: https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclient.timeout?view=net-10.0 "HttpClient.Timeout Property (System.Net.Http) | Microsoft Learn"
