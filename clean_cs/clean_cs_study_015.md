# 第15章：Entitiesは“フレームワーク非依存”🧼✨（中心をピュアに保つ）

この章のテーマはめちゃシンプル👇
**Entities（ドメインの中心）は「純粋なC#」で保って、EF Core・ASP.NET Core・JSON・UI都合を一切持ち込まない**こと！💎

クリーンアーキの大原則「依存は内側へ」ってやつね➡️⭕
内側（Entities）は外側（DB/HTTP/フレームワーク）を**名前すら**知らない、が理想だよ〜😌📌 ([クリーンコーダーブログ][1])

---

## 1) なんで“非依存”がそんなに大事なの？🤔💭

### ✅ ① 変更が怖くなくなる

* DBをSQL Server→PostgreSQLに変えたい
* Web API→gRPCにしたい
* ORMをEF→別のにしたい

…こういう「外側の変更」が来ても、**中心（Entities）が無傷**なら被害が小さいの🥹🛡️

### ✅ ② テストが速くて気持ちいい🧪🍰

Entitiesがピュアだと、DBもHTTPもいらないから
**テストが爆速＆安定**するよ✨

### ✅ ③ EF Coreでも“汚さず”にできる（公式が言ってる）

Microsoftのガイドでも、EF Coreは設定（OnModelCreating等）を外側に置くことで、**ドメインモデルを“汚さずに”DBへマッピングできる**って説明してるよ🧼 ([learn.microsoft.com][2])

---

## 2) やっちゃダメ！Entitiesが汚れる典型パターン🧯💥

### 🚫 パターンA：EF Core属性が混ざる

* `[Key]`, `[Table]`, `[Column]`, `[MaxLength]` とか
* `DbContext` / `DbSet` が見える
* ナビゲーションプロパティ前提の形に寄せちゃう

➡️ **DB都合が中心に侵入**してるサイン⚠️

### 🚫 パターンB：HTTP/UIの型が混ざる

* `HttpContext`, `IFormFile`, `ActionResult` が見える
* “画面用の都合”でプロパティが増える

➡️ **表示や通信の都合は外側の仕事**だよ〜🧩

### 🚫 パターンC：JSON/シリアライズ都合が混ざる

* `JsonPropertyName`, `JsonIgnore` などがEntityに付く
* 「APIの返却形」をEntityで直接やり始める

➡️ **APIの形は変わりがち**だから、中心で抱えると痛い🥲

---

## 3) OKな形：Entitiesは“純粋なC#ルールのかたまり”👑💎

ポイントはこれ👇

* **不変条件（ルール）を守れるコンストラクタ／メソッド**
* **外の事情（DB/HTTP/JSON）を一切知らない**
* **string地獄を避けてValue Objectを使う**（Titleとか📝）

### ✅ 例：ピュアなEntity（Memo）✍️✨

```csharp
namespace MyApp.Core.Entities;

public sealed class Memo
{
    public MemoId Id { get; }
    public MemoTitle Title { get; private set; }
    public bool IsArchived { get; private set; }

    public Memo(MemoId id, MemoTitle title)
    {
        Id = id;
        Title = title;
        IsArchived = false;
    }

    public void Rename(MemoTitle newTitle)
    {
        Title = newTitle;
    }

    public void Archive()
    {
        IsArchived = true;
    }
}

public readonly record struct MemoId(Guid Value);

public readonly record struct MemoTitle
{
    public string Value { get; }

    public MemoTitle(string value)
    {
        value = (value ?? "").Trim();
        if (value.Length is < 1 or > 60)
            throw new ArgumentException("タイトルは1〜60文字だよ📝");

        Value = value;
    }

    public override string ToString() => Value;
}
```

ここにはEFもHTTPもJSONも出てこないよね？🙆‍♀️✨
**これが“中心が方針になる”ってこと**！

---

## 4) じゃあDB保存はどうするの？➡️「外側でマッピング」する🗄️🔁

クリーンアーキの定番はこれ👇

* **Domain Entity（中心）**：ルールと振る舞い（ピュア）
* **Persistence Model（外側）**：DBに都合の良い形
* **変換（Mapper）**：外側で吸収

Microsoftのガイドでも、EF Coreのマッピングは“永続化層”でやることで、ドメインを汚さないって説明されてるよ🧼 ([learn.microsoft.com][2])

