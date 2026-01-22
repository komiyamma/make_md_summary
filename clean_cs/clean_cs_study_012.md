# 第12章：「貧血ドメイン」にならないコツ🩸✨（Entityに“ルール”を戻す練習）

## この章のゴール🎯💖

読み終わったら、これができるようになります👇

* 「あ、これ貧血ドメインっぽい…🩸」を**匂いで検知**できる👃✨
* ルールを **UseCase / Controller から Entity（＋Value Object）へ**戻せる🔁
* 「どのルールをどこに置く？」を**迷わず判断**できるようになる🧠⚖️

---

## 1) 「貧血ドメイン」ってなに？🩸😵‍💫

超ざっくり言うと👇

* **Entity が “ただの入れ物”**（get/setの袋）になってる
* ルールや計算や状態遷移は、ぜんぶ **Service / UseCase 側に散らばる**
* 結果、オブジェクト指向っぽい見た目なのに、中身は手続き型になりがち

Martin Fowlerも「貧血ドメインは、getter/setterの袋で、振る舞いがほぼ無いのが症状」と説明してます。 ([martinfowler.com][1])
さらに「ドメインモデルのコスト（永続化など）だけ払って、恩恵（複雑なロジック整理）を得られない」って話も出てきます。 ([martinfowler.com][1])

---

## 2) なんで困るの？😇💥（“地味に死ぬ”ポイント）

貧血ドメインが進むと、だいたいこうなります👇

### ① ルールが散らばって、変更が怖い😱🔧

「タイトル空禁止」が

* Controllerにもある
* UseCaseにもある
* 別のServiceにもある
  みたいな感じで増殖🦠

### ② テストが辛い🧪💦

Entityが何もしないから、**UseCaseやServiceのテスト**で全部確認することになる。
でもUseCaseは外部I/Oや分岐が混ざりやすいから、テストの準備が重くなりがち…😵‍💫

### ③ クリーンアーキの中心が弱くなる🥺🧼

クリーンアーキでは **Entitiesが“最も一般的で高レベルなルール”をカプセル化する**って位置づけ。 ([クリーンコーダーブログ][2])
ここが空っぽだと、中心がスカスカになっちゃうのね…🫠

---

## 3) クリーンアーキ的「正しい分担」💡⭕

ここ、超大事ポイント👇

* **Entity / Value Object**：その概念が守るべき**不変条件**・**状態遷移**・**計算**
* **UseCase（Interactor）**：手順の司令塔📣（並べる・呼ぶ・トランザクション境界）
* **Adapter（Controller/Presenter）**：外側の形↔内側の形を変換🔄

Uncle Bobの説明でも、Entitiesは“Enterprise wide business rules（最も中心のルール）”をカプセル化する層だよ、って書かれてます。 ([クリーンコーダーブログ][2])
Microsoftのアーキテクチャガイドでも、ビジネスロジックを中心に置いて、外側詳細は内側に依存する（逆転）って整理がされています。 ([Microsoft Learn][3])

---

## 4) ルールの置き場所：迷わない判断基準⚖️🧭

「これ、Entity？UseCase？」って迷ったら、まずこの3問👇

### Q1：そのルール、**そのEntityの“意味”そのもの**？🪪

例）Memoは「空タイトル禁止」「アーカイブ中は名前変更禁止」
→ **Entity（またはVO）**に置くのが強い💪

### Q2：そのルール、**アプリの都合の手順**？📋

例）「作成後に通知を送る」「プランにより作成数制限」「保存→イベント記録の順序」
→ **UseCase**が強い🎮

### Q3：複数Entityにまたがって、どこにも“自然に所属しない”？🧩

例）「AとBを突き合わせて価格を決める」みたいなやつ
→ 次章の **Domain Service（最後の手段）**候補✨

Fowlerの引用でも「サービス層は“薄く”、ドメイン層にロジックを置く」方向が強調されています。 ([martinfowler.com][1])

---

## 5) ハンズオン：Memoを“貧血→リッチ”へ戻す🔁💖

### 5-1) まず「貧血」な例（よくある）🩸

```csharp
public class Memo
{
    public Guid Id { get; set; }
    public string Title { get; set; } = "";
    public bool IsArchived { get; set; }
}
```

で、ルールはUseCase側へ…👇

```csharp
public sealed class RenameMemoUseCase
{
    private readonly IMemoRepository _repo;

    public RenameMemoUseCase(IMemoRepository repo) => _repo = repo;

    public async Task HandleAsync(Guid memoId, string newTitle)
    {
        if (string.IsNullOrWhiteSpace(newTitle))
            throw new ArgumentException("Title is required.");

        var memo = await _repo.GetAsync(memoId);

        if (memo.IsArchived)
            throw new InvalidOperationException("Archived memo can't be renamed.");

        memo.Title = newTitle;

        await _repo.SaveAsync(memo);
    }
}
```

この時点で匂いチェック👃💨

* Entityが **状態を守ってない**（誰でもTitleを書き換えられる）
* ルールがUseCaseに集中して **コピペ増殖**しやすい
* 「Titleの制約」が **概念の中にない**（外から眺めないと分からない）

---

### 5-2) Step1：Value Objectで「タイトル」を型にする💎

（9章の復習でもあるよ✨）

```csharp
public readonly record struct MemoTitle
{
    public string Value { get; }

    private MemoTitle(string value) => Value = value;

    public static MemoTitle Create(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new ArgumentException("Title is required.");

        if (value.Length > 100)
            throw new ArgumentException("Title is too long.");

        return new MemoTitle(value.Trim());
    }

    public override string ToString() => Value;
}
```

これで **string地獄**から1歩脱出🏃‍♀️💨
「タイトル」って概念にルールが宿る🌱

---

