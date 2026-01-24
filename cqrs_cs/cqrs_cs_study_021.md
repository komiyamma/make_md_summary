# 第21章　Queryの発展② 集計・検索の“読みモデル設計”📊🔎✨

この章はね、「**検索画面（一覧）で欲しい情報**」に合わせて、DBから**JOINや集計（COUNT/SUM）**を使って気持ちよく取り出す設計ができるようになる回だよ〜！😺🫶

---

### 今日できるようになること 🎯✨

* 「画面で欲しい列」から逆算して、**Read DTO（表示用の形）**を決められる👀📦
* **JOIN + 集計（件数/合計）**を“壊れにくく＆速く”作れる🏎️💨
* ありがちな地雷（N+1、行が爆増、COUNTが重い）を避けられる💣🧯
* 「今はSQLで集計」「後でRead専用テーブルにする」の判断ができる⚖️✨

---

## 1) まず最重要：Readモデルは「画面都合でOK」🥳📺

Writeモデル（更新用）は「整合性とルール」が大事。
Readモデル（参照用）は「**画面で必要な形に寄せる**」のが正解だよ！😺👍

たとえば注文一覧（管理画面）って、だいたいこういう列ほしくない？👇

* 注文ID
* 注文日時
* 購入者名
* ステータス
* **商品点数（合計）** ← 集計
* **合計金額** ← 集計
* （おまけ）最終更新日時、キャンセル理由、支払い状況…などなど

この「商品点数」「合計金額」みたいなのが、今回の主役だよ〜📊✨

---

## 2) 設計の手順（これで迷子にならない）🧭📝

### 手順A：画面（APIレスポンス）を先に決める 👀✨

「一覧で何を表示する？」を決めて、**Read DTO**を作る！

```csharp
public sealed record OrderListRowDto(
    Guid OrderId,
    DateTime OrderedAt,
    string CustomerName,
    string Status,
    int ItemCount,
    decimal TotalAmount
);

public sealed record OrderListQuery(
    string? Keyword,
    string? Status,
    DateOnly? From,
    DateOnly? To,
    int Page = 1,
    int PageSize = 20,
    string Sort = "OrderedAtDesc"
);
```

> コツ：Write側のEntity（Orderとか）をそのまま返さないよ〜！😅📦

---

### 手順B：フィルタとソートを最初に固定する 🔍↕️

検索画面はだいたいこれ👇

* キーワード（名前・メール・商品名）
* ステータス
* 日付範囲
* ソート（新しい順など）
* ページング

ここを先に決めると、クエリが作りやすいよ！😺✅

---

### 手順C：集計を「その場でやる」か「貯める」か決める 🧠⚖️

まずは基本の2択！

1. **その場で集計（JOIN + GROUP BY / サブクエリ）**

   * 早く作れる✨
   * データが増えると重くなりやすい💦

2. **集計済みを持つ（Read専用テーブル / Indexed View など）**

   * 読みが爆速になりやすい🏎️💨
   * その代わり更新コストが増える（書き込みが重くなる）⚠️
   * Indexed Viewは「大量行の集計に効くけど、頻繁更新には向きにくい」って公式にも書いてあるよ📌 ([Microsoft Learn][1])

この章ではまず **①その場で集計** をしっかり作れるようにするよ〜！💪✨
（②は後半のProjection章で本格的にやる感じ！）

---

## 3) まずやりがち地雷：N+1（絶対踏みがち）💥😇

ダメな例（ループ内で毎回DBアクセス）👇

```csharp
// ❌ N+1地獄：注文20件なら、+20回クエリが増える…
var orders = await db.Orders.AsNoTracking()
    .OrderByDescending(o => o.OrderedAt)
    .Skip(skip).Take(take)
    .ToListAsync();

var rows = new List<OrderListRowDto>();

foreach (var o in orders)
{
    var itemCount = await db.OrderItems.CountAsync(i => i.OrderId == o.Id);
    var total = await db.OrderItems
        .Where(i => i.OrderId == o.Id)
        .SumAsync(i => i.UnitPrice * i.Quantity);

    rows.Add(new(o.Id, o.OrderedAt, o.CustomerName, o.Status, itemCount, total));
}
```

