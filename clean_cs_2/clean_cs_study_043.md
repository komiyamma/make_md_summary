# 第43章：Entitiesのテスト（速い・堅い・気持ちいい）🍰🧪✨

Entities（Entity / Value Object）は、アプリの“心臓”だよね🫀
だからこそ **最優先でテストして守る** と、あとあと超ラクになります💖
しかもEntitiesはフレームワークに依存しない「純C#」だから、**テストが爆速**で気持ちいい〜😆⚡

（ちなみに今どきのC#は **C# 14 + .NET 10（LTS）** が軸だよ〜🧡 ([Microsoft Learn][1])）

---

## この章のゴール🎯✨

次ができるようになろう〜😊💪

* Value Object の **不変条件（Invariants）** をテストで守れる🚧💎
* Entity の **ふるまい（メソッド）** をテストで守れる🧠🪪
* 「外部なし」＝DBなし/HTTPなし/DIなしで、**超高速に**回せる🏎️💨
* テストが「仕様書」になって、設計がブレにくくなる📘✨

---

## Entitiesテストが“いちばんコスパ良い”理由💰💖

### 1) 速い⚡（だから毎回回せる）

* 依存がない＝起動も準備もいらない😆
* テスト実行が早いほど、気軽に何回も回せる🔁✨

### 2) 壊れやすいのは“ルール”🧨（だから守る）

* 変更で壊れがちなのって「タイトル空OKになっちゃった」とか「重複タグが入る」とか…地味だけど致命傷💀
* Entitiesテストは、そこをガチガチに守る🛡️✨

### 3) 設計がキレイになりやすい🧼

* テストしやすいEntitiesは、だいたい責務が整理されてる😊
* テスト書きながら「ここ変だな？」が見える👀✨

---

## テスト基盤は何を使う？🧰✨（おすすめ：xUnit）

Visual Studioで気持ちよく回すなら **xUnit** が定番だよ〜😊
今は **xUnit v3** が .NET 8+ をサポートしてるので、.NET 10でもOK🧡 ([xunit.net][2])
さらにVisual Studio 2026まわりでは Microsoft Testing Platform との話も進んでるよ〜🧪✨ ([xunit.net][3])

---

## まずは題材：MemoのEntitiesを“最小”で用意しよう📝✨

ここでは「メモ管理」のEntitiesだけ作って、テストするよ〜😊
（UseCaseとかAPIとかは一切いらない🙅‍♀️✨）

### 例：ドメインルール（テストで守りたいこと）📌

* タイトルは **空/空白だけNG** ❌
* タイトルは **最大100文字**（例）✍️
* タグ名は **空NG** ❌、**重複追加NG** ❌
* Archiveしたら `IsArchived=true` ✅

---

## 実装例：Entities（C#）🧩💎

> ここは「説明用にシンプル」だけど、テスト観点はそのまま実戦で使えるよ〜😊✨

```csharp
using System;
using System.Collections.Generic;

namespace MyApp.Core.Entities;

// ドメインのバリデーションエラー（“失敗＝仕様”）
public sealed class DomainValidationException : Exception
{
    public string Code { get; }

    public DomainValidationException(string code, string message) : base(message)
        => Code = code;
}

// Value Object：MemoTitle（不変条件をここで守る）
public sealed record MemoTitle
{
    public string Value { get; }

    private MemoTitle(string value) => Value = value;

    public static MemoTitle Create(string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new DomainValidationException("MemoTitle.Empty", "タイトルは必須です");

        var v = value.Trim();

        if (v.Length > 100)
            throw new DomainValidationException("MemoTitle.TooLong", "タイトルが長すぎます");

        return new MemoTitle(v);
    }

    public override string ToString() => Value;
}

// Value Object：TagName
public sealed record TagName
{
    public string Value { get; }

    private TagName(string value) => Value = value;

    public static TagName Create(string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new DomainValidationException("TagName.Empty", "タグ名は必須です");

        var v = value.Trim();

        if (v.Length > 30)
            throw new DomainValidationException("TagName.TooLong", "タグ名が長すぎます");

        return new TagName(v);
    }

    public override string ToString() => Value;
}

// Entity：Memo（同一性＋ふるまい）
public sealed class Memo
{
    public Guid Id { get; }
    public MemoTitle Title { get; private set; }
    public bool IsArchived { get; private set; }

    private readonly HashSet<TagName> _tags = new();
    public IReadOnlyCollection<TagName> Tags => _tags;

    public Memo(Guid id, MemoTitle title)
    {
        if (id == Guid.Empty)
            throw new DomainValidationException("Memo.IdEmpty", "IDが不正です");

        Id = id;
        Title = title;
    }

    public void Rename(MemoTitle newTitle)
    {
        // 例：Archivedでも改名できる仕様にする（必要なら禁止してOK）
        Title = newTitle;
    }

    public void Archive() => IsArchived = true;
    public void Unarchive() => IsArchived = false;

    public void AddTag(TagName tag)
    {
        if (!_tags.Add(tag))
            throw new DomainValidationException("Memo.TagDuplicate", "タグが重複しています");
    }
}
```

---

## テスト例：Value Object のテスト💎🧪✨（一番おいしい所）

### ✅ 何をテストする？

* “作れない状態”がちゃんと作れないか🚧
* 境界値（100文字OK / 101文字NG）📏
* Trimされるか（仕様なら）✂️

