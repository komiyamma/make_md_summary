# 第5章 入口で守る：Validationを“仕様”にする📜✨

この章は「第4章のガード節🛡️（入口で即弾く）」を **もう一歩だけ進めて**、
**検証ルールを “仕様書みたいに読める形” に整える** 練習だよ〜🙂🎀

（C# 14 / .NET 10 世代の書き味でいくね✨） ([Microsoft Learn][1])

---

## 0) 今日のゴール🏁🎉

できるようになること👇

* 入口の検証ルールを **「仕様（箇条書き）」→「コード」** に落とせる📝➡️💻
* 検証結果を **「エラーコード＋説明」** で返して、呼び出し側（UI/API）が扱いやすくなる📦✨
* **テストケース** を先に考えて、Validationが壊れないように守れる🧪🛡️
* AIに「抜けチェック」「テスト増殖」をやらせて時短できる🤖⚡

---

## 1) ガード節とValidationの違い（ここ大事）🛡️✨

## ガード節🛡️

* 目的：**その場で即死を防ぐ**（null/空/範囲外など）
* 例：`if (x is null) return ...;`

## Validation📜

* 目的：**「仕様としてのルール」を並べて、理由付きで返す**
* 例：`Emailは必須 / 形式 / 正規化 / 長さ / 重複禁止 …`

つまりこの章は、入口で守るのは同じでも
**“チェックの集合” を仕様として設計する章**だよ🙂📚✨

---

## 2) まずは「仕様」を箇条書きで書く📝🎀

題材は「会員登録（サブスク想定）」にするね😊
入力は境界（UI/API）から来るDTOって感じ👇

## 仕様（Validationルール）例📜✨

**SignUp（会員登録）**

* Email

  * 必須（空・空白だけはNG）🚫
  * 前後の空白はトリムする🧼
  * 小文字に正規化する（運用ルールとして）🔡
  * 形式がメールっぽいこと（ゆるめでOK）📧
  * 長すぎないこと（例：254文字以内）📏
* Password

  * 必須🚫
  * 12文字以上🔐
* Plan

  * `Basic / Pro / Student` のどれか🎫
* AgreeToTerms

  * true必須✅

ここでのコツ👇
**「仕様の文章がそのままコードの関数名になる」** ように書くのが勝ち🏆✨

---

## 3) “仕様っぽさ”を出す3点セット🧰✨

Validationを仕様に見せるには、これが効くよ👇

## ✅(1) ルールに名前を付ける🏷️

* `Email_IsRequired`
* `Email_IsValidFormat`
* `Password_MinLength`
  みたいに「読めば意味が分かる名前」にする🙂✨

## ✅(2) エラーは “コード＋人間向け文” にする📣

* コード：機械が扱う（分岐・ログ・分析）🤖
* メッセージ：人が読む（画面表示）🙂

## ✅(3) 1回で複数エラーを返せるようにする🧺

「EmailもPasswordもダメ」をまとめて返すと、UXが良い🎀✨

---

## 4) 実装してみよう（最小で気持ちいいやつ）💻✨

## 4-1) エラー表現（仕様の器）📦

```csharp
public sealed record ValidationError(string Code, string Message, string? Target = null);

public sealed class ValidationResult
{
    private readonly List<ValidationError> _errors = new();
    public IReadOnlyList<ValidationError> Errors => _errors;
    public bool IsValid => _errors.Count == 0;

    public void Add(string code, string message, string? target = null)
        => _errors.Add(new ValidationError(code, message, target));
}
```

* `Code`：仕様のID（後で超助かる）🏷️
* `Target`：どの項目？（UIで赤枠にする時とか便利）🎯

---

## 4-2) 入力DTO（境界のゆるい箱）🎁

```csharp
public sealed record SignUpRequest(
    string? Email,
    string? Password,
    string? Plan,
    bool AgreeToTerms
);
```

---

## 4-3) Validator（仕様をコード化する本体）📜➡️💻

```csharp
public static class SignUpValidator
{
    public static (SignUpRequest Normalized, ValidationResult Result) Validate(SignUpRequest input)
    {
        var result = new ValidationResult();

        // 正規化（仕様！）
        var email = (input.Email ?? "").Trim().ToLowerInvariant();
        var password = input.Password ?? "";
        var plan = (input.Plan ?? "").Trim();

        // 仕様：Email 必須
        if (string.IsNullOrWhiteSpace(email))
            result.Add("Email.Required", "メールアドレスを入力してね📧", target: "Email");

        // 仕様：Email 長さ
        if (!string.IsNullOrEmpty(email) && email.Length > 254)
            result.Add("Email.TooLong", "メールアドレスが長すぎるよ🥺（254文字以内）", target: "Email");

        // 仕様：Email 形式（ゆるめ）
        if (!string.IsNullOrEmpty(email) && !LooksLikeEmail(email))
            result.Add("Email.InvalidFormat", "メールアドレスの形が変かも…📧💦", target: "Email");

        // 仕様：Password 必須
        if (string.IsNullOrEmpty(password))
            result.Add("Password.Required", "パスワードを入力してね🔐", target: "Password");

        // 仕様：Password 最小長
        if (!string.IsNullOrEmpty(password) && password.Length < 12)
            result.Add("Password.MinLength", "パスワードは12文字以上が安心だよ🔒✨", target: "Password");

        // 仕様：Plan は候補のどれか
        if (!IsAllowedPlan(plan))
            result.Add("Plan.Invalid", "プランは Basic / Pro / Student から選んでね🎫", target: "Plan");

        // 仕様：規約同意は必須
        if (!input.AgreeToTerms)
            result.Add("Terms.Required", "利用規約に同意が必要だよ✅", target: "AgreeToTerms");

        var normalized = input with { Email = email, Plan = plan };
        return (normalized, result);
    }

    private static bool IsAllowedPlan(string plan)
        => plan is "Basic" or "Pro" or "Student";

    private static bool LooksLikeEmail(string email)
    {
        // 正規表現ゴリゴリはやりすぎになりがちなので “ほどほど” に🙂
        var at = email.IndexOf('@');
        if (at <= 0) return false;
        if (at != email.LastIndexOf('@')) return false;
        var dot = email.LastIndexOf('.');
        return dot > at + 1 && dot < email.Length - 1;
    }
}
```

