# 第28章：UseCases層の完成チェック ✅🎮📦✨

ここまでで作った UseCases 層（InputPort / RequestModel / Interactor / OutputPort / ResponseModel / Repository interface）が、**“内側だけで成立してるか”**を総点検する章だよ〜！🕵️‍♀️🔍
（2026/01/22時点だと、.NET 10（LTS）＋C# 14＋Visual Studio 2026 が最新の前提でOKだよ✨） ([Versions of .NET][1])

---

## この章のゴール 🎯💖

* UseCases層が **UI/DB/Framework を知らない**状態になってるか確認できる✅
* 「依存が漏れたときの直し方」が分かる🧯✨
* “増やしても崩れない型”のまま、次の層（Adapters）へ進める🚀🎉

---

## まずは合言葉🪄：UseCaseは「手順書」📜✨

UseCase（Interactor）がやるのはだいたいこの3つだけだよ〜👇😊

1. 入力を受け取る（InputPort / RequestModel）📨
2. Entityたちを動かしてルールを適用する🧠⚙️
3. 結果を OutputPort に渡す（表示やHTTPにしない！）🎤📦

> **「画面」「Web」「DB」「外部API」**は全部“外側の都合”だから、UseCases層には持ち込まない🙅‍♀️🚫

---

## 完成チェック：5点セット ✅✅✅✅✅

### ① 参照方向チェック（プロジェクト参照）🧭📌

**UseCasesプロジェクトが参照していい相手**は基本これだけ💡

* Entities（ドメイン）
* UseCases内で定義した interface（Repository / Gateway / OutputPort など）
* （あっても）共通の “Core寄り” な小さなプロジェクト（例：Abstractions）

**絶対NGの例**🙅‍♀️🔥

* Adapters（Web/API/Persistence）プロジェクト参照
* Framework（ASP.NET Core / EF Core / 設定系）プロジェクト参照

Visual Studioなら👀✨

* **UseCases プロジェクト** → **依存関係（Dependencies）** を見て

  * 変な参照（Web/Infrastructure/EF っぽいの）が無いかチェック！

---

### ② パッケージ依存チェック（NuGet）📦🧨

UseCases層に **Microsoft.AspNetCore.*** とか **Microsoft.EntityFrameworkCore.*** が入ってたら、だいたい事故のサイン😇💥
（ASP.NET Core 10 / EF Core 10 は “外側” で使うのが基本） ([Microsoft Learn][2])

CLIで一発チェックするならこれ👇

```bash
dotnet list .\src\MyApp.UseCases\MyApp.UseCases.csproj package --include-transitive
```

見るポイント👀✨

* **UseCasesが直接参照してるパッケージ**に、外側っぽいのが混ざってない？
* **transitive（芋づる）**で入ってくるのも要注意（便利ライブラリ経由で混入しがち😵‍💫）

---

### ③ “禁句”スキャン（名前で見つける）🔎🧹

UseCases層のコードで、こういう単語が出てきたら黄色信号〜！🚥💛

* `Controller` / `IActionResult` / `HttpContext` / `FromBody` など（HTTP）🌐
* `DbContext` / `DbSet` / `Migration` / `EntityTypeBuilder` など（EF）🗄️
* `Configuration` / `IOptions` / `appsettings` など（設定）⚙️
* `HttpClient` 直叩き（外部API直結）🌍⚡

Visual Studioの「検索（Ctrl+Shift+F）」で、文字列検索するだけでも強いよ💪✨
おすすめ検索ワード：
`Microsoft.AspNetCore` / `EntityFrameworkCore` / `DbContext` / `IActionResult` / `HttpContext`

---

### ④ “単独ビルド”できる？（境界の強さ）🏗️✅

UseCases層は **外側無しでもビルドできる**のが理想😍✨
（＝依存が漏れてないってこと）

```bash
dotnet build .\src\MyApp.UseCases\MyApp.UseCases.csproj -c Release
```

もしここで **ASP.NET の型が無い**とか **EF の型が無い**とか言われたら…
→ つまり UseCases層が外側に寄りかかってる🥲💦

---

### ⑤ “Fake差し替え”でUseCaseが動く？（動く完成チェック）🎭🧪