### ✅ 例：永続化用モデル（外側）＋変換（外側）🧩

```csharp
// Adapters.Persistence 側（外側）に置くイメージ
namespace MyApp.Adapters.Persistence.Models;

public sealed class MemoRecord
{
    public Guid Id { get; set; }
    public string Title { get; set; } = "";
    public bool IsArchived { get; set; }
}
```

```csharp
// 外側で変換（Mapper）も面倒見る
using MyApp.Core.Entities;
using MyApp.Adapters.Persistence.Models;

namespace MyApp.Adapters.Persistence.Mappers;

public static class MemoMapper
{
    public static MemoRecord ToRecord(this Memo memo) => new()
    {
        Id = memo.Id.Value,
        Title = memo.Title.Value,
        IsArchived = memo.IsArchived
    };

    public static Memo ToDomain(this MemoRecord record) =>
        new(new MemoId(record.Id), new MemoTitle(record.Title))
        {
            // IsArchived を private set にしたいなら、生成方法を工夫（Factory等）する
        };
}
```

> ここは「とりあえず形」ね😊
> “アーカイブ状態も安全に復元したい”なら、Factoryを用意して不変条件を守りながら復元するのがキレイ✨

---

## 5) すぐできる！ミニ課題（Chapter 15）🎮💪

### ✅ 課題A：Entitiesの“外側依存”を探せ！🔍

Entities/Coreプロジェクトで次をチェック👀

* `using Microsoft.EntityFrameworkCore` がない？
* `using Microsoft.AspNetCore` がない？
* `using System.Text.Json.Serialization` がない？
* NuGet参照に `Microsoft.EntityFrameworkCore*` が入ってない？
  （入ってたらほぼアウト😇）

### ✅ 課題B：わざと汚して→戻す（理解が爆上がり）🔥

1. MemoにEF属性を付けてみる（わざとね😆）
2. 「うわ、中心がDB都合になった…」を体感する
3. 属性を外側（Persistence Model）へ移す
4. 変換で吸収して、Entitiesをピュアに戻す✨

---

## 6) AI（Copilot/Codex）活用プロンプト例🤖💖

コピペで使えるよ〜👇

* 「この `Core/Entities` プロジェクトが参照している外部ライブラリ一覧を前提に、クリーンアーキ的にNG依存がないか指摘して」
* 「このEntityに混入している“永続化/HTTP/JSON”都合を3分類して、外側へ移す手順を書いて」
* 「Domain EntityとPersistence Modelを分ける設計で、マッピングの落とし穴（null/ID/既定値/復元）を列挙して」
* 「“Entityを汚さずにEF Coreでマッピングする”方針で、Fluent API構成案（EntityTypeConfiguration）を提案して」
* 「このEntityの不変条件が弱い。破られないようにコンストラクタ／メソッド設計を直して」

---

## 7) 仕上げチェックリスト✅✨（この章のゴール）

Entitiesがこうなってたら勝ち🏆💕

* [ ] Entityに **EF Core / ASP.NET Core / JSON** の要素が1つもない
* [ ] 不変条件が **“作れない・壊せない”** 形で守られてる🚧
* [ ] “DB保存の都合”は **外側のモデル＆設定** が持ってる🗄️
* [ ] 依存の向きが内側へ（中心が外側を知らない）になってる⭕➡️ ([クリーンコーダーブログ][1])

---

## 8) ちいさな理解テスト（3問）📘💡

1. Entityに `[Key]` を付けたくなった。クリーンアーキ的に何が起きてる？😵
2. APIの返却形に合わせてEntityに `JsonPropertyName` を付けた。何が将来つらい？🥲
3. 「でもEF CoreってEntityを汚さないと使えなくない？」にどう答える？🧼（ヒント：公式ガイド） ([learn.microsoft.com][2])

---

## 次（第16章）へのつながり🌈

第16章では、いま作ったEntitiesがちゃんと
**用語・不変条件・振る舞い・依存ゼロ**になってるかを総点検するよ✅💖

必要なら、この章の「汚れたEntity→キレイにする」用のサンプルを、もう少しガッツリ（復元Factory／例外の型／Resultパターン）まで発展させた版も作れるよ〜😊✨

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
[2]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-implementation-entity-framework-core "Implementing the infrastructure persistence layer with Entity Framework Core - .NET | Microsoft Learn"
