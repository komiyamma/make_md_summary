# 第38章：違反パターン診断（よくある崩れ方）🩺💥🧼

この章は「壊れてから直す」じゃなくて、**壊れる前に匂いで気づける**ようになる回だよ〜！😆🌸
クリーンアーキって、守れてるときは静かだけど、崩れ始めると一気に修羅場になる…ので早期発見が超大事✨

---

## 1) この章でできるようになること 🎯✨

* 「あ、これ崩れ始めてるやつだ😇」を**症状から当てられる**
* 違反を **3種類** に分けて、**最短ルートで直せる**
* “再発防止”のために、**ルールをテストで固定する入口**がわかる（次の章の伏線でもあるよ🧵）

---

## 2) 違反って、だいたいこの3タイプに分かれるよ 🧠🔍

### A. 依存方向違反（内→外を参照しちゃう）➡️❌

例：Domain が EF Core を参照、UseCase が ASP.NET Core 型を参照…みたいなやつ。

### B. 境界の漏れ（変換をサボって外の形が侵入）🫗❌

例：HTTPのDTOやDBモデルが、UseCase/Domainまでそのまま入ってくる。

### C. 責務の越境（「そこでやるな」問題）🏃‍♀️💨❌

例：Controllerが判断しまくる、Presenterがビジネスルールを持つ、Repositoryが巨大化…など。

---

## 3) まず最初にやる「60秒健康診断」⏱️🩺

### ✅ ① “using” を見て一瞬で匂いを嗅ぐ 👃💨

* Core（Entities/UseCases）内にこんなのが出たら黄色信号🚥

  * `Microsoft.AspNetCore.*`
  * `Microsoft.EntityFrameworkCore.*`
  * `System.ComponentModel.DataAnnotations`（※方針によるけど、Domainに持ち込みやすい）
  * `IConfiguration` / `ILogger` の具体実装（Serilog等）
  * `HttpContext` / `ActionResult` / `ControllerBase`

### ✅ ② 参照グラフを機械的に確認（ここが一番強い）🔗✅

CLIでもOK！（Windowsでそのままいけるよ✨）

```powershell
dotnet list .\src\YourApp.Core\YourApp.Core.csproj reference
dotnet list .\src\YourApp.UseCases\YourApp.UseCases.csproj reference
```

* **Core が何か参照してたら**、だいたいアウト寄り😇
* **UseCases が Web/DB を参照してたら**、ほぼアウト😇😇

---

## 4) “よくある崩れ方” 10選 🧨（症状→原因→直し方）

ここからが本番だよ〜！🧸💕

---

### ① Controller が DbContext 直叩き 🗡️🗄️（最頻出）

**症状**：Controllerに `DbContext` が注入されてる／SQLっぽい処理がある
**原因**：境界を飛び越えて「最外周→DB」に直結してる
**直し方**：Controllerは **InputPort呼ぶだけ** に戻す💪

**NG例（ダメ）**

```csharp
[ApiController]
public class MemoController : ControllerBase
{
    private readonly AppDbContext _db;

    public MemoController(AppDbContext db) => _db = db;

    [HttpPost("/memos")]
    public async Task<IActionResult> Create(CreateMemoDto dto)
    {
        _db.Memos.Add(new MemoDbEntity { Title = dto.Title });
        await _db.SaveChangesAsync();
        return Ok();
    }
}
```

**OKの方向性（良い）**：HTTP DTO → RequestModel に変換 → InputPort呼ぶ

```csharp
[ApiController]
public class MemoController : ControllerBase
{
    private readonly ICreateMemoInputPort _inputPort;

    public MemoController(ICreateMemoInputPort inputPort) => _inputPort = inputPort;

    [HttpPost("/memos")]
    public async Task<IActionResult> Create(CreateMemoDto dto)
    {
        var request = new CreateMemoRequest(dto.Title);
        await _inputPort.HandleAsync(request);
        return Ok();
    }
}
```

---

### ② UseCase が `IActionResult` / `HttpContext` を返す 🌐❌

**症状**：Interactorの戻り値が `IActionResult` とかになってる
**原因**：UseCaseが「Webの都合」を知っちゃってる
**直し方**：UseCaseは **OutputPortへ結果を渡す**（表現は外側）🎤

---

### ③ Domain Entity に `[Key]` / `[Table]` / EFの属性が付く 🧼❌

**症状**：Domainに永続化都合が混ざる（DB変更でドメインも揺れる）
**原因**：DBモデルとドメインモデルが同一になってる
**直し方**：DB用は別モデルにして、Adapterでマッピング🔁

---

### ④ UseCase が DBモデル（DbEntity）を受け取る/返す 🧊❌

**症状**：UseCaseの引数や戻り値に `MemoDbEntity` がいる
**原因**：境界の漏れ（変換不足）
**直し方**：UseCaseは Request/ResponseModel に閉じる📦

---

### ⑤ Repository interface が Infrastructure（外側）にある 🏚️❌

**症状**：`Infrastructure/Repositories/IMemoRepository.cs` みたいになってる
**原因**：内側が「出口の形」を定義できてない（依存が逆転してない）
**直し方**：**interfaceはUseCases（またはCore）**、実装は外側✨

---

### ⑥ Presenter がビジネスルールを持つ 🎤🧨

**症状**：Presenter内で「この条件なら更新禁止」とか判断してる
**原因**：責務越境（表示整形係が意思決定してる）
**直し方**：判断はDomain/UseCaseへ戻す🧠

