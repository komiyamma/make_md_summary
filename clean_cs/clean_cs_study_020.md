## 第20章：Interactor（UseCase実装）の骨格🧱✨

この章では、**「ユースケースの手順書」をコードにした中心人物＝Interactor**を、迷わず書けるようにします😊💕

---

### この章のゴール🎯💖

* Interactorが **何をやってOK / 何をやっちゃダメ** か言える🗣️✨
* InputPort → Interactor → OutputPort の流れで、**薄くて強いUseCase**が書ける💪
* まずはDBなし（インメモリ）で、CreateMemoInteractor を動かせる🚀

（※ちなみに今の最新は .NET 10 がLTSで、最新パッチも出ています🧡）([Microsoft for Developers][1])
（Visual Studio 2026 側の更新情報も継続的に出ています✨）([Microsoft Learn][2])

---

## 1) Interactorってなに？🧩

Interactorはひとことで言うと…

**「アプリとしての手順」を実行する係**です🧾✨

* 入力（Request）を受け取る
* エンティティ（ドメイン）を使って処理する
* 必要ならリポジトリ（interface）で保存/取得する
* 出力（Response）を OutputPort に渡す（表示は知らない！）🙅‍♀️

クリーンアーキの考え方（Ports & Adapters / Onion / Clean などの流れ）とも相性バッチリです🙂‍↕️✨([Microsoft Learn][3])

---

## 2) Interactorが「やること」✅😺

InteractorがやってOKなのはこのへん👇

* **ユースケースの順序**を決める（例：作成→保存→結果を返す）🧾
* **依存は interface 経由で呼ぶ**（Repo、外部APIクライアントなど）🔌
* **ドメインの振る舞いを呼び出す**（ドメインルールはEntity/VO側へ）👑
* **OutputPortに結果を渡す**（成功/失敗）🎤

---

## 3) Interactorが「やっちゃダメ」❌🙈

ここをやると一気に崩れます…🥲

* HTTPのこと（ステータスコード、ヘッダー、Controllerの都合）🌐❌
* DBの都合（DbContext直叩き、SQL、EF属性）🗄️❌
* 画面表示の都合（ViewModel整形、文字列の見た目調整）🎨❌
* ビジネスルールをInteractorに直書き（＝貧血/手続き肥大の入口）🩸❌

---

# 4) CreateMemoInteractor を「骨格から」作る🧱✨

題材：メモ作成（CreateMemo）📝
ここでは **インメモリ保存**でOKにします（DBは後の章で差し替え！）🔁

---

## 4-1. ファイル構成イメージ📁✨

* Core（中心）

  * UseCases/CreateMemo/

    * CreateMemoRequest
    * CreateMemoResponse
    * ICreateMemoInputPort
    * ICreateMemoOutputPort
    * CreateMemoInteractor
  * Entities/

    * Memo（Entity）
* Adapters（外側）

  * Persistence/

    * InMemoryMemoRepository
  * Presenters/

    * CreateMemoPresenter（OutputPort実装）

---

## 4-2. Core側：Request / Response / Port 定義🔌

### CreateMemoRequest（入力）

```csharp
namespace MyApp.Core.UseCases.CreateMemo;

public sealed record CreateMemoRequest(string Title, string Body);
```

### CreateMemoResponse（出力データ）

```csharp
namespace MyApp.Core.UseCases.CreateMemo;

public sealed record CreateMemoResponse(Guid MemoId, string Title);
```

### InputPort（Interactorが実装する入口）

```csharp
namespace MyApp.Core.UseCases.CreateMemo;

public interface ICreateMemoInputPort
{
    Task HandleAsync(CreateMemoRequest request, CancellationToken ct = default);
}
```

### OutputPort（Presenterが実装する出口）

「成功」「失敗」を分けるのが分かりやすいです😊

```csharp
namespace MyApp.Core.UseCases.CreateMemo;

public interface ICreateMemoOutputPort
{
    Task PresentSuccessAsync(CreateMemoResponse response, CancellationToken ct = default);
    Task PresentFailureAsync(string code, string message, CancellationToken ct = default);
}
```

---

## 4-3. Entity（超シンプル版）👑

本当はVOや不変条件が育っていきますが、骨格の理解が目的なので最小で✨

```csharp
namespace MyApp.Core.Entities;

public sealed class Memo
{
    public Guid Id { get; }
    public string Title { get; private set; }
    public string Body { get; private set; }

    private Memo(Guid id, string title, string body)
    {
        Id = id;
        Title = title;
        Body = body;
    }

    public static Memo Create(string title, string body)
    {
        // ドメインの入口で守る（不変条件の最小例）
        if (string.IsNullOrWhiteSpace(title))
            throw new ArgumentException("Title is required.");

        return new Memo(Guid.NewGuid(), title.Trim(), body ?? "");
    }
}
```

---

## 4-4. Repository interface（Core側に置く）🚪

Interactorは「保存する」けど、どこに保存するかは知らない🤫

```csharp
using MyApp.Core.Entities;

namespace MyApp.Core.UseCases;

public interface IMemoRepository
{
    Task AddAsync(Memo memo, CancellationToken ct = default);
}
```

---

