# 第14章：エラーもドメインの一部（失敗＝仕様）⚠️📜✨

この章のゴールはこれ👇
**「失敗パターン（＝仕様）」を、ドメイン（Entities/VO）にちゃんと“居場所”を作ってあげて、例外が暴れない設計にする**ことだよ〜🥰

---

## 1) まず大前提：「失敗」はバグじゃなくて仕様かも😳🧩

例：メモ作成📒

* タイトル空っぽ → それは“よくある失敗”で、仕様として扱うべき
* DBが落ちて保存できない → それは“システム障害”寄り（想定はするけど、扱いは別）

クリーンアーキだと、**内側（Domain/UseCase）は外側（Web/DB）を知らない**のが大原則だよね⭕
だから、**「HTTP 400にする」みたいな話は外側の責任**。内側は **「どう失敗したか」** を表現するだけにするよ✨ ([クリーンコーダーブログ][1])

---

## 2) 「例外」っていつ使うの？🤔💥（超だいじ）

Microsoft の設計ガイドラインでは、ざっくりこう👇

* **通常の制御フローに例外を使わない**（＝想定される失敗は Result などで返す）
* 例外は「本当に例外的」なとき（システム障害、レースコンディション等） ([Microsoft Learn][2])

なのでこの章では、こう分けるよ💡

### ✅ 期待される失敗（Expected failure）

* 仕様として起こりうる（入力ミス、業務ルール違反など）
* **DomainError / Result** で表現するのが相性よし✨

### 💥 期待しない失敗（Unexpected failure）

* バグ、ヌル参照、外部システム障害、想定外の状態
* **例外**（＋ログ）で扱うのが自然🔥

---

## 3) ドメインエラーの「型」を決めよう🧱✨（最小でOK）

ポイントはこれ👇

* **エラーは“種類（Code）”が命**（メッセージは後で変えやすい）
* ドメインはUI文言に責任を持たない（ただし“人間が理解できる説明”は持ってOK）
* 追加情報（例：最大文字数）をメタデータで持てると便利👜

### 例：DomainError と Result（自前で軽く作る）🛠️

```csharp
public sealed record DomainError(
    string Code,
    string Message,
    IReadOnlyDictionary<string, object>? Meta = null
);

public readonly struct Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public DomainError? Error { get; }

    private Result(bool isSuccess, T? value, DomainError? error)
    {
        IsSuccess = isSuccess;
        Value = value;
        Error = error;
    }

    public static Result<T> Ok(T value) => new(true, value, null);
    public static Result<T> Fail(DomainError error) => new(false, default, error);
}
```

> ここは“学習用の最小実装”だよ〜✨ 本番では拡張したり、チーム標準の Result を使ってもOK🙆‍♀️

---

## 4) Value Objectで「失敗＝仕様」を閉じ込める💎🔒

たとえば `MemoTitle`（タイトル）を VO にして、**作れない値は作れない**ようにするよ🚧

```csharp
public sealed record MemoTitle
{
    public const int MaxLength = 50;
    public string Value { get; }

    private MemoTitle(string value) => Value = value;

    public static Result<MemoTitle> Create(string? raw)
    {
        var v = (raw ?? "").Trim();

        if (v.Length == 0)
        {
            return Result<MemoTitle>.Fail(
                new DomainError("memo.title.empty", "タイトルは必須です")
            );
        }

        if (v.Length > MaxLength)
        {
            return Result<MemoTitle>.Fail(
                new DomainError(
                    "memo.title.too_long",
                    $"タイトルは{MaxLength}文字以内にしてください",
                    new Dictionary<string, object> { ["maxLength"] = MaxLength, ["actual"] = v.Length }
                )
            );
        }

        return Result<MemoTitle>.Ok(new MemoTitle(v));
    }
}
```

### ここが気持ちいいポイント🥳

* Controller や UseCase が「タイトル空なら…」って毎回書かなくて済む
* 失敗パターンが VO に集約される（仕様が散らからない）✨

---

## 5) Entity側の失敗も「仕様」として表現する👑⚙️

