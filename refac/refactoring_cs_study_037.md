# 第37章：外部依存を包む（Adapter / WrapperでSeamを作る）🧤🔌

## この章でできるようになること🎯✨

* HTTP / DB / ファイル / OS機能みたいな「外の世界」を、アプリの中心（ロジック）から遠ざけられるようになるよ🧁🎯
* テストで外部通信なしでも動作確認できる“差し替え口（Seam）”を作れるようになるよ🪡✅
* 「ラッパーが太りすぎる問題」を避けながら、最小のAPIで包めるようになるよ📏✨

---

## 1. 外部依存ってなに？🌍⚡

外部依存 = **アプリの外側の都合に振り回されやすいもの**だよ😵‍💫💦 たとえば…

* HTTP通信（外部API呼び出し）🌐
* DBアクセス（SQL/EF Core）🗄️
* ファイルI/O（読み書き、存在確認）📁
* 時刻、乱数、環境変数、OS情報⏰🎲🪟
* メッセージキュー、クラウドSDK☁️📨

こういうのをロジックのど真ん中に直書きすると、テストもしんどいし、変更にも弱くなるの🥲

---

## 2. なんで“包む”の？🧤✨（メリット4つ）

### ✅(1) テストが一気にラクになる🧪💖

外部APIやDBって、テストで毎回つないだら遅いし不安定💦
差し替えできれば、**ロジックだけを爆速＆安定**でテストできるよ🪄✨

### ✅(2) 変更が“端っこ”だけで済む🏝️➡️🏠

外部APIの仕様変更、認証方式変更、DBの差し替え…
包んでおけば **変更はアダプター側だけ**で済むことが多いよ🔧✨

### ✅(3) 例外・リトライ・タイムアウトを“境界”で吸収できる🚧⚠️

外の世界は失敗する前提😇
境界でまとめて面倒を見ると、中心ロジックがスッキリするよ🧼✨

### ✅(4) “意図”の名前が付く🏷️💡

`HttpClient.GetAsync(...)` って「何してるの？」が見えにくいけど、
`IShippingFeeGateway.GetFeeAsync(...)` なら意図が読める👀✨

---

## 3. 用語をゆるく整理🧠📝

### 🪡 Seam（シーム）って？

**「その場所を直接いじらずに、動きを差し替えられるポイント」**だよ🧷✨
依存を切ってテストしやすくしたり、観測（ログ/計測）を差し込んだりできるのが強い💪
この考え方はレガシー改善でも超重要だよ🧟‍♀️➡️🧁 ([martinfowler.com][1])

### 🧤 Adapter / Wrapper って？

* **Adapter**：合わないインターフェイス同士を“変換”してつなぐ🧩
* **Wrapper**：外部ライブラリの呼び出しを“包んで”使いやすくする🎁

要するに「外のものを、こっちの都合の良い形で使えるようにする」やつだよ✨ ([refactoring.guru][2])

---

## 4. ダメになりやすい例🥲（中心が外部にベタ結合）

例：ロジックの中で `HttpClient` を new して、URL組んで、JSON解析して…
これ、テストも変更もつらい😵‍💫💦

```csharp
using System.Net.Http.Json;

public sealed class OrderService
{
    public async Task<decimal> CalculateTotalAsync(int orderId, CancellationToken ct)
    {
        // 🚫 ロジックの真ん中に外部通信が直書き
        using var http = new HttpClient();
        var feeDto = await http.GetFromJsonAsync<ShippingFeeDto>(
            $"https://api.example.com/shipping/fee?orderId={orderId}", ct);

        if (feeDto is null) throw new InvalidOperationException("feeDto is null");

        // ここから先が本来のロジックだとしても、外部依存で汚れちゃう…
        return feeDto.Amount + 1000m;
    }

    private sealed record ShippingFeeDto(decimal Amount, string Currency);
}
```

* `HttpClient` の扱いも危険（作り方で問題が出る）😇💦
* 外部APIが落ちたらテストも落ちる
* JSON形が変わったら中心ロジックまで巻き添え

---

## 5. 正解の型🧁🎯：Port（interface） + Adapter（実装）

### ステップはこれだけ🪜✨

