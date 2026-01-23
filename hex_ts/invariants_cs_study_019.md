# 第19章 集合の不変条件①：重複禁止・上限・順序👥🧺✨

今日は「List って自由すぎて、気づいたら壊れてる」問題を、**型とメソッド（＝入口）**でガチガチに守る回だよ〜🛡️💪
（2026年1月時点は .NET 10 がLTSとして提供されてて、C# 14 も最新世代だよ🙂✨） ([Microsoft][1])

---

## 0. この章のゴール🎯💖

次の3つを「設計で」守れるようになること！

1. **重複禁止**：同じIDの要素が2回入らない🚫🔁
2. **上限**：件数・合計数などが増えすぎない📈🧱
3. **順序**：並び順に意味があるなら、勝手に崩れない📚➡️

---

## 1. “集合が壊れる”と何が起きる？😱💥

たとえばショッピングカート🛒で…

* 同じ商品が **2行に分裂**（重複）
  → 合計金額がズレる、割引が二重にかかる、送料計算がバグる💸💥
* 明細が無限に増える（上限なし）
  → 表示が崩壊、APIが重い、DBが悲鳴😭
* 「追加した順」が意味あるのに、どこかでソートされた（順序崩壊）
  → ユーザー体験が壊れる😵‍💫

集合は放置すると壊れやすい…だから**不変条件の主戦場**になりがちだよ👀🧺✨

---

## 2. 集合の不変条件テンプレ3点セット🧺📌

### A) 重複禁止（Unique）🚫

「同じ `ProductId` は 1行だけ」みたいなやつ！

* **キー**（識別子）で一意にするのが基本
* “同じもの” の定義が曖昧だと事故るので、**型（VO）でIDを表す**のが強い💎

### B) 上限（Limit）🧱

* 明細行数の上限：例）最大 50行
* 合計数量の上限：例）最大 999個
* 合計金額の上限：例）クレカ上限など

上限って「入力で守る」だけじゃ足りなくて、**内部でも必ず守る**のが大事だよ🛡️✨

### C) 順序（Order）📚

順序には3種類あるよ👇

1. **挿入順**（追加した順）
2. **ソート順**（価格順・名前順など）
3. **意味のある順**（優先度順、画面の並びと一致など）

「順序が仕様」なら、**仕様として固定**しよう🙂🔒

---

## 3. 守り方の結論：Listを“公開しない”🙅‍♀️🔒

集合の不変条件は、だいたいこれで勝てる🏆✨

* `private List<T>` を内部に持つ
* 外には `IReadOnlyList<T>` などで見せる（読み取り専用）
* 変更は **Add/Remove/Change** みたいなメソッド経由だけにする（＝入口を一本化）🚪🛡️

---

## 4. 例題：CartItems（同一商品は1行にまとめる）🛒✨

### 不変条件（この章の主役）📜

* 同じ `ProductId` は **必ず1行**（重複禁止）
* 明細行は **最大 50行**（上限）
* 並び順は **追加した順を維持**（順序）

---

## 5. 実装してみよっ🧑‍💻🎀（C#）

ポイントは「**Listを直接触らせない**」「**Addで必ず正規化**」だよ✅

