# 第26章：例外/エラーの流し方（Core→外）🌊⚠️✨

（テーマ：**「失敗」をキレイに伝えて、層を汚さない**💖）

---

## この章でできるようになること 🎯💪

* 「**想定内の失敗**」と「**想定外の事故**」を分けられる 😌⚠️
* Core（Entities/UseCases）から外側（UI/API）へ、**汚さずに失敗を渡すルート**を作れる 🚿✨
* HTTPや画面表示は外側でやりつつ、**Coreは“純粋な失敗情報”だけ**を返せる 🧼🧠
* APIなら **ProblemDetails** に落とす場所がわかる 🧾✨（外側担当ね！） ([Microsoft Learn][1])

---

## まず大前提：内側は外側を知らない 🧠⭕

クリーンアーキの鉄則として、**内側（Core）は外側（Web/DB/UI）の名前を出しちゃダメ**だよ〜🚫
だから **「HTTP 404」とか「ActionResult」とかをCoreに持ち込むのはNG**🙅‍♀️
（Output Portを使って、外側が実装するのが定石） ([blog.cleancoder.com][2])

---

## 失敗には2種類あるよ ⚠️🌸

ここ、めっちゃ大事！✨

### ① 想定内の失敗（= 仕様どおりの失敗）😌

例：

* タイトルが空だった（バリデーション）📝
* 対象のメモが存在しない（NotFound）🔎
* 同じタイトルが既にある（競合）⚔️

👉 これはアプリとして「普通に起こりうる」から、**例外で制御しない**のがキレイになりやすいよ✨
（.NETでも「例外は“本当に例外的なとき”に」って方針があるよ） ([Microsoft Learn][3])

### ② 想定外の事故（= バグ/障害/外部要因）💥

例：

* DB接続が落ちた🗄️💣
* 外部APIがタイムアウトした🌍⏳
* ヌル参照/予期せぬ例外😵

👉 これは **例外として捕まえて**、外側でログ＆安全な返しにするのが◎🧯✨

---

## この章の結論：Core→外への「失敗の運び方」🚚💖

おすすめの“型”はこれ👇

**Core側（UseCases/Entities）**

* 想定内の失敗：`Error`（または `Result`）として返す
* 想定外の事故：例外を捕まえて `Error(Unexpected)` に変換して外へ
* 外側の形式（HTTP/画面）は一切知らない

**外側（Presenter / Controller / Minimal API）**

* `Error` を見て、表示・HTTP・ProblemDetails に変換する
* APIなら `AddProblemDetails()` 等で統一した形にする ([Microsoft Learn][1])

---

## 実装：Coreで使う「エラー表現」を作ろう 🧩✨

### 1) Errorの共通型（Coreに置く）🧼

```csharp
namespace MyApp.Core;

public enum ErrorType
{
    Validation,
    NotFound,
    Conflict,
    Forbidden,
    Unexpected
}

public sealed record Error(string Code, string Message, ErrorType Type)
{
    public static Error Validation(string code, string message) => new(code, message, ErrorType.Validation);
    public static Error NotFound(string code, string message)   => new(code, message, ErrorType.NotFound);
    public static Error Conflict(string code, string message)   => new(code, message, ErrorType.Conflict);
    public static Error Forbidden(string code, string message)  => new(code, message, ErrorType.Forbidden);
    public static Error Unexpected(string code, string message) => new(code, message, ErrorType.Unexpected);
}
```

💡ポイント💖

* `Code` は機械向け（ログ/条件分岐）🧠
* `Message` は人間向け（表示するなら外側で調整してもOK）🗣️
* `ErrorType` は「外側に変換するヒント」になるよ✨

---

### 2) Result（成功/失敗）を作る（Coreに置く）🎁

