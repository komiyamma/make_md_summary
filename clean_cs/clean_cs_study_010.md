# 第10章：不変条件（Invariants）を入口で守る🚧✨

「不変条件（Invariant）」って、かんたんに言うと **“いつでも守られててほしい約束（ルール）”** だよ〜😊
そしてこの約束は、**Entity（や Aggregate）自身が責任を持って守る**のが超大事！
（DDDでも「集約（Aggregate）が状態変更のたびに不変条件を守るのが主責務」って言われるよ）([Microsoft Learn][1])

---

## 1) この章のゴール🎯💖

読み終わったら、こんなことができるようになるよ！

* 「不変条件って何？」を自分の言葉で説明できる🗣️✨
* **“壊れた状態を作れない設計”**にできる（入口で止める）🛑
* ルールが Controller / UseCase に散らばるのを防げる🧹

---

## 2) 「入口で守る」ってどこのこと？🚪👀

入口はだいたいこの2つ！

1. **生成時（Create / コンストラクタ / Factory）**

   * 例：タイトル空のMemoを作れない
2. **状態変更時（Rename / AddTag などのメソッド）**

   * 例：アーカイブ済みならRenameできない

つまり…
**“作る瞬間”と“変える瞬間”に必ずチェックが走る**ようにする感じだよ😊✨

> クリーンアーキでも、Entityはビジネスルールをカプセル化する存在だよ〜([クリーンコーダーブログ][2])

---

## 3) まずは例：メモアプリの不変条件を作ってみよ📝💡

今回の題材（Memo）で、よくある不変条件はこんな感じ👇

* タイトルは空禁止・最大100文字✍️
* タグは重複禁止・最大5個🏷️
* アーカイブしたMemoは編集禁止📦🔒

この「約束」が、**どこに書かれるべき？**
👉 答え：**Entity / Value Object の中**（中心）だよ！([Microsoft Learn][1])

---

## 4) 実装パターンは2つあるよ✌️（初心者はAがラク✨）

### A. 例外（DomainException）で止める🧯⚠️

* メリット：コードが短くて読みやすい
* 注意：例外を外側でちゃんと受け取って「ユーザー向け表示」に変換する必要あり（Presenter側の役目👍）

### B. Result型で返す🎁✅

* メリット：例外を乱発しない、テストしやすい
* 注意：型を用意するぶん少しだけ手間

この章では **B（Result型）** でいくね！（あとでUseCase → Presenterへ流すのが綺麗✨）

---

## 5) コード：Result型（超ミニ版）🧩✨

```csharp
namespace MyApp.Core;

public readonly record struct DomainError(string Code, string Message);

public readonly record struct Result
{
    public bool IsSuccess { get; }
    public DomainError? Error { get; }

    private Result(bool isSuccess, DomainError? error)
        => (IsSuccess, Error) = (isSuccess, error);

    public static Result Ok() => new(true, null);
    public static Result Fail(string code, string message) => new(false, new DomainError(code, message));
}

public readonly record struct Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public DomainError? Error { get; }

    private Result(bool isSuccess, T? value, DomainError? error)
        => (IsSuccess, Value, Error) = (isSuccess, value, error);

    public static Result<T> Ok(T value) => new(true, value, null);
    public static Result<T> Fail(string code, string message) => new(false, default, new DomainError(code, message));
}
```

---

## 6) コード：Value Object で「タイトルの不変条件」を封じ込める💎🔒

タイトル（string）をそのまま使うと、どこでも空文字が入っちゃう😇
だから **MemoTitle という型**にして、入口で止めるよ！

```csharp
namespace MyApp.Core;

public readonly record struct MemoTitle
{
    public string Value { get; }

    private MemoTitle(string value) => Value = value;

    public static Result<MemoTitle> Create(string? raw)
    {
        raw = raw?.Trim();

        if (string.IsNullOrWhiteSpace(raw))
            return Result<MemoTitle>.Fail("MemoTitle.Empty", "タイトルは空にできません😢");

        if (raw.Length > 100)
            return Result<MemoTitle>.Fail("MemoTitle.TooLong", "タイトルは100文字までだよ😵‍💫");

        return Result<MemoTitle>.Ok(new MemoTitle(raw));
    }

    public override string ToString() => Value;
}
```

✅ これで **「不正なタイトルのインスタンス」自体が作れない**🎉
これが「入口で守る」の強さだよ〜💪✨

---

## 7) コード：Entity（Memo）側でも「状態変更の入口」を守る👑🚧

