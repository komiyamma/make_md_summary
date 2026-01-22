# 第31章：Presenterが作る“出力モデル”の設計 📦✨

この章のゴールはこれっ👇😊

* **UseCaseの結果（ResponseModel）を、外側で使いやすい形に変換**できるようになる🎯
* **成功/失敗レスポンスの形をPresenter側で統一**できるようになる🧩
* **「DomainやUseCaseの型が、APIに漏れてない？」を自分で検査**できるようになる🔍✅

> Uncle Bobのクリーンアーキでも「Controller / Presenter / View は外側の層に属し、UseCaseとのやり取りは“モデル（データ構造）”で行う」考え方が示されています。([blog.cleancoder.com][1])

---

## 1) まずは超ざっくり：3つの“モデル”を分ける理由 🧠💡

Presenterの仕事は、ひとことで言うと👇
**「UseCaseの出力を、表示/APIに最適な形へ“翻訳”する」** です🎤✨

ここで混ざりやすい3兄弟を整理しよっ😊

| 名前                   | 置き場所       | 役割             | “絶対に”入れたくないもの          |
| -------------------- | ---------- | -------------- | ---------------------- |
| **ResponseModel**    | UseCases側  | UseCase結果の“事実” | Controller/HTTP/JSON都合 |
| **ViewModel**        | Presenter側 | 画面/APIが使いやすい形  | Domain Entityそのまま      |
| **API Response DTO** | Web側       | wire(通信)の契約    | Domain/UseCaseの型       |

Microsoftの.NETアーキテクチャガイドでも、中心（Application Core）に**Entities/Interfaces/DTO**を置き、外側がそれに依存する形が推奨されています。([Microsoft Learn][2])

---

## 2) Presenter設計の“鉄板ルール” 7つ 🧷✨

### ルール1：ResponseModelは「事実だけ」📌

* ✅ 例：`MemoId`, `CreatedAt`, `Title`
* ❌ ダメ：`StatusCode`, `Locationヘッダ`, `ProblemDetails`, `IResult`

### ルール2：Domain Entityを外へ“そのまま出さない”🧼

* APIに `MemoEntity` を直で返し始めると、将来の変更で詰みやすい😇
* Presenterで「必要な形に投影」しよう✨

### ルール3：成功/失敗の“形”を統一する📦⚖️

* 成功だけDTO、失敗だけ文字列…みたいにバラバラにしない🙅‍♀️
* **Presenterが“返し方のルール”を握る**と、Controllerが激薄になる😊

### ルール4：HTTPの事情は“Presenter以降”でOK🌐

* Web APIの場合、HTTPステータスやProblemDetailsは**外側の関心**。
* だから **Presenterが「HTTP寄りの結果」を作る**のはアリ（PresenterはAdapterだから）👍

### ルール5：エラーは「コード + 詳細 + フィールド」みたいに“構造化”🧱

* 失敗を文字列1本にすると、フロントや別UIで困る🥲
* 後々すごく効くのが **ErrorCode**（例：`ValidationFailed`, `NotFound`, `Conflict`）

### ルール6：DTOは“契約”なので、名前と形を慎重に📝

* DTOは「外部と約束する形」＝変えづらい
* 変わりやすいDomain/UseCaseの都合をDTOへ持ち込まない✨

### ルール7：Presenterは“翻訳専門”🔄

* PresenterにDBアクセス、UseCase呼び出し、ビジネス判断が入ったらアウト🧯
* **変換に徹する**のが美しい😍

---

## 3) 実装の型：ResponseModel → ViewModel → API DTO 🔄📦

題材：`CreateMemo`（メモ作成）でいくよ✍️😊

### 3-1) UseCases：ResponseModel と OutputPort 🧱

```csharp
// UseCases/CreateMemo/CreateMemoResponseModel.cs
public sealed record CreateMemoResponseModel(
    Guid MemoId,
    string Title,
    DateTimeOffset CreatedAt
);

// UseCases/CreateMemo/CreateMemoError.cs
public enum CreateMemoErrorCode
{
    ValidationFailed,
    Conflict,
    NotFound,
    Unknown
}

public sealed record CreateMemoError(
    CreateMemoErrorCode Code,
    string? Detail = null,
    IReadOnlyDictionary<string, string[]>? FieldErrors = null
);

// UseCases/CreateMemo/ICreateMemoOutputPort.cs
public interface ICreateMemoOutputPort
{
    void PresentSuccess(CreateMemoResponseModel response);
    void PresentFailure(CreateMemoError error);
}
```

