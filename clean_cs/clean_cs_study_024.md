# 第24章：UseCase内の「読み📚」と「書き✍️」って、どう考えるの？🧠✨

この章はね、**UseCase（Interactor）が“手順書”としてキレイに育つコツ**をつかむ回だよ〜！🥰
特に「読み取り（Query）」と「書き込み（Command）」をゴチャ混ぜにしないと、あとから爆速で楽になる💨💖

---

## 1) この章のゴール🎯✨

* UseCaseの中で **「読む」🧐 と「書く」✍️ を分けて設計**できる
* **必要最小のI/O（DBアクセス等）だけ**にして、UseCaseが太らない🍔❌
* 「GetMemo」「UpdateMemo」を **Ports/Models/Interactor で追加**できる✅✨

---

## 2) まず結論💡：読み📚と書き✍️は“目的が別”だから分けて考える😍

### ✅ 書き込み（Command）✍️

* **ルール（不変条件）を守って状態を変える**のが仕事💪
* だから、だいたいこうなる👇

  1. Entityを取得
  2. Entityのメソッドで更新（＝ルールが効く）
  3. 保存
  4. 結果をOutputPortへ

### ✅ 読み取り（Query）📚

* **見たい情報を取り出す**のが仕事👀✨
* ルールで状態を変えないなら、**Entityを無理に作らず投影（Projection）**でOKな場面が多いよ👍
* 例：一覧、検索、詳細表示など

> 現代の .NET は **.NET 10 がLTS**で、C# 14 もそこで動くよ〜🧁（Visual Studio 2026 と .NET 10 SDK で試せる） ([Microsoft Learn][1])
> EF Core 10 も .NET 10 前提で、こちらもLTSだよ🗄️✨ ([Microsoft Learn][2])
> ちなみに 2026/01/13 に .NET 10 の更新も出てるよ📦 ([マイクロソフトサポート][3])

---

## 3) UseCase内のI/O（読み書き）で守る“3つの約束”🤝💖

### 約束①：UseCaseは「手順」に集中🧾✨

* DBの都合（JOINとか最適化）を考え込みすぎない
* ただし **必要な形で取れるように、Gateway/Repositoryのメソッドを“目的ベース”に設計**するのはOK🙆‍♀️

### 約束②：I/Oは“必要最小回数”にする🔌

* 例：Updateで同じIDを何回も取りに行かない
* 例：一覧で1件ずつ追加取得（N+1地獄）を生みやすい形にしない💣

### 約束③：「読む用」「書く用」の出口を分ける（または分けられる形にする）🚪✨

* 初心者のうちは **1つのRepositoryにまとめてもOK**
* でも、慣れてきたら **Read用/Write用を分ける**と爆伸びする📈💕

---

## 4) 実装してみよ〜！🛠️✨（GetMemo / UpdateMemo）

ここでは「メモ帳アプリ」を前提に、UseCaseを2つ追加するよ📒💖
（第23章で作った Repository interface がある想定で進めるね！）

---

# 4-A) まずは “Read（GetMemo）” 📚✨

## ✅ 設計のコツ（Read）

* **見せたい形（ReadModel）で返す**のが気持ちいい😍
* Domain Entity をそのまま返すと、UI都合が入りやすいから注意⚠️

### 例：ReadModel（表示用の形）📦

```csharp
public sealed record MemoDetailReadModel(
    string Id,
    string Title,
    string Body,
    bool IsArchived,
    DateTimeOffset UpdatedAt
);
```

## ✅ Read用Gateway（例）

```csharp
public interface IMemoQueryService
{
    Task<MemoDetailReadModel?> GetDetailAsync(string id, CancellationToken ct);
}
```

> “QueryService”って名前にしておくと、**これは読み取り専門だよ📚**って伝わりやすいよ〜🥰

---

# 4-B) 次に “Write（UpdateMemo）” ✍️🔥

## ✅ 設計のコツ（Write）

