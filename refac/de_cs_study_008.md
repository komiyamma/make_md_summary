# 第8章 （任意）Visual Studio Code版の最小セット💻✨

## 8.0 この章のゴール🎯

Visual Studio Code（VS Code）でも、ミニEC題材のプロジェクトを **作る→動かす→デバッグする→テストする** まで一気に通せるようになります🧪✨
（エディタが違っても、設計の考え方は同じだよ〜🙂🌸）

---

## 8.1 まず入れるもの3点セット📦✨

### ① .NET SDK 🧩

VS CodeでC#を書くときも、実際にビルド/実行するのは **.NET SDK** だよ⌨️✨
.NETのダウンロードページでは、**.NET 10（LTS）** と **.NET 9（STS）** が並んでいて、SDKバージョンとリリース日も確認できます📅 ([Microsoft][1])

### ② Visual Studio Code 📝

いつもどおりVS Code本体を入れてOK👌✨

### ③ C# Dev Kit（拡張機能）🧰✨

VS CodeのC#言語サポートは、基本 **C# Dev Kit** を入れるのが近道だよ💨
C# Dev Kitはソリューション表示・デバッグ・テストの体験を強化してくれます🧭🧪 ([Visual Studio Code][2])

---

## 8.2 .NET SDKが入ってるか確認しよ✅⌨️

VS Codeのターミナル（PowerShell）で、これを打つだけ👇✨

```bash
dotnet --version
dotnet --info
dotnet --list-sdks
```

* `dotnet` が見つからない系のエラーが出たら、まず **SDK未インストール or PATH未反映** が多いよ😵‍💫💦
* いったんVS Codeを再起動すると直ることも多い👌✨

---

## 8.3 VS CodeにC#を“生やす”🌱🧠

### 拡張機能の入れ方（いちばん簡単）✨

1. VS Codeで拡張機能ビューを開く（`Ctrl + Shift + X`）🧩
2. **C# Dev Kit** で検索🔎
3. インストール✅

C# Dev KitがC#言語サポートの入口になっていて、C#ファイルを開いたときにインストールを促されることもあるよ🙂 ([Visual Studio Code][2])

---

## 8.4 「Visual Studioで作ったやつ」をVS Codeで開く🔁📂

やることはシンプル💡

* **フォルダごと開く**（File → Open Folder…）📁✨
* `.sln` / `.slnx` があるルートを開くのが安心だよ🙂

### `.slnx` って何？👀

最近の.NETでは **`.slnx`（XMLのソリューション形式）** を見かけることが増えてるよ📌
`.NET 10` では `dotnet new sln` の既定が `.slnx` になる変更も入っています🧾 ([Microsoft Learn][3])

---

## 8.5 VS Codeだけで“最小プロジェクト”を作って動かす🛠️🏃‍♀️

### 8.5.1 まずはConsoleアプリを1個つくる🎮✨

任意の作業フォルダで👇

```bash
mkdir MiniEc
cd MiniEc

dotnet new console -n MiniEc.App
cd MiniEc.App
dotnet run
```

「Hello, World!」が出たら勝ち〜🏁🎉

---

## 8.6 デバッグ（止めて中を見る）をやる🧪🔍

### 8.6.1 いちばんラクなやり方：Run and Debug から開始▶️🐞

1. 左の「Run and Debug（▶️🐞）」を開く
2. **Run and Debug** を押す
3. 聞かれたら **C#** を選ぶ（起動プロジェクトも選択）
4. ブレークポイント置いて、**F5** で開始✨

この流れは公式のデバッグ手順でも紹介されてるよ🧭 ([Microsoft Learn][4])

### 8.6.2 C# Dev Kitの“動的 launch 構成”が便利✨

C# Dev Kit入りだと、プロジェクトに合わせて **（一時的な）launch構成を作ってデバッグ** できるよ🧠
既存の `launch.json` がある/ないで作り方が少し変わるけど、どちらもVS Code側で案内が出ることが多いよ🙂 ([Visual Studio Code][5])

---

## 8.7 テストもVS Codeで回せる🧪🧁

