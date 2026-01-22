# 第23章：Gateway / Repository（外部依存の出口）🚪🗄️✨

この章は「DBとか外部サービスの都合」を **UseCaseから切り離す** ための超重要ポイントだよ〜！😊💕

---

## 1) 今日のゴール（ここまでできたら勝ち！）🏁💪

* UseCaseが **DB/EF Core/HTTP** を知らない状態を作れる😌✨
* 「Repository（= Gatewayの一種）」を **Core側に interface として置く理由** を説明できる🗣️
* `interfaceは内側 / 実装は外側` を、コードでスパッとできる🔪✨

この考え方はクリーンアーキの「依存は内側へ」ルールのど真ん中だよ〜！([クリーンコーダーブログ][1])

---

## 2) Gateway と Repository って何が違うの？🤔🔌

ざっくりこう！👇

* **Gateway**：外部世界への“出口”ぜんぶ（DB・外部API・ファイル・メール送信など）🌍
* **Repository**：その中でも特に「保存・取得（永続化）」に特化した出口🗄️

つまり、Repositoryは「Gatewayの一種」って理解でOK🙆‍♀️✨

---

## 3) なんでわざわざ interface を挟むの？😵‍💫➡️😆

もしUseCaseがDBを直叩きすると…

* DB都合の変更（カラム追加、テーブル分割、EFの設定変更）が **UseCaseまで波及** 😱
* テストでDBが必要になって、テストが遅い＆つらい😭
* 「やりたいこと（ユースケース）」より「保存の手続き」が主役になってしまう😵

だからこうする👇
**UseCaseは “保存してね” とお願いするだけ**
**保存のやり方は外側が担当** 🎀

Microsoftのクリーンアーキ解説でも「UIはApplication Coreのインターフェイスに依存し、実装はInfrastructureに置く」流れが図で説明されてるよ。([Microsoft Learn][2])

---

## 4) 置き場所ルール（迷子防止マップ）🗺️✨

### ✅ Core（UseCases / Application Core）

* `IMemoRepository` みたいな **interface（ポート）** を置く🧩
* UseCase（Interactor）は **interfaceだけ** を知る😌

### ✅ 外側（Adapters / Infrastructure）

* `EfCoreMemoRepository` みたいな **実装** を置く🛠️
* EF CoreやDbContext、SQLの都合は外側に隔離💅✨
  （EF Core 10は .NET 10 向けで、LTSとしてサポート期間も明記されてるよ）([Microsoft Learn][3])

---

## 5) 図で一発！データの流れ（超だいじ）🧠💡

```text
[Controller / API] 
     ↓（Request変換）
[InputPort] → [Interactor（UseCase）] → [IMemoRepository（interface）]
                                       ↓（DIで差し替え）
                          [EfCoreMemoRepository（外側）] → [DB]
```

UseCaseは **DBを知らない**。知ってるのは `IMemoRepository` だけ😊✨
（これが依存逆転＝DIPの気持ちよさ！）

---

## 6) 実装してみよう（メモアプリ例）📝💕

### 6-1) Coreに interface を置く（Repository = Port）🔌

ポイント：**「汎用にしすぎない」** が超重要！
「このアプリのUseCaseが必要な分だけ」置くのが正解🙆‍♀️

```csharp
// Core / UseCases 側（interface だけ！）
public interface IMemoRepository
{
    Task AddAsync(Memo memo, CancellationToken ct);
    Task<Memo?> GetByIdAsync(MemoId id, CancellationToken ct);
    Task UpdateAsync(Memo memo, CancellationToken ct);
    Task DeleteAsync(MemoId id, CancellationToken ct);
}
```

💡コツ

* `IQueryable` を返さない（EFのにおいが漏れる）🙅‍♀️
* `CancellationToken` を付ける（現代C#のお作法✨）

---

