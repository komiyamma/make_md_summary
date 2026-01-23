# 第23章 状態と不変条件①：状態って何？🎭✨

この章はね、「**不変条件って、値だけじゃなくて“状態”にもあるんだよ〜！**」って感覚をつかむ回だよ😊🧠
（いまのC#は **.NET 10 / C# 14** 世代が最新LTSとして出ていて、こういう設計を“素直に書ける道具”が揃ってるよ〜！）([Microsoft for Developers][1])

---

## 1) そもそも「状態（State）」って何？🎭

**状態＝「いま何段階？」**のことだよ🙂✨
たとえば注文なら…

* 📝 Draft（下書き：カート入れてるだけ）
* 💳 Paid（支払い済み）
* 📦 Shipped（発送済み）
* ❌ Cancelled（キャンセル済み）

みたいに、**段階が変わる**よね。

そして超たいじなのがここ👇

> 状態が変わると、**「やっていい操作」も変わる**✅🚫

---

## 2) 状態があると、不変条件の“種類”が増えるよ🛡️

不変条件って「数値は0以上」みたいな**値のルール**だけじゃないの。

状態が入ると、こうなる👇

### ✅(A) 常に守る不変条件（いつでも）

* 注文IDは空じゃない
* 明細は0件じゃない（例）
* 合計金額は明細の和と一致…など

### ✅(B) 状態ごとに守る不変条件（ここが今回の主役！）

* 💳 Paidなら「支払い情報が必ずある」
* 📦 Shippedなら「追跡番号が必ずある」
* ❌ Cancelledなら「これ以上、支払いも発送もできない」

つまり…
**「状態」そのものが、不変条件のスイッチ**になるんだよ🎛️✨

---

## 3) ありがち事故：boolフラグ地獄😵‍💫💥

状態をちゃんと作らないと、よくこうなる👇

* `IsPaid = true`
* `IsShipped = false`
* `IsCancelled = true`

…え、**キャンセル済みだけど支払い済み？** みたいな矛盾が発生😇💥
こういうのが「壊れた状態」だよ（第2章のやつ！）🧨

---

## 4) 状態で一番大事な考え方：「許可される操作」📌✨

状態って、雰囲気で付けるラベルじゃなくて

> **状態＝「許可される操作の集合」**📦✅🚫

って考えるとめちゃ設計がキレイになるよ😊

例：注文（Order）の操作を並べると👇

* `Pay()`（支払う）
* `Ship()`（発送する）
* `Cancel()`（キャンセルする）
* `AddItem()`（商品追加）
* `RemoveItem()`（商品削除）

で、状態ごとにこう変わる👇

### 📝 Draft

* ✅ AddItem / RemoveItem / Cancel / Pay
* 🚫 Ship（まだ払ってないのに発送は無理）

### 💳 Paid

* ✅ Ship / Cancel（方針次第）
* 🚫 AddItem / RemoveItem（支払い後に明細いじると地獄）

### 📦 Shipped

* ✅ （基本は閲覧だけ…）
* 🚫 Cancel / AddItem / RemoveItem（もう送ってる！）

### ❌ Cancelled

* ✅ （閲覧だけ）
* 🚫 Pay / Ship / AddItem / RemoveItem

こうやって「操作」を軸にすると、状態がスッと決まるよ🧠✨

---

## 5) “状態の不変条件”を言語化するコツ🗣️🛡️

状態ごと不変条件は、次のテンプレで言語化すると超ラク👇

* 「状態が **X** のとき、**必ずAが成り立つ**」
* 「状態が **X** のとき、**Bは絶対しない**」
* 「状態が **X** のとき、**できる操作はCだけ**」

例：

* 💳 Paid のとき、PaymentId は必須
* 📦 Shipped のとき、TrackingNumber は必須
* ❌ Cancelled のとき、Pay/Ship は禁止

---

## 6) C#での最小実装イメージ（“雰囲気”だけ掴む）🧩✨

この章はまだ「状態遷移表」や「遷移メソッド本格実装」は次（第24〜25章）なので、**最小の形**だけ見せるね🙂

```csharp
public enum OrderStatus
{
    Draft,
    Paid,
    Shipped,
    Cancelled
}

public sealed class Order
{
    public OrderStatus Status { get; private set; } = OrderStatus.Draft;

    public void Pay()
    {
        if (Status != OrderStatus.Draft) throw new InvalidOperationException("支払いできない状態だよ");
        Status = OrderStatus.Paid;
    }

    public void Ship()
    {
        if (Status != OrderStatus.Paid) throw new InvalidOperationException("発送できない状態だよ");
        Status = OrderStatus.Shipped;
    }

    public void Cancel()
    {
        if (Status == OrderStatus.Shipped) throw new InvalidOperationException("発送後はキャンセル不可だよ");
        Status = OrderStatus.Cancelled;
    }
}
```

ポイントはこれ👇

* `Status` を **1個だけ**持つ（bool複数にしない）🎯
* **操作メソッドが入口**になって、状態に応じてガードする🛡️🚪
* 変な順番の操作をすると即止める✅🚫

（次章で「表」作って、抜け漏れを潰すよ〜📋✨）

---

## 7) 演習：あなたの題材で「状態」を作ってみよ〜！🎀📝

題材はどれでもOK（会員登録、サブスク、予約、注文…）😊

### ステップ1：状態を3〜5個にする🎭

* 例：予約

  * Draft（入力中）
  * Confirmed（確定）
  * CheckedIn（来店）
  * Cancelled（キャンセル）

### ステップ2：操作を5〜8個並べる🧩

* `Confirm()`, `Cancel()`, `ChangeDate()`, `CheckIn()` …みたいに

### ステップ3：状態×操作で「できる/できない」を書く✅🚫

* まだ表にしなくてOK、箇条書きでOK！

### ステップ4：状態ごとの不変条件を1つずつ書く🛡️

* Confirmedなら「日付が未来」必須、とかね🙂

---

## 8) AIの使い方（この章向け）🤖💡

AIは「案出し」と「抜けチェック」が強いよ✅✨

### ✅ 状態候補を出させる

* 「注文の状態を4つ提案して。各状態の意味と、よくある落とし穴も添えて」

### ✅ 操作と禁止ルールの洗い出し

* 「状態ごとに許可される操作・禁止される操作を列挙して。不整合が起きる例も出して」

### ✅ “状態ごとの不変条件”を文章化させる

* 「各状態で必ず成り立つ条件（不変条件）を1〜3個ずつ文章で提案して」

---

## まとめ🎉

* 状態は「いま何段階？」🎭
* 状態が変わると「やっていい操作」が変わる✅🚫
* 状態ごとの不変条件（Paidなら支払い情報必須、など）が超大事🛡️
* boolフラグ複数は矛盾を生みやすい😵‍💫💥
* まずは「状態×操作」を言語化すると設計が一気にラクになるよ😊✨

---

次の第24章では、この「できる/できない」を **状態遷移表**にして、抜け漏れを潰すよ📋🖊️
もし演習の題材を「注文」「予約」「サブスク」のどれで行くか決めてたら、その題材に合わせて **状態案＋操作案＋不変条件案**をセットで作ってあげるね🥰🎀

[1]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