### 5-3) Step2：Entityに“状態変更メソッド”を生やす🌿🪪

ポイントはこれ👇

* setterを閉じる🔒
* 状態遷移はメソッド経由にする🚪
* ルールも一緒に閉じ込める🧼

```csharp
public class Memo
{
    public Guid Id { get; }
    public bool IsArchived { get; private set; }

    private MemoTitle _title;
    public MemoTitle Title => _title;

    private Memo(Guid id, MemoTitle title)
    {
        Id = id;
        _title = title;
    }

    public static Memo CreateNew(MemoTitle title)
        => new Memo(Guid.NewGuid(), title);

    public void Rename(MemoTitle newTitle)
    {
        if (IsArchived)
            throw new InvalidOperationException("Archived memo can't be renamed.");

        _title = newTitle;
    }

    public void Archive()
    {
        if (IsArchived) return;
        IsArchived = true;
    }
}
```

はい、ここで一気に“ドメインっぽさ”が出る〜！😆✨

* 「Renameできる条件」がEntityにある
* UseCaseは“指揮”に専念できる

---

### 5-4) Step3：UseCaseを“薄く”する🎮🧾

```csharp
public sealed class RenameMemoUseCase
{
    private readonly IMemoRepository _repo;

    public RenameMemoUseCase(IMemoRepository repo) => _repo = repo;

    public async Task HandleAsync(Guid memoId, string newTitle)
    {
        var memo = await _repo.GetAsync(memoId);

        // ルールは VO + Entity に任せる
        memo.Rename(MemoTitle.Create(newTitle));

        await _repo.SaveAsync(memo);
    }
}
```

UseCaseがやってるのは👇

* 取ってくる
* Entityに「やって」と頼む（Tell, don’t ask っぽい✨）
* 保存する

これが “薄いUseCase” の基本形だよ〜🥳

---

## 6) テストが気持ちよくなる🧪🍰（中心が強いと、速い）

Entityにルールが入ると、**Entity単体のテスト**が超ラクになります💖

```csharp
using Xunit;

public class MemoTests
{
    [Fact]
    public void ArchivedMemo_CantBeRenamed()
    {
        var memo = Memo.CreateNew(MemoTitle.Create("hello"));
        memo.Archive();

        Assert.Throws<InvalidOperationException>(() =>
            memo.Rename(MemoTitle.Create("new title")));
    }

    [Fact]
    public void Title_CantBeEmpty()
    {
        Assert.Throws<ArgumentException>(() =>
            MemoTitle.Create("   "));
    }
}
```

この“速いテスト”が、設計を守る土台になるよ🛡️✨

---

## 7) よくある落とし穴🕳️😵‍💫（回避ワザ付き）

### 落とし穴①：Entityに「DB都合」が混ざる🗄️🧪

「永続化の都合でpublic setterが必要…」って言い出すと、貧血に戻りやすい🩸
クリーンアーキでは内側は外側の詳細を知らないのが大原則。 ([クリーンコーダーブログ][2])
（DB形状の問題は、Adapter/Infrastructure側で吸収する方向が基本だよ🔄）

### 落とし穴②：UseCaseがまた太る🐷

「Entityに任せる」が増えると、UseCaseは自然にスリムになる。
逆に UseCaseに if が増殖してきたら黄色信号🚥

### 落とし穴③：“なんでもDomain Service”へ逃げる🏃‍♀️💨

それは次章でちゃんと整理するけど、まずは
「Entityに置けないか？」を最後まで粘るのがコツ✨ ([martinfowler.com][1])

---

## 8) AI（Copilot / Codex）に手伝ってもらうコツ🤖✨

AIはめっちゃ便利だけど、**“置き場所の哲学”は人が握る**のが安全👌

使いやすい頼み方例👇（そのままコピペOK💖）

* 「このクラスは貧血ドメイン？匂い（症状）を箇条書きで指摘して😆🩸」
* 「このUseCaseにあるルールを、VO/Entityへ移すリファクタ手順を段階的に出して🔁」
* 「Rename/Archiveの不変条件を洗い出して、xUnitテスト案（Given-When-Then）で出して🧪」
* 「public setterを減らしつつ、外側（永続化/DTO）へ影響を広げない方針で直して🔒」

---

## 9) 章末ミニ課題🎒✨（15〜30分）

### 課題A：タグ重複禁止🏷️🚫

Memoに `AddTag(TagName tag)` を作って、同じタグは追加できないようにしてみよ〜😆
（TagNameはVOにしてね💎）

### 課題B：タイトル変更履歴を残す📜✨（簡易でOK）

Memoに `Rename` したら、`LastRenamedAt` を更新する仕様を追加。
「このルール、Entity？UseCase？」も言語化してみてね🧠⚖️

### 課題C：匂い診断👃💨

自分の既存コード（過去プロジェクトでもOK）で、
「貧血っぽいEntity」を1つ見つけて、どこが匂うか書き出す📝

---

## まとめ🎉💖

* 貧血ドメインは「Entityが入れ物化」して、ルールが外へ散る状態🩸 ([martinfowler.com][1])
* クリーンアーキの中心（Entities）は、最も一般的で高レベルなルールを持つのが本来の姿⭕ ([クリーンコーダーブログ][2])
* コツは **setterを閉じる🔒 / VOで概念を型にする💎 / 状態遷移をメソッド化する🚪**
* するとテストが速くなって、変更が怖くなくなる🧪✨

次章は「Domain Serviceは“最後の手段”🧩」で、Entityに置けないロジックの置き場をキレイに整理するよ〜💖

[1]: https://martinfowler.com/bliki/AnemicDomainModel.html "Anemic Domain Model"
[2]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html "Clean Coder Blog"
[3]: https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures "Common web application architectures - .NET | Microsoft Learn"