```csharp
namespace MyApp.Core;

public readonly struct Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public Error? Error { get; }

    private Result(bool isSuccess, T? value, Error? error)
    {
        IsSuccess = isSuccess;
        Value = value;
        Error = error;
    }

    public static Result<T> Ok(T value) => new(true, value, null);

    public static Result<T> Fail(Error error) => new(false, default, error);

    public T GetValueOrThrow()
        => IsSuccess ? Value! : throw new InvalidOperationException("Result is failure.");
}
```

---

## UseCaseでの流し方：OutputPortに「成功」と「失敗」を渡す 🎤➡️

たとえば「メモ作成」UseCaseでいくね📝💕

### Output Port（Core側interface）🔌

```csharp
namespace MyApp.UseCases.CreateMemo;

public interface ICreateMemoOutputPort
{
    void PresentSuccess(CreateMemoResponse response);
    void PresentFailure(MyApp.Core.Error error);
}

public sealed record CreateMemoResponse(Guid MemoId, string Title);
```

---

## 例：Interactor（UseCase実装）での“失敗の運び方”🧱🌊

### まず：RepositoryはCore側interface（もう作ってある想定）🗄️

```csharp
namespace MyApp.UseCases;

public interface IMemoRepository
{
    Task<bool> ExistsTitleAsync(string title, CancellationToken ct);
    Task<Guid> CreateAsync(string title, CancellationToken ct);
}
```

### Interactor：想定内はErrorで返す／想定外は捕まえてUnexpectedへ🧯

```csharp
namespace MyApp.UseCases.CreateMemo;

using MyApp.Core;

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
        // ① 想定内：入力チェック（Validation）
        if (string.IsNullOrWhiteSpace(request.Title))
        {
            _output.PresentFailure(
                Error.Validation("memo.title.empty", "タイトルは必須だよ📝")
            );
            return;
        }

        if (request.Title.Length > 50)
        {
            _output.PresentFailure(
                Error.Validation("memo.title.too_long", "タイトルが長すぎるよ〜💦（50文字まで）")
            );
            return;
        }

        try
        {
            // ② 想定内：競合（Conflict）
            if (await _repo.ExistsTitleAsync(request.Title, ct))
            {
                _output.PresentFailure(
                    Error.Conflict("memo.title.duplicate", "同じタイトルのメモがあるよ⚔️")
                );
                return;
            }

            // ③ 成功
            var id = await _repo.CreateAsync(request.Title, ct);
            _output.PresentSuccess(new CreateMemoResponse(id, request.Title));
        }
        catch (OperationCanceledException)
        {
            // キャンセルはそのまま投げてOK（扱いは方針次第）
            throw;
        }
        catch (Exception)
        {
            // ④ 想定外：外部要因/事故（Unexpected）
            // ※ここで例外詳細をMessageに入れないのが安全だよ🛡️
            _output.PresentFailure(
                Error.Unexpected("memo.create.failed", "作成に失敗しちゃった…もう一回試してね🥺")
            );
        }
    }
}

public sealed record CreateMemoRequest(string Title);
```

✅ ここが超重要💖

* **CoreのErrorは“HTTPを知らない”**
* でも `ErrorType` と `Code` があるから、外側で好きに変換できる✨

---

## 外側（Presenter）での変換：APIならProblemDetailsへ 🧾✨

ASP.NET Core では **ProblemDetails を統一フォーマットとして使える**よ〜！
最近は `AddProblemDetails()` を使った設定・統一も案内されてる 🧩 ([Microsoft Learn][1])

### Presenter例（外側）：Error → HTTP/ProblemDetails（ここでやる！）