```csharp
using System;
using System.Collections.Generic;

public readonly record struct ProductId(Guid Value)
{
    public static ProductId Create(Guid value)
        => value == Guid.Empty ? throw new ArgumentException("ProductId is empty") : new ProductId(value);
}

public sealed record CartLine(ProductId ProductId, int Quantity)
{
    public CartLine Increase(int delta) => this with { Quantity = Quantity + delta };
    public CartLine SetQuantity(int quantity) => this with { Quantity = quantity };
}

public sealed class CartItems
{
    private const int MaxLines = 50;

    private readonly List<CartLine> _lines = new();
    public IReadOnlyList<CartLine> Lines => _lines; // 外からAdd/Removeできない✨

    public bool TryAdd(ProductId productId, int quantity, out string error)
    {
        error = "";

        if (quantity <= 0) { error = "数量は1以上だよ🙂"; return false; }
        if (_lines.Count >= MaxLines && !Contains(productId))
        {
            error = $"明細は最大{MaxLines}行までだよ🧱";
            return false;
        }

        var index = IndexOf(productId);
        if (index >= 0)
        {
            // ✅ 重複させず、同じ行にまとめる
            _lines[index] = _lines[index].Increase(quantity);
        }
        else
        {
            // ✅ 追加した順を維持（末尾追加）
            _lines.Add(new CartLine(productId, quantity));
        }

        return true;
    }

    public bool TryChangeQuantity(ProductId productId, int newQuantity, out string error)
    {
        error = "";

        if (newQuantity <= 0) { error = "数量は1以上だよ🙂"; return false; }

        var index = IndexOf(productId);
        if (index < 0) { error = "その商品はカートにないよ👀"; return false; }

        _lines[index] = _lines[index].SetQuantity(newQuantity);
        return true;
    }

    public bool TryRemove(ProductId productId, out string error)
    {
        error = "";

        var index = IndexOf(productId);
        if (index < 0) { error = "その商品はカートにないよ👀"; return false; }

        _lines.RemoveAt(index);
        return true;
    }

    private bool Contains(ProductId productId) => IndexOf(productId) >= 0;

    private int IndexOf(ProductId productId)
    {
        for (int i = 0; i < _lines.Count; i++)
            if (_lines[i].ProductId == productId) return i;
        return -1;
    }
}
```

### ここが偉いポイント🌟

* `Lines` は `IReadOnlyList` だから、外から `_lines.Add()` できない🔒
* `TryAdd()` の中で **重複禁止・上限・順序**を同時に守ってる🛡️✨
* “集合のルール”が **メソッドに集約**されてて、読むだけで仕様っぽい📜🙂

---

## 6. もう一段つよくするなら：Immutableコレクション❄️🧊

「外に渡したコレクション、あとから変えられたくない😢」が気になる時は
`System.Collections.Immutable` も便利だよ✨（ImmutableArray / ImmutableList など） ([Microsoft Learn][2])

ただし最初は、**今回の“private List + IReadOnly公開 + メソッド入口”**で十分勝てるよ🏆🎀

---

## 7. テスト観点（ここ超だいじ）🧪✨

最低これだけは欲しい👇

* **重複が行に増えない**（同じIDを2回Add → 行は1のまま、数量だけ増える）
* **上限で止まる**（51行目が追加できない）
* **順序が維持される**（A追加→B追加→A追加（数量加算）でも、行順は A,B のまま）

---

## 8. 演習（手を動かすと一気に理解できるよ）✍️🎀

### 演習1：上限を「合計数量」でも守る🔢🧱

* 例）合計数量は 999 まで
* `TryAdd()` で「追加後に合計が999超えるならNG」にしてみよ🙂

### 演習2：順序を「商品名順」固定にする📚✨

* 追加した順じゃなくて、常に `ProductName` の昇順にしたい、みたいな仕様に変更
* 「Addのたびにソート」or「挿入位置を探して入れる」どっちがよさそう？🤔

### 演習3：重複の定義を変える🧩

* `ProductId` じゃなくて `(ProductId, UnitPrice)` の組み合わせで一意にしたい、など
* “同じもの” の定義が変わると設計がどう変わる？を観察しよ👀✨

---

## 9. AIの使いどころ🤖💖（超相性いい！）

コピペで使えるよ👇

* 「この `CartItems` の不変条件を箇条書きで抜き出して。抜けも指摘して」🤖🔍
* 「xUnitで、重複禁止・上限・順序のテストケースを最小セットで提案して」🧪
* 「この設計で“外から不正状態を作れる抜け道”があるかレビューして」🛡️

※ AIは“案出し係”として最高だけど、**最終判断はあなた**ね🙂🎀

---

## 10. まとめ🏁✨

集合の不変条件は、だいたいこの型で守れるよ🧺🛡️

* **Listを公開しない**
* **入口（メソッド）を一本化**
* **重複・上限・順序をAdd/Updateの中で必ず守る**

次の第20章は、この集合を使って
**「明細の和＝合計」みたいな“部分と全体の整合性”**を守っていくよ➕🧾✨

[1]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[2]: https://learn.microsoft.com/ja-jp/dotnet/api/system.collections.immutable?view=net-10.0&utm_source=chatgpt.com "System.Collections.Immutable 名前空間"
