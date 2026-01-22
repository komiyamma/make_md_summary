# 第41章：Composition Root（組み立て場所は1箇所）🧵✨

> 目標：**「どこで何を“配線”するか」**がスパッと判断できて、DI登録が散らばって崩れる事故を防げるようになるよ〜😊💕

---

## 1) Composition Rootってなに？🤔🧩

**Composition Root（コンポジションルート）**は、アプリを動かすために必要な部品（クラスたち）を **最終的に“組み立てる場所”**のことだよ🧵✨
ここでやるのはざっくり言うと👇

* 「この `interface` の実体はこの `class` ね！」って **紐付け**する（DI登録）🔌
* 実行時の「オブジェクトのつながり（object graph）」を作る🏗️
  （Microsoft公式も “dependency graph / object graph” って呼んでるよ）([Microsoft Learn][1])

そして大事な定義がこれ👇
**「Composition Rootは（できれば）1箇所」**
アプリの入口に近いところで、まとめて組み立てるのが基本だよ〜🧠✨ ([blog.ploeh.dk][2])

---

## 2) なんで「1箇所」にこだわるの？🥺🧯

### ✅ 散らばると起きがちな地獄 😇🔥

* どこでDI登録してるか分からない → **追加/修正が怖い**😱
* 似た登録が複数箇所に出現 → **環境によって動いたり動かなかったり**😵‍💫
* 「とりあえず `new` しちゃえ」が増える → **テストできない**😭
* `IServiceProvider` をあちこちで解決（Service Locator化）→ **依存が見えなくなる**🫥

### ✅ 1箇所にすると嬉しいこと 😊🌸

* 依存関係が **一望**できる👀✨
* レイヤーの境界が保てる（クリーンアーキと相性抜群）🏗️💖
* テストで差し替えが簡単（Fake/Mock）🎭
* 設定漏れが減る✅

---

## 3) ASP.NET Core（最新）だとComposition Rootはどこ？🌐🧵

いまのASP.NET Core（Minimal hosting model）だと、基本は **`Program.cs`** が入口だよ🚪✨
`WebApplicationBuilder` を作って、`builder.Services` に登録して…って流れね😊
この形は公式ドキュメントでも中心の書き方になってるよ ([Microsoft Learn][3])

---

## 4) クリーンアーキ的に「第41章」が超重要な理由 🏛️💘

クリーンアーキは **内側（Core）ほど純粋**、外側ほど**詳細（DB/HTTP/Framework）**だよね🧼✨

だから依存の見え方はこう👇

* **Core（Entities/UseCases）**：`interface` を定義する（例：`IMemoRepository`）🧠
* **Adapters/Infrastructure**：`interface` の実装を置く（例：`EfMemoRepository`）🗄️
* **Frameworks/Web（最外周）**：それらを **“結婚（接続）させる”** 💍＝Composition Root🧵✨

つまり **「内側は“実装を知らない”」**を成立させる最後のピースが、Composition Rootなんだよ〜！🥹💖

---

## 5) 実装の基本形（Program.csに集約）🧵✅

まずは一番わかりやすい形からいこ〜😊✨
（後で“長くなったら分割”する！）

```csharp
// Program.cs

var builder = WebApplication.CreateBuilder(args);

// ① ここが Composition Root の中心：DI登録 🔌✨

// UseCases（Interactorなど）
builder.Services.AddScoped<ICreateMemoInputPort, CreateMemoInteractor>();
builder.Services.AddScoped<ICreateMemoOutputPort, CreateMemoPresenter>();

// Repository（Coreのinterface → 外側の実装）
builder.Services.AddScoped<IMemoRepository, EfMemoRepository>();

// EF Core / DbContext（詳細は外側）🗄️
builder.Services.AddDbContext<AppDbContext>(options =>
{
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default"));
});

// Controllers / Minimal API
builder.Services.AddControllers();

var app = builder.Build();

app.MapControllers();
app.Run();
```

### ✨ポイント（超大事）✨

* **登録はここに集約**（迷子にならない）🧭
* `CreateMemoInteractor` が `EfMemoRepository` を知らなくても動く（DIが注入する）🪄
* Core側は DIコンテナの存在を知らなくてOK（理想形）🧼

---

## 6) でもProgram.csが太る…！どうする？😵‍💫➡️スッキリ術✨

現実はユースケース増えると登録が増えるよね🥺
そこでよくやるのが **“拡張メソッドで整理”** だよ📦✨

⚠️ここで大事なのは
**「物理的にファイルが分かれても、“論理的に1箇所（入口から呼ぶ）”ならOK」**って考え方だよ〜🧠 ([blog.ploeh.dk][2])

### ✅ Program.csは「呼ぶだけ」🧵

```csharp
// Program.cs

var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddUseCases()
    .AddPresenters()
    .AddInfrastructure(builder.Configuration)
    .AddWeb();

var app = builder.Build();

app.MapControllers();
app.Run();
```

