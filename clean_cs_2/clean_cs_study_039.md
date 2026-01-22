# 第39章：Webフレームワークは最外周（Coreは知らない）🌐🧼

この章はひとことで言うと――
**「ASP.NET Core（Web）は“外側の着せ替え”で、中心（Core）はそれを一切知らない」**を体に入れる回です💪✨

---

## 1. この章のゴール🎯✨

読み終わったら、次ができるようになります👇

* 「なんでWebフレームワークは最外周なの？」を自分の言葉で説明できる😊
* **Core（Entities/UseCases）に `Microsoft.AspNetCore.*` を持ち込まない**設計ができる🚫
* ASP.NET Coreの入口を **Adapter（Controller/Minimal API + 変換）** で吸収できる🔄
* “Web以外の入口”（例：Console/Worker）にも同じUseCaseを使い回せる🔁

---

## 2. なぜ「Webは最外周」なの？🤔🌪️

クリーンアーキの超コアはこれ👇
**「依存は内側へ向く」**。内側は外側の存在（名前すら）を知らない。これが“憲法”です📜⚖️ ([blog.cleancoder.com][1])

そして、フレームワークはだいたい **変わりやすい** 😵‍💫

* 新機能が増える
* 破壊的変更が入る
* セキュリティ修正が来る
* 推奨の書き方が変わる

たとえば今どきは **.NET 10（LTS）** が中心で、パッチも定期的に出ます🧯 ([Microsoft][2])
ASP.NET Core 10 も「バリデーション強化」「OpenAPIまわり」など、ちゃんと進化中です🚀 ([Microsoft Learn][3])

だから、**変わりやすいもの（Web）を外に閉じ込めて、変えたくないルール（Core）を守る**のが勝ち筋💖

---

## 3. ありがちな事故パターン（最外周を守れないとこうなる）💥😇

### ❌事故1：UseCaseが `IActionResult` を返す

「表示やHTTPの都合」がUseCaseに混ざって、Web以外の入口に使い回せなくなる🥲

### ❌事故2：Domain/Entityが `HttpContext` を触る

これは完全にアウト🙅‍♀️
“中心のルール”がWebの仕組みに縛られて、テストも再利用も地獄👹

### ❌事故3：Coreに `Microsoft.AspNetCore.*` 参照が生える

依存ルールに反する（内側が外側の名前を知ってしまう）状態です🚨 ([blog.cleancoder.com][1])

---

## 4. 正しい形のイメージ図🧠⭕（ざっくりでOK）

* **Core**：Entities / UseCases（純粋なルール）
* **Adapters**：変換（HTTP⇄UseCase、UseCase⇄表示用モデル）
* **Frameworks（Web）**：ASP.NET Core（ルーティング、DI、ミドルウェア、認証、OpenAPI等）

「Webは入口の一つにすぎない」って感覚が超大事です🌟

---

## 5. “最外周”にWebを閉じるための実装ルール7つ📌✨

### ルール1️⃣：CoreにWeb型を一切入れない🚫

* `HttpRequest`, `HttpContext`, `IActionResult`, `ControllerBase`, 属性（`[FromBody]` 等）…ぜんぶ外側へ🏃‍♀️💨

### ルール2️⃣：Webは「受け取って→変換して→呼ぶ」だけ🍱➡️

* 形式チェック（JSONの形/必須項目）くらいはWeb/Adapter側でOK
* ただし **業務ルール（不変条件）はCoreが守る** 🔒

### ルール3️⃣：UseCase入出力は “Webと無関係のModel” にする📦

* RequestModel / ResponseModel は **アプリ都合**で決める
* HTTPステータスやレスポンス形は外側で決める

### ルール4️⃣：変換はAdapterに寄せて散らさない🧹

* 「DTO→RequestModel」「ResponseModel→APIレスポンス」を一箇所に集める

### ルール5️⃣：DI配線はWeb側（最外周）でやる🧵

* “どの実装を使うか” は外側の責任💡（次章でガッツリ！）

### ルール6️⃣：例外・エラーのHTTP化は外側でやる🌊

* Coreは「失敗＝仕様」を返す
* Webはそれを 400/404/409…に落とす

### ルール7️⃣：Web以外の入口でも同じUseCaseを叩ける設計にする🔁

* Console/Workerに差し替えできたら勝ち🎉

---

## 6. ミニ実装例（Minimal APIで“外側に閉じる”）🧩✨

ここでは「CreateMemo」を例に、**Webは薄く**、変換は外側、UseCaseは純粋…の形を見せます👀💕

### ✅ Web側（最外周）：DTOを受けてRequestModelに変換して呼ぶだけ

