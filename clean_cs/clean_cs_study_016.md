# 第16章：Entities層の完成チェック✅🧼💎（「中心がちゃんと中心」になってる？）

この章はね、**Entities（ドメインの中心）を“最終健康診断”する回**だよ〜🏥✨
ここがキレイだと、後のUseCaseやDB差し替えがめちゃ楽になる😌💖

ちなみに今どきのC#は **C# 14** が最新で、**.NET 10** に対応してるよ〜🚀（.NET 10 の最新版は **10.0.2 / 2026-01-13**、VS 2026の更新は **18.2.1 / 2026-01-20** あたりが目安）📌✨ ([Microsoft Learn][1])

---

## 16.1 今日のゴール🎯✨

**Entities層が「方針（ポリシー）」として完成している**ことを確認するよ✅
チェックするのはこの4つ💡

1. **用語が揃ってる**（ドメインの言葉で話せる）🗣️📚
2. **不変条件が守れる**（壊れた状態が作れない）🚧
3. **振る舞いがある**（データ箱じゃない）🎭
4. **依存ゼロ**（フレームワーク・DB・HTTPを知らない）🧼

クリーンアーキの中心思想は「依存は内側へ」だよね➡️⭕ ([blog.cleancoder.com][2])

---

## 16.2 Entities層「完成」のDefinition of Done✅📝（これ全部YESなら合格！）

### A. 依存の純度🧼

* [ ] `Microsoft.*`（AspNetCore / EF Core / DI / Logging 等）を **参照してない**
* [ ] `System.Net.Http` みたいな外部通信っぽいものを **参照してない**
* [ ] 属性（`[Key]` `[Table]` など）を **付けてない**
* [ ] 設定値や接続文字列を **知らない**

### B. モデルの強さ💪

* [ ] Entityは **ID（同一性）** を持ってる🪪
* [ ] Value Object は **不変＆等価**（できれば`record`/`record struct`）💎
* [ ] 不変条件は **コンストラクタ/Factory/メソッド入口**で必ず守る🚧
* [ ] 状態はむやみに `public set;` しない（勝手に壊せない）🧯

### C. 振る舞い中心🎬

* [ ] 「名詞だけ」じゃなくて「動詞」がある（`Rename` `Archive` `AddTag`…）🧠
* [ ] ルールがControllerやUseCaseに散ってない（Entitiesに戻ってる）🏠

### D. テスト可能🍰

* [ ] Entitiesだけを参照するテストで主要ルールが守れる🧪
* [ ] “壊れる例”がテストで再現できる（境界値・例外パターン）⚠️

---

## 16.3 依存ゼロチェック🔍✨（3分でできるやつ）

### ① 参照関係を目で見る👀

* ソリューションで **Entitiesプロジェクト**を右クリック
  → 参照（References）を見て、変な参照がないか確認✅
  （Entitiesは基本「自分とSystemだけ」でいたい😌）

### ② CLIで“パッケージ混入”を検出🐍

```bash
dotnet list path/to/Your.Entities.csproj package
dotnet list path/to/Your.Entities.csproj reference
```

* **EntitiesにNuGet入ってたら黄色信号**🚥（テストは別プロジェクトでOK✨）

### ③ 禁止ワード検索（VSの「検索」でもOK）🕵️‍♀️

禁止の例：`EntityFrameworkCore` / `AspNetCore` / `DbContext` / `HttpClient`

```bash
rg "EntityFrameworkCore|DbContext|AspNetCore|HttpClient|\[Key\]|\[Table\]" .
```

（PowerShellでもOKだよ〜💻✨）

---

## 16.4 “データ箱”になってない？📦➡️🎭（よくある崩れ方）

### ダメ寄り例🙅‍♀️（貧血っぽい）

* `public set;` だらけ
* ルールは外側（UseCase/Controller）に散らばる
* EntityはDTOみたいに運ばれるだけ

### 目指す形🙆‍♀️（ドメインが生きてる）

* 状態変更は **メソッド経由**（入口でルールを守る）🚧
* Entityが「やっていい/ダメ」を自分で判断できる🧠
* 外側は「呼ぶだけ」になる📞

---

## 16.5 不変条件は“入口で必ず”守る🚧💎（3つの入口だけ覚えよ）

不変条件を守る場所はだいたいここ👇

1. **生成時**：コンストラクタ or Factory（`Create`）
2. **更新時**：状態変更メソッド（`Rename`とか）
3. **Value Object生成時**：`Title.Create()` みたいに閉じ込める

「どこでもチェック」じゃなくて「入口だけ」だと、漏れないしラク😊✨

---

## 16.6 Entitiesだけで動く“超ミニ”実装例🧪✨（メモ題材）

「DBもHTTPも知らない」Entitiesの雰囲気を、1セット置くね〜💖

### DomainError（超シンプル版）⚠️

```csharp
namespace MyApp.Core.Domain;

public enum DomainErrorCode
{
    TitleEmpty,
    TitleTooLong,
    TagEmpty,
    TagTooLong,
    TagDuplicate,
    ArchivedCannotRename,
}

public sealed class DomainException : Exception
{
    public DomainErrorCode Code { get; }
    public DomainException(DomainErrorCode code) : base(code.ToString()) => Code = code;
}
```

### Value Object：Title 💎

