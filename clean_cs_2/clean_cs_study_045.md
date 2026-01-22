# 第45章：Dependency Ruleを“自動で守る”（アーキテクチャテスト）🔒✅✨

ここまで積み上げたクリーンアーキ、いちばん怖い敵は **「いつの間にか崩れる」** ことです…😱
だから最終章は、人の注意力に頼らず **ルール違反を自動で検知して落とす仕組み** を作ります💪🧪

---

## この章のゴール 🎯💖

* **内側（Core/UseCases）が外側（Web/EF/外部SDK）を参照したら即NG**にできる🚫
* PRの時点で **CIが自動で落として**、崩壊を未然に防げる🚦
* ルールが“文化”じゃなく **“仕組み”** になる🔧✨

※「依存は内側へ」「内側は外側を知らない」はクリーンアーキの憲法だよ〜📜➡️ ([Microsoft Learn][1])

---

## アーキテクチャテストって何？🧠🔍

**コンパイル後のアセンブリ（DLL）を解析して**、
「この層はこの名前空間（やパッケージ）に依存しちゃダメ！」を **テストとして表現**するやり方だよ🧪✨

これをCIに入れると、**違反＝テスト失敗＝マージできない** になる😎🚧

---

## 使える道具（2026年1月時点）🧰✨

代表どころを3つだけ押さえればOK👌

| 選択肢                   | いいところ                                        | 向いてる                                            |
| --------------------- | -------------------------------------------- | ----------------------------------------------- |
| **NetArchTest.Rules** | シンプルで導入が早い。アーキを“自己テスト化”してビルドパイプラインにも組み込みやすい✨ | まず最短で形にしたい人 ([archunitnet.readthedocs.io][2])   |
| **ArchUnitNET**       | ルール表現が強力。**依存サイクル**みたいな検査も書ける🌀              | ルールを増やして育てたい人 ([archunitnet.readthedocs.io][3]) |
| **NDepend（商用）**       | ルール・品質ゲート・レポートが強い。大規模で“見える化”したい時に便利📊        | チーム/大規模/ガチ運用 ([Zenn][4])                        |

この章では **まず NetArchTest で最短ゴール** → 余裕があれば ArchUnitNET も紹介、の順でいくね💨💖

---

## ハンズオン①：NetArchTestで“依存ルール違反を落とす”🧪🚨

### 0) まず「守りたいルール」を3本に絞る🪓✨

最初から盛ると絶対つらいので、まずはこれだけでOK👇

1. **Core（Entities含む）は外側技術に依存しない**（ASP.NET Core / EF Core / HttpClient系 など）🚫
2. **UseCasesはWebに依存しない**（HTTPやControllerを知らない）🚫
3. **AdaptersはCore/UseCasesに依存してOK、でも逆はダメ**（方向を固定）➡️

---

### 1) ArchitectureTests用プロジェクトを追加📦✨

* `MyApp.ArchitectureTests`（xUnit推奨）をソリューションに追加
* `MyApp.Core` / `MyApp.UseCases` / `MyApp.Adapters` / `MyApp.Web` を参照できるようにする（解析対象のDLLが必要）

---

### 2) マーカー型を1個ずつ置く（参照しやすくする）📍🙂

各プロジェクトに1個だけ、空クラスを置くと超便利！

例：Core に `CoreAssemblyMarker` を追加

```csharp
namespace MyApp.Core;

public sealed class CoreAssemblyMarker { }
```

UseCases/Adapters/Webにも同様に `UseCasesAssemblyMarker` などを置くよ👌✨

---

### 3) 依存禁止テストを書く（コピペでOK）🧪💥

まずは **Coreが外側技術に依存してないか** を落とす！

```csharp
using NetArchTest.Rules;
using Xunit;
using MyApp.Core;

public class ArchitectureTests
{
    [Fact]
    public void Core_should_not_depend_on_frameworks_or_drivers()
    {
        var coreAssembly = typeof(CoreAssemblyMarker).Assembly;

        // 「外側っぽい依存」を文字列で列挙（まずはこのくらいでOK）
        string[] forbidden = new[]
        {
            "Microsoft.AspNetCore",
            "Microsoft.EntityFrameworkCore",
            "System.Net.Http",
            "Microsoft.Extensions."
        };

        var result = Types.InAssembly(coreAssembly)
            .ShouldNot()
            .HaveDependencyOnAny(forbidden)
            .GetResult();

        Assert.True(result.IsSuccessful, result.ToString());
    }
}
```

NetArchTestは「アーキをテストで守る」用途を想定していて、ビルドパイプラインにも組み込みやすいよ🧰✨ ([archunitnet.readthedocs.io][2])

---

### 4) UseCases → Web 依存も禁止にする🚫🌐