### ✅ 例：Infrastructureの登録をまとめる（外側に置く）🗄️

```csharp
// Infrastructure/DependencyInjection.cs
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Configuration;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(
        this IServiceCollection services,
        IConfiguration config)
    {
        services.AddDbContext<AppDbContext>(options =>
        {
            options.UseSqlServer(config.GetConnectionString("Default"));
        });

        services.AddScoped<IMemoRepository, EfMemoRepository>();

        return services;
    }
}
```

> こうしておくと、「DBまわり変えたい」って時に **Infrastructureだけ見ればいい**ので楽だよ〜😊✨

---

## 7) DIライフタイムの“ざっくり結論”⏳💡

ASP.NET CoreのDIには主に3つの寿命があるよ（公式）👇 ([Microsoft Learn][1])

* **Transient**：毎回new（軽いやつ向け）🐣
* **Scoped**：1リクエスト内で同じ（Webで一番よく使う）🧾✨
* **Singleton**：アプリ起動中ずっと同じ（状態持つと危険）🗿⚠️

クリーンアーキ教材的なおすすめはまずこれ👇😊

* **UseCase（Interactor）**：`Scoped` が無難✨
* **Repository / DbContext**：だいたい `Scoped`（DbContextも基本これ）🗄️
* **Presenter**：使い方次第だけど、多くは `Scoped` に寄せると安全🎤

---

## 8) “やっちゃダメ”集（Composition Root違反）🚫😱

### ❌ 1) UseCaseの中で `new EfMemoRepository()` する

* 依存が固定されて差し替え不能 😭
* テストしにくい 😵‍💫

### ❌ 2) あちこちで `IServiceProvider.GetRequiredService<T>()`

* “見えない依存”が増えて、設計が腐る🧟‍♀️
* Service Locator化しやすい⚠️（DIの逆走） ([InfoQ][4])

### ❌ 3) `builder.Services.BuildServiceProvider()` を途中で呼ぶ

* 二重コンテナになって寿命管理が崩れがち😇🔥
  （「とりあえず取れるからOK」は罠〜！）

---

## 9) ミニ課題：DI登録を「1ファイルに集約」して事故を消す🧹✨

### 🎯お題

いま散らばってる “登録っぽい処理” を見つけて、**Composition Root（Program.cs）に寄せる**よ！

### ✅ 手順（迷わない版）🧭

1. ソリューション全体で `AddScoped` / `AddTransient` / `AddSingleton` を検索🔎
2. “登録してる場所” を全部メモ📝
3. Program.cs に集める（最初はベタ書きでOK）🧵
4. 長くなったら `AddInfrastructure()` みたいに整理📦
5. 動作確認＆テスト✅

### 🤖AI（Copilot/Codex）に頼むと速いプロンプト例

* 「このSolutionでDI登録が散らばりそうな場所を洗い出して、Program.csに集約する方針を提案して」
* 「`AddInfrastructure(builder.Configuration)` の拡張メソッド雛形を作って」
* 「登録漏れが起きやすいサービス一覧を、参照関係から推測してチェックリスト化して」

---

## 10) 仕上げチェックリスト✅💖（これ通れば強い！）

* [ ] DI登録は **入口（Program.cs）から辿れる**（迷子にならない）🧭
* [ ] Core（Entities/UseCases）が **EF/HTTP/ASP.NET型を参照してない**🧼
* [ ] `new` が UseCase層にほぼ無い（依存は注入）🪄
* [ ] `IServiceProvider` を注入して解決して回ってない（Service Locator化してない）🚫
* [ ] どの実装が使われるか、Program.csを見れば分かる👀✨

---

## おまけ：2026時点の前提に合わせた一言📌✨

いまは **.NET 10（LTS）**が最新の安定ラインとして案内されてるよ（サポートも長め）([Microsoft for Developers][5])
だから「Composition Rootを `Program.cs` に置く」前提は、今後もしばらく安心して使ってOK〜😊💕

---

次の章（第42章）は「DB/ライブラリの“詳細”を外側で完結させる」だから、**“Composition Rootで配線した結果、Coreが汚れてないか？”**をさらに強く確認していくよ〜🧰✨

[1]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection?utm_source=chatgpt.com "Dependency injection - .NET"
[2]: https://blog.ploeh.dk/2011/07/28/CompositionRoot/?utm_source=chatgpt.com "Composition Root - ploeh blog"
[3]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/webapplication?view=aspnetcore-10.0&utm_source=chatgpt.com "WebApplication and WebApplicationBuilder in Minimal API ..."
[4]: https://www.infoq.com/articles/DI-Mark-Seemann/?utm_source=chatgpt.com "Dependency Injection with Mark Seemann - InfoQ"
[5]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10 - Microsoft Dev Blogs"
