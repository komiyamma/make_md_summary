# 第27章 境界で守る②：API（Web）入口の置き方🌐🚪✨

## この章のゴール🎯

* API の入口（Controller / Minimal API）を **“薄く”** 保てるようになる🙂✨
* 「受信 → 検証 → 変換 → 実行 → 応答」を **型と責務で分けて**、不変条件が壊れない流れを作れる🛡️
* エラー応答を **ProblemDetails** で揃えて、クライアントが扱いやすい API にできる📦✨（RFC 7807 ベース）([Microsoft Learn][1])

---

## 1. まず結論：Controller は“郵便受け”📮でいい✉️

Controller（または Minimal API の handler）は、基本これだけでOK👇😊

1. 受け取る（Model binding）📥
2. 入口の検証（形式・必須・長さ）✅
3. 内部モデルへ変換（DTO → Command → VO）🔁
4. ユースケースを呼ぶ☎️
5. 結果を HTTP 応答へ変換（ProblemDetails / 201 / 200）📤

**ビジネスルール（不変条件の本丸）を Controller に置かない**のがコツです🛡️✨

---

## 2. なぜ“薄い入口”が不変条件に効くの？🧠💡

## 入口が太ると起きがちな事故💥

* Controller が巨大化して「どこで不変条件が守られてるか」分からなくなる😵‍💫
* 同じ検証・同じ変換が複数箇所にコピペされて、片方だけ更新される🌀
* Domain に `HttpContext` や `ModelState` が混ざって汚染される🧼💦

## 逆に、薄くすると嬉しいこと🎁

* 不変条件が **VO / Entity / UseCase** 側に集まる → 壊れにくい🛡️
* 入口の責務が明快 → テストしやすい🧪
* エラー応答が統一される → クライアントが楽🙂✨（ProblemDetails / ValidationProblemDetails）([Microsoft Learn][1])

---

## 3. API入口の“王道分割”🧱✨（おすすめ構造）

たとえばフォルダをこう分けるイメージ👇

* **Presentation**（API）🌐

  * Request DTO / Response DTO
  * Controller（薄く！）
  * エラー → HTTP 変換（ProblemDetails）
* **Application**（ユースケース）🎮

  * Command（入力の意味を固めた型）
  * UseCase（手続きの中心）
* **Domain**（不変条件の本拠地）🏰

  * Value Object（Email, UserName…）
  * Entity / Aggregate
  * ルール（不変条件）

---

## 4. 入口の検証：Controller と Minimal API の最新おすすめ✅✨

## 4.1 Controller の場合（[ApiController] が強い）💪

`[ApiController]` を付けると、モデル検証エラーで **自動的に 400** を返してくれます。なので `if (!ModelState.IsValid)` を手で書かなくてOK🙆‍♀️
しかも既定の 400 は **ValidationProblemDetails**（RFC 7807）になります📦✨([Microsoft Learn][1])

## 4.2 Minimal API の場合（.NET 10 の built-in validation）✨

Minimal API でも **built-in validation** が用意されていて、`AddValidation()` を呼ぶと DataAnnotations の検証が走ります✅
失敗したら **400 が自動で返る**のも嬉しいポイント🙂([Microsoft Learn][2])

---

## 5. ハンズオン題材：会員登録 API で“薄い入口”を作る🎀📮

## 5.1 Request DTO（入口はゆるくてOK）🙂

* 入口では **string のまま** 受けてOK（ここは境界だから！）
* ただし **必須・長さ・形式** みたいな “入口レベル” はここで落とす✅

```csharp
using System.ComponentModel.DataAnnotations;

public sealed record RegisterMemberRequest(
    [Required, EmailAddress] string Email,
    [Required, StringLength(30, MinimumLength = 2)] string UserName
);
```

---

## 5.2 Domain の VO（ここが不変条件の本丸🏰🛡️）

例：Email を「作れた時点で正しい」状態にする✨

