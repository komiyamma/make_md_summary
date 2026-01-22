# 第36章：外部サービスAdapter（HTTP等）🌍📡✨

外部API（翻訳、決済、通知、AI、天気、住所検索…）って、**仕様変更・障害・遅延**がつきものだよね😵
この章では、それらの「外の都合」を**Coreに波及させない**ための作り方を、C#でやさしくまとめるよ🫶

---

## この章のゴール🎯💖

* 外部API呼び出しを **差し替え可能**にできる（実装が入れ替わってもUseCaseは無傷）🔁
* HTTPのつらさ（タイムアウト/リトライ/429/落ちる等）を **Adapter側に閉じ込める**🧯
* 「外部のDTO」をCoreに持ち込まず、**変換（ACL）**で吸収できる🧼✨

---

## まず結論：外部サービスは“出口のPort”にする🚪🔌

### 依存の形（イメージ）🌀

* UseCase（内側）：「タグ提案が欲しいな〜」→ **インターフェイス（Port）**を呼ぶ
* Adapter（外側）：「HTTPで叩いて、返り値を変換して返す」

外部APIの呼び出しは、HttpClientや認証ヘッダやJSON形式など**細かい事情だらけ**。
だから、**外の事情はAdapterに全部押し込む**のが正解🙆‍♀️✨

---

## HTTP呼び出しの“安全な基本セット”🧰💪

ここは最新の公式ガイドに寄せるね📘✨

* HttpClientを雑に new しまくると **ソケット枯渇**しやすい😇
* さらにDNSが変わる環境だと **古いIPを掴み続ける**問題も出る😵
* なので基本は **IHttpClientFactory（AddHttpClient）** を使うのが定番👍

  * 内部でハンドラをプールして、ソケット問題やDNS問題を回避しやすいよ✨ ([Microsoft Learn][1])
* ただし注意：typed client や HttpClient を **Singletonに捕獲**すると、せっかくの寿命管理が効かずDNS問題が再発しうるよ⚠️ ([Microsoft Learn][2])

---

## 例題：外部「タグ提案API」を呼ぶAdapterを作ろう🏷️🤖✨

> メモ本文から「おすすめタグ」を返してくれる外部APIがある想定にするね（架空でOK）🫧
> 目的は “HTTPの実装詳細をCoreから隔離する” ことだよ💡

---

# 1) Core側：Port（インターフェイス）とモデルを定義する🧠✨

ポイントはこれ👇
✅ **HttpClient / HttpResponseMessage / JSON DTO をCoreに入れない**
✅ Coreは「欲しい結果」と「失敗の種類」だけ知ってればOK

```csharp
namespace MyApp.UseCases.External;

public interface ITagSuggestionGateway
{
    Task<TagSuggestionResult> SuggestAsync(TagSuggestionRequest request, CancellationToken ct);
}

public sealed record TagSuggestionRequest(string Text);

public sealed record TagSuggestionResult(
    bool IsSuccess,
    IReadOnlyList<string> Tags,
    ExternalServiceError? Error)
{
    public static TagSuggestionResult Success(IReadOnlyList<string> tags)
        => new(true, tags, null);

    public static TagSuggestionResult Fail(ExternalServiceError error)
        => new(false, Array.Empty<string>(), error);
}

public sealed record ExternalServiceError(
    ExternalServiceErrorKind Kind,
    string Message,
    int? HttpStatusCode = null);

public enum ExternalServiceErrorKind
{
    Timeout,
    TransientFailure,
    Unauthorized,
    RateLimited,
    BadRequest,
    UnexpectedResponse,
    Unknown
}
```

### ここがえらい👏💕

* Coreは「HTTPの世界」を知らない🌍❌
* 外部APIの仕様変更が起きても、基本は **Adapterだけ直せばOK**🔧✨
* 失敗を例外で上に投げ散らかすより、**意味のある失敗**（Timeout/RateLimited等）に整形できる👍

---

# 2) Adapter側：HTTP実装（変換・例外整理・ログ）を書く📡🛠️

Adapterの役割はこの3つに絞るとキレイ😍

1. **通信する（HTTP）**
2. **外部DTO ⇄ Coreモデルに変換（ACL）**
3. **失敗を分類してCoreに返す（例外を飼いならす）**

