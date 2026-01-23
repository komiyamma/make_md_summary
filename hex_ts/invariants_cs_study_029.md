# 第29章 DB制約は“最後の砦”🏰🗄️✨

（テーマ：**アプリでもDBでも**二重に不変条件を守る💪💎）

---

## 1) この章のゴール🎯✨

この章が終わると、こんなことができるようになります😊🌸

* 「この不変条件、**DBで守れる？守れない？**」を判断できる🔍
* DBの代表的な制約（NOT NULL / UNIQUE / CHECK / FK）を“意味つき”で使える🛡️
* EF Coreで **制約をマイグレーションに落とす**基本がわかる🧱
* DB制約エラーを、境界で **ユーザー向けメッセージに変換**できる🙂📣

---

## 2) まず感覚：DB制約は“最後の砦”🏰✨

アプリで型やガードで守ってても、現実はこういうことが起きます😇💦

* バグで「本来通らない値」が保存されちゃう🐛💥
* 別のバッチ/運用SQL/管理画面から “直に” 書き込まれる🧑‍💻🗄️
* 同時実行で「チェックした瞬間はOK」→「保存時にはNG」になる⚔️⏱️

だから、**DB側にもルールを置く**と、データが“腐りにくい”んだよね🍎✨
（これが **Defense in Depth（多重防御）** のイメージ！🛡️🛡️）

---

## 3) 2026/01/20時点の前提（最新確認）🧭✨

この章のサンプルは、今どきの .NET + SQL Server の流れで説明するよ🙂

* .NET 10 系（例：10.0.2 が 2026-01-13 にリリース）([Microsoft][1])
* Visual Studio 2026 は .NET 10 / C# 14 をサポートする流れになってるよ🧰✨ ([Microsoft Learn][2])
* SQL Server 2025 (17.x) は **GA が 2025-11-18**（リリースノートに build と日付が明記）([Microsoft Learn][3])

---

## 4) DB制約って何があるの？🧱🔰

ざっくり「守れる系」を並べるとこんな感じ😊

### A. NOT NULL（空っぽ禁止）🚫🥲

* 「必須項目」をDBでも担保できる
* アプリの nullable 設計とセットで効く（第15章の世界観と相性◎）

### B. UNIQUE（重複禁止）🚫👯

* メールアドレスや外部IDなど「同じの2ついらない！」に最強
* SQL Serverの UNIQUE 制約は、内部的に **ユニークインデックス**が作られて守られるよ([Microsoft Learn][4])

### C. CHECK（範囲・条件のルール）✅🔢

* 例：価格は 0 より大きい、開始日 ≤ 終了日、など
* 「1行の中で完結する条件」が得意（行をまたぐのは苦手）
* CHECK の性質・注意点（NULL が UNKNOWN になって素通り等）も押さえたい([Microsoft Learn][4])

### D. FOREIGN KEY（参照整合性）🔗👨‍👩‍👧‍👦

* 子テーブルが「存在しない親」を参照できないようにする
* カスケード削除など、運用ルールとセットで設計するのが大事🙂([Microsoft Learn][5])

### E. フィルター付き UNIQUE INDEX（条件付きの重複禁止）🪄🧠

* 「ある条件のときだけ一意」を作れる（例：Active のものは1つだけ）
* SQL Server の filtered index は公式ドキュメントあり([Microsoft Learn][6])

---

## 5) どの不変条件をDBで守る？判断ルール🧠✨

迷ったら、まずこの3つでOK！😊💡

### ①「DBだけ見て判断できる？」👀🗄️

* できる → DB制約候補
* 外部APIの状態が必要 → DBだけじゃ無理（アプリ側）

### ②「1行（1レコード）で完結する？」📄

* 1行で完結 → CHECK が得意
* 複数行の合計とか → CHECK は苦手（別の手段へ）

### ③「同時実行で壊れそう？」⚔️⏱️

* 「チェックしてから保存」系は競合で壊れがち
* ここは DB の UNIQUE がめちゃ強い（競合したらDBが止める）💪✨

---

## 6) 例題：サブスク課金の“壊れた状態”→DB制約へ🏗️💳

### 不変条件（例）🧾✨

サブスク（Subscription）を考えるよ🙂

* (I1) UserId は必須（NULLダメ）
* (I2) PlanId は必須
* (I3) PriceCents > 0
* (I4) StartedAt <= EndedAt（EndedAt は null でもOK：継続中）
* (I5) 「Active のサブスクは、ユーザーごとに1つだけ」
* (I6) Subscription は必ず User を参照する（幽霊ユーザー禁止）

このうち DB でやれるのはどれ？って分類すると…👇😊