```csharp
public sealed record Email
{
    public string Value { get; }

    private Email(string value) => Value = value;

    public static Result<Email> Create(string? raw)
    {
        raw ??= "";
        var v = raw.Trim().ToLowerInvariant();

        if (v.Length == 0) return Result.Fail("Email is required.");
        if (v.Length > 254) return Result.Fail("Email is too long.");
        if (!v.Contains('@')) return Result.Fail("Email format is invalid.");

        return Result.Ok(new Email(v));
    }
}
```

> 入口の `[EmailAddress]` は「入口の形式チェック」
> VO の `Create` は「内部の不変条件（正規化・上限・禁止）」
> こんなふうに **二段構え** にすると堅いです🛡️✨

---

## 5.3 Command（Application に渡す“意味のある型”📦）

```csharp
public sealed record RegisterMemberCommand(Email Email, string UserName);
```

---

## 5.4 Mapper（DTO → Command の変換専用）🔁

「変換に失敗したら ValidationProblem にできる形」で返すのがコツ🙂✨

```csharp
public static class RegisterMemberMapper
{
    public static Result<RegisterMemberCommand, Dictionary<string, string[]>> ToCommand(RegisterMemberRequest req)
    {
        var errors = new Dictionary<string, string[]>();

        var emailR = Email.Create(req.Email);
        if (!emailR.IsSuccess) errors["email"] = new[] { emailR.Error };

        var name = (req.UserName ?? "").Trim();
        if (name.Length < 2) errors["userName"] = new[] { "UserName must be at least 2 chars." };

        if (errors.Count > 0)
            return Result.Fail(errors);

        return Result.Ok(new RegisterMemberCommand(emailR.Value!, name));
    }
}
```

---

## 5.5 Controller（薄い！薄い！薄い！🪶✨）

`[ApiController]` なら、DataAnnotations の失敗は自動 400 に任せてOK✅([Microsoft Learn][1])
ここでは「VO 変換で落ちた分」を `ValidationProblem(...)` で返して揃えます🙂

```csharp
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/members")]
public sealed class MembersController : ControllerBase
{
    private readonly RegisterMemberUseCase _useCase;
    public MembersController(RegisterMemberUseCase useCase) => _useCase = useCase;

    [HttpPost]
    public async Task<IActionResult> Register([FromBody] RegisterMemberRequest req, CancellationToken ct)
    {
        var cmdR = RegisterMemberMapper.ToCommand(req);
        if (!cmdR.IsSuccess)
            return ValidationProblem(cmdR.Error); // ValidationProblemDetails で返せる✨:contentReference[oaicite:5]{index=5}

        var result = await _useCase.Handle(cmdR.Value!, ct);

        if (!result.IsSuccess)
            return Problem(title: result.Error, statusCode: 409); // 例：重複など

        return Created($"/api/members/{result.Value}", new { id = result.Value });
    }
}
```

---

## 6. Minimal API 版（同じ思想でいける）🌿✨

## 6.1 built-in validation を有効化✅

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddValidation(); // .NET 10: Minimal API の built-in validation を有効化:contentReference[oaicite:6]{index=6}

