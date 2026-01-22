# 42章：DB/ライブラリの“詳細”は外側で完結させる🧰

（※本章の前提に合うように、2026-01-13 時点の最新パッチ版として **.NET 10.0.2 / EF Core 10.0.2** を前提に話を組み立てます📌） ([Microsoft][1])

---

## 1) この章のゴール🎯💖

この章を終えると、次ができるようになります☺️✨

* **Core（Entities/UseCases）がDBやEF Coreを一切知らない**状態にできる🧼
* 接続文字列・マイグレーション・EF設定などの“濃い話”を **外側（Frameworks側）に隔離**できる🧱
* 「DBを変えたい」「ORMを変えたい」「設定を変えたい」が来ても、**Coreが無傷**でいられる🛡️

---

## 2) そもそもDBやライブラリは“詳細”ってどういう意味？🤔🧩

クリーンアーキ的には、DB・ORM（EF Core）・ログ基盤・外部SDKなどは **“いつでも変わり得る都合”＝詳細** です🌀

* DBの種類（SQL Server / PostgreSQL / SQLite…）が変わるかも🗄️
* EF Coreの設定や癖が変わるかも⚙️
* マイグレーション運用が変わるかも🚚
* 接続情報の置き方が変わるかも🔐

だから **中心（Core）に入れない** のが勝ち筋です🏆✨
中心が汚れると、変更がドミノ倒しで広がります💥

---

## 3) 置き場所の鉄板パターン🏠✨（ざっくり図）

イメージはこう👇

* **Core**：純粋なC#（Entity/VO/UseCase/Port）🧼
* **Adapters**：変換（Controller/Presenter/Repository実装の“手前”）🔄
* **Frameworks(外側)**：EF Core、DbContext、接続、マイグレ、外部SDK、設定…🧰

たとえばプロジェクト分割はこんな感じが分かりやすいです😊

* `MyApp.Core`（Entities/UseCases/Ports）
* `MyApp.Infrastructure`（EF Core / DbContext / Repository実装）
* `MyApp.Web`（ASP.NET Core / DI / appsettings / 起動）

ポイントは **EF Coreの参照（NuGet）を Core に入れない** ことです❗️

---

## 4) 実装でやること（最短ルート）🏃‍♀️💨

### 4-1. Core側：インターフェイスだけ置く🔌✨

Core（UseCases）に **出口（Port）** を置きます。DBの話はゼロでOK☺️

```csharp
// MyApp.Core
public interface IMemoRepository
{
    Task AddAsync(Memo memo, CancellationToken ct);
    Task<Memo?> FindAsync(MemoId id, CancellationToken ct);
}
```

✅ ここで **DbContext** とか **Entity Framework** とか言い出したらアウトです🙅‍♀️💦

---

### 4-2. Infrastructure側：EF Core “だけ”で完結させる🗄️🧰

Infrastructure にだけ EF Core を入れて、DbContextと実装を置きます✨

```csharp
// MyApp.Infrastructure
using Microsoft.EntityFrameworkCore;

public sealed class MemoDbContext : DbContext
{
    public MemoDbContext(DbContextOptions<MemoDbContext> options) : base(options) { }

    public DbSet<MemoRecord> Memos => Set<MemoRecord>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<MemoRecord>(e =>
        {
            e.HasKey(x => x.Id);
            e.Property(x => x.Title).HasMaxLength(100);
        });
    }
}

public sealed class MemoRecord
{
    public Guid Id { get; set; }
    public string Title { get; set; } = "";
}
```

そして Repository 実装も Infrastructure に置きます👇

```csharp
// MyApp.Infrastructure
using Microsoft.EntityFrameworkCore;

public sealed class EfMemoRepository : IMemoRepository
{
    private readonly MemoDbContext _db;

    public EfMemoRepository(MemoDbContext db) => _db = db;

    public async Task AddAsync(Memo memo, CancellationToken ct)
    {
        _db.Memos.Add(new MemoRecord { Id = memo.Id.Value, Title = memo.Title.Value });
        await _db.SaveChangesAsync(ct);
    }

    public async Task<Memo?> FindAsync(MemoId id, CancellationToken ct)
    {
        var rec = await _db.Memos.AsNoTracking().FirstOrDefaultAsync(x => x.Id == id.Value, ct);
        return rec is null ? null : Memo.Rebuild(new MemoId(rec.Id), new Title(rec.Title));
    }
}
```

✅ **EFの都合（Record/DbContext/AsNoTracking）** は全部外側に閉じ込められました🎉

---

### 4-3. Web（Composition Root）：DIと設定値はここで配線🧵✨

`Program.cs` 側で **接続文字列 → DbContext → Repository** を組み立てます🪄
（EF Core は ASP.NET Core のDIに `AddDbContext` で追加するのが基本です） ([Microsoft Learn][2])