Entityの操作（例：Rename）でも、仕様として失敗しうるよね👇

* アーカイブ済みは名前変更禁止
* 同じタイトルなら更新不要（仕様としてエラーにするか、成功扱いにするかは設計次第）

```csharp
public sealed class Memo
{
    public Guid Id { get; }
    public MemoTitle Title { get; private set; }
    public bool IsArchived { get; private set; }

    public Memo(Guid id, MemoTitle title)
    {
        Id = id;
        Title = title;
    }

    public Result<Unit> Rename(MemoTitle newTitle)
    {
        if (IsArchived)
        {
            return Result<Unit>.Fail(
                new DomainError("memo.rename.archived", "アーカイブ済みのメモは変更できません")
            );
        }

        Title = newTitle;
        return Result<Unit>.Ok(Unit.Value);
    }

    public void Archive() => IsArchived = true;
}

public readonly struct Unit
{
    public static readonly Unit Value = new();
}
```

---

## 6) UseCaseでの「流し方」🌊➡️（例外を内側に持ち込まない）

UseCase（Interactor）はこういう方針にすると安定するよ✨

* **VO/Entityが返した失敗を、そのまま“結果”として扱う**
* 「HTTP 何番」みたいな話はここでしない（外側へ）

```csharp
public sealed record CreateMemoRequest(string? Title);

public interface ICreateMemoOutputPort
{
    void Present(CreateMemoResponse response);
}

public sealed record CreateMemoResponse(
    bool Success,
    Guid? MemoId,
    DomainError? Error
);

public interface IMemoRepository
{
    Task AddAsync(Memo memo, CancellationToken ct);
}

public sealed class CreateMemoInteractor
{
    private readonly IMemoRepository _repo;
    private readonly ICreateMemoOutputPort _output;

    public CreateMemoInteractor(IMemoRepository repo, ICreateMemoOutputPort output)
    {
        _repo = repo;
        _output = output;
    }

    public async Task HandleAsync(CreateMemoRequest request, CancellationToken ct)
    {
        var titleResult = MemoTitle.Create(request.Title);
        if (!titleResult.IsSuccess)
        {
            _output.Present(new CreateMemoResponse(false, null, titleResult.Error));
            return;
        }

        var memo = new Memo(Guid.NewGuid(), titleResult.Value!);

        // ここはDBなので「障害」が起きうる → 例外は外側で握ってOK（後の章で整備）
        await _repo.AddAsync(memo, ct);

        _output.Present(new CreateMemoResponse(true, memo.Id, null));
    }
}
```

> 「DB保存失敗」を Result で返すべきか？は議論が分かれやすい所だけど、まずはこの章では **“ドメイン起因の失敗を Result 化”** に集中しよ〜🧠✨

---

## 7) 外側（Presenter/Controller）で “ユーザーに伝わる形” に変換する🎤🪄

ここで初めて、HTTPとか画面の都合が出てくるよ🌐
ASP.NET Core だと **ProblemDetails** が定番（Microsoft docsはRFC 7807ベースとして説明してるよ）([Microsoft Learn][3])
ちなみに Problem Details のRFCは **RFC 9457 が RFC 7807 を obsolete（廃止）**にしてるので、仕様面はRFC 9457も知っておくと今っぽい✨ ([RFC エディター][4])

Presenter側で「DomainError → ProblemDetailsっぽい形」にするイメージ👇

```csharp
public sealed record ApiError(string Type, string Title, int Status, string Detail, object? Extensions = null);

public sealed class CreateMemoPresenter : ICreateMemoOutputPort
{
    public object? ViewModel { get; private set; }

    public void Present(CreateMemoResponse response)
    {
        if (response.Success)
        {
            ViewModel = new { id = response.MemoId };
            return;
        }

        // ドメインエラーCodeで、外側が表現を決める（HTTP/画面はここ）
        ViewModel = response.Error?.Code switch
        {
            "memo.title.empty" => new ApiError(
                Type: "https://example.com/problems/memo-title-empty",
                Title: "入力エラー",
                Status: 400,
                Detail: "タイトルを入力してください😊"
            ),
            "memo.title.too_long" => new ApiError(
                Type: "https://example.com/problems/memo-title-too-long",
                Title: "入力エラー",
                Status: 400,
                Detail: "タイトルが長すぎます🥺",
                Extensions: response.Error.Meta
            ),
            _ => new ApiError(
                Type: "https://example.com/problems/unknown",
                Title: "エラー",
                Status: 400,
                Detail: "処理できませんでした😢"
            )
        };
    }
}
```

