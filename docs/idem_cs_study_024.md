# 第24章：仕上げ（テスト・観測・チェックリスト・卒業課題）🎓✨

## 24.0 この章のゴール🎯

この章では、冪等性を「実装した気がする」から「壊れないって証明できる💪」に仕上げます✨
やることは4つだけ👇

* **テスト**で壊れないのを確認する✅
* **観測（ログ/トレース/メトリクス）**で壊れた時に秒速で追えるようにする🔍
* **チェックリスト**で見落としをゼロに近づける🧾
* **卒業課題**で「実務っぽい完成形」にする🎁

---

## 24.1 冪等性テストの全体像（3層で守る）🛡️🧪

冪等性は、**「1回なら動く」じゃダメ**で、こういう“現実”に耐える必要があるよね😇

* 同じリクエストが **2回/10回** 来る🔁
* ほぼ同時に **並列で** 来る🏎️💥
* 途中でタイムアウトして **成功なのに失敗扱い** になる⌛

だからテストも3層でいくのが王道✨

1. **単体テスト**：冪等キーの判定ルール（同一/差分/期限切れなど）を小さく検証
2. **統合テスト**：HTTPで叩いて、APIとして冪等に見えるか確認（TestServer）([Microsoft Learn][1])
3. **並列テスト**：同時アクセスで“1件に収束”するか確認🏁

---

## 24.2 統合テスト（HTTPで“冪等に見えるか”を保証する）📮✅

ASP.NET Core の統合テストは、**アプリをテスト用に起動して HttpClient で叩く**のが定番だよ〜✨
`WebApplicationFactory<T>` がそのための仕組みを用意してくれてます([Microsoft Learn][2])

### 24.2.1 テストで最低限チェックしたい3本柱🧱

#### ✅ (A) 同じキー + 同じ本文 → 同じ結果

* 1回目：注文作成（orderId が返る）
* 2回目：同じ `Idempotency-Key` で再送 → **同じ orderId が返る**（再実行しない）

#### ✅ (B) 同じキー + 違う本文 → 衝突として止める（例：409）

* “同じチケットで別の内容”は危険⚠️（攻撃・バグ・誤実装の温床）

#### ✅ (C) 連打（10回）でも破綻しない

* 成功回数は1回、結果は10回同じ、が理想✨

---

### 24.2.2 サンプル：xUnit + WebApplicationFactory で冪等性を統合テスト🔁🧪

> 例：`POST /orders` に `Idempotency-Key` ヘッダーを付ける想定
> （統合テストの土台として `Microsoft.AspNetCore.Mvc.Testing` を使うよ）([NuGet][3])

```csharp
using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

public class IdempotencyTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public IdempotencyTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task SameKey_SameBody_ReturnsSameResult()
    {
        var key = Guid.NewGuid().ToString("N");

        var body = new
        {
            customerId = "C-001",
            items = new[] { new { sku = "SKU-AAA", qty = 1 } }
        };

        // 1回目
        var req1 = new HttpRequestMessage(HttpMethod.Post, "/orders")
        {
            Content = JsonContent.Create(body)
        };
        req1.Headers.Add("Idempotency-Key", key);

        var res1 = await _client.SendAsync(req1);
        res1.EnsureSuccessStatusCode();

        var json1 = await res1.Content.ReadFromJsonAsync<OrderResponse>();
        Assert.NotNull(json1);

        // 2回目（再送）
        var req2 = new HttpRequestMessage(HttpMethod.Post, "/orders")
        {
            Content = JsonContent.Create(body)
        };
        req2.Headers.Add("Idempotency-Key", key);

        var res2 = await _client.SendAsync(req2);
        res2.EnsureSuccessStatusCode();

        var json2 = await res2.Content.ReadFromJsonAsync<OrderResponse>();
        Assert.NotNull(json2);

        Assert.Equal(json1!.orderId, json2!.orderId);
    }

    [Fact]
    public async Task SameKey_DifferentBody_ReturnsConflict()
    {
        var key = Guid.NewGuid().ToString("N");

        var body1 = new { customerId = "C-001", items = new[] { new { sku = "SKU-AAA", qty = 1 } } };
        var body2 = new { customerId = "C-999", items = new[] { new { sku = "SKU-BBB", qty = 9 } } };

        // 1回目
        var req1 = new HttpRequestMessage(HttpMethod.Post, "/orders") { Content = JsonContent.Create(body1) };
        req1.Headers.Add("Idempotency-Key", key);

        var res1 = await _client.SendAsync(req1);
        res1.EnsureSuccessStatusCode();

        // 2回目（キー同じ・本文違い）
        var req2 = new HttpRequestMessage(HttpMethod.Post, "/orders") { Content = JsonContent.Create(body2) };
        req2.Headers.Add("Idempotency-Key", key);

        var res2 = await _client.SendAsync(req2);

        Assert.Equal(HttpStatusCode.Conflict, res2.StatusCode);
    }

    private sealed record OrderResponse(string orderId);
}
```

