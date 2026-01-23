# 第15章 Nullable参照型で null 事故を減らす🚫null🧷✨

この章のテーマはひとことで言うと――
**「null を“許す場所”を境界に限定して、内部をスッキリ安全にする」**だよ😊💕

---

## 1) この章でできるようになること🎯✨

* `string` と `string?` の違いを、**「設計の意思表示」**として使える🙂🧠
* Nullable参照型（NRT）の**警告を“味方”にして**、NullReferenceException を減らせる🛡️
* **DTOはnullable OK / 内部モデルはnon-null前提**に整理できる🚪➡️🏛️
* 「最小コストで直す」ための**定番パターン**が手に入る🧰✨

> Nullable参照型の基本と有効化（`<Nullable>enable</Nullable>`）は Microsoft Learn のチュートリアルと仕様で確認できるよ。([Microsoft Learn][1])

---

## 2) null事故って、何がつらいの？😵‍💫💥

null事故の怖さは、**「壊れたのが“実行してから”分かる」**こと…！
たとえば、

* 画面入力で Email が空だった
* APIの JSON にプロパティが無かった
* DBの古いデータに欠損があった
* 外部APIが気まぐれで null を返した

…みたいなやつね😇💣

Nullable参照型（NRT）は、ここに対して
**「その変数、null入る可能性ある？」をコンパイラがうるさく言ってくれる機能**だよ👀✨

---

## 3) Nullable参照型（NRT）の基本🎀

### ✅ 3-1. `string` と `string?` の意味

* `string`：**null は入らない前提**（入れようとすると警告が出る）🛡️
* `string?`：**null が入りうる前提**（呼び出し側が丁寧に扱う）🤲

これってつまり、**型で意思表示**してるんだよね🙂✨
「この値は必須」「これは任意」を、コメントじゃなく型で言える💪

### ✅ 3-2. 有効化は2通り（全部 or 一部）

**プロジェクト全体で有効化**（おすすめ）
`.csproj` にこれ👇

```xml
<PropertyGroup>
  <Nullable>enable</Nullable>
</PropertyGroup>
```

**一部のファイルだけ有効化**（段階導入したい時）
ファイルの先頭にこれ👇

```csharp
#nullable enable
```

> `.NET 6` 以降の新規テンプレートは `<Nullable>enable</Nullable>` が入るようになっていて、古いプロジェクトは明示的に opt-in する説明があるよ。([Microsoft Learn][2])

---

## 4) よく見る警告の“読み方”👀📣

ここ、最初つまずきやすいから「ありがち」だけ先にまとめるね😊✨

### ⚠️ パターンA：`null` が入りうる値を、non-null に突っ込んでる

例：`string?` を `string` に代入、みたいなやつ。

対処はだいたい3択👇

1. **本当に null 来ない**なら、作る場所を直す（初期化/コンストラクタ/境界）
2. **null 来る**なら、型を `?` にして呼び出し側で扱う
3. その場で **`??`** などで吸収する（ただし設計的にOKなら）

### ⚠️ パターンB：初期化されない non-null プロパティ（いわゆる CS8618 系）

例：`public string Name { get; set; }` が、コンストラクタで必ず入る保証がない。

対処はだいたい👇

* コンストラクタで必ず入れる（いちばん綺麗）✨
* `required` を使って「初期化必須」を表現（ただし実行時保証は別途！）
* どうしてもなら `= ""` みたいにダミー初期化（最後の手段😇）

---

## 5) 「最小コストで直す」定番パターン5つ🧰✨

### ✅ パターン1：入口で null を弾く（ガード）🚪🛡️

「内部に入れない」が最強だよ😊

```csharp
public static void EnsureNotNull(object? value, string name)
{
    if (value is null) throw new ArgumentNullException(name);
}
```

使う側👇

```csharp
EnsureNotNull(request.Email, nameof(request.Email));
```

---

### ✅ パターン2：`??` / `??=` で“意味あるデフォルト”を入れる🧃

「空なら空でいい」じゃなくて、**仕様としてデフォルトが正しい**時だけね🙂

```csharp
var displayName = request.DisplayName ?? "名無し";
```

---

### ✅ パターン3：`is null` / `is not null` で分岐する🎭

読みやすくておすすめ✨

```csharp
if (email is null) return Result.Fail("Emailが必要です🥺");
```

---

### ✅ パターン4：`!`（null許容の打ち消し）は“最後の最後”😇🧨

`!` は「ここは絶対nullじゃないから黙って！」っていう宣言。

```csharp
var name = user.Name!; // ← 乱用すると事故る💥
```

使っていいのは、**人間の目で “絶対に null じゃない” が保証できる**時だけだよ🫠
（例：直前で `if (user.Name is null) return ...` 済み、など）

---

### ✅ パターン5：Try系 + Nullable属性で、コンパイラに“保証”を教える📚✨

`TryParse` 的な「成功したら non-null」を綺麗に表現できるやつ🎀

Microsoft Learn に Nullable解析用の属性がまとまってるよ。([Microsoft Learn][3])

例👇（成功時に `value` が non-null になるのを伝える）

```csharp
using System.Diagnostics.CodeAnalysis;

public static bool TryGetEmail(string? input, [NotNullWhen(true)] out string? value)
{
    if (string.IsNullOrWhiteSpace(input))
    {
        value = null;
        return false;
    }

    value = input.Trim().ToLowerInvariant();
    return true;
}
```