**直し方**：集計は「まとめて一発」で取る！😺🔧

---

## 4) パターン①：GroupByで集計してJOINする（読みやすい王道）👑📊

OrderItemsを先に集計して、OrdersにJOINするよ！

```csharp
public async Task<IReadOnlyList<OrderListRowDto>> GetOrderListAsync(
    OrderListQuery query,
    CancellationToken ct)
{
    var q = db.Orders.AsNoTracking();

    // フィルタ（必要な分だけでOK）
    if (!string.IsNullOrWhiteSpace(query.Status))
        q = q.Where(o => o.Status == query.Status);

    if (query.From is not null)
        q = q.Where(o => o.OrderedAt >= query.From.Value.ToDateTime(TimeOnly.MinValue));

    if (query.To is not null)
        q = q.Where(o => o.OrderedAt < query.To.Value.AddDays(1).ToDateTime(TimeOnly.MinValue));

    if (!string.IsNullOrWhiteSpace(query.Keyword))
        q = q.Where(o => o.CustomerName.Contains(query.Keyword));

    // itemsをOrderIdごとに集計
    var itemAgg =
        db.OrderItems.AsNoTracking()
            .GroupBy(i => i.OrderId)
            .Select(g => new
            {
                OrderId = g.Key,
                ItemCount = g.Sum(x => x.Quantity),
                TotalAmount = g.Sum(x => x.UnitPrice * x.Quantity),
            });

    // JOIN（注文が0件でも落ちないようにLEFT JOINっぽく）
    var joined =
        from o in q
        join a in itemAgg on o.Id equals a.OrderId into gj
        from a in gj.DefaultIfEmpty()
        select new OrderListRowDto(
            o.Id,
            o.OrderedAt,
            o.CustomerName,
            o.Status,
            a != null ? a.ItemCount : 0,
            a != null ? a.TotalAmount : 0m
        );

    // ソート（例：OrderedAtDescだけ対応）
    joined = joined.OrderByDescending(x => x.OrderedAt);

    // ページング
    var skip = (query.Page - 1) * query.PageSize;

    return await joined.Skip(skip).Take(query.PageSize).ToListAsync(ct);
}
```

EF Coreの「compiled query」みたいな高速化オプションも公式で紹介されてるよ（ホットパス向け）🚀 ([Microsoft Learn][2])
※ただ、初心者のうちは「クエリ形を安定させる」ほうが先でOK！😺👍

---

## 5) パターン②：ページングしてから集計（大規模で強い）🦾📈

データが増えると、**全体をJOINしてからSkip/Take** が重くなりやすいの。
そんなときは「ページ対象のOrderIdを先に決める」作戦が強いよ！🧠✨

流れ👇

1. フィルタ＆ソート済みの Orders から **OrderIdだけ**ページングして取る
2. そのOrderIdの集合に対して items をまとめて集計
3. メモリ上で合体（or SQLで合体）

メリット：DBが余計な集計をしなくて済むことが多い🏎️💨
（「検索は厳しいけど、表示は20件だけ」って画面はこれが効きやすい！）

---

## 6) 「集計 + 総件数」って実は別腹 🍰📌

一覧画面ってよく「総件数」も欲しくなるよね？

* 表示リスト：20件だけ
* 総件数：全体の件数

これ、同じクエリで頑張ると重くなることがあるから、基本はこう👇

* **一覧取得クエリ**
* **Count用クエリ（条件だけ同じ）**

みたいに分けるのが現実的だよ〜😺🫶

---

## 7) インデックスの当たり前（でも効果デカい）📌⚡

検索でよく使うのはだいたいこの列👇

* Orders：OrderedAt、Status、CustomerName（キーワード次第）
* OrderItems：OrderId（JOINキー）

だから例えばSQL Serverなら、まずこのへんが候補！

```sql
-- Orders: 日付 + 状態で絞って新しい順に並べるなら
CREATE INDEX IX_Orders_Status_OrderedAt
ON dbo.Orders(Status, OrderedAt DESC);

-- OrderItems: OrderIdで集計するなら
CREATE INDEX IX_OrderItems_OrderId
ON dbo.OrderItems(OrderId);
```