---

## 24.3 並列テスト（“同時に来たら1件に収束”を確認）🏎️💥✅

冪等性の本番ポイントはここ！
**同じキーがほぼ同時に2〜10本来ても、結果が1件に収束する**のが合格ライン🎯

### 24.3.1 サンプル：同じキーを10並列で叩く🔁🔁🔁

```csharp
using System.Net.Http.Json;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

public class ConcurrencyIdempotencyTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public ConcurrencyIdempotencyTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task SameKey_Parallel10_AllReturnSameOrderId()
    {
        var key = Guid.NewGuid().ToString("N");
        var body = new
        {
            customerId = "C-001",
            items = new[] { new { sku = "SKU-AAA", qty = 1 } }
        };

        async Task<string> CallOnce()
        {
            var req = new HttpRequestMessage(HttpMethod.Post, "/orders")
            {
                Content = JsonContent.Create(body)
            };
            req.Headers.Add("Idempotency-Key", key);

            var res = await _client.SendAsync(req);
            res.EnsureSuccessStatusCode();

            var json = await res.Content.ReadFromJsonAsync<OrderResponse>();
            return json!.orderId;
        }

        var tasks = Enumerable.Range(0, 10).Select(_ => CallOnce()).ToArray();
        var results = await Task.WhenAll(tasks);

        // 全部同じ orderId ならOK✨
        Assert.True(results.Distinct().Count() == 1);
    }

    private sealed record OrderResponse(string orderId);
}
```

### 24.3.2 並列テストが落ちた時の“ありがち原因”😭

* DB の **一意制約**が無い / 効いてない🧨
* トランザクション境界がズレてる🌀
* 「作成」→「冪等記録保存」の順が逆で、隙間がある😵
* In-Progress の扱いがあいまいで二重実行になる⚠️

---

## 24.4 観測（ログ・トレース・メトリクス）で“追える冪等性”にする🔍📈✨

冪等性って、**壊れた時に原因が追えないと運用で詰む**の…😇
なので「ログに何を出すか」を仕上げます🧰

### 24.4.1 ログに必ず出したい3点セット🧾✨

* **相関ID（Correlation ID）**：1リクエストを追跡するためのID🧵
* **冪等キー（Idempotency-Key）**：今回の冪等の主役🔑
* **結果の状態**：`Created / Replayed / Conflict / InProgress` みたいな分類🏷️

### 24.4.2 まずは “ログスコープ” で一気に楽する🪄

```csharp
using System.Diagnostics;

app.Use(async (ctx, next) =>
{
    var correlationId =
        ctx.Request.Headers.TryGetValue("X-Correlation-ID", out var cid) && !string.IsNullOrWhiteSpace(cid)
            ? cid.ToString()
            : Guid.NewGuid().ToString("N");

    ctx.Response.Headers["X-Correlation-ID"] = correlationId;

    var idemKey =
        ctx.Request.Headers.TryGetValue("Idempotency-Key", out var ik) ? ik.ToString() : "(none)";

    // Activity は分散トレースの基礎（TraceIdなど）にもなるよ✨
    var traceId = Activity.Current?.TraceId.ToString() ?? "(no-trace)";

    using (logger.BeginScope(new Dictionary<string, object>
    {
        ["correlationId"] = correlationId,
        ["idempotencyKey"] = idemKey,
        ["traceId"] = traceId
    }))
    {
        await next();
    }
});
```