### 6-2) UseCase（Interactor）は interface にだけ依存する🎮

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
        var memo = Memo.Create(request.Title, request.Body); // Domainのルールで生成😊
        await _repo.AddAsync(memo, ct);

        await _output.OkAsync(new CreateMemoResponse(memo.Id.Value), ct);
    }
}
```

ここ、UseCaseに **DbContextが1ミリも出てこない** のが最高ポイント！🥳✨

---

## 7) 外側で実装する（まずはInMemoryで練習）🧪🍭

### 7-1) InMemory実装（テストにも使える！）

```csharp
// Infrastructure / Adapters 側
public sealed class InMemoryMemoRepository : IMemoRepository
{
    private readonly Dictionary<string, Memo> _store = new();

    public Task AddAsync(Memo memo, CancellationToken ct)
    {
        _store[memo.Id.Value] = memo;
        return Task.CompletedTask;
    }

    public Task<Memo?> GetByIdAsync(MemoId id, CancellationToken ct)
    {
        _store.TryGetValue(id.Value, out var memo);
        return Task.FromResult(memo);
    }

    public Task UpdateAsync(Memo memo, CancellationToken ct)
    {
        _store[memo.Id.Value] = memo;
        return Task.CompletedTask;
    }

    public Task DeleteAsync(MemoId id, CancellationToken ct)
    {
        _store.Remove(id.Value);
        return Task.CompletedTask;
    }
}
```

✅ これがあると、DBなしでUseCaseテストができるようになるよ（後の章で大活躍！）🎉

---

## 8) EF Coreで実装するときの“安全ルール”🧯✨

EF Core 10（.NET 10向けLTS）を使うなら、重要なのはこれ👇 ([Microsoft Learn][3])

* **DomainモデルにEF属性を付けない**（Coreを汚さない）😌
* DB用Entity（永続化モデル）を別に作って **マッピングで吸収** する（第34章につながる！）🔁
* Repositoryの戻り値は **Domain型 or UseCaseのResponse用モデル**（EF依存の型を返さない）🙅‍♀️

---

## 9) 「Repositoryを汎用化しすぎ」問題あるある😇💥

### ❌ ダメになりがち

* `IGenericRepository<T>` を作って、何でも `GetAll()` とか `Query()` とか増えまくる
* 結果、UseCaseが「DB検索の指示書」になっていく…😵‍💫

### ✅ こうすると強い

* **UseCase単位で必要な操作だけ** interface に置く
* 「このメソッド、どのUseCaseが使うの？」って自分に聞く🫶

---

## 10) ミニ課題（手を動かすと一気に理解できるよ！）🎯💖

### 課題A：interfaceを“必要最小限”に削る✂️

* 「この4メソッド、ほんとに今必要？」をチェックして
* いらないのがあれば削ってOK🙆‍♀️（必要になったら後で追加！）

### 課題B：UseCaseを1個追加する➕

* `RenameMemo` を作ってみてね😊
* Repositoryのメソッド追加が必要なら、**追加理由を一言メモ**（超えらい✨）

---

## 11) Copilot / Codex に頼るときの“いい聞き方”🤖💬✨

そのままコピペで使ってOKだよ👇

* 「CreateMemo / RenameMemo のUseCase一覧を渡すので、**必要最小のIMemoRepository** を提案して。汎用化しすぎはNGで、各メソッドの利用UseCaseも書いて」
* 「InMemory実装を作って。**スレッド安全性が必要か** もコメントで判断して」
* 「EF Core実装は、Domainを汚さない方針で。永続化モデルとDomainのマッピング案も出して」

---

## まとめ（ここだけ覚えて帰ってOK）🎒✨

* Repository/Gatewayは **“外部依存への出口”** 🚪
* **interfaceは内側（Core）**、**実装は外側（Infrastructure）** 🧩🛠️([Microsoft Learn][2])
* UseCaseは **DBもEFも知らない** → テストしやすい・変更に強い💪💖
* EF Core 10は .NET 10向けLTSとして整理されてるので、外側に閉じ込める設計がより効くよ✨([Microsoft Learn][3])

次の章（24章）は、このRepositoryを使った「読み書きの考え方」をもっと気持ちよく整理していくよ〜！📚✍️💖

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
[2]: https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures?utm_source=chatgpt.com "Common web application architectures - .NET"
[3]: https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew?utm_source=chatgpt.com "What's New in EF Core 10"