> コツ：インデックスは「増やせば増やすほど良い」じゃないよ！
> 書き込みが遅くなるから、“検索で本当に使うやつ”だけ厳選ね😇📌

---

## 8) それでも重い時の“奥の手”紹介（読みが爆速になるやつ）🪄🏎️

「毎回SUM/COUNTするの重いよ〜😭」ってなったら、こういう選択肢があるよ👇

* **Read専用テーブル**（OrderSummaryみたいに合計を保持）
* **View / Indexed View**（集計を“物理化”する）
  公式でも「大量行の集計に効く」って明記されてるよ📌 ([Microsoft Learn][1])
* SQL Serverなら **Query Store** でプランの変化を追える（ヒントで調整もできる）🕵️‍♀️
  ヒントが永続化して再起動でも残る、みたいな説明があるよ ([Microsoft Learn][3])

このへんは後半章でさらにやるけど、「選択肢として知ってる」だけで強い！😺✨

---

## 9) ミニ演習（やってみよ！）🧪🎀

### お題：注文一覧に「商品点数」「合計金額」を追加する📊

1. `OrderListRowDto` に `ItemCount` と `TotalAmount` を追加
2. `OrderItems` を `GroupBy(OrderId)` で集計して JOIN
3. ページング・ソートが崩れてないか確認
4. 最後に「N+1になってないか」をログで確認（SQL発行回数を見る）👀🧾

できたらさらに✨

* ステータスフィルタ（Paid / Cancelled など）を追加
* 日付範囲（From/To）を追加
* キーワード（CustomerName）を追加

---

## 10) AI活用プロンプト（超おすすめ）🤖💬✨

そのままコピペで使えるやつ置いとくね！😺🫶

* 「この画面（列と検索条件）に必要なRead DTO案を出して。過不足も指摘して」📦
* 「このLINQがN+1になってないか確認して、改善案を2つ出して」🧯
* 「SQL Server向けに、このWHERE/ORDER BYに効くインデックス案を提案して（書き込みコストも説明して）」📌
* 「このSQL/ LINQ の危険点（全件スキャン、行爆増、重いCOUNTなど）をチェックして」⚠️

> ただし！AIが出したSQLは必ず「パラメータ化」と「実行計画の確認」ね🙅‍♀️💉✨

---

## 11) この章のまとめ（チェックリスト）✅😺

* [ ] Read DTOは画面都合で作った（Entity直返ししてない）📦
* [ ] 集計は “一発クエリ” で取ってる（N+1してない）📊
* [ ] ページングとソートが正しく効いてる📄
* [ ] よく使う検索条件にだけインデックスを貼った📌
* [ ] 重くなったら「ページング→集計」や「Read専用テーブル/Indexed View」の選択肢を思い出せる🧠✨

---

### ちょい最新メモ（2026-01時点）📌✨

* .NET 10 はLTSで、サポート表では 2026-01-13 時点の最新パッチが 10.0.2 になってるよ ([Microsoft][4])
* EF Core 10 もLTSで、2025年11月リリース＆2028年11月までサポートって明記されてるよ ([Microsoft Learn][5])
* Dapperのバージョンは NuGet に 2.1.66（2025-02-06）として掲載があるよ ([NuGet][6])

---

次の章（第22章）では、こういうQuery/Commandを受け取る **API層を薄くする作法**（Controller/Minimal APIを“受け取って投げる係”にする）を、テンプレ化してラクにしていくよ〜📮✨

[1]: https://learn.microsoft.com/en-us/sql/relational-databases/views/views?view=sql-server-ver17&utm_source=chatgpt.com "Views - SQL Server"
[2]: https://learn.microsoft.com/en-us/ef/core/performance/advanced-performance-topics?utm_source=chatgpt.com "Advanced Performance Topics - EF Core"
[3]: https://learn.microsoft.com/en-us/sql/relational-databases/performance/query-store-hints?view=sql-server-ver17&utm_source=chatgpt.com "Query Store Hints - SQL Server"
[4]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[5]: https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew?utm_source=chatgpt.com "What's New in EF Core 10"
[6]: https://www.nuget.org/packages/dapper/?utm_source=chatgpt.com "Dapper 2.1.66"