---

## 8) “エラー設計”のチェックリスト✅🧷

### ドメイン（Entities/VO）

* ✅ 仕様として起こる失敗を **DomainError（Code）で列挙**できる
* ✅ 不正な状態を **作らせない**（Createで弾く）
* ✅ UI/HTTP/DB用語が混ざってない（例：BadRequest、DbContext…は禁止🙅‍♀️）

### UseCase

* ✅ ドメインエラーは Result として流せる
* ✅ どの失敗をどのタイミングで返すかが「手順書」になってる🧾

### 外側（Presenter/Controller）

* ✅ エラーをユーザーに伝わる形へ変換できる（ProblemDetailsなど） ([Microsoft Learn][3])

---

## 9) ありがち事故😇💥（先に潰そ〜）

* ❌ **例外で入力エラーを制御**しちゃう（try/catchだらけ）
  → “普通に起こる失敗”は Result がラク。ガイドライン的にもおすすめ方向だよ ([Microsoft Learn][2])
* ❌ DomainError に「HTTP 400」とか「画面文言」を入れちゃう
  → 外側でやろう！内側は “Code” と “意味” が中心✨
* ❌ Codeが適当で増殖してカオス
  → `memo.title.*` みたいに **名前空間っぽく**揃えると運用しやすいよ🧹

---

## 10) ミニ課題🎮💖（手を動かすやつ）

### 課題A：失敗ケースを10個出す📝

「メモ作成」で起こりうる失敗を10個書いて、

* ドメイン起因（入力・業務ルール）
* システム起因（DB/ネットワーク）
  に分類してみてね✨

### 課題B：DomainErrorを3つ実装🧩

* `memo.title.empty`
* `memo.title.too_long`
* `memo.rename.archived`
  を VO / Entity に入れて、UseCaseで流す！

### 課題C：テスト🧪

* `MemoTitle.Create("")` は失敗になる
* `MemoTitle.Create(51文字)` は `maxLength` を持って失敗になる
  みたいなのを xUnit で書いてみよ〜🍰

---

## 11) Copilot / Codex に頼むと捗るプロンプト例🤖✨

* 「このVOの仕様（空NG、50文字まで）に対して、境界値テストケースを列挙して」
* 「Result<T> のユニットテスト（成功/失敗）雛形をxUnitで作って」
* 「DomainErrorのCode命名規則案を、衝突しにくい形で提案して」

※出てきたコードは **“層をまたぐ依存が混ざってないか”** だけ必ず目視チェックしてね😉🧯

---

## 今回のまとめ🎁✨

* **失敗は仕様**。だから「ドメインの言葉」で表現する⚠️
* **想定内の失敗は Result / DomainError**、想定外は例外💥 ([Microsoft Learn][2])
* 外側で ProblemDetails などに変換して、ユーザーに伝わる形にする🌐 ([Microsoft Learn][3])
* そして今どきの最新土台は **.NET 10（LTS）** が来てるよ〜🧡 ([Microsoft for Developers][5])

次の章以降で、この「エラーの流れ」をもっと綺麗に“全層で整える”方向に進められるよ🧵✨

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
[2]: https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/exception-throwing?utm_source=chatgpt.com "Exception Throwing - Framework Design Guidelines"
[3]: https://learn.microsoft.com/en-us/aspnet/core/web-api/?view=aspnetcore-10.0&utm_source=chatgpt.com "Create web APIs with ASP.NET Core"
[4]: https://www.rfc-editor.org/rfc/rfc9457.html?utm_source=chatgpt.com "RFC 9457: Problem Details for HTTP APIs"
[5]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
