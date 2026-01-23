# 第2章 Dependency Ruleの一言まとめ：矢印の向きを固定する🧭➡️

## この章でできるようになること🎯✨

* 「Dependency Ruleって結局なに？」を**一言で説明**できるようになる🙆‍♀️💬
* コードの「依存（＝矢印➡️）」を見て、**向きが正しいか**ざっくり判定できる👀✅
* 「中心（方針）」と「外側（詳細）」を**分類**できるようになる📌🧠

---

## 1) まず“一言”で言うね📌💡
![](./picture/dpn_rule_cs_study_002_dependency_rule_circle.png)

**Dependency Rule =「ソースコードの依存（矢印➡️）は、外側から内側へしか向けない」**🧭➡️

もっと噛み砕くと…
**“中心の大事なルール（方針）”が、“外側の細かい都合（詳細）”に引っ張られないように固定する**ってこと😊🧷

このルールは Clean Architecture の根っこにある考え方で、
「依存は内側へだけ向く」「内側は外側のことを何も知らない」が核です。([Clean Coder Blog][1])

---

## 2) “中心”と“外側”ってなに？🧅🗺️
![](./picture/dpn_rule_cs_study_002_center_vs_outer.png)

## ✅ 中心（内側）＝ 方針・ルール・意思決定 🎯

長生きするやつ🌱

* 業務ルール（ドメイン）🧠
* ユースケース（アプリのやりたいこと）📝
* “こうあるべき”の判断（計算、バリデーション、状態遷移…）⚖️

## ✅ 外側（外側）＝ 詳細・道具・交換されがち 🔁🧰

入れ替わりやすいやつ🌀

* DB（SQL Server / SQLite など）🗄️
* UI（Web / Desktop / Console）🖥️📱
* フレームワーク（ASP.NET Core / EF Core など）🧩
* 外部API・メール送信・決済など🌐💳

---

## 3) なんで「矢印➡️」を固定すると嬉しいの？😊🎉

## 🌟 嬉しい①：変更が怖くなくなる😌🛡️

UIを変えても、DBを変えても、**中心のルールが巻き添えになりにくい**✨
→ 「ちょっと画面直しただけで、業務ロジックが壊れた😭」が減る！

## 🌟 嬉しい②：テストがめちゃ楽になる🧪💕

中心がDBやUIを知らなければ、**中心だけを軽くテストできる**✅
（DB起動いらない！画面操作いらない！）

## 🌟 嬉しい③：設計の迷子が減る🧭

迷ったらこれだけ：
**「それ、中心？外側？ 矢印➡️は内側向き？」**
これで判断できるようになる👍✨

---

## 4) C#で「依存（矢印➡️）」って具体的に何？👀🔎

ざっくり言うと、AがBに依存してるのはこういうとき⬇️

* `using` して **型名を知ってる**（`DbContext` とか）📛
* **newしてる**（具体クラスを直接作ってる）🧨
* **継承してる / 属性で参照してる**（外側の型にベタ付け）🧷
* プロジェクト参照で **参照方向が外→内になってない**📦➡️

> Clean Architecture の説明では「内側は外側の“名前”を出しちゃダメ」が強めに書かれてます。([Clean Coder Blog][1])
> （※最初は“完璧”より“方向”を意識できればOKだよ😊）

---

## 5) いちばん小さい例で体感しよう🧸➡️

## ❌ ダメな矢印（中心が外側に依存）😵‍💫

「注文合計を計算する」みたいな中心ルールが、DB詳細を知っちゃうパターン💥

```csharp
// 例：中心っぽいロジックが、外側（DB/EF）を直接知ってしまう（イメージ）
using Microsoft.EntityFrameworkCore;

public class OrderService
{
    private readonly DbContext _db; // 外側の詳細に依存😭

    public OrderService(DbContext db) => _db = db;

    public decimal CalcTotal(int orderId)
    {
        // DB都合が中心ロジックに混ざりやすい…😇
        // （例なので中身は省略）
        return 0m;
    }
}
```

**何がつらい？😢**

* DBの変更（EF → Dapper、SQL Server → SQLite…）で中心が揺れる🌀
* テストが重くなる（DBが必要）🧪💦

