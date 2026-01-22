# 第18章：Input Port（入力境界）を設計する🔌⬅️✨

この章は「外側（Controllerとか）から“ユースケースを呼ぶ窓口”をキレイに固定する」回だよ〜！😊🌸
クリーンアーキの狙いは、**ビジネス側（UseCase）が外側の都合を知らない**こと。だから「呼び出し口＝Input Port」が超大事になるんだ🧠🔥
（依存は内側へ、内側は外側の名前すら知らない、が基本ルール！） ([クリーンコーダーブログ][1])

---

## 1) Input Portってなに？（一言で）🚪✨

**Input Port = ユースケースを呼ぶための“契約（interface）”**だよ😊🔌
Controller（外側）は、その契約だけを知っていればOK。
処理の流れはこんな感じ👇

* User → View → Controller
* Controller は **Request（外側のDTO）** を受け取る
* Controller が **RequestModel（ユースケース用）** に変換して
* **Input Port を通して Interactor（UseCase実装）を呼ぶ**
* Interactor は ResponseModel を作り、Output Port 経由で Presenter へ渡す🎤✨ ([Plainionist][2])

---

## 2) なんでInput Portが必要なの？🤔💡

Input Portを「interface」にしておくと、いいことが2つ大きいよ〜！🌟

1. **テストがラク**🧪
   Controllerをテストするとき、Interactorの代わりにスタブ/モックを差し替えられる👍 ([Plainionist][2])

2. **Interface Segregation（必要なものだけ見せる）ができる**✂️
   複数のControllerが同じInteractorを触るときでも、Controllerごとに必要最小のAPIだけ見せられる✨ ([Plainionist][2])

さらに大枠のメリットとして、クリーンアーキは「フレームワーク非依存・テスト容易・UI/DB差し替え容易」を目指す設計で、そのために境界と依存の向きを強制するんだよね🏗️💖 ([クリーンコーダーブログ][1])

---

## 3) Input Port設計のコツ（初心者でも迷わないやつ）🧭✨

### コツA：**“1ユースケース＝1 Input Port”**に寄せる🎯

例：CreateMemo / UpdateMemo / DeleteMemo …
「何でも屋UseCase」にしないのが大事🙅‍♀️💦

### コツB：メソッド名は **動詞＋目的語**が強い💪

* ✅ `HandleAsync(CreateMemoRequest request, ...)`
* ✅ `ExecuteAsync(CreateMemoRequest request, ...)`
* ❌ `Do()` / `Process()`（何するの？ってなる😇）

### コツC：引数は **RequestModel 1個**にするのが扱いやすい📨

引数が増えると呼び出し側が壊れやすいし、拡張もしにくいよ〜💦

### コツD：**外側の型を持ち込まない**（超重要🔥）

Input Port（UseCases側）に入れちゃダメな例👇

* `HttpContext` / `IActionResult` / `ControllerBase`
* EF Core の `DbContext`
* API DTO（Swagger用のやつ）

「外側の都合」はController/Adapter側で止める🛑✨

---

## 4) 実装してみよう（CreateMemo Input Port）🛠️💖

ここからは「メモ作成」を例にするね😊📝
登場人物はこう！

* **Input Port**：Controllerが呼ぶ“入口”🔌
* **RequestModel**：ユースケースが欲しい入力📨
* **Interactor**：Input Portを実装するUseCase本体🧱
* （この章では Output Port は軽く触れるだけ。次の章で濃くやるよ🎤✨）

---

### 4-1) UseCases側に RequestModel を作る📨✨

ポイント：**API DTOじゃなくて、UseCaseが必要な形にする**！

```csharp
namespace MyApp.UseCases.Memos.Create;

public sealed record CreateMemoRequest(
    string Title,
    string Body
);
```

> もし前の章で Value Object（例：`MemoTitle`）を作ってるなら、`string`の代わりにVOを使うともっと強いよ💎😊
> でも「まず形を作る」段階では `string` でもOK！

---

### 4-2) Input Port（interface）を作る🔌⬅️

Controllerはこれだけ知っていればOKにするよ！

```csharp
namespace MyApp.UseCases.Memos.Create;

public interface ICreateMemoInputPort
{
    Task HandleAsync(CreateMemoRequest request, CancellationToken ct = default);
}
```

💡 **CancellationToken** をつけておくと、外側が「キャンセル（通信切れとか）」を伝えられて現代的👍✨

---

### 4-3) Interactor が Input Port を実装する🧱✨

Interactorは「手順書」だから、ここでドメインを呼び出して、保存して、結果を外へ渡す…ってやる😊
（クリーンアーキでは Interactor が RequestModel を受け取って処理して、ResponseModel を Output Port に渡す流れが典型だよ🎤） ([Plainionist][2])

今回は雰囲気が掴める最小骨格👇

```csharp
namespace MyApp.UseCases.Memos.Create;

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
        // 1) ドメイン生成（本当はVOや不変条件でガチガチにする💪）
        var memo = Memo.Create(request.Title, request.Body);

        // 2) 保存
        await _repo.AddAsync(memo, ct);

        // 3) 出力（表示・HTTPは知らない！Output Portへ渡す）
        await _output.PresentAsync(new CreateMemoResponse(memo.Id), ct);
    }
}
```

