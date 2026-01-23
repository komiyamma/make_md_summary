# 第10章 不正な値を作らせない：Factoryで生成を集中🏭🔒

## まず今日のゴール🎯✨

この章が終わったら、こんなことができるようになります😊

* 「new された瞬間に壊れてる」みたいな値を **作れない** ようにできる🧱🔒
* 「生成（作る）」の入口を **1か所に集約** して、ルールが散らばらないようにできる🏭✨
* 生成に失敗したとき、例外じゃなく **Result（成功/失敗）** で安全に返せる📦🙂

そして次の第11〜13章（Value Object連続）へ、めちゃスムーズに繋がります📈💎

---

## 1. なんで「new」が危ないの？😱🧨

「文字列のメールアドレス」を例にすると…

* 空文字の Email
* @ が無い Email
* 前後に空白がある Email（気づかずDBに入る）
* でたらめだけど “たまたま通っちゃう” Email

こういうのって、**作れた時点で負け** なんです🥲💥
一度システムに入ると、あちこちで if チェックが増えて「if地獄」へ…（第9章のやつ！）😵‍💫🌀

なので発想を逆転します👇
✅ **「不正な値を作れない」ようにする**
これが Factory（生成の集中）です🏭🔒

---

## 2. Factoryの基本形：private コンストラクタ + Create🏗️🛡️

やることはシンプル✨

* コンストラクタを private にする（外から new できない）
* 静的メソッド（Create / TryCreate / From など）だけが作れる
* Create の中で検証＆正規化（trim など）して、OKなら生成✅

---

## 3. 2026年の前提：C# 14 + .NET 10（LTS）を使うよ🧁✨

いまの「最新の土台」はこんな感じです👇（2026-01-20時点）

* **C# 14 は 2025年11月リリース** とされ、公式の履歴にも載っています📚✨ ([Microsoft Learn][1])
* **.NET 10 は LTS** で、配布ページでは **10.0.2（2026-01-13）** が “latest” として並んでいます🧩⬆️ ([Microsoft][2])
* さらに .NET Blog の 2026年1月の更新でも **.NET 10.0.2** が明記されています🛠️🗞️ ([Microsoft for Developers][3])

（※Factory自体は言語バージョンに左右されにくいけど、最新環境で書くと気持ちいいのでこれでいきます😊）

---

## 4. まずは「Result型」を用意しよう📦🙂

第7章でやった「失敗を戻り値で返す」を、ここでも使います💪✨
ここでは “ミニResult” を自作します（軽くて学びやすい）🎀

### Resultの設計方針🧠✨

* 成功：値（Value）が入ってる✅
* 失敗：エラー一覧（Errors）が入ってる❌
* 例外は「想定外」へ寄せる（第6章の話）⚡

---

## 5. 実装してみよう：Email.Create(string)🏭📧

### 5-1. DomainError と Result<T> を作る🧱✨

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public sealed record DomainError(string Code, string Message);

public sealed class Result<T>
{
    private Result(bool isSuccess, T? value, IReadOnlyList<DomainError> errors)
    {
        IsSuccess = isSuccess;
        Value = value;
        Errors = errors;
    }

    public bool IsSuccess { get; }
    public bool IsFailure => !IsSuccess;

    public T Value { get; }  // 成功時だけ使う想定
    public IReadOnlyList<DomainError> Errors { get; }

    public static Result<T> Ok(T value)
        => new(true, value, Array.Empty<DomainError>());

    public static Result<T> Fail(params DomainError[] errors)
        => new(false, default, errors);

    public static Result<T> Fail(IEnumerable<DomainError> errors)
        => new(false, default, errors.ToArray());
}
```

ポイント💡😊

* 失敗時の Value は使わない前提（使うときは IsSuccess を見てね）
* エラーは Code を持たせると、UI表示やログが整理しやすいです🏷️✨

---

### 5-2. Email を「new禁止」にする🔒🚫

```csharp
using System;

public sealed class Email
{
    private Email(string value)
    {
        Value = value;
    }

    public string Value { get; }

    public static Result<Email> Create(string? raw)
    {
        // 1) null/空白チェック
        if (string.IsNullOrWhiteSpace(raw))
        {
            return Result<Email>.Fail(
                new DomainError("email.empty", "メールアドレスを入力してね🙂📧")
            );
        }

        // 2) 正規化（まず trim）
        var trimmed = raw.Trim();

        // 3) 超ミニ構文チェック（正規表現でガチらない方針🙂）
        //    - '@' が1個
        //    - 先頭/末尾が '@' じゃない
        var atIndex = trimmed.IndexOf('@');
        if (atIndex <= 0 || atIndex != trimmed.LastIndexOf('@') || atIndex == trimmed.Length - 1)
        {
            return Result<Email>.Fail(
                new DomainError("email.format", "メールアドレスの形式が変かも…😵‍💫 例：a@b.com")
            );
        }

        // 4) ここまで来たら「Emailとして成立」🎉
        return Result<Email>.Ok(new Email(trimmed));
    }