ポイント🎯

* UseCases側は **HTTPを1ミリも知らない** ✅
* 失敗も「構造化」して、Presenterで使いやすくしておく👌

---

### 3-2) Presenter：ViewModel と “統一された結果” を作る 🎤✨

まずViewModel（UI/APIが欲しい形）を作る👇

```csharp
// Adapters/Presenters/CreateMemo/CreateMemoViewModel.cs
public sealed record CreateMemoViewModel(
    string MemoId,
    string Title,
    string CreatedAtIso
);
```

次に PresenterResult（成功/失敗を同じ入れ物で返す）を作る👇
※Controllerを薄くするための“器”だよ😊

```csharp
// Adapters/Presenters/PresenterResult.cs
public sealed class PresenterResult
{
    public int StatusCode { get; }
    public object? Body { get; }

    private PresenterResult(int statusCode, object? body)
        => (StatusCode, Body) = (statusCode, body);

    public static PresenterResult Created(object body) => new(201, body);
    public static PresenterResult Ok(object body) => new(200, body);
    public static PresenterResult BadRequest(object body) => new(400, body);
    public static PresenterResult NotFound(object body) => new(404, body);
    public static PresenterResult Conflict(object body) => new(409, body);
    public static PresenterResult ServerError(object body) => new(500, body);
}
```

Presenter本体👇

```csharp
// Adapters/Presenters/CreateMemo/CreateMemoPresenter.cs
public sealed class CreateMemoPresenter : ICreateMemoOutputPort
{
    public PresenterResult? Result { get; private set; }

    public void PresentSuccess(CreateMemoResponseModel response)
    {
        var vm = new CreateMemoViewModel(
            MemoId: response.MemoId.ToString("N"),
            Title: response.Title,
            CreatedAtIso: response.CreatedAt.ToString("O")
        );

        Result = PresenterResult.Created(vm);
    }

    public void PresentFailure(CreateMemoError error)
    {
        // ここでは“HTTP向けの形”まで作っちゃう（PresenterはAdapterだからOK）👍
        var problem = new
        {
            type = "https://example.com/problems/create-memo",
            title = "メモ作成に失敗しました",
            detail = error.Detail,
            errorCode = error.Code.ToString(),
            fieldErrors = error.FieldErrors
        };

        Result = error.Code switch
        {
            CreateMemoErrorCode.ValidationFailed => PresenterResult.BadRequest(problem),
            CreateMemoErrorCode.NotFound         => PresenterResult.NotFound(problem),
            CreateMemoErrorCode.Conflict         => PresenterResult.Conflict(problem),
            _                                    => PresenterResult.ServerError(problem)
        };
    }
}
```

ここが気持ちいいポイント😍

* Controllerは **「呼ぶ」→「返す」**だけにできる✨
* 成功も失敗も、Presenterが **同じ型（PresenterResult）**にまとめてくれる📦

---

### 3-3) Web：Controller/Minimal API は“激薄”にする 🚪🪶

```csharp
// Web/Endpoints/CreateMemoEndpoint.cs (例：Minimal API)
app.MapPost("/memos", async (CreateMemoRequestDto dto, ICreateMemoInputPort inputPort, CreateMemoPresenter presenter) =>
{
    await inputPort.HandleAsync(new CreateMemoRequestModel(dto.Title), presenter);

    var result = presenter.Result ?? PresenterResult.ServerError(new { title = "結果がありません" });

    return Results.StatusCode(result.StatusCode, result.Body);
});
```

✅ これでWeb側は「変換ロジック」をほぼ持たない！最高！🎉

---

## 4) “最新の推し”エラー形式：ProblemDetails 🧯✨

今のASP.NET Coreでは **ProblemDetails** を標準化して扱いやすくする流れが強いよ〜😊