```csharp
namespace MyApp.Core;

public sealed class Memo
{
    private readonly HashSet<TagName> _tags = new();

    public Guid Id { get; }
    public MemoTitle Title { get; private set; }
    public bool IsArchived { get; private set; }
    public IReadOnlyCollection<TagName> Tags => _tags;

    private Memo(Guid id, MemoTitle title)
        => (Id, Title) = (id, title);

    public static Result<Memo> Create(MemoTitle title)
        => Result<Memo>.Ok(new Memo(Guid.NewGuid(), title));

    public Result Rename(MemoTitle newTitle)
    {
        if (IsArchived)
            return Result.Fail("Memo.Archived", "アーカイブ済みのメモは編集できないよ📦🔒");

        Title = newTitle;
        return Result.Ok();
    }

    public Result AddTag(TagName tag)
    {
        if (IsArchived)
            return Result.Fail("Memo.Archived", "アーカイブ済みのメモにタグ追加できないよ📦🔒");

        if (_tags.Count >= 5)
            return Result.Fail("Memo.Tags.Limit", "タグは最大5個までだよ🏷️💦");

        if (!_tags.Add(tag))
            return Result.Fail("Memo.Tags.Duplicated", "同じタグは2回付けられないよ😆");

        return Result.Ok();
    }

    public Result Archive()
    {
        IsArchived = true;
        return Result.Ok();
    }
}

public readonly record struct TagName
{
    public string Value { get; }
    private TagName(string value) => Value = value;

    public static Result<TagName> Create(string? raw)
    {
        raw = raw?.Trim();

        if (string.IsNullOrWhiteSpace(raw))
            return Result<TagName>.Fail("TagName.Empty", "タグ名は空にできません😢");

        if (raw.Length > 20)
            return Result<TagName>.Fail("TagName.TooLong", "タグ名は20文字までだよ😵‍💫");

        return Result<TagName>.Ok(new TagName(raw));
    }

    public override string ToString() => Value;
}
```

ポイントはこれ👇💖

* `public set;` を無くして、**メソッド経由でしか変えられない**ようにする🔐
* 生成も `Create` だけにして、**入口を1つにする**🚪✨

---

## 8) “外側のValidation”と“内側のInvariant”は役割が違うよ🧠🧼

* 外側（API/画面）👉 **形式チェック**（必須、数値、フォーマット…）
* 内側（Domain）👉 **意味のルール**（ビジネスとして成り立つか）

ASP.NET Core側の検証は今どんどん良くなってるけど、**それでもDomainの不変条件は別腹で必要**だよ🍰✨([blog.elmah.io][3])

---

## 9) AI（Copilot/Codex）にやらせると強いところ🤖✨

### ① 不変条件の洗い出し補助🧠

* 「Memoの仕様から、不変条件を10個提案して。重複しないように、生成時/更新時に分類して」

### ② 境界値テスト案の生成🧪

* 「MemoTitle.Create のテストケースを境界値中心に列挙して（null/空/空白/100/101など）」

### ③ “ルールの置き場所”レビュー🧹

* 「このルールは Entity / VO / UseCase のどこに置くべき？理由付きで！」

---

## 10) よくある事故パターン集🚑💥（超あるある）

* ✅ Controllerでだけチェックして、Domainはスルー
  → **別経路（バッチ/他API/テスト）から壊れる**😇
* ✅ Entityに `public set;` が生えてて、どこでも破壊可能
  → “守ってるつもり”が簡単に破れる💣
* ✅ DB制約だけに頼る
  → アプリ内は一瞬壊れた状態になりがち（例外が飛び散る）([Microsoft Learn][4])

---

## 11) ミニ課題🎮✨（手を動かすと定着するよ！）

### 課題A（かんたん）🍬

* `MemoTitle` に「先頭/末尾の空白は自動でTrim」
* `TagName` に「大文字小文字は区別しない（同じとみなす）」を追加してみて🏷️

### 課題B（ちょいムズ）🍛

* `Memo` に `Unarchive()` を追加

  * ただし「アーカイブ解除は、24時間以内だけ可能」みたいなルールをつけてみよ⏰

---

## 12) まとめ🎀✅

* 不変条件は **“いつでも守る約束”**
* 守る場所は **Entity/Value Object（中心）** が基本([クリーンコーダーブログ][2])
* 「入口（生成・状態変更）」を **1箇所に寄せる**と壊れにくい🚧✨
* Result型にすると、UseCase → Presenter への流れが作りやすい🎁

---

次の章（第11章）は「EntityとVOの切り分け練習⚖️」だったね😊
この章のコード（MemoTitle / TagName / Memo）があると、切り分けがめっちゃやりやすくなるよ〜💖

[1]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-model-layer-validations?utm_source=chatgpt.com "Designing validations in the domain model layer - .NET"
[2]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
[3]: https://blog.elmah.io/new-in-net-10-and-c-14-fast-model-validation-for-apis/?utm_source=chatgpt.com "New in .NET 10 and C# 14: Fast Model Validation for APIs"
[4]: https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-ddd?utm_source=chatgpt.com "Using tactical DDD to design microservices"