これで以降のログに `correlationId / idempotencyKey / traceId` を自然に混ぜられる👌✨

---

## 24.5 OpenTelemetry で “トレース/メトリクス/ログ” を揃える（最短ルート）🛰️✨

2026年時点の .NET は、**Activity/ILogger など土台がフレームワークにあり**、OpenTelemetry はそれを活用する形になってます([Microsoft Learn][4])
ASP.NET Core 側でも OpenTelemetry を使った可視化が公式ドキュメントとして案内されています([Microsoft Learn][5])

### 24.5.1 「まずローカルで可視化」するなら：OTLP + Dashboard が便利🖥️✨

OTLP で吐いたテレメトリを、ダッシュボードで眺める例が紹介されています([Microsoft Learn][6])

> ここは“運用の入り口”なので、最初は **Trace（どこで止まった？）** が見えればOK🙆‍♀️
> メトリクス（成功率/衝突率）まで見えると強い💪

---

## 24.6 実務チェックリスト（これを守れば事故が激減する）🧾✅✨

### 24.6.1 API設計チェック🔑📮

* [ ] 冪等キーの受け取り場所が決まってる（例：`Idempotency-Key` ヘッダー）
* [ ] キーの形式・最大長が決まってる（UUID推奨など）
* [ ] **同じキー + 本文違い**は衝突扱い（409など）
* [ ] 「同じキー」は **同じレスポンス**を返す（再実行しない）

### 24.6.2 DB/整合性チェック🗃️🛡️

* [ ] 冪等記録テーブルに **一意制約**（キー+操作種別など）
* [ ] 競合時（ユニーク違反など）の処理がある（既存結果を返す等）
* [ ] In-Progress の状態がある（並列で二重実行しない）
* [ ] TTL（保持期限）とクリーンアップ方針が決まってる🧹

### 24.6.3 セキュリティ/運用チェック🔒🧯

* [ ] レスポンス保存に **個人情報**を入れすぎない（必要最小限）
* [ ] ログに機微情報を出さない（カード情報・秘密など）
* [ ] 冪等キーの **再利用リスク**（推測されない/漏れない）に配慮
* [ ] 監視したい指標が決まってる（例：Replay率、Conflict率、InProgress滞留）📈

### 24.6.4 テストチェック🧪✅

* [ ] 同一要求を2回 → 同じ結果
* [ ] 同一要求を10回 → 同じ結果
* [ ] **10並列** → 1件に収束
* [ ] 同じキーで本文違い → 409（または設計で決めたエラー）
* [ ] タイムアウト想定（疑似） → 再送しても破綻しない

### 24.6.5 観測チェック🔍✨

* [ ] ログに `correlationId / idempotencyKey / traceId` が入ってる
* [ ] `Created / Replayed / Conflict / InProgress` の分類がログから分かる
* [ ] 追跡の起点（相関ID）がレスポンスにも返る

---

## 24.7 卒業課題🎁：注文作成APIを“実務品質”に仕上げよう🛒🎓

### 🎯 課題内容

「注文作成API」を **冪等キー方式**で冪等化し、**並列でも1件に収束**させる✨
さらに **ログ/観測**で追えるようにする🔍

### ✅ 必須要件（合格ライン）🏁

* [ ] `POST /orders` が冪等キーを受け取る
* [ ] 同じキー + 同じ本文 → **同じ結果**
* [ ] 同じキー + 本文違い → **409 Conflict**（または明確なエラー）
* [ ] 同じキーで10回再送 → 結果が全部同じ
* [ ] 同じキーで10並列 → **結果が全部同じ**（収束）
* [ ] ログに `correlationId / idempotencyKey / traceId` が出る