```csharp
using NetArchTest.Rules;
using Xunit;
using MyApp.UseCases;

public class UseCaseArchitectureTests
{
    [Fact]
    public void UseCases_should_not_depend_on_Web()
    {
        var ucAssembly = typeof(UseCasesAssemblyMarker).Assembly;

        var result = Types.InAssembly(ucAssembly)
            .ShouldNot()
            .HaveDependencyOnAny(new[]
            {
                "MyApp.Web",
                "Microsoft.AspNetCore"
            })
            .GetResult();

        Assert.True(result.IsSuccessful, result.ToString());
    }
}
```

---

### 5) 「違反をわざと作る」→ 落ちるのを確認😈🧪

例えば Core にうっかりこれを書いたら…

```csharp
using Microsoft.EntityFrameworkCore; // ← これが入った瞬間アウトにしたい😇
```

テストが落ちて、**“事故がPRで止まる”** 状態になるよ🚦✨

---

## ハンズオン②：CIで“違反したらマージ不可”にする🚦🧨

GitHub Actionsの例（Windowsランナー）だよ🪟✨
`checkout@v6` が案内されてて、`setup-dotnet` も v5系が現行だよ📌 ([GitHub][5])

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v6

      - name: Setup .NET
        uses: actions/setup-dotnet@v5
        with:
          dotnet-version: '10.0.x'

      - name: Restore
        run: dotnet restore

      - name: Test
        run: dotnet test -c Release --no-build
```

`.NET 10` は `.NET 9` の後継で、LTSとして提供されるよ（最新版の前提にちょうど合う✨） ([Microsoft Learn][6])
C#側も `C# 14` が `.NET 10 SDK` とセットで案内されてるよ📚✨ ([Microsoft Learn][7])

---

## もう一段上：ArchUnitNETで“依存サイクル”も潰す🌀🔨

「名前空間同士がぐるぐる依存しはじめた…😵‍💫」って時に効く！

ArchUnitNETは **Slices（切り分け）** を使って **循環依存の禁止** みたいなルールが書けるよ🧠🌀 ([archunitnet.readthedocs.io][3])

（最初はNetArchTestで十分！増えてきたらArchUnitNETを足すのが安心ルート💖）

---

## AI（Copilot/Codex）に手伝わせるコツ🤖💡

AIはここでめちゃ役立つよ！

* ✅ 「禁止依存リストの候補」を出させる
  例：「Coreに入ったら困る依存（ASP.NET/EF/Logging/Httpなど）を列挙して」
* ✅ 「テスト雛形」を作らせる
  例：「NetArchTest.Rulesで、Core→EF依存禁止、UseCases→Web禁止のxUnitテストを書いて」
* ✅ “落ちた時の修正案”を複数出させる
  例：「この依存違反を解消する設計案を3つ。境界/ポート/移動/抽出で」

ただし最後は人間が、**「その依存は本当に外側か？」** を判断してね😉✨

---

## ミニ課題（15分）⏱️🎀

1. Coreで `System.Net.Http` を使うコードをわざと書く😈
2. テストが落ちるのを確認🧪💥
3. 修正方針を選ぶ👇

   * A：その処理をUseCases/Adaptersへ移動
   * B：Coreに必要なら **interface（Port）** を作って外側実装へ逃がす
4. テストが通るところまで戻す✅✨

---

## よくある落とし穴（ここ避けると勝ち🏆）😇

* **ルールを一気に増やしすぎて地獄** → 最初は「3本」だけ🪓
* **禁止が強すぎて開発が止まる** → “禁止”は段階導入（WARNING期間→ERROR）でもOK🌱
* **Coreに便利クラスを置きすぎて何でも屋になる** → “内側ほど純粋に”を徹底✨ ([Microsoft Learn][1])

---

## まとめ 🎁💖

* クリーンアーキの最後の仕上げは、**アーキを“自動で守る”仕組み** 🔒✅
* **NetArchTestで最短導入** → CIで落とす → 崩壊を未然に防ぐ🧪🚦 ([archunitnet.readthedocs.io][2])
* もっと強くしたくなったら **ArchUnitNETでサイクル潰し** 🌀🔨 ([archunitnet.readthedocs.io][3])
* これで「設計が崩れない学習プロジェクト」が完成だよ〜！おつかれさまっ🥳🎉💖

[1]: https://learn.microsoft.com/ja-jp/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures "一般的な Web アプリケーションアーキテクチャ - .NET | Microsoft Learn"
[2]: https://archunitnet.readthedocs.io/en/stable/guide/ "ArchUnitNET"
[3]: https://archunitnet.readthedocs.io/en/latest/guide/ "ArchUnitNET"
[4]: https://zenn.dev/gkuroki/articles/dotnet10-feature ".NET 10 (C# 14) の新機能をまとめる"
[5]: https://github.com/actions/checkout "GitHub - actions/checkout: Action for checking out a repo"
[6]: https://learn.microsoft.com/ja-jp/dotnet/core/whats-new/dotnet-10/overview?utm_source=chatgpt.com "NET 10 の新機能"
[7]: https://learn.microsoft.com/ja-jp/dotnet/csharp/whats-new/csharp-14 "C# 14 の新機能 | Microsoft Learn"