* NOT NULL：I1, I2
* CHECK：I3, I4（※NULL注意あり）
* FK：I6
* filtered unique index：I5（条件付き一意）

---

## 7) SQL Server でのDB制約サンプル🧱🗄️

（雰囲気が伝わればOK！細かい列名は好きに変えてね😊）

```sql
CREATE TABLE dbo.[User] (
    UserId UNIQUEIDENTIFIER NOT NULL,
    Email NVARCHAR(320) NOT NULL,
    CONSTRAINT PK_User PRIMARY KEY (UserId),
    CONSTRAINT UQ_User_Email UNIQUE (Email)
);

CREATE TABLE dbo.[Subscription] (
    SubscriptionId UNIQUEIDENTIFIER NOT NULL,
    UserId UNIQUEIDENTIFIER NOT NULL,
    PlanId NVARCHAR(50) NOT NULL,
    Status NVARCHAR(20) NOT NULL,  -- 'Active','Canceled','Expired' など
    PriceCents INT NOT NULL,
    StartedAt DATETIME2(0) NOT NULL,
    EndedAt DATETIME2(0) NULL,

    CONSTRAINT PK_Subscription PRIMARY KEY (SubscriptionId),

    CONSTRAINT FK_Subscription_User
        FOREIGN KEY (UserId) REFERENCES dbo.[User](UserId),

    CONSTRAINT CK_Subscription_Price
        CHECK (PriceCents > 0),

    -- EndedAt が NULL のときは継続中としてOKにする形（NULLの扱い注意）
    CONSTRAINT CK_Subscription_DateRange
        CHECK (EndedAt IS NULL OR StartedAt <= EndedAt)
);

-- 「Active はユーザーごとに1つだけ」をDBで担保（条件付き一意）
CREATE UNIQUE INDEX UX_Subscription_Active_OnePerUser
ON dbo.[Subscription](UserId)
WHERE Status = N'Active';
```

### ここで大事ポイント💡😌

* UNIQUE と CHECK は、SQL Server の “制約”としてデータ整合を守る代表格だよ([Microsoft Learn][4])
* filtered index は「一部の行だけに効くインデックス」で、サイズ削減や性能にもメリットがあるよ([Microsoft Learn][6])

---

## 8) EF Core で “DB制約”をコード側に持ってくる🧩✨

EF Core だと「Fluent API」で **UNIQUE / Filter / CHECK** を書けるよ🙂
（公式ドキュメントでも、`HasIndex().IsUnique()` や `HasFilter()`、`HasCheckConstraint()` が紹介されてる）([Microsoft へようこそ][7])

