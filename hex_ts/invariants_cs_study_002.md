# 第2章 “壊れた状態”を見つける練習👀💣

## この章のゴール🎯✨

* 「壊れた状態」＝**不変条件（守る約束）が破れてる状態**を、自分でどんどん挙げられるようになる🙂📝
* 「会員登録」「注文」「課金」で、**壊れ方を各5個ずつ**サクサク列挙できるようになる💪💕

---

## 1) そもそも「壊れた状態」って？🤔🧨

ざっくり言うと…

* **本来ありえないのに、データとして存在できちゃう状態**😱
* そしてそれはたいてい、あとで別の場所で爆発します💥（集計がズレる、例外が飛ぶ、請求が間違う、など…）

たとえば会員なら👇

* 名前が空文字 `""`（え、誰…？）
* 年齢が `-5`（時空が歪む…🌀）
* Email が `null`（連絡できない📮）

こういうのが「壊れた状態」だよ〜って感じです🙂✨

---

## 2) 壊れ方の“よくある型”カタログ📚✨（まずはここから！）

「壊れた状態」を探すときは、まずこのカテゴリを順番に当てはめると強いよ💪🛡️

| 壊れ方カテゴリ         | 例                                    | ありがちな事故💥      |
| --------------- | ------------------------------------ | -------------- |
| 空/欠け（空文字・null）  | `Name=""` / `Email=null`             | 画面に空表示、通知不能📩  |
| 範囲外（負数・上限超え）    | `Age=-1` / `Quantity=0`              | 計算・在庫・料金が崩壊🧾  |
| 形式違反（フォーマット）    | `Email="aaa@"`                       | メール送れない・登録不能📧 |
| 未正規化（空白・大小文字）   | `"  user  "` / `"A@B.com"`           | 重複判定ミス、検索漏れ🔍  |
| 組み合わせ不整合（クロス項目） | `Paid=true` なのに `PaymentMethod=null` | 「払ったのに情報ない」💸❓ |
| 時間の矛盾（日付順序）     | `Start > End`                        | 期間・予約が破綻📅     |
| 集合の矛盾（重複・合計ズレ）  | 同一商品が2行 / 合計が明細の和と違う                 | 請求・集計がズレる🛒    |

この表を“型”として覚えると、壊れた状態が出しやすくなるよ〜😊🌸

---

## 3) 壊れた状態を見つける手順（テンプレ）🧩🖊️

やり方はシンプルでOK！👇

## ステップ①：対象を決める🎯

* 会員登録？注文？課金？（今回はこの3つ！）

## ステップ②：項目を並べる🧾

* 例：会員登録なら `UserName / Email / Password / BirthDate ...`

## ステップ③：単体チェック（1項目ずつ）🔎

* 空？null？範囲外？形式？未正規化？

## ステップ④：組み合わせチェック（2項目以上）🧠

* 「AならB必須」「この状態のときこの値は禁止」みたいなルール！

## ステップ⑤：集合・合計・日付を疑う🧨

* カートの明細、合計、日付順…ここめっちゃ壊れやすい🥹

---

## 4) まずはウォーミングアップ🔥（見つけゲーム👀）

次のデータ、どこが壊れてる？（複数あり）👇

* 会員：`Name=""`, `Email="  A@B.com "`, `Age=-1`
* 注文：`Items=[]`, `Total=1200`, `Status="Paid"`
* 課金：`Amount=-500`, `Currency="JPY"`, `PaidAt=null`, `IsPaid=true`

答え例📝✨

* 会員：名前空、年齢負数、Email未正規化（空白＋大小文字）
* 注文：明細ゼロなのに合計あり、Paidなのに商品なしは変（仕様次第だけど怪しい）
* 課金：金額負数、支払い済みなのに支払日時なし（組み合わせ不整合）

「仕様次第」って出たところがポイントで、**壊れた状態は“仕様（不変条件）を言語化する入口”**になるよ🙂🛡️

---

## 5) 演習①：会員登録で“壊れた状態”を5個🧑‍💻🎀

想定項目（例）👇

* `UserName`, `Email`, `Password`, `BirthDate`, `AgreeToTerms`

壊れた状態例（サンプル回答）📝✨

1. `UserName=""`（空）
2. `Email=null`（欠け）
3. `Email="a@b"`（形式が弱すぎる/仕様次第だけど要検討）
4. `BirthDate` が未来日（時間矛盾）
5. `AgreeToTerms=false` なのに登録成功扱い（組み合わせ不整合）

コツ💡

* 「必須」「形式」「正規化」「時間」「同意」あたりは鉄板で壊れるよ〜🥹🛡️

---

## 6) 演習②：注文で“壊れた状態”を5個🛒📦

想定項目（例）👇

* `OrderId`, `Items`, `ShippingAddress`, `Status(Draft/Paid/Shipped)`, `Total`

壊れた状態例（サンプル回答）📝✨

