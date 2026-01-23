# 第9章 “型で守る”入門：ifチェック地獄から卒業🎓✨

この章は、「**不変条件を“型”に引っ越し**して、ifチェックの重複を減らす」ための最初の一歩だよ〜😊💕

ちなみに今の最新ラインだと、.NET は **.NET 10（LTS）**、C# は **C# 14** が現行だよ📌✨ ([Microsoft for Developers][1])
（この章のサンプルは “いまのC#” で気持ちよく書ける形に寄せていくね🫶）

---

## 1) この章のゴール🎯💗

* 「`string` と `int` だけで全部表す」と何がつらいのか説明できる😵‍💫
* 「型＝安全な箱📦」の感覚が掴める🙂✨
* **プリミティブ地獄（Primitive Obsession）**を “少しずつ” 解消するリファクタ手順が分かる🛠️
  （これ、代表的なコードスメルとしてよく挙げられるよ）([リファクタリング・グル ][2])
* そして次章（第10章）の「**不正な値を作らせない**」にスムーズに入れる🚀✨

---

## 2) まず「ifチェック地獄」って何？😇💥

たとえばこんな感じ👇
「メール形式チェック」「空白チェック」「金額が負数じゃないか」…が、**あちこちに散らばる**やつ😵‍💫

* 同じチェックがコピペで増える📎
* 片方だけ直して、もう片方は古いまま…が起きる😱
* そもそも「この `string` ってメール？ユーザー名？住所？」が分からない🌀

で、バグる💥（そして泣く😭）

---

## 3) `string/int` のままが危ない理由😱🧨

### 3-1. “意味”が型に乗ってない🫥

`string email` と書いても、コンパイラ的にはただの `string`。
**Emailっぽい文字列**も、**UserNameっぽい文字列**も、全部 `string` で区別不能🥲

### 3-2. “取り違え”がコンパイルで止まらない🙈

たとえば👇

* `userName` と `email` を入れ替えて渡しても、型が同じだから通る😇
* `price`（円）と `point`（ポイント）を混ぜても通る😇

### 3-3. ルールが拡散して、修正が地獄👹

「メールはtrimして小文字にする」と決めたのに、
修正箇所が10箇所あったら…？😵‍💫

これが **Primitive Obsession（プリミティブ偏愛）** の典型パターンだよ〜🧟‍♀️ ([リファクタリング・グル ][2])

---

## 4) 解決の考え方：「型＝安全な箱」📦🛡️

### 4-1. “外”はゆるく、“中”はかたく🏰✨

* 外（UI入力/HTTP/DB）は、どうしても `string` とか `int` が来る
* でも中（ドメイン）は、**壊れた値を入れたくない**

だからやることはシンプル👇

✅ **境界（入口）で `string/int` を “意味ある型” に変換**
✅ 中では **意味ある型だけ** を使う

---

## 5) 型の厚みは3段階あるよ🧁✨

この章では、まず **①②** を触って「型で守れる感覚」を作るよ😊
（③は次章でガッツリ！）

1. **命名で意味を乗せる**（まだ `string` だけど意識が変わる）
2. **薄いラッパ型**（取り違えがコンパイルで止まる🎉）
3. **生成を集中して不正値を作れない**（Factory/検証/Result ← 第10章）

---

## 6) ハンズオン：サブスク登録を “型で” 安全にする💳🌸

題材：サブスク登録（会員 + 月額課金）🎀

### 6-1. まずは “危ない版” 😇💥

```csharp
public static void Register(string userName, string email, int monthlyFeeYen)
{
    if (string.IsNullOrWhiteSpace(userName)) throw new ArgumentException("userName");
    if (string.IsNullOrWhiteSpace(email)) throw new ArgumentException("email");
    if (monthlyFeeYen < 0) throw new ArgumentException("monthlyFeeYen");

    // どこか別の場所でも同じチェックをまた書く…😵‍💫
}
```

この状態だと、こういう事故が起きやすい👇😱

```csharp
Register(email, userName, monthlyFeeYen); // 入れ替えてもコンパイル通っちゃう😭
```

---

### 6-2. “薄いラッパ型” にして取り違えを止める🛡️✨

まずは「意味の違うものは、型を分ける」だけでOK🙆‍♀️

```csharp
public readonly record struct UserName(string Value);
public readonly record struct Email(string Value);
public readonly record struct Yen(int Value);
```

そして署名を変える👇✨

```csharp
public static void Register(UserName userName, Email email, Yen monthlyFee)
{
    // ここでは「意味が合ってる値が来る前提」で書きやすくなる🙂
    // まだこの章では「不正値を作れない」まではやらないよ（次章！）
}
```