    public override string ToString() => Value;
}
```

ここが超大事🛡️✨
✅ Email は private コンストラクタなので、外から new Email(" ") ができません
つまり **不正な Email が“型として存在”できない** ようにしてます🏰🔒

---

## 6. 使う側（境界側）はこうなる🚪🔁

たとえば「会員登録フォーム」から来た raw string を内部へ入れるとき👇

```csharp
public static Result<string> RegisterMember(string? emailText)
{
    var emailResult = Email.Create(emailText);
    if (emailResult.IsFailure)
    {
        // ここはUI/API向けの表現に変換する場所（第8章の話）🎀
        var message = string.Join("\n", emailResult.Errors.Select(e => e.Message));
        return Result<string>.Fail(new DomainError("register.invalid", message));
    }

    Email email = emailResult.Value;

    // 本来はDB保存など…（今は省略）
    return Result<string>.Ok($"登録できたよ🎉 Email={email.Value}");
}
```

気持ちよさポイント😍✨

* 変な email が入ってきても、**境界で止めて** 内部へ入れない🛡️
* 内部のコードは Email 型を信じて進める（if地獄が減る）🎓

---

## 7. 命名どうする？Create / TryCreate / From 🏷️🤔

結論：迷ったらこれでOK🙆‍♀️✨

* **Create**：失敗理由が欲しい（Resultで返す）📦
* **TryCreate**：boolで軽く判定したい（outで値）🙂
* **From**：すでに正しい値だと “強く” 信じる（内部専用にしがち）⚠️

このへんの “好み” はチームで統一が一番強いです🤝✨
（公式ドキュメント上でも、C#はAPI表現の幅が広いので「読みやすさ優先」が勝ちやすいです🙂）

---

## 8. よくある落とし穴🕳️🐾

### 落とし穴①：record struct にすると default が怖い😱

struct は必ず default が作れちゃいます（Email の default が “空” みたいな）💥
不変条件をガチで守りたい章の流れでは、まずは class（参照型）で作るのが安全です🛡️✨

### 落とし穴②：正規表現で頑張りすぎる🤯

メールの仕様は奥が深すぎて、初心者が完璧を目指すと沼りがちです🌀
この教材では「必要十分」でOK🙂✨（KISS精神）

### 落とし穴③：Createの外で勝手に正規化する

trim をあちこちでやると、ルールが散らばります😵‍💫
**正規化はCreateに寄せる** が勝ちです🏭✨

---

## 9. ミニ演習（手を動かすやつ）🧪🔥

### 演習A：Email.Create を強化しよう💪📧

次のルールを追加してみてね👇

* 先頭と末尾の空白は削る（もうやった！）🧼
* 連続した空白を弾く（例：a @b.com）🚫
* エラーメッセージを “ユーザー向け” に調整する📣

### 演習B：Errorを複数返せるようにする🧾✨

今は「1個のエラーで返す」ことが多いけど、
「まとめて返したい」ケースもあります🙂
Result.Fail に複数の DomainError を渡して、UIに一覧表示してみよう✅

### 演習C：会員登録のコマンドを作る🎀🧱

* RegisterMemberCommand（EmailText など）を作る
* 境界で Email.Create を呼ぶ
* 成功なら Email 型だけを内部に渡す

---

## 10. AI（Copilot / Codex）に頼ると強いところ🤖✨

“AIは案出し係＋テスト量産係” が最強です💪🎉

### そのまま投げてOKなプロンプト例🪄

* 「Email.Create の境界値テストケースを 20 個、成功/失敗に分類して出して」🧪🤖
* 「DomainError の Code 命名案を、短く一貫性ある形で 10 個出して」🏷️🤖
* 「この Create を読みやすくリファクタして。初心者にも追える形で」🧹🤖
* 「TryCreate(out Email) 版も追加して、使い分け方もコメントで」🧩🤖

---

## 11. まとめ：この章で手に入れた武器🛡️🎀

* 不変条件は “あとで守る” じゃなくて **作る瞬間に守る** 🏭🔒
* private ctor + Create で **生成の入口が1つ** になる✨
* Resultで返すと、境界で **丁寧にエラー表示** できる🙂📣
* 次章（MoneyなどのValue Object）で、この形がそのまま増殖していく💰💎

---

## おまけ：自分チェックリスト✅✨

* [ ] 型のコンストラクタは外から呼べない（new禁止）🔒
* [ ] Create の中に「検証＋正規化」がまとまってる🏭
* [ ] 成功/失敗が Result で表現できてる📦
* [ ] 境界で変換して、内部に raw string を持ち込んでない🚪🧼

---

次の第11章は、このFactoryの形をそのまま使って **Money（通貨＋金額）** を作ります💰💎
「丸め」「負数OK？」「通貨違いの加算禁止」みたいな、型で守ると気持ちいいやつがいっぱいです🥳✨

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-version-history?utm_source=chatgpt.com "The history of C# | Microsoft Learn"
[2]: https://dotnet.microsoft.com/en-us/download/dotnet "Browse all .NET versions to download | .NET"
[3]: https://devblogs.microsoft.com/dotnet/dotnet-and-dotnet-framework-january-2026-servicing-updates/ ".NET and .NET Framework January 2026 servicing releases updates - .NET Blog"