* **更新は必ずEntityを通す**（ルールを守るため）🛡️
* RequestModelは必要最小🍱✨
* 「どう更新するか」の判断は UseCase、
  「更新して良いか」の最終判断は Entity（不変条件）💎

---

## 5) 初級向け：Repositoryを1つで始める版（簡単で迷子にならない🥺💖）

### ✅ Write側のRepository（Core側interface）

```csharp
public interface IMemoRepository
{
    Task<Memo?> FindByIdAsync(MemoId id, CancellationToken ct);
    Task SaveAsync(Memo memo, CancellationToken ct);
}
```

### ✅ Read側も同じRepositoryに生やす（最初はアリ！）

```csharp
public interface IMemoRepository
{
    Task<Memo?> FindByIdAsync(MemoId id, CancellationToken ct);
    Task SaveAsync(Memo memo, CancellationToken ct);

    // Read向け（最初はここに置いてOK）
    Task<MemoDetailReadModel?> GetDetailAsync(string id, CancellationToken ct);
}
```

> ただし、ReadModelが増えてくると太りやすいから、後で分離できる形にしておくと安心だよ🫶✨

---

## 6) 中級に一歩：Read と Write を分ける版（UseCaseが育ちやすい🌱💖）

### ✅ Write用（Entityが戻る）

```csharp
public interface IMemoCommandRepository
{
    Task<Memo?> FindByIdAsync(MemoId id, CancellationToken ct);
    Task SaveAsync(Memo memo, CancellationToken ct);
}
```

### ✅ Read用（ReadModelが戻る）

```csharp
public interface IMemoQueryService
{
    Task<MemoDetailReadModel?> GetDetailAsync(string id, CancellationToken ct);
}
```

---

## 7) UseCase（Ports/Models/Interactors）サンプル✨

## 7-A) GetMemo UseCase 📚

### InputPort / Request

```csharp
public interface IGetMemoInputPort
{
    Task HandleAsync(GetMemoRequest request, CancellationToken ct);
}

public sealed record GetMemoRequest(string MemoId);
```

### OutputPort / Response

```csharp
public interface IGetMemoOutputPort
{
    Task PresentAsync(GetMemoResponse response, CancellationToken ct);
}

public sealed record GetMemoResponse(
    bool Found,
    MemoDetailReadModel? Memo
);
```

### Interactor（読み取りは QueryService だけ呼ぶ）

```csharp
public sealed class GetMemoInteractor : IGetMemoInputPort
{
    private readonly IMemoQueryService _query;
    private readonly IGetMemoOutputPort _output;

    public GetMemoInteractor(IMemoQueryService query, IGetMemoOutputPort output)
    {
        _query = query;
        _output = output;
    }

    public async Task HandleAsync(GetMemoRequest request, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(request.MemoId))
        {
            await _output.PresentAsync(new GetMemoResponse(false, null), ct);
            return;
        }

        var memo = await _query.GetDetailAsync(request.MemoId, ct);

        await _output.PresentAsync(
            new GetMemoResponse(memo is not null, memo),
            ct
        );
    }
}
```

---

## 7-B) UpdateMemo UseCase ✍️

### InputPort / Request

```csharp
public interface IUpdateMemoInputPort
{
    Task HandleAsync(UpdateMemoRequest request, CancellationToken ct);
}

public sealed record UpdateMemoRequest(
    string MemoId,
    string NewTitle,
    string NewBody
);
```

### OutputPort / Response

```csharp
public interface IUpdateMemoOutputPort
{
    Task PresentAsync(UpdateMemoResponse response, CancellationToken ct);
}

public sealed record UpdateMemoResponse(
    bool Succeeded,
    string? ErrorMessage
);
```

### Interactor（Entityを取って、Entityメソッドで更新して、保存✨）