---

### ⑦ Validation が散乱して二重三重になる 🧩🌀

**症状**：ControllerでもUseCaseでもDomainでも同じチェックしてる
**原因**：「形式チェック」と「不変条件」が混ざってる
**直し方**：

* 形式（null/型/フォーマット）は Adapter で止める🛑
* ルール（不変条件）は Domain が守る🚧

---

### ⑧ Domain/UseCase が `DateTime.Now` を直で呼ぶ ⏰😇

**症状**：テストが不安定／時間依存のバグが出る
**原因**：外部依存（時間）が内側に埋め込まれてる
**直し方**：`IClock` を用意して注入（これも依存逆転✨）

```csharp
public interface IClock { DateTimeOffset Now { get; } }

public sealed class SystemClock : IClock
{
    public DateTimeOffset Now => DateTimeOffset.Now;
}
```

---

### ⑨ UseCase が外部HTTPクライアントの具体実装を new する 🌍❌

**症状**：Interactor内で `new HttpClient()` とかやってる
**原因**：差し替え不能＋テスト不能
**直し方**：UseCase側に interface、実装はAdapterへ🚪

---

### ⑩ Core に “便利ライブラリ” が直接入ってくる（例：特定Logger、ORM、DI）🧰❌

**症状**：Coreのcsprojに外部パッケージが増えていく
**原因**：「便利だから」で中心が汚染される
**直し方**：Coreは**純粋C#**に寄せる（必要ならPortを切る）🫶

---

## 5) 実戦ミニ課題：わざと1個違反を作って、治療してみよ🧪🩹✨

### Step 1：わざと違反（Controller→DbContext直叩き）を入れる 😈

* Controllerに `DbContext` 注入
* `Add` と `SaveChangesAsync` を書く

### Step 2：どこが悪いか「言葉で診断」🗣️

* 「依存方向違反？境界漏れ？責務越境？」を1つ選んで説明✍️

### Step 3：治療 🩺✨

* ControllerはInputPortだけ呼ぶ
* DBアクセスはRepository実装（Adapter）へ移動
* UseCaseはRepository interface に依存（内側）へ

---

## 6) “違反を自動で見つける” をちょい味見 🍭🤖

ここから先は次の「自動で守る」章につながるんだけど、入口だけ触っておくね✨
アーキテクチャテスト用ライブラリとして **ArchUnitNET** や **NetArchTest系** が定番だよ（NuGetでも活発に更新されてる）🧪✨ ([NuGet][1])

**ArchUnitNETの“namespace依存チェック”の雰囲気（例）**

```csharp
using ArchUnitNET.Domain;
using ArchUnitNET.Loader;
using ArchUnitNET.Fluent;
using static ArchUnitNET.Fluent.ArchRuleDefinition;

public class ArchitectureTests
{
    private static readonly Architecture Architecture =
        new ArchLoader().LoadAssemblies(
            typeof(YourApp.Core.AssemblyMarker).Assembly,
            typeof(YourApp.UseCases.AssemblyMarker).Assembly
        ).Build();

    [Fact]
    public void Core_Should_Not_Depend_On_Web()
    {
        var rule =
            Types().That().ResideInNamespace("YourApp.Core", true)
                .Should().NotDependOnAny(
                    Types().That().ResideInNamespace("Microsoft.AspNetCore", true));

        rule.Check(Architecture);
    }
}
```

この書き味（`NotDependOnAny`）は公式ガイドにも載ってるよ🧁 ([ArchUnitNET][2])

---

## 7) Copilot / Codex に頼むと強い “診断プロンプト” 🧠🤖💬

* 「このクラスの責務はControllerとして適切？やりすぎ箇所を指摘して、薄くする案を出して」
* 「UseCaseから外側フレームワーク依存を消したい。依存の発生箇所（using / 型 / NuGet）を列挙して、修正手順を提案して」
* 「DBモデルとDomainモデルが混ざってる。マッピング設計（どこに置くか）を3案出して、メリデメ比較して」

👉 コツ：**“どの層のルールか”を指定**して頼むと、返答の精度が上がるよ〜✨

---

## 8) まとめ 🧡✅

* 違反はだいたい **依存方向 / 境界漏れ / 責務越境** のどれか🎯
* まずは **using** と **参照グラフ** を見るのが最速👀
* よくある崩れ方10個を覚えておくと、事故が「未遂」で止まる🛟
* 自動検出（ArchUnitNET/NetArchTest）は次章以降の武器になる🧪✨ ([NuGet][1])

ちなみに今の最新周辺だと、.NET 10（LTS）と Visual Studio 2026 が同時期に出てて、IDE側もAI支援が強めになってるよ🤖✨ ([Microsoft for Developers][3])

---

次（第39章）に進む前に、もしよければ「あなたの題材」で、今いちばん怪しい違反パターンを1つ選んで教えて〜！😆🔍
（「Controllerが太ってるかも」とか「UseCaseにDTOが入り込んだ」とか、そんなのでOKだよ🫶）

[1]: https://www.nuget.org/packages/TngTech.ArchUnitNET?utm_source=chatgpt.com "TngTech.ArchUnitNET 0.13.1"
[2]: https://archunitnet.readthedocs.io/en/latest/guide/?utm_source=chatgpt.com "User Guide - ArchUnitNET - Read the Docs"
[3]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