# 5) いよいよ本体：CreateMemoInteractor🧱🔥

ポイントはこれだけです👇

* Requestを受け取る
* Memoを作る（Entity呼ぶ）
* Repoに保存（interface経由）
* OutputPortに渡す（成功/失敗）

```csharp
using MyApp.Core.Entities;
using MyApp.Core.UseCases;

namespace MyApp.Core.UseCases.CreateMemo;

public sealed class CreateMemoInteractor : ICreateMemoInputPort
{
    private readonly IMemoRepository _repo;
    private readonly ICreateMemoOutputPort _output;

    public CreateMemoInteractor(IMemoRepository repo, ICreateMemoOutputPort output)
    {
        _repo = repo;
        _output = output;
    }

    public async Task HandleAsync(CreateMemoRequest request, CancellationToken ct = default)
    {
        // ここで「表示」や「HTTP」には絶対寄らないよ🙂‍↕️✨
        try
        {
            var memo = Memo.Create(request.Title, request.Body);

            await _repo.AddAsync(memo, ct);

            var response = new CreateMemoResponse(memo.Id, memo.Title);
            await _output.PresentSuccessAsync(response, ct);
        }
        catch (ArgumentException ex)
        {
            // 例外を「仕様の失敗」として外へ伝える（後の章で洗練する）🌊
            await _output.PresentFailureAsync("ValidationError", ex.Message, ct);
        }
    }
}
```

✅ これが「Interactorの骨格」です！
“薄いのに、アプリの中心”って感じが出てきます😊💕

---

# 6) 外側：インメモリRepo（Adapters側）🗄️✨

```csharp
using MyApp.Core.Entities;
using MyApp.Core.UseCases;

namespace MyApp.Adapters.Persistence;

public sealed class InMemoryMemoRepository : IMemoRepository
{
    private readonly List<Memo> _store = new();

    public Task AddAsync(Memo memo, CancellationToken ct = default)
    {
        _store.Add(memo);
        return Task.CompletedTask;
    }
}
```

---

# 7) 外側：Presenter（OutputPort実装）🎤✨

ここでは「画面用モデル」を作る担当にします（いまは簡易版）😊

```csharp
using MyApp.Core.UseCases.CreateMemo;

namespace MyApp.Adapters.Presenters;

public sealed class CreateMemoPresenter : ICreateMemoOutputPort
{
    public CreateMemoResponse? Success { get; private set; }
    public (string Code, string Message)? Failure { get; private set; }

    public Task PresentSuccessAsync(CreateMemoResponse response, CancellationToken ct = default)
    {
        Success = response;
        Failure = null;
        return Task.CompletedTask;
    }

    public Task PresentFailureAsync(string code, string message, CancellationToken ct = default)
    {
        Success = null;
        Failure = (code, message);
        return Task.CompletedTask;
    }
}
```

---

# 8) 動かしてみる（超ミニ実行）🚀💖

```csharp
using MyApp.Adapters.Persistence;
using MyApp.Adapters.Presenters;
using MyApp.Core.UseCases.CreateMemo;

var repo = new InMemoryMemoRepository();
var presenter = new CreateMemoPresenter();

var interactor = new CreateMemoInteractor(repo, presenter);

await interactor.HandleAsync(new CreateMemoRequest("はじめてのメモ", "クリーンアーキ楽しい！"));

if (presenter.Success is not null)
{
    Console.WriteLine($"OK: {presenter.Success.MemoId} / {presenter.Success.Title}");
}
else
{
    Console.WriteLine($"NG: {presenter.Failure?.Code} / {presenter.Failure?.Message}");
}
```

---

# 9) よくある事故ポイント🩹😵

* InteractorがDTOやHTTPモデルを受け取りはじめる → **汚染スタート**🥲
* InteractorがDbContextを知る → **交換不能**になりがち🗄️💥
* 「ルール」をInteractorに書き足していく → **肥大化**してテストが辛い🩸
* OutputPortを使わず return で返す → 最初は楽でも、後でPresenter分離が痛い😣

---

# 10) ミニ課題🎒✨（手を動かすやつ！）

1. CreateMemoRequest に「Tags（文字列配列）」を追加してみる🏷️
2. Entity側で「タグは最大5個」を守らせる（不変条件）🚧
3. 失敗したら PresentFailureAsync に流す🌊

---

# 11) AI（Copilot/Codex）活用のコツ🤖💖

* 「Interactorのテンプレ作って」→ **OK**（雛形生成は得意✨）
* でも必ずチェックしてね👇

  * InteractorがHTTP/DBを触ってない？🙅‍♀️
  * ルールがEntity側に寄ってる？👑
  * 依存が interface 経由？🔌

Visual Studio 2026 でも Copilot まわりの更新が続いてるので、補助役としてかなり使いやすいです😊✨([Microsoft Learn][2])

---

もし次に進めるなら、第21章（OutputPort設計）で「Presenterをもっと綺麗に設計する」流れに入ると、ここで作ったInteractorが一気に気持ちよくなりますよ〜😆🎉

[1]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
[2]: https://learn.microsoft.com/ja-jp/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 リリース ノート"
[3]: https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures?utm_source=chatgpt.com "Common web application architectures - .NET"
