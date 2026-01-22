# 第11章：Entity と Value Object の切り分け練習⚖️💎🪪

この章は「ドメインをキレイにする最初の分かれ道」だよ〜！😊✨
Entity と Value Object（VO）をちゃんと分けられるようになると、**コードがスッキリ**して、**変更が怖くなく**なるよ💪🌸

---

## 0) この章でできるようになること🎯✨

* 「これは Entity？それとも VO？」を**理由つきで説明**できる🗣️💡
* 迷いやすいケース（Tag とか Address とか）を**条件で判断**できる🤔✅
* C#で VO を作って、**不変（壊れない）**にできる🔒💎
* Entity を「データ箱」じゃなくて、**ルールを持つ主役**にできる👑✨

---

## 1) 超ざっくり定義（まずはこれだけ覚えよ！）📌😆

### Entity（エンティティ）🪪

* **同一性（Identity）がある**
  例：MemoId が同じなら “同じメモ” ✨
* **時間とともに変わる**（状態・ライフサイクルがある）⏳
* 等価性は「値が同じか」より **“ID が同じか”** が大事
* クリーンアーキの “Entities” は「アプリを超えて使えるビジネスルールの核」って位置づけだよ🧠🔥 ([クリーンコーダーブログ][1])

### Value Object（値オブジェクト）💎

* **同一性がない**（“それが何か” だけが大事）
  例：Title("買い物") は、どれも “同じタイトル” ✨
* **不変（Immutable）**にするのが基本🔒
* 等価性は **“中身（値）が同じか”** が大事
* Microsoft の DDD ガイドでも「VO は identity を持たない」「値で意味を表す」って扱いだよ💡 ([Microsoft Learn][2])

---

## 2) 迷ったときの判断フローチャート🧭🤔

次の順で YES/NO していくと、ほぼ外さないよ〜！😊✨

1. **追跡したい “個体” ですか？（履歴・参照・ライフサイクル）**

   * YES 👉 Entity 🪪
   * NO 👉 次へ

2. **中身が同じなら “同じもの” 扱いでいい？**

   * YES 👉 VO 💎
   * NO 👉 次へ

3. **丸ごと置き換えで困らない？**（部分更新より “差し替え” が自然）

   * YES 👉 VO 💎
   * NO 👉 Entity 寄り🪪

4. **単体で保存・共有・権限・参照される？**

   * YES 👉 Entity 🪪
   * NO 👉 VO 💎（Entity の一部として生きることが多い）

---

## 3) 例：メモアプリ題材で仕分けしてみよ📒✨

### まずは定番の仕分け（迷いにくい）✅

| モノ                    | どっち？     | 理由                       |
| --------------------- | -------- | ------------------------ |
| Memo                  | Entity🪪 | メモは「このメモ」を追跡する（更新・削除・参照） |
| MemoId                | VO💎     | 値として ID を表す（同じ値なら同じ）     |
| Title                 | VO💎     | “タイトルという意味の値”／不変にしたい     |
| Content               | VO💎     | “本文という意味の値”（制約を閉じ込めやすい）  |
| CreatedAt / UpdatedAt | VO💎     | “日時の値”（ルールがあるならVO化）      |
| TagName               | VO💎     | “タグ名という値”／文字列地獄を防ぐ       |

---

## 4) いちばん迷うやつ：Tag は Entity？VO？🏷️😵‍💫

ここ、めちゃ大事！🔥
**「タグをどう扱いたいか」**で結論が変わるよ😊

### A案：Tag = VO（シンプル路線）💎✨

* メモごとに `List<TagName>` を持つ
* 「タグ名」が一致すれば同じ扱い
* タグの “辞書” を持たない
  ✅ 向いてる：個人用メモ／小さめアプリ／まず動くもの作りたいとき

### B案：Tag = Entity（辞書・共有路線）🪪✨

* タグ自体に `TagId` がある
* タグを “マスタ” として管理（名前変更が全メモに反映）
* 人気タグ集計・タグの権限・タグの削除などがある
  ✅ 向いてる：チーム利用／タグが資産になる／分析や共有が強い

**結論：ドメインの仕様で決める！**（どっちも正解になり得る）💡✨

---

## 5) C#で VO を作る（いちばん実用的な形）🛠️💎

VO は「**不変 + 値で等価**」が命！
C# なら `readonly record struct` が作りやすいよ😊✨（record は値ベースの等価を用意しやすい）

### 5-1) まずは DomainException（ルール違反を表す）⚠️

```csharp
public sealed class DomainException : Exception
{
    public string Code { get; }

    public DomainException(string code, string message) : base(message)
        => Code = code;
}
```

### 5-2) MemoTitle（VO）を作る✍️💎

```csharp
public readonly record struct MemoTitle
{
    public string Value { get; }

    private MemoTitle(string value) => Value = value;

    public static MemoTitle Create(string? value)
    {
        value = (value ?? "").Trim();

        if (value.Length == 0)
            throw new DomainException("memo.title.empty", "タイトルは空にできないよ🥺");

        if (value.Length > 50)
            throw new DomainException("memo.title.too_long", "タイトルは50文字までだよ🥺");

        return new MemoTitle(value);
    }

    public override string ToString() => Value;
}
```

### 5-3) TagName（VO）も同じ感じ🏷️💎