これだけで超でかい進歩💥🎉

```csharp
Register(new Email("a@b.com"), new UserName("komi"), new Yen(980));
// ↑ もし入れ替えたらコンパイルで止まる✨
```

✅ **取り違えが“実行時バグ”から“コンパイルエラー”になる**
これ、めっちゃ強いよ〜🫶💕

---

### 6-3. 「じゃあ入力は結局 string で来るんだけど？」問題🤔🧩

うん！来る！
だから **境界で変換**する（第8章の復習っぽいところ）🚪🔁

たとえば画面入力DTOがこう👇

```csharp
public sealed class RegisterRequest
{
    public string UserName { get; set; } = "";
    public string Email { get; set; } = "";
    public int MonthlyFeeYen { get; set; }
}
```

境界で “薄い型” に詰め替える👇

```csharp
public static void RegisterFromRequest(RegisterRequest req)
{
    // ここ（境界）で string/int → 意味のある型 に変換する
    var userName = new UserName(req.UserName);
    var email = new Email(req.Email);
    var fee = new Yen(req.MonthlyFeeYen);

    Register(userName, email, fee);
}
```

この章の到達点はここまででOK🙆‍♀️✨
次章で「`new Email(...)` 自体を禁止にして、Createでしか作れない」みたいにしていくよ🏭🔒

---

## 7) “型で守る” リファクタ手順（迷子防止マップ🗺️✨）

### Step A：ドメイン用語を3つ拾う🔍

例）

* Email（メール）
* UserName（表示名）
* Yen（円）

### Step B：まずは「引数/戻り値」から型を差し替える🧷

特におすすめは👇

* **重要な関数の引数**（取り違え防止が効く）
* **ドメインの戻り値**（以降の処理が安全になる）

### Step C：境界に “詰め替え” を置く🚪📦

* DTOはゆるく
* ドメインはかたく

### Step D：コンパイルエラーを道しるべに進める🧭✨

型を変えるとエラーが出る → そこが “直すべき接続点”
コンパイラが案内係になってくれるの、最高だよね😆💕

---

## 8) AI活用コーナー🤖💞（案出し係にしよう）

### 8-1. 「型にした方がいい候補」出してもらう🔍

プロンプト例👇

```text
このC#コードの引数やフィールドのうち、Primitive Obsessionになってそうなものを列挙Remember that。  
それぞれ「新しい型名案」「その型が守るべき不変条件」をセットで提案して。
```

### 8-2. 「薄いラッパ型」を一気に作ってもらう🏭

```text
次のドメイン用語の薄いラッパ型（record struct）を作って。
UserName, Email, Yen
Valueプロパティ名は Value で統一して。
```

AIは便利だけど、**型名**と**意味**だけはあなたが決めてOKだよ😊🫶
（命名は設計のど真ん中✨）

---

## 9) 演習📝🎀（この章はここがメイン！）

### 演習1：あなたのアプリで「string/int地獄」候補を3つ挙げてね👀

例：

* `string` : Email / UserName / ProductCode / Address
* `int` : Yen / Point / Age / Quantity

「なぜ型にしたいか」を1行で書く✍️✨
（第9章アウトラインの課題そのまま🎓）

---

### 演習2：取り違え事故を “コンパイルエラー” に変える🛡️

次のうち1個を選んで、薄い型にしてみてね👇

* `Email`
* `Money（Yen）`
* `UserName`

そして、わざと引数を入れ替えて **コンパイルで止まる**のを確認👀✨
「止まった！」が成功体験だよ〜🎉🎉🎉

---

### 演習3：境界の詰め替え関数を作る🚪🔁

DTO → 薄い型 → ドメイン関数呼び出し
この “1本道” を作ってみよう😊💕

---

## 10) まとめ🏁✨

* `string/int` だけで全部表すと、意味が消えて事故る😱
* **型を分ける**だけで「取り違え」がコンパイルで止まる🎉
* 入口で `string/int` を受けて、**境界で型に詰め替える**のが基本形🚪📦
* 次章で「**不正な値を作れない**（new禁止ゾーン）」に進化させるよ🏭🔒

C# 14 / .NET 10 の現行ラインでガンガン書ける設計にしていくね😊✨ ([Microsoft Learn][3])

---

次に進む前に確認だけ💡
第10章で `Email.Create(string)` みたいに「作り方を1箇所に固定」していくんだけど、題材はこのまま **サブスク課金**で統一して進めちゃうね？💳🎀

[1]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
[2]: https://refactoring.guru/refactoring/smells?utm_source=chatgpt.com "Code Smells"
[3]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-version-history?utm_source=chatgpt.com "The history of C# | Microsoft Learn"