* `AddProblemDetails()` でProblemDetails生成をミドルウェアと一緒に扱える
* `IProblemDetailsService` が用意されてる
  …とMicrosoft Learnにまとまっています。([Microsoft Learn][3])

ProblemDetails自体はRFCで標準化されていて（RFC 9457）、APIエラーの“機械可読な形式”として定義されています。([RFC エディタ][4])

さらにMinimal APIでは `TypedResults` / `Results` や `TypedResults.Problem(...)` などレスポンス構築が体系化されていて、**成功/失敗をきれいに表現**できます。([Microsoft Learn][5])

> つまり：Presenterでエラーを“ProblemDetailsっぽい構造”に寄せておくと、Web側で統一しやすいよ〜💡😊

---

## 5) よくある事故💥→こう直す🛠️

### 事故1：UseCaseが `IResult` を返し始める😇

* ❌ UseCasesがWeb依存しちゃう
* ✅ UseCasesは **ResponseModel + OutputPort** だけにする

### 事故2：PresenterがDomain Entityをそのまま返す🧟‍♀️

* ❌ API契約がDomainに引っ張られる
* ✅ ViewModel/DTOに投影（必要な項目だけ）

### 事故3：エラーが文字列だけで、後で地獄👹

* ✅ `ErrorCode` + `Detail` + `FieldErrors` の構造にする

---

## 6) ミニ課題（手を動かそ〜！）🧪💖

### 課題A：CreateMemoの失敗パターンを3つ増やす🧩

* `TitleTooLong`
* `ForbiddenWord`
* `RateLimited`

👉 `CreateMemoErrorCode` を増やして、Presenterの `switch` で返し方を決めてみてね😊

### 課題B：GetMemo（取得）も同じ“返し方”で作る📦

* 成功：`200 OK`（ViewModel）
* 無し：`404 NotFound`（problem構造）

### 課題C：Controllerが“判断”してないかチェック✅

Controllerにこんなのが増えてたら黄色信号🚥

* `if (xxx) return ...` が増殖
* DTO変換が散らばる
* エラー文言がControllerごとに違う

---

## 7) Copilot / Codex の使いどころ（雑に速くする🤖✨）

* 「ResponseModelからViewModelへのマッピング雛形作って」
* 「ErrorCodeごとにHTTPステータス割り当て案を出して」
* 「FieldErrorsの形、フロントで扱いやすい案にして」
* 「このPresenterが“変換だけ”になってるかレビューして」

👀 **ただし！** 最後は人間が「責務が混ざってない？」を必ず見るのがコツだよ😊🧠

---

## 8) まとめチェックリスト✅🎀

* [ ] ResponseModelにHTTP/JSON都合が入ってない
* [ ] Domain EntityがAPIへ漏れてない
* [ ] 成功/失敗がPresenterで同じ流儀に統一されてる
* [ ] Controllerは“呼んで返すだけ”になってる
* [ ] エラーが構造化されてる（Code/Detail/FieldErrors）
* [ ] 将来DTOを変えたくなった時、Presenterが吸収できる

---

### おまけ：2026年1月時点の“.NETの現在地”🧭✨

.NETの1月アップデート情報として **.NET 10.0 / 9.0 / 8.0 の更新（例：10.0.2など）** が案内されています。([Microsoft Dev Blogs][6])

---

次の第32章は **「Validationをどこで止める？（Adapterで止める/Domainで守る）」** だから、
今日作った「失敗の統一ルール」がそのまま効いてくるよ〜！🛑💖

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
[2]: https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures "Common web application architectures - .NET | Microsoft Learn"
[3]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling-api?view=aspnetcore-10.0 "Handle errors in ASP.NET Core APIs | Microsoft Learn"
[4]: https://www.rfc-editor.org/rfc/rfc9457.html?utm_source=chatgpt.com "RFC 9457: Problem Details for HTTP APIs"
[5]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/responses?preserve-view=true&view=aspnetcore-10.0 "Create responses in Minimal API applications | Microsoft Learn"
[6]: https://devblogs.microsoft.com/dotnet/dotnet-and-dotnet-framework-january-2026-servicing-updates/ ".NET and .NET Framework January 2026 servicing releases updates - .NET Blog"