```csharp
using System;
using Xunit;
using MyApp.Core.Entities;

namespace MyApp.Core.Entities.Tests;

public sealed class MemoTitleTests
{
    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void Create_EmptyOrWhiteSpace_Throws(string? input)
    {
        var ex = Assert.Throws<DomainValidationException>(() => MemoTitle.Create(input));
        Assert.Equal("MemoTitle.Empty", ex.Code);
    }

    [Fact]
    public void Create_TooLong_Throws()
    {
        var longTitle = new string('a', 101);

        var ex = Assert.Throws<DomainValidationException>(() => MemoTitle.Create(longTitle));
        Assert.Equal("MemoTitle.TooLong", ex.Code);
    }

    [Fact]
    public void Create_Trim_Works()
    {
        var title = MemoTitle.Create("  hello  ");
        Assert.Equal("hello", title.Value);
    }

    [Fact]
    public void Create_MaxLength100_IsOk()
    {
        var ok = new string('a', 100);
        var title = MemoTitle.Create(ok);
        Assert.Equal(100, title.Value.Length);
    }
}
```

💡ポイント😍

* 例外の `message` より **Code** をテストするのがおすすめ✨（文言変更でテストが壊れにくい👍）

---

## テスト例：Entity のふるまいテスト🪪🧪✨

### ✅ 何をテストする？

* 状態が正しく変わるか（Rename / Archive）🔁
* ルール違反が止まるか（重複タグ）🛑

```csharp
using System;
using Xunit;
using MyApp.Core.Entities;

namespace MyApp.Core.Entities.Tests;

public sealed class MemoTests
{
    [Fact]
    public void NewMemo_HasTitle_And_NotArchived()
    {
        var memo = new Memo(Guid.NewGuid(), MemoTitle.Create("first"));

        Assert.Equal("first", memo.Title.Value);
        Assert.False(memo.IsArchived);
    }

    [Fact]
    public void Rename_ChangesTitle()
    {
        var memo = new Memo(Guid.NewGuid(), MemoTitle.Create("old"));

        memo.Rename(MemoTitle.Create("new"));

        Assert.Equal("new", memo.Title.Value);
    }

    [Fact]
    public void Archive_SetsArchivedTrue()
    {
        var memo = new Memo(Guid.NewGuid(), MemoTitle.Create("x"));

        memo.Archive();

        Assert.True(memo.IsArchived);
    }

    [Fact]
    public void AddTag_Duplicate_Throws()
    {
        var memo = new Memo(Guid.NewGuid(), MemoTitle.Create("x"));
        var tag = TagName.Create("work");

        memo.AddTag(tag);

        var ex = Assert.Throws<DomainValidationException>(() => memo.AddTag(tag));
        Assert.Equal("Memo.TagDuplicate", ex.Code);
    }

    [Fact]
    public void Constructor_EmptyGuid_Throws()
    {
        var ex = Assert.Throws<DomainValidationException>(() =>
            new Memo(Guid.Empty, MemoTitle.Create("x"))
        );

        Assert.Equal("Memo.IdEmpty", ex.Code);
    }
}
```

---

## テストの書き方テンプレ📐✨（迷子防止）

### Arrange / Act / Assert（AAA）🧁

* Arrange：準備🍳
* Act：実行🧨
* Assert：確認✅

テスト名もテンプレ化しちゃうと超ラク😆✨

* `Create_Empty_Throws`
* `AddTag_Duplicate_Throws`
* `Archive_SetsTrue`

---

## “やっちゃダメ”集🙅‍♀️💥（でもみんな通る😂）

* ❌ DBやHTTPを混ぜる → Entitiesテストの強み（速さ）が死ぬ💀
* ❌ privateメソッドを直接テストしたくなる → **公開されたふるまい**で検証しよ😊
* ❌ テストが「実装に依存」しすぎ → “仕様”だけを見よう📘✨
* ❌ 例外メッセージ文字列を固定でAssert → 文言変更で折れる🥲（Code推し💖）

---

## AIの使いどころ🤖✨（Entitiesテストは相性よすぎ）

### 1) 境界値の洗い出し📏

AIにこう聞くと強いよ〜😊

* 「このVOの制約から境界値テストケースを列挙して」
* 「null/空/空白/最大/最大+1/絵文字/全角…も含めて」

### 2) テスト名の統一🧠

* 「命名規則をこの形に揃えて」
* 「Given-When-Thenに変換して」

### 3) 失敗ケースを“仕様”として固める⚠️

* 「この失敗はドメインの仕様？アダプタ側の形式エラー？」って相談相手にするの最高😆✨

---

## ミニ課題🎮💖（15〜30分）

### 課題A：VOをもう1つ増やす💎

* 例：`MemoBody`（本文）

  * 空はOK/NG？
  * 最大長は？
  * Trimする？
    → 仕様を決めて、テストを書いて守ってね🧪✨

### 課題B：Entityにルールを1つ足す🪪

* 例：Archived中は `AddTag` できない仕様にする

  * できないなら例外Codeは？
  * テストはまず失敗させてから直す（TDDっぽく）😆🔁

---

## 章末チェックリスト✅🧡

* [ ] VOの不変条件がテストで守られてる💎🧪
* [ ] Entityの主要なふるまいがテストで守られてる🪪✨
* [ ] テストが速い（外部依存ゼロ）⚡
* [ ] 例外は `Code` をAssertしてる（壊れにくい）🛡️
* [ ] 境界値（最大/最大+1）が入ってる📏

---

次の第44章では、この「Port差し替え」の考え方で **UseCaseもDBなしでテスト**していくよ〜🎭🧪✨

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://xunit.net/?utm_source=chatgpt.com "xUnit.net: Home"
[3]: https://xunit.net/docs/theory-data-stability-in-vs?utm_source=chatgpt.com "Theory Data Stability in Test Explorer [2025 November 27]"