### ⭐ 加点（できたら強い）💪✨

* [ ] In-Progress を表現し、滞留したら検知できる
* [ ] Replay/Conflict をメトリクス化してダッシュボードで見える
* [ ] 期限切れ（TTL）後の挙動が仕様として説明できる

### 📝 提出物

* テストコード（統合テスト + 並列テスト）
* 実装コード（冪等の中核）
* チェックリストに “✅” が付いた状態のメモ🧾

---

## 24.8 ミニ小テスト（8問）🧠✨

1. 冪等性が必要になる典型例を2つ言ってね🔁
2. 同じ冪等キーで本文が違う時、なぜ危険？⚠️
3. 「10並列で1件に収束」を壊すありがちな原因を1つ言ってね🏎️
4. 統合テストで `WebApplicationFactory` を使うメリットは？📮 ([Microsoft Learn][2])
5. ログに入れるべき3点セットは？🧾
6. In-Progress 状態を持つメリットは？🌀
7. TTL（保持期限）が無いと何が起きがち？🧹
8. 観測が弱いと、冪等性はなぜ運用で詰みがち？😇

---

## 24.9 AI活用（Copilot/Codex）で仕上げを爆速にする🤖⚡

### 24.9.1 テスト生成プロンプト例🧪

* 「`POST /orders` の冪等性統合テストを xUnit + WebApplicationFactory で書いて。
  同じIdempotency-Keyで2回送ると同じorderId、本文違いは409、10並列も追加して。」

### 24.9.2 ログ改善プロンプト例🧾

* 「ASP.NET Coreで correlationId / idempotencyKey / traceId をログスコープに入れるミドルウェア案を出して。
  さらに Created/Replayed/Conflict をログに残す実装例も。」

### 24.9.3 Copilot を“テスト向き”に使うコツ💡

* 先にテストの **期待仕様（Given/When/Then）** を日本語で箇条書き
* それをそのまま貼って生成させる
* 生成後は「並列」「衝突」「タイムアウト」を追加で要求する✨
  Visual Studio の Copilot には補完やチャットのガイドが用意されています([Microsoft Learn][7])

---

## 24.10 おまけ：いまの .NET の“最新版”メモ（2026年1月時点）🗒️✨

* .NET 10 は **LTS** で、2025年11月リリース・2028年11月までサポート予定([Microsoft][8])
* Visual Studio 2022 は 2026年1月時点で 17.14 系が継続アップデートされています([Microsoft Learn][9])

[1]: https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests?view=aspnetcore-10.0&utm_source=chatgpt.com "Integration tests in ASP.NET Core"
[2]: https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.mvc.testing.webapplicationfactory-1?view=aspnetcore-10.0&utm_source=chatgpt.com "WebApplicationFactory<TEntryPoint> Class"
[3]: https://www.nuget.org/packages/Microsoft.AspNetCore.Mvc.Testing?utm_source=chatgpt.com "Microsoft.AspNetCore.Mvc.Testing 10.0.2"
[4]: https://learn.microsoft.com/en-us/dotnet/core/diagnostics/observability-with-otel?utm_source=chatgpt.com ".NET Observability with OpenTelemetry"
[5]: https://learn.microsoft.com/en-us/aspnet/core/log-mon/metrics/metrics?view=aspnetcore-10.0&utm_source=chatgpt.com "ASP.NET Core metrics"
[6]: https://learn.microsoft.com/ja-jp/dotnet/core/diagnostics/observability-otlp-example?utm_source=chatgpt.com "OTLP とスタンドアロン Aspire Dashboard を OpenTelemetry ..."
[7]: https://learn.microsoft.com/en-us/visualstudio/ide/visual-studio-github-copilot-get-started?view=visualstudio&utm_source=chatgpt.com "Get Started with GitHub Copilot - Visual Studio (Windows)"
[8]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[9]: https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-history?utm_source=chatgpt.com "Visual Studio 2022 Release History"