---

## ✅ 良い矢印（外側が中心に合わせる）😊🧭

中心側は「欲しい能力」を **インターフェースで宣言**して、外側がそれを実装する✨

```csharp
// ✅ 中心（方針）側：欲しいことだけ宣言する
public interface IOrderRepository
{
    decimal GetTotal(int orderId);
}

public class OrderService
{
    private readonly IOrderRepository _repo; // 中心は契約だけ知る😊

    public OrderService(IOrderRepository repo) => _repo = repo;

    public decimal CalcTotal(int orderId)
        => _repo.GetTotal(orderId); // 中心は「どう取るか」を知らない✨
}
```

矢印のイメージはこう👇

* **依存（矢印）**：`OrderService → IOrderRepository`（中心の中で完結）🎯
* **実装**：外側が `IOrderRepository` を実装して合わせにくる🔧

これが「矢印➡️を固定する」って感覚だよ🧭💕

---

## 6) “中心/外側”の見分け方：3秒ルール⏱️🧠

迷ったら、この質問を自分に投げるだけ！

## Q1：それって交換されがち？🔁

* はい → 外側っぽい（DB / UI / framework / 外部サービス）🧩
* いいえ → 中心っぽい（業務ルール・方針）🎯

## Q2：それが変わったら「ルール」まで変えたい？🤔

* 変えたくない → 外側！🚪
* 変えたい → 中心！🏠

---

## 7) ミニ演習（紙でも脳内でもOK）📝✨

## 演習A：中心/外側を分類してみよ📌🧺

次を「中心」「外側」に分けてみてね👇

* 注文の合計計算🧾
* 割引ルール（会員ランク）🎟️
* EF Core の `DbContext` 🧩
* ASP.NET Core の Controller 🌐
* ログ出力（Serilogなど）📒
* 支払い（外部決済API）💳

**コツ**：交換されそうな道具は外側🔁🧰

---

## 演習B：矢印➡️を描いてみよ✍️➡️

頭の中でOK！こんな図を描いて…

* 中心：`OrderService` / `DiscountRule` 🎯
* 外側：`EfOrderRepository` / `WebController` 🧩

そして **依存の矢印➡️** を引く！
✅ 正解の方向は「外側 → 中心」になるように工夫する🧭✨

---

## 8) AI活用コーナー🤖💖（Copilot/Codex でOK）

## ① 分類を手伝わせる📌🤖

「中心/外側」をAIに仕分けさせると、自分の理解が固まるよ！

```text
次の要素を「中心（方針）」「外側（詳細）」に分類して、
それぞれ理由も1行で説明して：

- OrderService
- IOrderRepository
- EfOrderRepository
- DbContext
- Controller
- DiscountRule
```

## ② “矢印が逆”になってる所を探させる🔎🤖

```text
このコードで「中心が外側に依存している」匂いがある箇所を指摘して。
Dependency Ruleの観点で、どう直すかも提案して。
（コードはこの後貼るね）
```

## ③ 注意⚠️：AIの提案を採用する前の一言チェック✅

**「その変更で、矢印➡️は内側向きになってる？」**
ここだけは人間が最終確認しよっ😊🧭

---

## 9) まとめ💐✨（今日の持ち帰り）

* Dependency Rule は **「依存の矢印➡️は内側へ」**🧭➡️ ([Clean Coder Blog][1])
* **中心＝長生きする方針**、**外側＝交換されがちな詳細**🧅🧰
* 迷ったら **「それ交換される？」「ルールまで変えたい？」**で判断😊✅

---

## おまけ（今のC#周りの“最新”メモ）📌✨

C# は **C# 14** が最新で、**.NET 10** 上でサポートされています。([Microsoft Learn][2])
.NET 10 は **2025-11-11** リリースの LTS として案内されています。([Microsoft for Developers][3])

---

次の第3章では、この「中心と外側の地図🗺️」をもっと具体的にして、**Domain / Application / Infrastructure / UI** に分ける感覚を作っていくよ〜😊🧅✨

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "Clean Architecture - Clean Coder Blog - Uncle Bob"
[2]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[3]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