```csharp
using System.Net;
using System.Net.Http.Json;
using Microsoft.Extensions.Logging;
using MyApp.UseCases.External;

namespace MyApp.Adapters.External;

public sealed class TagSuggestionHttpGateway : ITagSuggestionGateway
{
    private readonly HttpClient _http;
    private readonly ILogger<TagSuggestionHttpGateway> _logger;

    public TagSuggestionHttpGateway(HttpClient http, ILogger<TagSuggestionHttpGateway> logger)
    {
        _http = http;
        _logger = logger;
    }

    public async Task<TagSuggestionResult> SuggestAsync(TagSuggestionRequest request, CancellationToken ct)
    {
        try
        {
            var dtoReq = new SuggestTagsApiRequest { text = request.Text };

            using var resp = await _http.PostAsJsonAsync("v1/tags/suggest", dtoReq, ct);

            // 401/403：認証系
            if (resp.StatusCode is HttpStatusCode.Unauthorized or HttpStatusCode.Forbidden)
                return TagSuggestionResult.Fail(new(ExternalServiceErrorKind.Unauthorized, "認証に失敗したよ😢", (int)resp.StatusCode));

            // 429：レート制限
            if ((int)resp.StatusCode == 429)
                return TagSuggestionResult.Fail(new(ExternalServiceErrorKind.RateLimited, "混んでるみたい…少し待ってね⏳", 429));

            // 400：リクエストが悪い（入力の問題）
            if (resp.StatusCode == HttpStatusCode.BadRequest)
                return TagSuggestionResult.Fail(new(ExternalServiceErrorKind.BadRequest, "送った内容がダメだったっぽい🙈", 400));

            // その他のエラー（5xx等）
            if (!resp.IsSuccessStatusCode)
            {
                var body = await SafeReadBodyAsync(resp, ct);
                _logger.LogWarning("Tag API failed: {Status} {Body}", (int)resp.StatusCode, body);

                return TagSuggestionResult.Fail(new(
                    ExternalServiceErrorKind.TransientFailure,
                    "外部サービス側でエラーが起きたよ😵",
                    (int)resp.StatusCode));
            }

            var dtoRes = await resp.Content.ReadFromJsonAsync<SuggestTagsApiResponse>(cancellationToken: ct);

            if (dtoRes?.tags is null)
                return TagSuggestionResult.Fail(new(ExternalServiceErrorKind.UnexpectedResponse, "返ってきた形が想定と違うよ🙈"));

            // ✅ ここがACL（外部の都合をアプリの都合に変換）
            var tags = dtoRes.tags
                .Where(t => !string.IsNullOrWhiteSpace(t))
                .Select(t => t.Trim())
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .ToArray();

            return TagSuggestionResult.Success(tags);
        }
        catch (TaskCanceledException) when (!ct.IsCancellationRequested)
        {
            // ctがキャンセルされてないのにTaskCanceled → タイムアウト扱いが多い
            return TagSuggestionResult.Fail(new(ExternalServiceErrorKind.Timeout, "タイムアウトしたよ⌛️"));
        }
        catch (HttpRequestException ex)
        {
            _logger.LogWarning(ex, "HTTP request failed");
            return TagSuggestionResult.Fail(new(ExternalServiceErrorKind.TransientFailure, "通信に失敗したよ📡"));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error");
            return TagSuggestionResult.Fail(new(ExternalServiceErrorKind.Unknown, "想定外の失敗だよ💥"));
        }
    }

    private static async Task<string> SafeReadBodyAsync(HttpResponseMessage resp, CancellationToken ct)
    {
        try { return await resp.Content.ReadAsStringAsync(ct); }
        catch { return "<unreadable>"; }
    }

    // 外部API用DTO（Coreに持ち込まない！）
    private sealed class SuggestTagsApiRequest
    {
        public required string text { get; init; }
    }

    private sealed class SuggestTagsApiResponse
    {
        public string[]? tags { get; init; }
    }
}
```

### いい感じポイント💖

* 外部のJSON構造が変わっても **このファイル周りだけ修正**で済みやすい🔧
* 例外はCoreに投げずに **意味ある失敗に整形**して返す🧠✨
* ログはAdapterで取る（Coreは静かにしておく）🔇➡️📝

---

# 3) DIで配線：AddHttpClient（typed client）を使う🧵✨

IHttpClientFactory は、DI/ログ/設定、さらにハンドラ寿命管理などに強いよ💪 ([Microsoft Learn][1])

さらに最近は、HTTPの回復性（リトライ等）を “素で” 組みやすい公式パッケージもあるよ📦✨
Microsoft.Extensions.Http.Resilience は、HttpClient向けの回復性機構を提供してるよ ([Microsoft Learn][3])