1. 中心（ロジック）が欲しい能力を **小さな interface** にする（Port）📌
2. 外部API/DB/ファイルを触るのは **Adapter側だけ** にする🧤
3. テストでは interface を **Fake** に差し替える🧪✨

---

## 6. 実践①：HTTPを包む（typed client + Adapter）🌐🧤

### 6-1) まず“中心”が欲しい形を決める🏷️

ここが超大事！外部APIの都合じゃなくて、**こっちの都合**で決めるよ😎✨

```csharp
public sealed record ShippingFee(decimal Amount, string Currency);

public interface IShippingFeeGateway
{
    Task<ShippingFee> GetFeeAsync(int orderId, CancellationToken ct);
}
```

### 6-2) Adapter（外部APIを叩く側）を書く🔌✨

* HTTPの詳細（URL、DTO、失敗処理）はここに閉じ込めるよ🚪🔒
* `ReadFromJsonAsync` などの変換も境界でやっちゃう🧪🧼

```csharp
using System.Net.Http.Json;

public sealed class ShippingFeeHttpGateway : IShippingFeeGateway
{
    private readonly HttpClient _http;

    public ShippingFeeHttpGateway(HttpClient http) => _http = http;

    public async Task<ShippingFee> GetFeeAsync(int orderId, CancellationToken ct)
    {
        // 外部APIのURL構築はここだけに隔離🧱
        using var res = await _http.GetAsync($"shipping/fee?orderId={orderId}", ct);

        // 失敗は境界で“わかりやすく”して投げる/変換する🚧
        res.EnsureSuccessStatusCode();

        var dto = await res.Content.ReadFromJsonAsync<ShippingFeeDto>(cancellationToken: ct)
                  ?? throw new InvalidOperationException("ShippingFeeDto is null");

        // DTO → ドメイン（中心で扱いたい形）へ変換🧩✨
        return new ShippingFee(dto.amount, dto.currency);
    }

    // 外部都合のDTOは外に漏らさない🫥
    private sealed record ShippingFeeDto(decimal amount, string currency);
}
```

### 6-3) “作り方”は推奨のやり方で🧠✨（ここ最新ルール！）

`HttpClient` は「毎回newして捨てる」と、接続まわりで事故りやすいの🥲
推奨は **長寿命 + PooledConnectionLifetime** か、**IHttpClientFactory** のどっちかだよ📌 ([Microsoft Learn][3])
`IHttpClientFactory` を使うなら **typed client** が推奨されてるよ🧤✨ ([Microsoft Learn][3])

登録イメージ（typed client）👇

```csharp
using Microsoft.Extensions.DependencyInjection;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddShippingFeeGateway(this IServiceCollection services)
    {
        services.AddHttpClient<IShippingFeeGateway, ShippingFeeHttpGateway>(client =>
        {
            client.BaseAddress = new Uri("https://api.example.com/");
            client.Timeout = TimeSpan.FromSeconds(3);
        });

        return services;
    }
}
```

※ `IHttpClientFactory` は `HttpMessageHandler` をプールして、接続枯渇（ソケット枯渇）を避ける仕組みがあるよ🧯✨ ([Microsoft Learn][3])

---

## 7. テスト：Fakeに差し替えるだけ🧪💕

中心ロジック側は **IShippingFeeGateway だけ知ってればOK**。
テストではFake実装に差し替えるだけで、外部通信ゼロ😆✨

```csharp
public sealed class FakeShippingFeeGateway : IShippingFeeGateway
{
    public Task<ShippingFee> GetFeeAsync(int orderId, CancellationToken ct)
        => Task.FromResult(new ShippingFee(250m, "JPY"));
}
```

---

## 8. 実践②：ファイルI/Oを包む📁🧤

`File.ReadAllText` とか静的メソッド直叩きは、テストで地獄になりがち😵‍💫💦
方法は2つあるよ👇

### A) 自分で小さいinterfaceを作る（おすすめ基本）🧁🎯

```csharp
public interface IReceiptStorage
{
    Task SaveAsync(string orderId, string content, CancellationToken ct);
    Task<string?> LoadAsync(string orderId, CancellationToken ct);
}
```

### B) 既存の“抽象化ライブラリ”を使う（ガチ便利）🛠️✨