### 例：ModelBuilder（超ざっくり版）🧱

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<User>(b =>
    {
        b.HasKey(x => x.UserId);
        b.HasIndex(x => x.Email).IsUnique();
        b.Property(x => x.Email).IsRequired();
    });

    modelBuilder.Entity<Subscription>(b =>
    {
        b.HasKey(x => x.SubscriptionId);

        b.Property(x => x.UserId).IsRequired();
        b.Property(x => x.PlanId).IsRequired();
        b.Property(x => x.Status).IsRequired();
        b.Property(x => x.PriceCents).IsRequired();
        b.Property(x => x.StartedAt).IsRequired();

        b.HasOne<User>()
            .WithMany()
            .HasForeignKey(x => x.UserId);

        // CHECK（テーブルに付く）
        b.ToTable(t =>
        {
            t.HasCheckConstraint("CK_Subscription_Price", "[PriceCents] > 0");
            t.HasCheckConstraint("CK_Subscription_DateRange", "[EndedAt] IS NULL OR [StartedAt] <= [EndedAt]");
        });

        // 条件付き unique index（SQL Server）
        b.HasIndex(x => x.UserId)
            .IsUnique()
            .HasDatabaseName("UX_Subscription_Active_OnePerUser")
            .HasFilter("[Status] = N'Active'");
    });
}
```

---

## 9) “DBが止めたエラー”を、境界でいい感じに変換する🙂📣

DB制約を入れると、違反時に例外が飛ぶよね⚡
ここで雑に「500！」にすると悲しいので😢、境界でこうするのがおすすめ👇

* **DB例外（DbUpdateException など）**をキャッチ
* 「どの制約名が落ちた？」を手がかりに、**ユーザー向けメッセージ**に変換
* ただし、**エラーメッセージ文字列のパース**はDB依存で壊れやすいから、できれば「制約名」で寄せる🧠✨

```csharp
try
{
    await db.SaveChangesAsync();
}
catch (DbUpdateException ex)
{
    // 例：ex.InnerException の内容から制約名を拾う（DB依存）
    // ここは“変換層”で吸収して、UIには分かりやすい文言へ🙂
    throw new InvalidOperationException("保存に失敗しました。入力内容を確認してください。", ex);
}
```

> コツ：**制約名を読みやすく付ける**と、トラブルシュートも変換も楽になるよ🧸✨
> 例：`UQ_User_Email` / `CK_Subscription_Price` / `UX_Subscription_Active_OnePerUser`

---

## 10) よくある落とし穴集💣（ここ超大事）

### 落とし穴①：CHECK と NULL 😵‍💫

SQL Server の CHECK は、NULL が入ると式が UNKNOWN になって “通る” ことがあるよ（例：`MyColumn=10` でも NULL が通る）([Microsoft Learn][4])
➡️ **NULL を許すなら `IS NULL OR ...` を明示**するのが安全👌

### 落とし穴②：UNIQUE と NULL 🤔

SQL Server の UNIQUE は、NULL を許すけど “扱い”が独特（列ごとに NULL 1件だけ等）なので、仕様に合うか確認してね([Microsoft Learn][4])

### 落とし穴③：既存データが汚れてると制約追加できない🧹

UNIQUE 追加時、既に重複があると追加できずエラーになるよ([Microsoft Learn][4])
➡️ 先に **重複の棚卸し** → **移行スクリプト** が必要！

---

## 11) 演習：不変条件→DBで守れる/守れない分類表を作ろう📝✨

### お題：あなたの題材でOK（会員/注文/予約どれでも）🎀

1. 不変条件を10個書く（第2章の“壊れた状態”から逆算でもOK）
2. それを次の3つに分類👇

* A：型（VO/enum/record）で守る💎
* B：アプリ境界（入力変換/ガード）で守る🚪🛡️
* C：DB制約で守る🏰🗄️

3. C について「NOT NULL / UNIQUE / CHECK / FK / filtered unique」どれかに落とす

### 仕上げチェック✅

* 「同時実行で壊れそうなやつ」は DB で止められてる？⚔️
* CHECK は NULL で抜けない？😵‍💫
* 制約名は分かりやすい？🧸

---

## 12) AIの使いどころ（この章は相性いい！）🤖🧠✨

そのままコピって使えるプロンプト例だよ💕

```text
あなたはDB設計のレビュー係です。
以下の不変条件一覧を、DB制約で守れるもの（NOT NULL/UNIQUE/CHECK/FK/filtered unique）に分類し、
各制約の具体案（制約名案も）を提案してください。
さらに「DBでは守れないのでアプリ側で守るべき理由」も短く書いてください。

不変条件:
- ...
- ...
```

```text
EF Core の Fluent API で、以下のDB制約を表現するコード例を作ってください。
対象DBは SQL Server です。
- UNIQUE: ...
- CHECK: ...
- filtered unique index: ...
制約名の命名規則も提案してください。
```

---

## まとめ🏁🎉

* **アプリで守る**（型・境界・更新メソッド）＋ **DBで守る**（制約）＝最強の二重防御🛡️🛡️
* DB制約は “最後の砦” だからこそ、**シンプルで強いルール（NOT NULL/UNIQUE/CHECK/FK）**から入れるのが気持ちいい🙂✨
* 例外が出たら、境界で **ユーザー向け表現に変換**して、優しく返すのがプロっぽい🌸📣

---

次の章（第30章）は、ここまでの全部を一本につなぐ総合演習だよ🏁✨
もしよければ、あなたの題材（会員＋課金 / 注文＋配送 / 予約＋キャンセル）を **第30章の題材に固定**して、演習が積み上がる形にしていこう😊💗

[1]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0 "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[2]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes "Visual Studio 2026 Release Notes | Microsoft Learn"
[3]: https://learn.microsoft.com/ja-jp/sql/sql-server/sql-server-2025-release-notes?view=sql-server-ver17 "SQL Server 2025 リリース ノート - SQL Server | Microsoft Learn"
[4]: https://learn.microsoft.com/en-us/sql/relational-databases/tables/unique-constraints-and-check-constraints?view=sql-server-ver17 "Unique constraints and check constraints - SQL Server | Microsoft Learn"
[5]: https://learn.microsoft.com/ja-jp/sql/relational-databases/tables/create-foreign-key-relationships?view=sql-server-ver17 "外部キー リレーションシップを作成する - SQL Server | Microsoft Learn"
[6]: https://learn.microsoft.com/en-us/sql/relational-databases/indexes/create-filtered-indexes?view=sql-server-ver17 "Create Filtered Indexes - SQL Server | Microsoft Learn"
[7]: https://aka.ms/efcore-docs-check-constraints "Indexes - EF Core | Microsoft Learn"
