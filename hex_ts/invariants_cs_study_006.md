# 第6章 失敗の表現①：例外って何者？⚡😵‍💫

この章は「例外（Exception）」を **“雑に投げない・雑に握りつぶさない”** ための基礎だよ〜🫶✨
（次の第7章で Result/戻り値に進むための、めちゃ大事な土台！）

ちなみに今どきの最新前提だと、.NET は **.NET 10 が LTS**、C# は **C# 14** が最新ラインだよ〜🧁✨ ([Microsoft][1])

---

## 6.1 例外ってなに？（ざっくり一言）🧠⚡

例外は **「処理を続けられない失敗が起きた！」っていう、ランタイムの非常ベル** だよ🚨
ふつうの if 分岐と違って、例外が投げられると **その場で処理が中断**されて、呼び出し元へ一気に伝播するのが特徴💨 ([Microsoft Learn][2])

---

## 6.2 “例外が向いてる失敗” / “向いてない失敗” 🎯✨

ここがこの章の最重要ポイントだよっ😤🛡️

## ✅ 例外が向いてる（使ってOK寄り）⚡

* **想定外**（プログラムの前提が崩れた）
* **回復が難しい**（この場で直しようがない）
* **バグ・不整合・外部障害**（ネットワーク断、DB接続不能など）

.NET のガイドも「例外を避けられる一般条件は例外にしないでね」って言ってる＝逆に言えば **避けられない/回復困難な失敗**が例外向きだね🧯 ([Microsoft Learn][3])

## ❌ 例外が向いてない（やりがち注意）😵

* **ユーザー入力ミス**（空欄、形式違い、範囲外…）
* **業務ルール的に起こり得る失敗**（在庫切れ、ポイント不足、支払い拒否…）

このへんを例外で表すと、あとで UI/API 側の扱いが **めんどくさくなりがち**😇
（だから第7章の Result が効いてくるの〜🧾✨）

---

## 6.3 例外は「どこで投げて」「どこで捕まえる」？🚪🧱

## 基本の型：境界（UI/API）で捕まえるのが気持ちいい🎀

* **ドメイン内部**：なるべく「不正な状態を作れない設計（型・Factory）」へ寄せる
* **境界**：外から来たデータを変換するときに失敗が起きるので、ここで整理してユーザー向けに返す

ただし！
「入力ミス」をドメイン内部で例外にすると、境界で catch が増えて **分岐だらけ**になりやすい…という観察を、次の演習でやるよ👀✨

---

## 6.4 C# の例外：超基本セット（これだけ覚えればOK）🧰✨

## よく使う標準例外たち（まずこれで十分）🙂

* 引数が null：**ArgumentNullException**
* 引数が不正：**ArgumentException**
* 範囲外：**ArgumentOutOfRangeException**
* 形式が違う：**FormatException**
* 今の状態ではできない：**InvalidOperationException**

「まずは用意されてる例外型を使おうね」ってのが推奨だよ🧡 ([Microsoft Learn][3])

---

## 6.5 演習：入力不正を “例外” で表す版を作ってみる👀💥

ここではあえて **ユーザー入力ミスを例外で表す** 版を作って、
「扱いにくさ」を観察するよ〜🔬✨

## お題：会員登録（Email）📧

### ① Email を例外で作る（Factory）🏭⚡

```csharp
using System;

public sealed class Email
{
    public string Value { get; }

    private Email(string value) => Value = value;

    public static Email From(string raw)
    {
        if (raw is null)
            throw new ArgumentNullException(nameof(raw));

        var v = raw.Trim();

        if (v.Length == 0)
            throw new ArgumentException("Email must not be empty.", nameof(raw));

        // ゆるめチェック（教材なのでKISSで🙂）
        if (!v.Contains('@'))
            throw new FormatException("Email format is invalid.");

        return new Email(v.ToLowerInvariant());
    }

    public override string ToString() => Value;
}
```

ポイント🌟

* 例外メッセージは **短く・何が悪いか分かる** ようにするのが推奨だよ📝 ([Microsoft Learn][3])
* ここでは「空」や「形式違い」は **ユーザー入力ミス**だけど、あえて例外にしてるよ（観察用）👀✨

---

### ② “境界” で catch して HTTP 400 に変換する🌐🧱

（最小API風のイメージだよ〜）

```csharp
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;

var app = WebApplication.Create(args);

app.MapPost("/register", (RegisterRequest dto) =>
{
    try
    {
        var email = Email.From(dto.Email);
        // 本当はここで登録処理…（省略）
        return Results.Ok(new { message = "Registered!", email = email.Value });
    }
    catch (ArgumentNullException)
    {
        return Results.BadRequest(new { message = "Email is required." });
    }
    catch (ArgumentException)
    {
        return Results.BadRequest(new { message = "Email must not be empty." });
    }
    catch (FormatException)
    {
        return Results.BadRequest(new { message = "Email format is invalid." });
    }
});

app.Run();

public record RegisterRequest(string? Email);
```