### 8.7.1 まずはテストプロジェクトを作る🧩

ソリューション直下で、こんな感じ👇（例）

```bash
cd ..  # MiniEc フォルダへ

dotnet new sln -n MiniEc
dotnet sln add MiniEc.App/MiniEc.App.csproj

dotnet new xunit -n MiniEc.Tests
dotnet sln add MiniEc.Tests/MiniEc.Tests.csproj

dotnet add MiniEc.Tests/MiniEc.Tests.csproj reference MiniEc.App/MiniEc.App.csproj

dotnet test
```

* `dotnet new` の基本は公式CLIの説明どおりでOKだよ📘 ([Microsoft Learn][6])
* `dotnet sln` でソリューションにプロジェクト追加/一覧/削除ができるよ🧺 ([Microsoft Learn][7])

### 8.7.2 VS CodeのTest Explorer（ビーカーのアイコン🧪）で実行✨

* 左の **ビーカー🧪** を押すとテスト一覧が出る
* そこからRun/Debugできるよ🥳 ([Visual Studio Code][8])

⚠️テストが出てこない時の超あるある：
**一度ビルドが通ってからテストが表示される** ことがあるよ（Refresh Tests/Buildしてね、というやつ）🧹✨ ([Visual Studio Code][9])

---

## 8.8 よくある詰まりポイント集（ここだけ見てOK）🧯✨

### A) `dotnet` が見つからない😵‍💫

* SDK入れたあと **VS Codeを再起動**
* それでもダメなら **PowerShellを開き直す**（PATH反映待ち）
* 最後に `dotnet --info` で確認✅

### B) F5で「構成がない」っぽいエラーが出る🌀

* Run and Debug → **Run and Debug** から入り直す
* `Debug: Select and Start Debugging` を使って起動先を選び直す
  C# Dev Kitはデバッグ開始の導線がいくつかあるよ🧭 ([Visual Studio Code][5])

### C) テストが見えない👻

* まず **ビルド**（Solution Explorer からBuild、またはRefresh Tests）
* それでも出ないなら、いったん `dotnet test` が通るかターミナルで確認✅
  C# Dev Kitは「ビルドできてること」が前提になることがあるよ🧪 ([Visual Studio Code][9])

---

## 8.9 チェック✅（この章のゴール達成リスト🎀）

* `dotnet --info` が表示できた✅
* VS CodeでC# Dev Kitを入れた✅ ([Visual Studio Code][2])
* `dotnet run` でアプリが動いた✅
* ブレークポイントで止めて、F5でデバッグできた✅ ([Microsoft Learn][4])
* `dotnet test` と Test Explorer の両方でテストが回せた✅ ([Visual Studio Code][8])

[1]: https://dotnet.microsoft.com/en-us/download?utm_source=chatgpt.com "Download .NET (Linux, macOS, and Windows) | .NET"
[2]: https://code.visualstudio.com/docs/languages/csharp?utm_source=chatgpt.com "Installing C# support"
[3]: https://learn.microsoft.com/en-us/dotnet/core/compatibility/10?utm_source=chatgpt.com "Breaking changes in .NET 10"
[4]: https://learn.microsoft.com/en-us/dotnet/core/tutorials/debugging-with-visual-studio-code?utm_source=chatgpt.com "Debug a .NET console application using Visual Studio Code"
[5]: https://code.visualstudio.com/docs/csharp/debugging?utm_source=chatgpt.com "Debugging"
[6]: https://learn.microsoft.com/ja-jp/dotnet/core/tools/dotnet-new?utm_source=chatgpt.com "dotnet new <TEMPLATE> - .NET CLI"
[7]: https://learn.microsoft.com/ja-jp/dotnet/core/tools/dotnet-sln?utm_source=chatgpt.com "dotnet sln コマンド - .NET CLI"
[8]: https://code.visualstudio.com/docs/csharp/testing?utm_source=chatgpt.com "Testing with C# Dev Kit"
[9]: https://code.visualstudio.com/docs/csharp/cs-dev-kit-faq?utm_source=chatgpt.com "C# Dev Kit FAQ"