```csharp
// Web側のDTO（HTTPの形）: これは外側に置く
public sealed record CreateMemoDto(string Title, string Body);

// ルーティング（最外周）
app.MapPost("/memos", async (
    CreateMemoDto dto,
    ICreateMemoInputPort inputPort,
    ICreateMemoPresenter presenter,
    CancellationToken ct) =>
{
    // DTO -> UseCase RequestModel（変換は外側）
    var request = new CreateMemoRequest(dto.Title, dto.Body);

    await inputPort.HandleAsync(request, presenter, ct);

    // HTTP化（外側の責任）
    return presenter.ToHttpResult();
});
```

ポイント🍀

* `CreateMemoDto` は **HTTP都合**なので外側に置く
* `CreateMemoRequest` は **UseCase都合**なのでCore側（UseCases）
* `ToHttpResult()` は外側のPresenterが持つ（CoreはHTTPを知らない）✨

### ✅ Presenter（Adapter側）：UseCase結果をHTTPに落とす（外側でOK）

```csharp
public interface ICreateMemoPresenter
{
    void PresentSuccess(CreateMemoResponse response);
    void PresentFailure(CreateMemoError error);

    IResult ToHttpResult(); // ← HTTPは外側の都合だから、Presenterに置ける
}

public sealed class CreateMemoPresenter : ICreateMemoPresenter
{
    private IResult? _result;

    public void PresentSuccess(CreateMemoResponse response)
        => _result = Results.Created($"/memos/{response.Id}", new { response.Id });

    public void PresentFailure(CreateMemoError error)
        => _result = error switch
        {
            CreateMemoError.InvalidTitle => Results.BadRequest(new { message = "タイトルが不正だよ🥲" }),
            CreateMemoError.TooLong      => Results.BadRequest(new { message = "長すぎるよ〜💦" }),
            _                            => Results.Problem("予期しないエラー😵‍💫")
        };

    public IResult ToHttpResult() => _result ?? Results.Problem("結果が未設定だよ😇");
}
```

> 「HTTPの形」はPresenter（外側）で自由に決めてOK🎀
> Coreは「成功/失敗の意味」だけ知ってればいい感じ🧠✨

---

## 7. “Webを交換できる”と何が嬉しい？（超体感コーナー）😆🔁

同じUseCaseを、**WebじゃなくてConsoleから呼べたら**勝ちです🏆

* Webが落ちてもバッチ処理は動く
* 入口が増えても中心は安定
* テストが爆速（HTTP不要）

「入口は差し替え可能な“皮”」って感覚が、ここで一気に腹落ちします🍞💕

---

## 8. チェックリスト（この章の完成条件）✅💯

あなたのソリューションを見て、これが全部YESなら勝ち🎉

* [ ] Core/UseCasesプロジェクトに `Microsoft.AspNetCore.*` 参照がない
* [ ] UseCaseは `IResult` / `IActionResult` を返してない
* [ ] Controller/Minimal API は「変換→呼ぶ」しかしてない
* [ ] HTTPステータスやレスポンス形はPresenter/外側にある
* [ ] Web以外の入口（Console/Worker）でも同じUseCaseが呼べそう

---

## 9. Copilot/Codexに頼るとこ🤖💖（使いどころが超うまい）

### 👀 依存漏れ監査

AIにこう頼むと強いです👇

* 「CoreにASP.NET Coreの型が混ざってないか、混ざってたら場所と直し方を指摘して」
* 「Controllerが判断しすぎてたら、薄くするリファクタ案出して」

### 🔄 変換コード量産（DTO→RequestModel）

* ただし **“変換ロジックを散らさない”** ように、置き場所は人間が決めるのがコツ🧠✨

---

## 10. まとめ🍰🌈

* クリーンアーキの核は「依存は内側へ」📌 ([blog.cleancoder.com][1])
* ASP.NET Core（Web）は変わりやすいから **最外周に閉じる** 🌪️ ([Microsoft Learn][3])
* CoreはWebの型も名前も知らない（知らないほど強い）💪
* 入口（Web）はAdapterで吸収して、UseCaseは純粋に保つ🧼✨
* 今どきの基準として .NET 10（LTS）で運用していくのが自然な流れだよ🧯 ([Microsoft][2])

---

次の章（DI）に入ると、「じゃあ外側の実装をどうやって内側に差し込むの？」がスッキリつながります🪄✨

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "Clean Architecture by Uncle Bob - The Clean Code Blog"
[2]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[3]: https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0?view=aspnetcore-10.0&utm_source=chatgpt.com "What's new in ASP.NET Core in .NET 10"