```csharp
public readonly record struct TagName
{
    public string Value { get; }

    private TagName(string value) => Value = value;

    public static TagName Create(string? value)
    {
        value = (value ?? "").Trim();

        if (value.Length == 0)
            throw new DomainException("tag.empty", "タグ名は空にできないよ🥺");

        if (value.Length > 20)
            throw new DomainException("tag.too_long", "タグ名は20文字までだよ🥺");

        if (value.Contains(' '))
            throw new DomainException("tag.space", "タグ名にスペースは入れないルールだよ🥺");

        return new TagName(value);
    }

    public override string ToString() => Value;
}
```

> こうしておくと、UseCase や Controller に「文字数チェック」が散らばらないよ〜！🎉✨
> ルールが VO に “封印” される感じ🔒💎

---

## 6) Entity を「主役」にする（データ箱卒業🎓✨）🪪👑

Memo（Entity）は、**振る舞い（メソッド）でルールを守る**のがポイント！
（クリーンアーキ的にも、中心のルールを閉じ込めるイメージだよ🧠🔥 ([クリーンコーダーブログ][1])）

```csharp
public readonly record struct MemoId(Guid Value)
{
    public static MemoId New() => new(Guid.NewGuid());
}

public sealed class Memo
{
    public MemoId Id { get; }
    public MemoTitle Title { get; private set; }
    public string Content { get; private set; } // まずは簡単に。後でVO化もOK💎
    private readonly HashSet<TagName> _tags = new();

    public IReadOnlyCollection<TagName> Tags => _tags;

    private Memo(MemoId id, MemoTitle title, string content)
    {
        Id = id;
        Title = title;
        Content = content ?? "";
    }

    public static Memo CreateNew(MemoTitle title, string content)
        => new(MemoId.New(), title, content);

    public void Rename(MemoTitle newTitle)
        => Title = newTitle; // ルールは MemoTitle 側で保証済み💎

    public void AddTag(TagName tag)
    {
        if (!_tags.Add(tag))
            throw new DomainException("tag.duplicate", "同じタグは2回つけられないよ〜😆");
    }

    public void RemoveTag(TagName tag)
    {
        _tags.Remove(tag);
    }
}
```

---

## 7) 仕分け練習問題（ここで身体に入れる！）🏋️‍♀️✨

### 問1：`EmailAddress` は？📧

* だいたい **VO** 💎
  理由：値として意味があり、同じ値なら同じ扱いが自然。形式ルールも閉じ込めやすい。

### 問2：`Money(Amount, Currency)` は？💰

* ほぼ **VO** 💎
  同じ金額・通貨なら同じ。計算ルールも持てる。

### 問3：`User` は？👤

* ほぼ **Entity** 🪪
  「同じ人」を追跡する（ログイン、権限、履歴…）

### 問4：`Address` は？🏠

* 仕様次第！

  * 注文の配送先 “スナップショット” 👉 VO 💎（値として扱う）
  * 住所帳の “登録住所” 👉 Entity 🪪（管理・履歴・既定住所…）
    こういう説明は Microsoft の DDD ガイドの例とも相性いいよ💡 ([Microsoft Learn][2])

### 問5：`Tag` は？🏷️

* さっきの通り **仕様で変わる**（VO/Entity 両方あり得る）⚖️✨

---

## 8) AI（Copilot / Codex）に手伝わせるやり方🤖✨

AI は「答え」じゃなくて「判断材料づくり」に使うと強いよ💪🌸

### 8-1) 仕分けの壁打ちプロンプト🧠

```text
次のドメイン要素を Entity / Value Object に分類して。
分類だけじゃなくて「なぜ？」も一言ずつ。
迷うものは “仕様AならVO / 仕様BならEntity” みたいに分岐で出して。

要素:
- Memo
- MemoId
- Title
- Tag
- TagName
- Address
- Money
前提: クリーンアーキテクチャの Entities レイヤーに置くモデル。
```

### 8-2) ありがちミス検出プロンプト🩺

```text
この設計（Entity/VO）で、ありがちなミスを10個挙げて。
特に「string地獄」「更新メソッドの散乱」「等価比較ミス」「不変条件の漏れ」を重点に。
```

---

## 9) まとめ：最強の合言葉✨🗝️

* **Entity = “誰？”（IDで追跡）** 🪪
* **VO = “何？”（値そのものが意味）** 💎
* 迷ったら **まず VO 寄り**で作って、必要になったら Entity に昇格でもOK🙆‍♀️✨
* ルールは **VO と Entity に封じ込める**と、外側が平和になるよ🕊️🌸

---

## おまけ：この章の「最新」要素ちょい足し📌✨

* いまの最新は **.NET 10（LTS）**で、C# は **C# 14** が最新だよ〜！🎉
  Microsoft 公式のアナウンス＆ドキュメントでもそうなってるよ📣 ([Microsoft for Developers][3])
* C# 14 は .NET 10 でサポートされる、って明記されてるよ✅ ([Microsoft Learn][4])

---

次は「第12章：貧血ドメインにならないコツ🩸」に行くと、今日の Entity/VO の分け方がさらに効いてくるよ〜！😊💖

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
[2]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/implement-value-objects?utm_source=chatgpt.com "Implementing value objects - .NET"
[3]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
[4]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