---

## 6) 本題🔥「null を境界に閉じ込める」設計パターン🚪➡️🏛️

ここが第15章のいちばん大事なところだよ😊💕

### 🎀 方針

* **境界（UI/API/DB/外部I/O）**：ゆるい（null来る前提）
* **内部（ドメイン）**：堅い（null来ない前提）

### 例：会員登録（API）📩👤

#### 6-1. 境界DTO（nullable OK）

```csharp
public sealed class RegisterRequestDto
{
    public string? Email { get; init; }
    public string? DisplayName { get; init; }
}
```

#### 6-2. 内部コマンド（non-null前提）

```csharp
public sealed record RegisterCommand(string Email, string DisplayName);
```

#### 6-3. 変換（ここで null を処理する！）🛡️

Result は第7章でやった想定で、軽い形にしてるよ🙂

```csharp
public sealed record Error(string Message);

public sealed class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public Error? Error { get; }

    private Result(bool ok, T? value, Error? error)
        => (IsSuccess, Value, Error) = (ok, value, error);

    public static Result<T> Ok(T value) => new(true, value, null);
    public static Result<T> Fail(string message) => new(false, default, new Error(message));
}

public static class RegisterMapper
{
    public static Result<RegisterCommand> ToCommand(RegisterRequestDto dto)
    {
        if (string.IsNullOrWhiteSpace(dto.Email))
            return Result<RegisterCommand>.Fail("Emailが空だよ🥺📧");

        if (string.IsNullOrWhiteSpace(dto.DisplayName))
            return Result<RegisterCommand>.Fail("表示名が空だよ🥺🏷️");

        var email = dto.Email.Trim().ToLowerInvariant();
        var name  = dto.DisplayName.Trim();

        return Result<RegisterCommand>.Ok(new RegisterCommand(email, name));
    }
}
```

✅ これで **内部は `RegisterCommand` を受け取った瞬間から non-null 前提で書ける**✨
nullチェック地獄から卒業できるよ🎓🎀

> 「nullable を設計に取り込む」チュートリアルも Microsoft Learn にあるよ。([Microsoft Learn][1])

---

## 7) ちょい最新トピック🍒：C# 14 の null 周り（読みやすさUP）✨

C# 14 では **null条件演算子の代入（null-conditional assignment）**が仕様として整理されていて、
`if (x is not null) x.Prop = ...;` を短く書ける場面が増えるよ🙂✨ ([Microsoft Learn][4])

たとえば👇（“いるなら代入する”）

```csharp
customer?.Order = GetOrder(customer.Id);
```

※ 便利だけど、「本当は居なきゃ困る」場面でこれを使うと、**バグが静かに消える**ので注意ね😇💥
（“必須ならガードで弾く”が基本！）

---

## 8) 演習（ミニ実践）🧪✨

### 演習1：DTOだけ nullable、内部を non-null にして警告を減らす🧹

1. `RegisterRequestDto` を nullable で作る
2. `RegisterCommand` は non-null にする
3. Mapper で `string.IsNullOrWhiteSpace` を使って弾く
4. 内部処理側で null チェックが不要になってるか確認👀✨

**チェックポイント✅**

* 内部ロジックで `?.` や `??` だらけになってない
* “必須”に対して `!` で黙らせてない

---

### 演習2：警告ログ貼り付け→「最小コスト修正」をAIに出させる🤖🛠️

AIへのお願い例👇（コピペでOK✨）

* 「この警告の意味を1行で」
* 「直し方を3案。最小修正 / 設計改善 / 将来拡張向け」
* 「`!` を使う場合は “使っていい根拠” も書いて」

---

### 演習3：Try系にして “成功時 non-null” をコンパイラに伝える🎯

`TryGetEmail` を作って、呼び出し側がこう書けるのを目標にしてね😊

```csharp
if (TryGetEmail(dto.Email, out var email))
{
    // この中では email が non-null 扱いになってほしい✨
    DoSomething(email);
}
```

Nullable属性の一覧はここが公式だよ。([Microsoft Learn][3])

---

## 9) まとめ🎀🧠✨

* Nullable参照型は **「nullが入りうるか？」を型で表現する道具**🧷
* **nullは境界に置く**（DTO/外部I/O）→ **内部は non-null 前提**が気持ちいい🏛️✨
* 警告は敵じゃなくて、**設計の穴を教えてくれるアラーム**🔔
* `!` は最終手段😇（使うなら“保証の根拠”が必須！）

---

## 次章へのつなぎ🔜🔢✨

次は **数値の不変条件（範囲・丸め・単位）**に入るよ！
Nullableで「存在」を守ったら、次は「値の正しさ」を固める感じ😊🛡️

[1]: https://learn.microsoft.com/ja-jp/dotnet/csharp/tutorials/nullable-reference-types "null 許容参照型を使用して設計する - C# | Microsoft Learn"
[2]: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/nullable-reference-types?utm_source=chatgpt.com "Nullable reference types - C#"
[3]: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/attributes/nullable-analysis?utm_source=chatgpt.com "Attributes interpreted by the compiler: Nullable static analysis"
[4]: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/proposals/csharp-14.0/null-conditional-assignment "Null conditional assignment - C# feature specifications | Microsoft Learn"
