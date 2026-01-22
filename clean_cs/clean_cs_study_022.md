# 第22章：Presenter（出力のAdapter）を理解する🎤✨

この章は「**出力を“見せる形”に整えるのは誰？**」をハッキリさせる回だよ〜😊💖
結論から言うと、**UseCaseの結果（ResponseModel）を、画面やAPIレスポンス向け（ViewModel/DTO）に変換する係**がPresenterだよ🎁✨
そして重要ポイントは、**UseCaseは“見せ方”を一切知らない**ってこと！🙅‍♀️

---

## 1) Presenterが必要になる“あるある”😇💥

Presenterがいない/弱いと、こうなりがち👇

* Controllerが肥大化して「なんでも屋」になる😵‍💫
* 返すJSONがエンドポイントごとにバラバラで、フロントが泣く😭
* 画面が増えた時（Web + CLIとか）に同じUseCaseを使い回せない😱
* Domain/Entityをそのまま返して、内部構造が漏れる（事故）💣

Presenterがいると👇

* UseCaseは**“何が起きたか”**だけを出す
* Presenterが**“どう見せるか”**を決める
* 表示やHTTP都合の変更が、UseCaseに波及しにくい✨

この「UseCaseはOutput Port（インターフェース）を呼び、Presenterがそれを実装する」って説明は、Uncle Bobの有名な図のまんまの考え方だよ🧠⭕ ([クリーンコーダーブログ][1])

---

## 2) 位置関係を1枚でイメージ🗺️✨

流れはこう👇（第20〜22章のつながり！）

* Controller：受け取ってUseCase呼ぶだけ🚪
* Interactor：手順を実行する🧱
* Output Port：UseCaseが呼ぶ“出口の約束”🔌➡️
* Presenter：結果をViewModel/DTOへ変換🎤
* View/API：それを返す・表示する🌈

（この「ResponseModel→Presenter→ViewModel」流れは、実装例の説明でもよくこう整理されるよ） ([Plainionist][2])

---

## 3) 似てる言葉の整理（ここ超大事）🧠💡

### ✅ ResponseModel（UseCaseの出力）

* **“業務としての結果”**を表す
* 例：`作成できた（MemoIdがこれ）/ 失敗（タイトル重複）`
* **HTTPコード**や**表示文言**は基本入れない🙅‍♀️

### ✅ ViewModel / Response DTO（見せる用）

* **UI/HTTPの都合に合わせた形**
* 例：`{ id, title, createdAt }`、`errors: []`、`message: "OK!"` など
* どの画面/APIかで形が変わってOK👌

### ✅ Presenter

* ResponseModel → ViewModel/DTO に変換する人🎤✨
* UseCaseはPresenterの“実体”を知らず、**Output Portだけ知る**（依存ルールを守るため！） ([クリーンコーダーブログ][1])

---

## 4) C#ミニ実装：CreateMemoのPresenterを作ってみよう🎮💖

ここでは「メモ作成」を例にするね📝✨
（コードは最小構成で、“Presenterってこう作る”が伝わる形にしてあるよ）

## 4-1) UseCases側：Output Port と ResponseModel（HTTPを知らない）🔌➡️

```csharp
// UseCases（Core側）

public sealed record CreateMemoResponse(
    Guid MemoId,
    string Title,
    bool Success,
    string? ErrorCode = null
);

public interface ICreateMemoOutputPort
{
    Task PresentAsync(CreateMemoResponse response, CancellationToken ct);
}
```

Interactorは処理して、最後にOutput Portを呼ぶだけ👇

```csharp
public sealed class CreateMemoInteractor : ICreateMemoInputPort
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
        // 例：重複チェック（本当はDomainルールと協力してね）
        if (await _repo.ExistsTitleAsync(request.Title, ct))
        {
            await _output.PresentAsync(
                new CreateMemoResponse(Guid.Empty, request.Title, Success: false, ErrorCode: "TITLE_DUPLICATE"),
                ct
            );
            return;
        }

        var memoId = Guid.NewGuid();
        await _repo.SaveAsync(new Memo(memoId, request.Title), ct);

        await _output.PresentAsync(
            new CreateMemoResponse(memoId, request.Title, Success: true),
            ct
        );
    }
}
```

> UseCaseは「HTTP 409にしよ」とか一切言わないよ🙅‍♀️
> そこはPresenterの仕事🎤✨

---

## 4-2) Adapters側：Presenterが“HTTP返却用モデル”に変換する🎁✨

PresenterはOutput Portを実装する（＝約束を守る）形が基本だよ🧩
この「UseCaseが決めたOutput Portを、Presenterが実装する」が王道説明だよ〜 ([クリーンコーダーブログ][1])

```csharp
// Adapters（Web側など）

public sealed record CreateMemoResponseDto(
    string id,
    string title,
    string message
);

public sealed class CreateMemoPresenter : ICreateMemoOutputPort
{
    public int StatusCode { get; private set; } = 500;
    public object? Body { get; private set; }

    public Task PresentAsync(CreateMemoResponse response, CancellationToken ct)
    {
        if (response.Success)
        {
            StatusCode = 201; // Created
            Body = new CreateMemoResponseDto(
                id: response.MemoId.ToString("D"),
                title: response.Title,
                message: "作成できたよ〜✨"
            );
            return Task.CompletedTask;
        }

        // 失敗の見せ方は“外側の都合”でOK👌
        // 例：重複 → 409 Conflict とか
        if (response.ErrorCode == "TITLE_DUPLICATE")
        {
            StatusCode = 409;
            Body = new { error = "同じタイトルがあるよ🥺", code = response.ErrorCode };
            return Task.CompletedTask;
        }

        StatusCode = 400;
        Body = new { error = "入力がだめかも🥲", code = response.ErrorCode };
        return Task.CompletedTask;
    }
}
```