---

## ③ 観察してみよう👀📝（ここが演習の本体！）

✅ ここで感じる「例外の扱いにくさ」あるある👇

* **失敗が “1個目” で止まる**（複数エラーを集めたいのに難しい）
* catch が増えるほど **境界が分岐だらけ**😇
* 例外メッセージをそのまま返すと **UI向け文言の管理が難しくなる**（翻訳・文言統一など）

→ ね？「入力ミスは Result の方が自然そう…」って気配がしてくるはず🧾✨

---

## 6.6 例外でやっちゃダメ寄り集⚠️（事故が多い）💥

## ❌ catch (Exception) を雑に置く

「一般例外を捕まえるな」ってルール（CA1031）でも言われるやつ！🧯 ([Microsoft Learn][4])
本当にやるなら **最上位（アプリの入口）** でログして 500 を返す、みたいな場所に限定するのが安全寄り。

## ❌ 例外を握りつぶす（何もしない catch）

バグ調査が地獄になるよ〜😭

---

## 6.7 例外を “再スロー” するときの超重要ポイント🔥

## ✅ 正しい：throw;（スタックトレース維持）🧵

## ❌ ダメ：throw ex;（スタックトレースがリセット）😱

これはマジで超頻出の事故！
公式ガイドでも「再スローは適切に」って話があるし、throw と throw ex の差はデバッグ体験を破壊するよ🫠 ([Microsoft Learn][3])

---

## 6.8 自作例外って作るべき？🧩✨

結論：**必要なときだけ**でOK🙂
たとえば「外部API失敗」や「ドメインの致命的不整合」を **意味のある名前**で上に伝えたいときに便利！

Microsoft のガイドだと、自作するなら **“〜Exception” で終わる名前**、**よく使うコンストラクタを用意**みたいな話があるよ🛠️ ([Microsoft Learn][5])

※ ちなみに .NET では **古いシリアライズ系のAPIが obsolete 扱い**になってたりもするので、例外クラスの設計は “今どきの推奨”に寄せようね〜🧊 ([Microsoft Learn][6])

---

## 6.9 AI活用コーナー🤖✨「この例外、本当に例外？」

## 使い方1：例外レビュー（超おすすめ）🧑‍⚖️⚡

AIにコード貼って、こう聞く👇

* 「この例外は **想定外**？それとも **起こり得る失敗**？どっち？」
* 「例外で表すより Result の方が自然な箇所を指摘して」
* 「catch が増えすぎない設計にするなら、どこで変換するのが良い？」

## 使い方2：例外型の選定🤖🧠

* 「この throw は ArgumentException / InvalidOperationException / FormatException のどれが自然？」
* 「例外メッセージを UI 向けにするなら、どこで変換すべき？」

---

## 6.10 ミニチェックテスト✅🎀（3分でOK）

次のうち「例外が向いてる」のはどれ？（複数OK）🙂

1. ユーザーが Email 欄を空で送信
2. DB に接続できない
3. 注文が “配送済み” なのに “キャンセル” を実行しようとした
4. 外部決済APIがタイムアウトした

**目安**：

* 2,4 は例外寄り（外部障害・回復困難）
* 1 は Result 寄り（想定内の入力ミス）
* 3 は設計次第：Result にすることも多いけど、「絶対に起きない前提」なら例外でバグ検知でもOK（ただし慎重に）🧠✨ ([Microsoft Learn][3])

---

## 6.11 まとめ🏁✨

* 例外は **非常ベル**：処理が止まって上へ伝播する⚡
* **想定内の失敗（入力ミス）**に例外を使うと、境界が **catch地獄**になりがち😇
* 再スローは **throw;** が基本（throw ex; は事故）🧵
* catch (Exception) は乱用しない（CA1031 的にも注意）🧯 ([Microsoft Learn][4])

---

## 次の第7章の予告📣🧾✨

次は「入力ミスや業務的に起こり得る失敗」を **Result/戻り値で安全に返す**やり方をやるよ〜！
第6章で感じた「例外版のモヤモヤ」を、スッキリ解決しにいこっ🥰🎀

[1]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[2]: https://learn.microsoft.com/en-us/dotnet/standard/exceptions/?utm_source=chatgpt.com "Handling and throwing exceptions in .NET"
[3]: https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions?utm_source=chatgpt.com "Best practices for exceptions - .NET"
[4]: https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca1031?utm_source=chatgpt.com "CA1031: Do not catch general exception types"
[5]: https://learn.microsoft.com/en-us/dotnet/standard/exceptions/how-to-create-user-defined-exceptions?utm_source=chatgpt.com "How to: Create User-Defined Exceptions - .NET"
[6]: https://learn.microsoft.com/en-us/dotnet/fundamentals/syslib-diagnostics/syslib0051?utm_source=chatgpt.com "SYSLIB0051: Legacy serialization support APIs are obsolete"