`System.IO.Abstractions` は `IFileSystem` を提供してて、`File.ReadAllText` みたいなAPIを **注入可能＆テスト可能**にしてくれるよ📦✨ ([GitHub][4])

---

## 9. 実践③：DBアクセスも“中心”から隔離する🗄️🧤

DB（EF Core）を中心ロジックが直に触ると、テストと変更が重くなりがち😮‍💨
よくある形はこれ👇

* 中心：`IUserRepository` みたいな interface（Port）
* 外側：EF Coreで実装した Repository（Adapter）

### テスト戦略の注意⚠️🧪

EF Coreの **InMemoryプロバイダをテストに使うのは推奨されない**（挙動が本番DBとズレやすい）って公式でも言われてるよ😇 ([Microsoft Learn][5])
代わりに **SQLiteのin-memory** は「リレーショナルDBとしての挙動」に近くなりやすい、って整理があるよ🧠✨ ([Microsoft Learn][6])

---

## 10. “良いラッパー”のコツ5つ🧁✨

1. **最小API**にする（使う側が今ほしい機能だけ）📏
2. 外部のDTOや例外を **中心に漏らさない**（変換して返す）🧽
3. リトライ/タイムアウト/ログは **境界で** まとめる🚧
4. Adapterの中に **ビジネス判断** を入れない（中心に置く）🚫🧠
5. 名前は「技術」より「意図」寄りに🏷️（例：`PaymentGateway`）

---

## 11. ミニ演習📝✨：外部呼び出しを1枚ラップしてモック可能にする✅

### お題🎒

「注文合計を計算する処理」が、配送手数料を外部APIから取ってきている…という想定で、Seamを作るよ🪡✨

### 手順🪜

1. 外部呼び出し部分を見つける👀🔎
2. 中心が欲しい形で `IShippingFeeGateway` を作る🏷️
3. 既存コードを移して `ShippingFeeHttpGateway` に閉じ込める🧤
4. 中心のロジックは interface だけを見るようにする🧁🎯
5. テストでは `FakeShippingFeeGateway` を差し替えて動作確認🧪✅

### 合格ライン🌈

* 外部APIが落ちても、中心ロジックのユニットテストが通る💖
* 外部APIのJSON形が変わっても、修正箇所がAdapter側に寄ってる🔧✨

---

## 12. PRに出す前チェックリスト✅📌

* [ ] 中心ロジックに `HttpClient` / `DbContext` / `File.*` が出てこない👀❌
* [ ] interface（Port）が “最小” で、用途が分かる名前になってる🏷️✨
* [ ] 外部DTOを中心に漏らしてない（変換して返してる）🧽
* [ ] 失敗（例外/Result）は境界で整理されてる🚧
* [ ] Fake/Mockでテストが書けてる🧪💚

---

## 13. AI拡張の使い方（安全運転）🤖🛡️✨

### そのままコピペで使える頼み方💬

* 「このクラスの外部依存（HTTP/DB/File）を列挙して、境界に押し出すinterface案を3つ出して」🤖🗂️
* 「最小APIになるように、interfaceのメソッド数を減らして。理由も」📏✨
* 「DTO→ドメイン変換を境界に閉じ込める形にして」🧽🧩
* 「Fake実装を作って、ユニットテストが外部なしで動く形にして」🧪✅

（提案は採用前に、差分とテストで必ず確認ね📌✨）

[1]: https://martinfowler.com/bliki/LegacySeam.html?utm_source=chatgpt.com "Legacy Seam - Martin Fowler"
[2]: https://refactoring.guru/design-patterns/adapter?utm_source=chatgpt.com "Adapter"
[3]: https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/http/httpclient-guidelines?utm_source=chatgpt.com "Guidelines for using HttpClient"
[4]: https://github.com/TestableIO/System.IO.Abstractions?utm_source=chatgpt.com "TestableIO/System.IO.Abstractions"
[5]: https://learn.microsoft.com/en-us/ef/core/providers/in-memory/?utm_source=chatgpt.com "EF Core In-Memory Database Provider"
[6]: https://learn.microsoft.com/en-us/ef/core/testing/?utm_source=chatgpt.com "Overview of testing applications that use EF Core"