---

## 4-3) Controller（or Minimal API）：Presenterの結果を返すだけ🚪✨

```csharp
// Frameworks/Web（Controller）

[ApiController]
[Route("api/memos")]
public sealed class MemosController : ControllerBase
{
    private readonly ICreateMemoInputPort _input;
    private readonly CreateMemoPresenter _presenter;

    public MemosController(ICreateMemoInputPort input, CreateMemoPresenter presenter)
    {
        _input = input;
        _presenter = presenter;
    }

    [HttpPost]
    public async Task<IActionResult> Create([FromBody] CreateMemoApiRequestDto dto, CancellationToken ct)
    {
        // DTO → RequestModel（第30章の話につながるよ🍱）
        var request = new CreateMemoRequest(dto.title);

        await _input.HandleAsync(request, ct);

        return StatusCode(_presenter.StatusCode, _presenter.Body);
    }
}

public sealed record CreateMemoApiRequestDto(string title);
```

Controllerは「受け取って渡して返す」だけ！薄い！えらい！🥳✨

---

## 5) Presenter設計のコツ3つ🎯💖

### ① “Entityをそのまま返さない”🙅‍♀️💣

内部構造が漏れるし、将来の変更が怖い…！
PresenterでDTOへ変換して守ろう🛡️✨

### ② “UseCaseのResponseModelは安定させる”🧱

ResponseModelは**業務の言葉**で、UI/HTTPの都合を入れないのがキレイ✨
（UseCaseがOutput Portを呼び、Presenterが外側で変換する流れが狙いそのもの） ([クリーンコーダーブログ][1])

### ③ “画面が増える未来に強くなる”📱💻🖥️

同じUseCaseでも、

* Web用Presenter
* CLI用Presenter
  みたいに差し替えできるのが強み💪
  （複数ViewだとPresenterが複数になる話もよく議論されるよ） ([Software Engineering Stack Exchange][3])

---

## 6) ミニ課題（手を動かして覚える）📝✨

### 課題A：成功/失敗の“統一レスポンス形式”を作る🎁

* 成功：`{ data: ..., message: ... }`
* 失敗：`{ error: ..., code: ... }`
* Presenterだけ直して、UseCaseは触らないでね🙆‍♀️✨

### 課題B：GetMemoにもPresenterを付ける🔎

* ResponseModel：`MemoId, Title, Archived` みたいな業務結果
* Presenter：HTTP都合に整形（たとえば `archivedAt` 追加とか）OK👌

### 課題C：Presenterのユニットテストを書く🧪🍰

* 入力：`CreateMemoResponse(...)`
* 出力：`StatusCode` と `Body` が期待通りか確認✨
  Presenterは変換しかしないから、テストが超ラクだよ〜😊

---

## 7) AI（Copilot/Codex）を使うときの“うまい頼み方”🤖✨

### ✅ AIに頼むと速いもの

* PresenterのDTO変換ひな形生成（成功/失敗の分岐）⚡
* テストケース案（境界値、エラーコード別）🧪
* 命名案（Response/DTO/Presenter名）📛

### ❌ AIに任せっぱなしにしないもの

* Entity直返しになってない？（事故りがち💣）
* UseCaseがHTTP用語を持ってない？（`StatusCode` とかがCoreに入るとアウト🙅‍♀️）
* ErrorCodeがUI都合すぎない？（業務の言葉になってる？）🧠

※Visual Studio 2026のリリースノートでも、Copilotまわりの強化が継続的に入ってるよ（2026-01-13に18.2.0、2026-01-20に18.2.1）🧰✨ ([Microsoft Learn][4])
（この章では“AIの使い方そのもの”は主役じゃないけど、補助としてガンガン使ってOKだよ🤖💖）

---

## 8) よくあるミス集（ここ踏むと崩れる）😵‍💫🧨

* ❌ PresenterがUseCaseを参照し始めて循環依存🌀
* ❌ UseCaseのResponseModelが“画面の都合”だらけ（表示文言まみれ）📺
* ❌ ControllerがPresenterをすっ飛ばして整形し始める（肥大化）🍔
* ❌ 例外がそのままHTTP 500で漏れる（ユーザーが困る）🥲

---

## まとめ🎀✨

* Presenterは **ResponseModel → ViewModel/DTO** 変換係🎤
* UseCaseは **“見せ方”を知らない**（依存ルールのため）⭕ ([クリーンコーダーブログ][1])
* Presenterを置くと、Controllerが薄くなって、UI変更に強くなる💪✨

次の章（23章：Gateway/Repository）では、**DBみたいな外部依存の出口**も同じ発想で切っていくよ〜🚪🗄️✨

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
[2]: https://plainionist.github.io/Implementing-Clean-Architecture-Controller-Presenter/?utm_source=chatgpt.com "Implementing Clean Architecture - Of controllers and ..."
[3]: https://softwareengineering.stackexchange.com/questions/420341/what-should-presenters-return-in-clean-architecture?utm_source=chatgpt.com "What should presenters return in Clean Architecture?"
[4]: https://learn.microsoft.com/ja-jp/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 リリース ノート"