## ここが「仕様っぽい」ポイント💡✨

* `Email.Required` みたいに **コードが仕様ID**になってる📜🏷️
* 「正規化（trim/lower）」も仕様として明示してる🧼🔡
* 1回のValidateで **複数エラーが溜まる**🧺✨

---

## 5) 入口（API/画面）での使い方イメージ🚪✨

ここでは「入口で受けて、Validationして、外向けに返す」が目的🙂

```csharp
var (normalized, vr) = SignUpValidator.Validate(req);
if (!vr.IsValid)
{
    // UIならフォームに表示、APIなら400で返す、みたいな変換はここで🎀
    return Results.BadRequest(new { errors = vr.Errors });
}

// ここから先は「正しい入力」だけが通る世界🌈✨
```

（この “外向け変換” は第8章でさらに綺麗にやるよ〜🚪🔁）

---

## 6) テストで「仕様」を固定する🧪🛡️

Validationは仕様そのものだから、**テストが超相性いい**よ🙂✨
xUnit例👇

```csharp
using Xunit;

public class SignUpValidatorTests
{
    [Fact]
    public void Email_is_required()
    {
        var req = new SignUpRequest(Email: "   ", Password: "123456789012", Plan: "Basic", AgreeToTerms: true);
        var (_, vr) = SignUpValidator.Validate(req);

        Assert.False(vr.IsValid);
        Assert.Contains(vr.Errors, e => e.Code == "Email.Required");
    }

    [Fact]
    public void Password_min_length_12()
    {
        var req = new SignUpRequest(Email: "a@b.com", Password: "short", Plan: "Basic", AgreeToTerms: true);
        var (_, vr) = SignUpValidator.Validate(req);

        Assert.Contains(vr.Errors, e => e.Code == "Password.MinLength");
    }
}
```

---

## 7) 演習✍️🎀（箇条書き→コードに落とす）

## 演習A：仕様を書いてから実装📝➡️💻

次の仕様を「あなたの言葉」で箇条書きして、同じ形でValidatorにしてみてね🙂✨

* UserName（表示名）

  * 必須
  * 3〜20文字
  * 前後空白はトリム
  * 禁止文字（例：改行・タブ）NG

**提出物（自分用でOK）**

1. 仕様箇条書き📜
2. エラーコード一覧🏷️
3. Validator実装💻

---

## 演習B：テストケースを先に作る🧪✨

境界値で5個だけ作ってみて👇

* ちょうど3文字✅
* 2文字❌
* ちょうど20文字✅
* 21文字❌
* `"\n"`入り❌

---

## 8) AIの使いどころ（この章はめちゃ相性いい）🤖🧪✨

## 8-1) “仕様→テストケース” を増殖させる🧫

AIにこれを投げる👇

* 「この仕様から境界値テストを20個ください。正常/異常を混ぜて。エラーコードも付けて」

👉 テストが一気に増えて安心感が爆上がり🧪🛡️✨

## 8-2) “抜け” をレビューさせる🔍

* 「このValidation仕様、抜けがちな落とし穴を指摘して」
* 「悪用パターン（空白、全角、長文、特殊文字）を増やして」

## 8-3) メッセージを “優しい日本語” に整える🎀

* 「女子大生に説明する感じで、短くて優しい文にして。絵文字も少し添えて」

---

## 9) ありがちな落とし穴あるある⚠️🥺

* 仕様がコードに埋もれて「どこに何が書いてあるか分からない」😵‍💫
  → **エラーコード＋関数名**で仕様っぽくする🏷️✨
* 正規表現で完璧を目指して沼る🌀
  → 入口は “ほどほど” でOK、厳密は必要になってから🙂
* UI/APIで同じValidationを二重実装しちゃう😭
  → **入口で1回**、表示用に変換するだけ🎀

---

## 10) まとめ🏁🎉

この章のコアはこれ👇🙂✨

* Validationは「チェック」じゃなくて **仕様**📜
* 仕様を **名前（コード）** として残す🏷️
* 仕様を **テスト** で固定する🧪🛡️
* AIは「抜け探し」「テスト量産」で最強の相棒🤖⚡

---

## おまけ：いまの開発環境まわりの“最新”メモ🧷✨

* C# 14 の最新情報（拡張メンバーなど）は Microsoft Learn と .NET Blog が基点になるよ📚✨ ([Microsoft Learn][1])
* .NET 10 の全体像（C# 14含む）は公式の “What’s new” がまとまってるよ🧠✨ ([Microsoft Learn][2])
* Visual Studio 2026 のリリースノートも公式にまとまってる（Insidersもあるよ）🛠️✨ ([Microsoft Learn][3])
* Visual Studio 2022 の現行更新もちゃんと履歴が追えるよ（2026-01-13 の更新が載ってる）📅✨ ([Microsoft Learn][4])

---

次の第6章は「失敗の表現①：例外って何者？⚡😵‍💫」だけど、
その前に質問！😊🎀

**第5章の演習題材、会員登録のまま続ける？それとも「注文・カート」系がいい？🛒✨**

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/overview?utm_source=chatgpt.com "What's new in .NET 10"
[3]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
[4]: https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-history?utm_source=chatgpt.com "Visual Studio 2022 Release History"