UseCases層の完成チェックでいちばん気持ちいいのがコレ！🥳✨

* Repository を **Fake**（インメモリ）にする
* OutputPort を **Fake Presenter** にする
* Interactor を叩いて、結果が取れる

例：CreateMemo の“テストっぽい最小実行”イメージ👇（雰囲気でOK！）

```csharp
// Fake Repository（インメモリ）
public sealed class InMemoryMemoRepository : IMemoRepository
{
    private readonly Dictionary<string, Memo> _store = new();
    public Task SaveAsync(Memo memo, CancellationToken ct)
    {
        _store[memo.Id.Value] = memo;
        return Task.CompletedTask;
    }
}

// Fake OutputPort（受け取った結果を保持）
public sealed class CapturingPresenter : ICreateMemoOutputPort
{
    public CreateMemoResponse? Response { get; private set; }
    public Task PresentAsync(CreateMemoResponse response, CancellationToken ct)
    {
        Response = response;
        return Task.CompletedTask;
    }
}
```

**ここでの判定基準**は超シンプル😍

* ✅ UseCases層だけで「処理の流れ」が完結してる
* ✅ 外側（HTTP/DB/UI）の都合が1ミリも要らない
* ✅ 失敗ケース（ドメインエラー）も“仕様として”返せる

---

## よくある崩れ方あるある 🧟‍♀️💥 → 直し方 🛠️✨

### あるある①：RequestModelにAPI DTOをそのまま入れちゃう🍱➡️📨

**症状**：`[Required]` とか `JsonPropertyName` とか、外の都合が混入😵‍💫
**直し方**：

* API DTO（外）→ RequestModel（内）へ **変換**を置く（変換はAdapter側で！）🔄✨

---

### あるある②：Interactor内でDbContextを触る🗄️💥

**症状**：`DbContext` が見えてる時点で境界崩壊😂
**直し方**：

* UseCases側：`IMemoRepository` みたいな interface を定義
* 外側：EFで実装してDIで注入🪄✨

---

### あるある③：エラーを例外で投げっぱなし⚠️💣

**症状**：Controllerまで例外が飛び出して、表示がグチャる😇
**直し方**：

* UseCase結果を「成功/失敗」で表現（Result型や専用ResponseでOK）📦
* どう見せるか（HTTP 400/404/500 等）は Presenter/Controller の仕事🎤🌐

---

## “依存チェック”の自動化（ちょい先取り）🤖🔒✨

この章では手動チェックが中心だけど、将来はテストで自動化すると強いよ〜！💪
たとえば **ArchUnitNET** は「アーキテクチャのルールをテストにできる」系ライブラリだよ📐🧪 ([GitHub][3])
（依存ルールをCIで落とすのは後半でめちゃ効くやつ🔥）

---

## ミニ課題（提出イメージ）📝💖

次の3つが揃ったら、この章はクリア🎉✨

1. UseCasesプロジェクトの参照が “内向きだけ” になってる✅
2. `dotnet list package --include-transitive` で外側パッケージが混入してない✅
3. Fake差し替えで Interactor を動かして、結果（成功/失敗）が取れる✅

---

## Copilot / Codex に頼むと捗る魔法のお願い文🤖✨

そのまま投げてOKだよ〜😆💕

* 「UseCases層に `Microsoft.AspNetCore` / `EntityFrameworkCore` 依存が混入してないか、検索ワードとチェック手順を作って！」🔎
* 「CreateMemoInteractor を Fake Repository / Fake Presenter で動かす最小テストを書いて！」🧪
* 「RequestModel と API DTO を分離する変換コード案を出して！ただし変換はAdapter側に置く前提で！」🔄

---

次の章（29章）からは、いよいよ **Controller（入口）** 側に行くよ〜！🚪✨
その前にこの28章で「UseCasesは清い😇」って胸を張れる状態にしておくと、後がめちゃ楽になるよ🥰🎉

[1]: https://versionsof.net/core/10.0/10.0.0/?utm_source=chatgpt.com "NET Core 10.0.0"
[2]: https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/overview?utm_source=chatgpt.com "What's new in .NET 10"
[3]: https://github.com/TNG/ArchUnitNET?utm_source=chatgpt.com "TNG/ArchUnitNET: A C# architecture test library to specify ..."