```csharp
// MyApp.Web - Program.cs
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<MemoDbContext>(options =>
{
    var cs = builder.Configuration.GetConnectionString("MainDb");
    options.UseSqlServer(cs);
});

builder.Services.AddScoped<IMemoRepository, EfMemoRepository>();

var app = builder.Build();
app.Run();
```

✅ **接続文字列はコードに直書きしない**（appsettings / 環境変数 / シークレットへ）🔐✨
この「設定の置き場所」も **詳細だから外側**です👍

---

## 5) マイグレーションは“外側の都合”そのもの🚚🧱

マイグレーションは **DBスキーマ運用の話**なので、Coreに近づけないのが吉です☺️

### 5-1. 「マイグレーション用プロジェクト」を分離できる✨

EF Coreは **マイグレーションを別プロジェクトに置く**公式手順があります📚 ([Microsoft Learn][3])

* `MyApp.Infrastructure`：DbContext（本体）
* `MyApp.Migrations`：マイグレーションだけ（必要なら）
* `MyApp.Web`：起動プロジェクト（Startup）

「DbContextがある場所」と「起動プロジェクト」が違うときは、CLIで明示できます🔧 ([Microsoft Learn][4])

例（概念）👇

* `--project`：マイグレーションを生成するプロジェクト
* `--startup-project`：実行時の設定を読むプロジェクト（appsettings等）

```bash
dotnet ef migrations add Init --project MyApp.Migrations --startup-project MyApp.Web
dotnet ef database update --project MyApp.Migrations --startup-project MyApp.Web
```

（EF Core CLIのリファレンスもここで確認できます📖） ([Microsoft Learn][5])

---

## 6) DbContextの寿命問題も“外側で吸収”できる🧯✨

通常のWebアプリは `AddDbContext`（scoped）が素直でOK👍 ([Microsoft Learn][2])
でも、UIが長寿命になりやすい種類（例：Blazor Serverなど）では **DbContextの使い回しが事故りやすい**ため、`AddDbContextFactory` を使うケースもあります🧪 ([Microsoft Learn][6])

ここでもポイントは同じで、
**Coreは寿命の話を知らない** → 外側で注入の仕方を変えるだけ🪄✨

---

## 7) よくある事故パターン🚨（秒で診断できる）

### ❌事故1：CoreがEF Core参照してる

* `MyApp.Core.csproj` に `Microsoft.EntityFrameworkCore` が入ってる
  → **即アウト**🙅‍♀️💦
  ✅ 対処：EFパッケージはInfrastructureだけに移動

### ❌事故2：Entityに `[Table]` とかEF属性が付いてる

* DomainがDB形状に引っ張られる😵
  ✅ 対処：永続化用Record（DBモデル）を外側に作ってマッピング（34章の発想）🔁✨

### ❌事故3：接続文字列がコード直書き

* 環境差分・漏洩・テストが地獄😱
  ✅ 対処：設定へ退避（appsettings / 環境変数 / シークレット）🔐

---

## 8) ミニ課題🎮💖（30〜60分）

1. `Core` から **EF参照ゼロ**にする（NuGetもusingも）🧼✨
2. `Infrastructure` に `DbContext` と `EfMemoRepository` を置く🗄️
3. `Web` の `Program.cs` でDI配線して動かす🧵🪄
4. 余裕があれば：マイグレーションを別プロジェクトへ分離🚚 ([Microsoft Learn][3])

---

## 9) Copilot/Codexに頼むと強いプロンプト例🤖✨

* 「CoreにEF参照が混ざってないか、プロジェクト構造と参照をチェックして」🔎
* 「DbContext/Repository実装をInfrastructureに寄せたうえで、Coreのinterfaceだけで成立する形にリファクタして」🧹
* 「マイグレーションを別プロジェクトに移す手順と、dotnet ef コマンド例をこの構成向けに出して」🚚

---

## まとめ🎁✨

* DB・EF・設定・マイグレは **全部“詳細”** → **外側に閉じ込める**🧰🧱
* Coreは **ルールと手順（Entity/UseCase/Port）だけ**でピカピカに保つ🧼✨
* 変更が来たときに、直す場所が **Infrastructure/Webに限定**されるのが最大の勝ち🏆💖

次（43章）は、いよいよ **中心（Entities）のテスト**で“速くて気持ちいい安心感”を作っていくよ〜🧪🍰💕

[1]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[2]: https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/?utm_source=chatgpt.com "DbContext Lifetime, Configuration, and Initialization"
[3]: https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/projects?utm_source=chatgpt.com "Using a Separate Migrations Project - EF Core"
[4]: https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/managing?utm_source=chatgpt.com "Managing Migrations - EF Core"
[5]: https://learn.microsoft.com/ja-jp/ef/core/cli/dotnet?utm_source=chatgpt.com "EF Core ツールのリファレンス (.NET CLI)"
[6]: https://learn.microsoft.com/ja-jp/ef/core/dbcontext-configuration/?utm_source=chatgpt.com "DbContext の有効期間、構成、および初期化 - EF Core"