1. `Items` に同一商品が重複して2行（集合の矛盾）
2. `Quantity=0` の明細がある（範囲外）
3. `Status="Shipped"` なのに `ShippingAddress=null`（組み合わせ不整合）
4. `Total` が「明細の合計」と一致しない（合計ズレ）
5. `Items=[]` なのに `Total>0`（整合性崩れ）

---

## 7) 演習③：課金で“壊れた状態”を5個💳💥

想定項目（例）👇

* `Amount`, `Currency`, `PaymentMethod`, `IsPaid`, `PaidAt`, `InvoiceId`

壊れた状態例（サンプル回答）📝✨

1. `Amount<=0`（負数・ゼロ）
2. `Currency="JPY"` なのに小数が大量（仕様次第：通貨の最小単位ルール）
3. `IsPaid=true` なのに `PaidAt=null`（組み合わせ不整合）
4. `PaymentMethod=null` なのに課金確定（組み合わせ不整合）
5. 同一 `InvoiceId` で二重請求が作れる（集合/一意性の不変条件）

---

## 8) ミニ実装：壊れた状態を“検出”するだけでも価値ある🛠️✨

「第2章」では、まだ“型で完全防御”しなくてOK🙂
まずは **“壊れを見つけて弾ける”** を体験しよ〜！

### 例：入力（ゆるい）→ 検出（エラー配列）✅

```csharp
using System;
using System.Collections.Generic;

public sealed record RegisterMemberCommand(
    string? UserName,
    string? Email,
    DateTime? BirthDate,
    bool AgreeToTerms
);

public static class RegisterMemberValidator
{
    public static IReadOnlyList<string> Validate(RegisterMemberCommand cmd)
    {
        var errors = new List<string>();

        if (string.IsNullOrWhiteSpace(cmd.UserName))
            errors.Add("ユーザー名が空だよ🥺");

        if (string.IsNullOrWhiteSpace(cmd.Email))
            errors.Add("メールアドレスが空だよ🥺");
        else
        {
            var email = cmd.Email.Trim(); // まずトリム（正規化の第一歩🧼）
            if (!email.Contains("@"))
                errors.Add("メールアドレスの形式が変かも…📧💦");
        }

        if (cmd.BirthDate is null)
            errors.Add("生年月日が未入力だよ📅");
        else if (cmd.BirthDate.Value.Date > DateTime.Today)
            errors.Add("生年月日が未来日になってるよ🌀");

        if (!cmd.AgreeToTerms)
            errors.Add("利用規約に同意してね🙏");

        return errors;
    }
}
```

ここで大事なのは👇

* **壊れた状態を“作れてしまう”前提**で、入口で検出する✅
* でもこの章の主役は「検出コード」じゃなくて、**壊れた状態の洗い出し力**だよ👀✨

---

## 9) AIに“抜け”をチェックさせるプロンプト集🤖✅（そのままコピペOK）

## ① 壊れた状態の追加出し

「会員登録の仕様はこれです：（仕様箇条書き）
この仕様に対して、壊れた状態をカテゴリ別（空/範囲/形式/組合せ/日付/集合）に20個出してください。最後に“起きやすさ順”に並べて。」

## ② テストデータ化

「列挙した壊れた状態それぞれについて、再現用の具体的な入力例（JSONでもOK）を作って。」

## ③ 仕様の穴あぶり出し

「この壊れた状態リストの中で、“仕様を決めないと正否が判断できない”ものを抽出して、質問リストにして。」

AIは“案出し係”としてめちゃ便利😊✨
ただ、**最終判断（仕様）はあなたが握る**のがコツだよ🛡️💕

---

## 10) おまけ：2026年のC#/.NETの“最新”メモ🧷✨

* **C# 14 は .NET 10 上で動く最新版**だよ（.NET 10 SDK と一緒に使える）([Microsoft Learn][1])
* .NET 10 は **2025-11-11リリースのLTS**で、サポート期限なども公式表で追えるよ([Microsoft][2])
* C# 14 には、`field` を使う **field-backed properties** みたいに「あとから不変条件を足したい」場面で便利な機能も入ってるよ（後の章で効いてくるやつ💪）([Microsoft Learn][3])
* Visual Studio 2026 側も **C# 14 の構文をフルサポート**する流れが明記されてるよ([Microsoft Learn][4])

（ここは“道具の最新状況”として置いとくね🙂🧰）

---

## まとめ🏁🎉

* 「壊れた状態」を出すのは、センスじゃなくて**型（カテゴリ）で出せる**👀✨
* 今日の成果は「会員/注文/課金」で**壊れ方を各5個**出せたこと📝💮
* 次の章では、その壊れを**どこ（境界）で止めるか**に進むよ🚪🧱✨

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14 "What's new in C# 14 | Microsoft Learn"
[2]: https://dotnet.microsoft.com/en-us/platform/support/policy?utm_source=chatgpt.com "The official .NET support policy"
[3]: https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/overview "What's new in .NET 10 | Microsoft Learn"
[4]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes "Visual Studio 2026 Release Notes | Microsoft Learn"