```csharp
using MyApp.UseCases.External;
using MyApp.Adapters.External;

var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddHttpClient<ITagSuggestionGateway, TagSuggestionHttpGateway>(client =>
    {
        client.BaseAddress = new Uri(builder.Configuration["TagApi:BaseUrl"]!);
        client.Timeout = TimeSpan.FromSeconds(10); // まずは短めが安心🙆‍♀️
        client.DefaultRequestHeaders.Add("Accept", "application/json");
    })
    // 回復性：リトライ/タイムアウト/サーキット等を“いい感じ”に付与（パッケージ側の標準セット）
    .AddStandardResilienceHandler();

var app = builder.Build();
app.Run();
```

> 💡 補足：AddStandardResilienceHandler は “標準の回復性セット” を付けるイメージだよ。
> 細かく調整したい場合も、まずこれで土台を作るのがラクちん☺️

---

## ありがちな事故あるある😇⚠️（超だいじ）

### ❌ 事故1：UseCaseの中でHttpClientを直接叩く

* Coreが外部仕様に汚染される → 章の目的が崩壊💥

### ❌ 事故2：HttpClient（やtyped client）をSingletonに抱え込む

* IHttpClientFactoryを使ってても、寿命管理が効かずDNS問題が起きやすい⚠️ ([Microsoft Learn][2])

### ❌ 事故3：タイムアウト/キャンセル無しで外部API呼び出し

* 外部が遅いと、あなたのアプリも固まる😵
* CancellationToken をちゃんと流そうね🧊

### ❌ 事故4：外部APIのDTOをCoreに置いちゃう

* 外部APIの都合がドメインに混入して、将来の変更が地獄になる🙈

---

## “外部サービスAdapter”のチェックリスト✅💖

* [ ] Core側に **インターフェイス（Port）** がある
* [ ] Coreは **HTTP型（HttpClient/HttpResponseMessage/JsonDocument等）** を知らない
* [ ] Adapterで **外部DTO ⇄ Coreモデル** の変換が完結してる（ACL）
* [ ] 失敗が **Timeout/RateLimit/Unauthorized…** みたいに分類されてる
* [ ] リトライ等の回復性が **DIの設定で付与**できる（コードにベタ書きしない） ([Microsoft Learn][3])
* [ ] typed client を **Singletonに捕獲してない** ([Microsoft Learn][2])

---

## ミニ課題🎮✨（やると一気に身につくよ！）

### 課題A：Fake実装でUseCaseを壊さずテストしよう🧪💕

* ITagSuggestionGateway の Fake を作って

  * 成功（タグ3つ返す）
  * 失敗（RateLimited返す）
    の2パターンでUseCaseが期待通り動くか確認✨

### 課題B：外部APIのエラーを“やさしい失敗”に翻訳しよう🧠

* 401 → Unauthorized
* 429 → RateLimited
* 500台 → TransientFailure
* JSONが壊れてる → UnexpectedResponse
  …みたいに分類を増やしてみてね💪

---

## AIの使いどころ🤖💡（便利だけど任せすぎ注意！）

* 「この外部APIレスポンスからDTOクラス作って〜」➡️ 雛形作りは得意👏
* 「想定すべき失敗ケースを列挙して〜」➡️ 抜け漏れ防止に最高🫶
* ただし ❗ APIキーや秘密情報は貼らないでね🔐💦（そこは人間が守る！）

---

## ちょい最新トピック🍀（バージョン選びの安心材料）

.NET 10 は 2025/11/11 リリースのLTSで、パッチも継続提供中だよ📦✨ ([Microsoft][4])
（外部通信まわりはセキュリティ修正も入りやすいので、LTS追従はかなり大事〜！🛡️）

---

次の章（第37章）は、このAdapter層が「変換の置き場としてちゃんと集約できてるか？」を点検する回だよ✅🔍
もし今のプロジェクト題材（メモ管理）で「外部サービス何にする？」も一緒に決めたいなら、用途に合わせて候補を3つくらい提案するよ〜🥰✨

[1]: https://learn.microsoft.com/en-us/dotnet/core/extensions/httpclient-factory "Use the IHttpClientFactory - .NET | Microsoft Learn"
[2]: https://learn.microsoft.com/en-us/dotnet/core/extensions/httpclient-factory-troubleshooting "Troubleshoot IHttpClientFactory issues - .NET | Microsoft Learn"
[3]: https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience "Build resilient HTTP apps: Key development patterns - .NET | Microsoft Learn"
[4]: https://dotnet.microsoft.com/ja-jp/platform/support/policy/dotnet-core ".NET および .NET Core の公式サポート ポリシー | .NET"