```csharp
namespace MyApp.Core.ValueObjects;

using MyApp.Core.Domain;

public sealed record Title
{
    public const int MaxLength = 100;
    public string Value { get; }

    private Title(string value) => Value = value;

    public static Title Create(string? raw)
    {
        if (string.IsNullOrWhiteSpace(raw))
            throw new DomainException(DomainErrorCode.TitleEmpty);

        var value = raw.Trim();
        if (value.Length > MaxLength)
            throw new DomainException(DomainErrorCode.TitleTooLong);

        return new Title(value);
    }

    public override string ToString() => Value;
}
```

### Value Object：TagName 💎

```csharp
namespace MyApp.Core.ValueObjects;

using MyApp.Core.Domain;

public sealed record TagName
{
    public const int MaxLength = 20;
    public string Value { get; }

    private TagName(string value) => Value = value;

    public static TagName Create(string? raw)
    {
        if (string.IsNullOrWhiteSpace(raw))
            throw new DomainException(DomainErrorCode.TagEmpty);

        var value = raw.Trim();
        if (value.Length > MaxLength)
            throw new DomainException(DomainErrorCode.TagTooLong);

        return new TagName(value);
    }

    public override string ToString() => Value;
}
```

### Entity：Memo 🎭

```csharp
namespace MyApp.Core.Entities;

using MyApp.Core.Domain;
using MyApp.Core.ValueObjects;

public readonly record struct MemoId(Guid Value)
{
    public static MemoId New() => new(Guid.NewGuid());
}

public sealed class Memo
{
    private readonly HashSet<TagName> _tags = new();

    public MemoId Id { get; }
    public Title Title { get; private set; }
    public bool IsArchived { get; private set; }
    public IReadOnlyCollection<TagName> Tags => _tags;

    private Memo(MemoId id, Title title)
    {
        Id = id;
        Title = title;
    }

    public static Memo CreateNew(Title title) => new(MemoId.New(), title);

    public void Rename(Title newTitle)
    {
        if (IsArchived)
            throw new DomainException(DomainErrorCode.ArchivedCannotRename);

        Title = newTitle;
    }

    public void AddTag(TagName tag)
    {
        if (!_tags.Add(tag))
            throw new DomainException(DomainErrorCode.TagDuplicate);
    }

    public void Archive() => IsArchived = true;
}
```

ポイント🌟

* EF属性ゼロ！🧼
* HTTP型ゼロ！🧼
* ルールはメソッド入口で守ってる！🚧

---

## 16.7 Entitiesだけのテスト✅🧪（速くて気持ちいいやつ🍰）

テストは別プロジェクトでOKだよ〜（Entitiesにテスト依存を入れない）✨

```bash
dotnet new xunit -n MyApp.Core.Tests
dotnet add MyApp.Core.Tests reference path/to/MyApp.Core.csproj
```

```csharp
using Xunit;
using MyApp.Core.Domain;
using MyApp.Core.Entities;
using MyApp.Core.ValueObjects;

public class MemoTests
{
    [Fact]
    public void CreateNew_sets_id_and_title()
    {
        var memo = Memo.CreateNew(Title.Create("Hello"));
        Assert.NotEqual(Guid.Empty, memo.Id.Value);
        Assert.Equal("Hello", memo.Title.Value);
    }

    [Fact]
    public void Rename_archived_memo_throws_domain_exception()
    {
        var memo = Memo.CreateNew(Title.Create("A"));
        memo.Archive();

        var ex = Assert.Throws<DomainException>(() => memo.Rename(Title.Create("B")));
        Assert.Equal(DomainErrorCode.ArchivedCannotRename, ex.Code);
    }

    [Fact]
    public void AddTag_duplicate_throws()
    {
        var memo = Memo.CreateNew(Title.Create("A"));
        var tag = TagName.Create("work");

        memo.AddTag(tag);

        var ex = Assert.Throws<DomainException>(() => memo.AddTag(tag));
        Assert.Equal(DomainErrorCode.TagDuplicate, ex.Code);
    }
}
```

このテストがサクッと通れば、**Entitiesが“単体で成立”してる証拠**になるよ〜😆✨

---

## 16.8 AI補助の使い方🤖💖（“レビュー役”にすると強い）

AIは「実装担当」より「監査担当」にするとめちゃ効くよ✅

### 依存チェックの観点を出させる🧠

* 「Entities層に入れちゃダメな依存を20個、理由つきで列挙して」📝

### “データ箱になってないか”レビューさせる📦

* 「このEntity、振る舞いが薄いなら改善案を3パターン出して。public setを減らす方針で」✂️

### テストの抜けを埋めさせる🧪

* 「TitleとTagNameの境界値テストを追加したい。観点を列挙して、xUnitで雛形作って」🍰

※最終判断は人間がやるのが大事だよ〜🙆‍♀️✨

---

## 16.9 仕上げの“最終チェックリスト”✅🧼（ここは毎回やる）

最後にこの5個だけは必ず確認しよっ☺️💕

* [ ] Entitiesプロジェクトに **外側参照が1つも無い**（DB/HTTP/フレームワーク）🧼
* [ ] 重要な不変条件が **必ず入口で守られる**🚧
* [ ] Entityに最低でも **3つ以上の振る舞いメソッド**がある🎭
* [ ] VOが **不変＆等価**になってる💎
* [ ] Entitiesだけのテストが **数本でも通ってる**🧪

---

## 次章（第17章）へのつながり🔜🎮

Entitiesが整ったら、次はいよいよ **Use Case（手順書）** を作っていくよ📦✨
ここまでで中心が固いと、UseCase側はすっごく作りやすくなる😌💖

---

必要なら、あなたの題材（メモ以外でもOK）に合わせて、**「Entities完成チェック用の具体チェック表」**をそのまま配布できるプリント風に整えて出すよ📄✨

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