> 「UseCaseはインフラ詳細に依存しないように、Coreにinterface（抽象）を置いて外側が実装する」が基本方針だよ🧼✨ ([Microsoft Learn][3])

※ `ICreateMemoOutputPort` / `CreateMemoResponse` / `IMemoRepository` は次章以降でしっかり整えるよ😊💕

---

### 4-4) Controller（外側）が Input Port を呼ぶ🚪➡️🔌

ここがこの章のゴール！
Controllerは「受け取って、変換して、呼ぶだけ」😆👍

例：Minimal API風（イメージ）

```csharp
app.MapPost("/memos", async (
    CreateMemoApiRequest dto,
    ICreateMemoInputPort inputPort,
    CancellationToken ct) =>
{
    // DTO -> RequestModel（外→内への変換）
    var request = new CreateMemoRequest(dto.Title, dto.Body);

    await inputPort.HandleAsync(request, ct);

    // 返す形はPresenter側で作る想定（この章では省略）
    return Results.Accepted();
});

public sealed record CreateMemoApiRequest(string Title, string Body);
```

ここでの重要ポイントはこれ👇✨

* Controllerが受け取るのは **API DTO（外側の都合）**
* UseCaseが受け取るのは **RequestModel（内側の都合）**
* 間の変換は **Controllerの責務**（Adapterの仕事） ([Plainionist][2])

---

## 5) ありがちな事故パターン集（先に潰そ😉）💥😇

### ❌ 事故1：Input Portが `IActionResult` を返す

→ UseCaseがHTTPを知っちゃう。境界が崩れる😭

### ❌ 事故2：Input Portに `HttpContext` を渡す

→ もう完全に外側依存💦

### ❌ 事故3：Input Portが “何でも受け取る” 汎用メソッド

例：`HandleAsync(object any)`
→ 型安全が死ぬし、変更に弱い😇

### ❌ 事故4：RequestModelが “DB都合” になってる

例：`DbMemoRow` をRequestにする
→ ドメインがDBの形に引っ張られる🗄️💦

---

## 6) ミニ課題（手を動かすと定着する✍️💖）

### 課題A：Input Portを3つ作る🔌✨

* `IGetMemoInputPort`
* `IUpdateMemoInputPort`
* `IDeleteMemoInputPort`

それぞれ RequestModel を「必要最小限」で設計してみてね😊📨

### 課題B：Controllerを“薄く”する🧻✨

Controller内に `if/else` が増えてきたら黄色信号🚥

* 形式チェック → Adapter（Controller側）
* ルール（不変条件） → ドメイン側
  に寄せるとキレイになるよ💖

---

## 7) セルフチェックリスト✅💯

* [ ] Input Portは `interface` になってる？🔌
* [ ] 引数は RequestModel 1個にまとまってる？📨
* [ ] UseCase側に `HttpContext` / `IActionResult` / EF型が入ってない？🛑
* [ ] Controllerは DTO→RequestModel に変換して呼ぶだけになってる？🚪
* [ ] “何でも屋UseCase” になってない？（1ユースケース1入口）🎯

---

## 8) Copilot / Codex に頼るときのコツ（ズレ防止）🤖✨

そのまま貼れる系の指示文いくよ〜😆🌸

* 「`CreateMemo` の Input Port interface と RequestModel を作って。UseCase層に置き、HTTPやEFの型は絶対に含めないで。」
* 「Controller（Minimal API）側で DTO→RequestModel へ変換する例を書いて。Controllerは薄く、if/else最小にして。」
* 「このInput Port設計が ‘外側依存’ になってないか、違反例を3つ挙げて理由も説明して。」

AIは勢いで **HttpContext混入** とかしがちだから、最後はチェックリストで人間が締めるのがコツだよ✅😊

---

## 9) 今回のまとめ🌈✨

* **Input Portは “UseCaseを呼ぶための契約（interface）”**🔌
* Controllerは **DTO→RequestModelに変換してInput Portを呼ぶだけ**🚪
* これで「外側の変更」がUseCaseに波及しにくくなる🎉
* クリーンアーキの基本目的（分離・テスト容易・外側に引っ張られない）に直結する超重要パーツだよ🏗️💖 ([クリーンコーダーブログ][1])
* いまどきの基盤として .NET 10（LTS）や Visual Studio 2026 がリリース済み、という前提で進めてOKだよ🧰✨ ([Microsoft for Developers][4])

---

次の「第19章 Request Model」で、**“入力データをどこまで整える？”**をもっと具体的にやろうね📨💖😊

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html "Clean Coder Blog"
[2]: https://plainionist.github.io/Implementing-Clean-Architecture-Controller-Presenter/ "
        
        Implementing Clean Architecture - Of controllers and presenters
        
    "
[3]: https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures "Common web application architectures - .NET | Microsoft Learn"
[4]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/ "Announcing .NET 10 - .NET Blog"