```csharp
public sealed class UpdateMemoInteractor : IUpdateMemoInputPort
{
    private readonly IMemoCommandRepository _repo;
    private readonly IUpdateMemoOutputPort _output;

    public UpdateMemoInteractor(IMemoCommandRepository repo, IUpdateMemoOutputPort output)
    {
        _repo = repo;
        _output = output;
    }

    public async Task HandleAsync(UpdateMemoRequest request, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(request.MemoId))
        {
            await _output.PresentAsync(new UpdateMemoResponse(false, "IDが空だよ〜🥺"), ct);
            return;
        }

        var id = new MemoId(request.MemoId);
        var memo = await _repo.FindByIdAsync(id, ct);

        if (memo is null)
        {
            await _output.PresentAsync(new UpdateMemoResponse(false, "メモが見つからないよ〜🔎💦"), ct);
            return;
        }

        // ここが超重要💖：ルールは Entity に効かせる！
        var result = memo.UpdateContent(request.NewTitle, request.NewBody);

        if (!result.Succeeded)
        {
            await _output.PresentAsync(new UpdateMemoResponse(false, result.ErrorMessage), ct);
            return;
        }

        await _repo.SaveAsync(memo, ct);
        await _output.PresentAsync(new UpdateMemoResponse(true, null), ct);
    }
}
```

> ※ Entity側の UpdateContent は「タイトル空禁止」とか「長さ制限」とかを守る場所だよ💎✨
> こうすると UseCase が “if地獄” になりにくい〜🥰

---

## 8) AI（Copilot / Codex）に頼むと捗るポイント🤖✨

### ✅ 使いどころ①：「ReadModelの設計」📦

* 「画面に必要な項目だけ」を列挙してもらう
* 余計なフィールドを削るチェックも頼める✂️

### ✅ 使いどころ②：「Repositoryのメソッド名」🧠

* 「目的ベースになってる？」（例：FindByIdAsync より GetDetailAsync の方が“用途”が伝わる場面もある）

### ✅ 使いどころ③：「I/O増えすぎ監査」🔍

* 「このUseCase、DBアクセス何回？減らせる？」ってレビュー役にする😆

（プロンプト例💬）

```text
このInteractorはClean ArchitectureのUseCaseです。
I/O（Repository呼び出し）が増えすぎないか、責務が混ざってないかレビューして、
改善案を3つください。修正例コードもください。
```

---

## 9) ミニ課題🎮✨（手を動かすと理解が爆伸び！）

### 課題①：GetMemoに「Found=false時の理由」を足す📝

* 例：ID空 / 見つからない で分ける
* ただし **HTTPステータスの話はしない**（Presenterの仕事だよ😉）

### 課題②：UpdateMemoに「Archive」も追加📦

* UpdateMemoRequest に IsArchived を足す？
* それとも UseCase を分けて ArchiveMemo にする？（迷ったら分けるのが安全💖）

### 課題③：Readを“一覧用ReadModel”にする📚

* MemoListItemReadModel（Id, Title, UpdatedAt だけ）みたいにしてみよ〜✨

---

## 10) よくある事故💥（ここだけ避ければ勝ち！🏆）

* ❌ ReadでEntityを返して、UI都合のプロパティがEntityに増える
* ❌ UpdateでEntityを取らずに、DTOをそのままSaveしてルールが抜ける
* ❌ UseCaseが「検索条件の組み立て」や「表示整形」までやり始める
* ❌ Repositoryが“万能化”して、何でも取れる/何でも保存できるAPIになる（地味に崩壊コース😇）

---

## 11) 次章へのつながり💳✨

この章で「読み📚 / 書き✍️」整理できたら、次は **トランザクション境界**だよ〜！🔥
「1ユースケース＝1トランザクション」の感覚を入れると、整合性が超強くなる🛡️💖

---

必要なら、この第24章の内容に合わせて「GetMemo/UpdateMemo のPresenter例」もセットで作るよ🎤✨

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew?utm_source=chatgpt.com "What's New in EF Core 10"
[3]: https://support.microsoft.com/en-us/topic/-net-10-0-update-january-13-2026-64f1e2a4-3eb6-499e-b067-e55852885ad5?utm_source=chatgpt.com ".NET 10.0 Update - January 13, 2026"