var app = builder.Build();
```

`RegisterMemberRequest` の DataAnnotations が自動で評価され、失敗したら 400 が返ります✅([Microsoft Learn][2])

---

## 6.2 handler（薄い！）🪶

```csharp
app.MapPost("/api/members", async (RegisterMemberRequest req, RegisterMemberUseCase useCase, CancellationToken ct) =>
{
    var cmdR = RegisterMemberMapper.ToCommand(req);
    if (!cmdR.IsSuccess)
        return Results.ValidationProblem(cmdR.Error);

    var result = await useCase.Handle(cmdR.Value!, ct);
    return result.IsSuccess
        ? Results.Created($"/api/members/{result.Value}", new { id = result.Value })
        : Results.Problem(title: result.Error, statusCode: 409);
});
```

---

## 7. エラー応答を“ProblemDetailsで統一”する🧯📦✨

API は、エラーを「機械が読める形」で返すと運用が超ラクです🙂
ASP.NET Core には **ProblemDetails サービス**があって、`AddProblemDetails()` と `UseExceptionHandler()` / `UseStatusCodePages()` を組み合わせる構成が紹介されています📦✨([Microsoft Learn][3])

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
builder.Services.AddProblemDetails(); // ProblemDetails サービス:contentReference[oaicite:9]{index=9}

var app = builder.Build();
app.UseExceptionHandler();  // 例外を ProblemDetails に寄せる:contentReference[oaicite:10]{index=10}
app.UseStatusCodePages();   // body がない 4xx/5xx も ProblemDetails 化しやすい:contentReference[oaicite:11]{index=11}

app.MapControllers();
app.Run();
```

---

## 8. 演習💪🎀（やると一気に身につく！）

## 演習1：Controller を“6行”にするゲーム🪶🎮

* 既存の API を1本選ぶ
* Controller から下記を全部外へ追い出す👇

  * 文字列の正規化（trim/lower）🧼
  * VO 作成（Create）🏰
  * エラー辞書生成📦
  * DB/外部呼び出し📡
* Controller に残すのは

  * 受ける / Mapper呼ぶ / UseCase呼ぶ / 応答に変換
    だけ✨

## 演習2：同じ API を Minimal API でも作る🌿

* `AddValidation()` を入れて、Request DTO を DataAnnotations 付きで作る✅([Microsoft Learn][2])
* 変換失敗は `Results.ValidationProblem(...)` で返す🙂

## 演習3：ProblemDetails の統一📦✨

* `AddProblemDetails()` + `UseExceptionHandler()` + `UseStatusCodePages()` を入れる🧯([Microsoft Learn][3])
* 400/409/500 のレスポンス形が揃うか Postman/Swagger で確認👀

---

## 9. AI活用コーナー🤖✨（入口が薄いほどAIが効く！）

Copilot / Codex に投げると強いプロンプト例👇

* 「この Request DTO に必要な DataAnnotations を提案して✅」
* 「DTO → Command 変換の Mapper を、エラー辞書（string→string[]）で返す形で書いて🙂」
* 「この UseCase の失敗を ProblemDetails に変換するポリシー案を3つ出して⚖️」
* 「この API の境界値テスト（最小/最大/空/形式）を列挙して🧪」

---

## 10. よくある落とし穴⚠️😵‍💫（ここだけ避ければ勝ち）

* ❌ Controller で VO を作らず string を Domain に渡す（不変条件が漏れる）
* ❌ Domain が `HttpContext` / `ModelState` を知ってしまう（汚染）
* ❌ エラー形式がバラバラ（クライアントが毎回つらい）
* ✅ `[ApiController]` の自動 400（ValidationProblemDetails）を活かす([Microsoft Learn][1])
* ✅ Minimal API は `AddValidation()` を入れて built-in validation を活かす([Microsoft Learn][2])

---

## まとめ🏁🎉

* API入口は「郵便受け」📮
* 不変条件は「Domain」🏰
* 入口は「受信→検証→変換→実行→応答」だけにして薄く🪶
* エラーは ProblemDetails で揃えると、運用もクライアントも楽🙂📦([Microsoft Learn][3])

---

次の章（第28章）は「外部API/DBの“汚れ”を中に入れない」なので、今回作った **Mapper/変換層** がそのまま主役になるよ🧼🧱✨

[1]: https://learn.microsoft.com/en-us/aspnet/core/web-api/?view=aspnetcore-10.0 "Create web APIs with ASP.NET Core | Microsoft Learn"
[2]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis?view=aspnetcore-10.0 "Minimal APIs quick reference | Microsoft Learn"
[3]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling-api?view=aspnetcore-10.0 "Handle errors in ASP.NET Core APIs | Microsoft Learn"