```csharp
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using MyApp.Core;
using MyApp.UseCases.CreateMemo;

public sealed class CreateMemoPresenter : ICreateMemoOutputPort
{
    public IResult Result { get; private set; } = Results.StatusCode(500);

    public void PresentSuccess(CreateMemoResponse response)
    {
        Result = Results.Created($"/memos/{response.MemoId}", new
        {
            id = response.MemoId,
            title = response.Title
        });
    }

    public void PresentFailure(Error error)
    {
        // ここが「変換所」🚉✨
        Result = error.Type switch
        {
            ErrorType.Validation => Results.BadRequest(ToProblemDetails(error, 400)),
            ErrorType.NotFound   => Results.NotFound(ToProblemDetails(error, 404)),
            ErrorType.Conflict   => Results.Conflict(ToProblemDetails(error, 409)),
            ErrorType.Forbidden  => Results.Forbid(),
            _                    => Results.Problem(title: "Unexpected error", statusCode: 500)
        };
    }

    private static ProblemDetails ToProblemDetails(Error error, int statusCode)
        => new()
        {
            Title = error.Message,
            Status = statusCode,
            Extensions =
            {
                ["code"] = error.Code
            }
        };
}
```

💡補足：

* APIの統一エラー応答をちゃんとやるなら、例外処理ミドルウェア＋ProblemDetails統一がラクだよ🧩 ([Microsoft Learn][1])
* 例外の使い方は「例外的なときに」ってガイドもあるよ（普段の分岐はResultがスッキリしがち） ([Microsoft Learn][3])

---

## ミニ課題（この章のゴール）🎮💖

次の **3種類の失敗** を「Core→外」で通してみてね✨

1. `memo.title.empty`（Validation）📝
2. `memo.title.duplicate`（Conflict）⚔️
3. `memo.create.failed`（Unexpected）💥

✅チェックポイント✅

* UseCaseは **HTTP** を知らない？🙆‍♀️
* 失敗は `Error` として外へ出てる？🙆‍♀️
* 外側で `ErrorType` を見て、レスポンスに変換してる？🙆‍♀️

---

## よくある事故パターン（あるある😭）🩺

* **UseCaseが `ActionResult` を返す** → 外側依存が侵食😵（アウト）
* **Coreで `HttpRequestException` や `DbUpdateException` をそのまま返す/投げる** → 外部詳細が漏れる💦
* **想定内の失敗を例外で投げまくる** → 流れが追いにくい＆パフォ落ちやすい⚠️（例外は例外的に） ([Microsoft Learn][3])
* **例外の詳細をユーザーに返す** → セキュリティ的に危険🛡️（外側でログ、返すのは安全な文言）

---

## AI（Copilot/Codex）に頼むと超ラクなところ 🤖✨

そのままコピペして使える系👇（レビューは必ずね！👀💕）

* 「`Error` と `Result<T>` を **null安全**にして、ユニットテストも付けて」🧪
* 「`ErrorType` → APIレスポンス（ProblemDetails）への変換をPresenterに実装して」🧾
* 「Interactorの `catch` 方針（OperationCanceledExceptionは再throw等）を整えて」🧯

---

## ちょい最新メモ（2026年1月時点）🗒️✨

* .NET は **.NET 10 がLTS**で、2025-11-11開始のライフサイクルが案内されてるよ📅 ([Microsoft Learn][4])
* ASP.NET Core 側の **APIエラーハンドリング**では、ProblemDetailsの統一（`AddProblemDetails()`）などがガイドされてるよ🧩 ([Microsoft Learn][1])

---

## まとめ 💖🎉

* **想定内の失敗**：`Error`（Result）で流す 🌸
* **想定外の事故**：例外を捕まえて `Unexpected` に変換 🧯
* **HTTP/表示**：外側（Presenter/Controller）で変換 🧾✨
* これで **Coreがずっとキレイ**なまま保てるよ〜🧼💖

次の章（27章）は、この型をテンプレ化して「UseCaseを増やしても崩れない」感じにしていこうね📐✨

[1]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling-api?view=aspnetcore-10.0&utm_source=chatgpt.com "Handle errors in ASP.NET Core APIs"
[2]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
[3]: https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions?utm_source=chatgpt.com "Best practices for exceptions - .NET"
[4]: https://learn.microsoft.com/ja-jp/lifecycle/products/microsoft-net-and-net-core?utm_source=chatgpt.com "Microsoft .NET および .NET Core - Microsoft Lifecycle"
