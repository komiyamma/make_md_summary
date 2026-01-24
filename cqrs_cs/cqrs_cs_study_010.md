# 第10章　プロジェクト構成（フォルダ・命名・責務）📁✨

この章はね、「**コードの置き場所ルール**」を先に決めて、**迷子にならないCQRS**にする回だよ〜！😺🧭💕

---

## 0. まず結論：CQRSは「置き場所」を決めないと崩壊しやすい😇💥

CQRSって「読む/書く」を分けるから、放っておくと…

* Command がいろんな所に散らばる🧨
* Query が肥大化して見つからない🫠
* Handler が神クラス化する👑💦

…ってなりやすいの。なので **“構成ルール”を先に固定**しちゃおうね！📌✨

---

## 1. この章で作る「迷わない3点セット」🎁

この章のゴールはこれ👇

1. **フォルダ構成**（どこに何を置くか）📁
2. **命名規約**（名前を見ただけで役割が分かる）🏷️
3. **責務ルール**（Controller/Handler/DBの境界）🚧

---

## 2. おすすめ構成：最初は「縦割り（Feature）+ CQRS箱」🍱✨

初心者にいちばん優しいのは **“機能ごと（Featureごと）”** にまとめる構成だよ！
例：Orders（注文）/ Products（商品）/ Customers（顧客）みたいに。

### ✅ フォルダ例（1プロジェクトで始める版）

※学習用の最小形。後で複数プロジェクトに分割できるよ👍

```text
MyApp/
  Features/
    Orders/
      Commands/
        CreateOrder/
          CreateOrderCommand.cs
          CreateOrderHandler.cs
          CreateOrderValidator.cs
      Queries/
        GetOrderList/
          GetOrderListQuery.cs
          GetOrderListHandler.cs
          OrderListItemDto.cs
      Contracts/
        OrderId.cs
    Products/
      ...
  Infrastructure/
    Db/
      AppDbContext.cs
      Migrations/
    Repositories/
  Shared/
    Abstractions/
      ICommand.cs
      IQuery.cs
      IResult.cs
    Errors/
      DomainError.cs
    Time/
      IClock.cs
  Api/
    Endpoints/
      OrdersEndpoints.cs   (Minimal APIならここ)
    Controllers/
      OrdersController.cs  (Controllerならここ)
  Program.cs
```

### ここでの考え方（超大事）📌

* **Features**：ユースケースの置き場（CQRSの主戦場）⚔️
* **Api**：受け取って渡すだけ（薄く！）📮
* **Infrastructure**：DBや外部サービス（現実担当）🧱
* **Shared**：共通の最低限（増やしすぎ注意！）⚠️

ASP.NET Core は Controller ベースのWeb API と Minimal API の両方が選べるよ〜（どっちでもOK！）😺✨ ([Microsoft Learn][1])

---

## 3. もう一段きれいに：Solutionを「4プロジェクト」に分ける版🏗️✨

チーム開発っぽくしたいなら、早めに分けると後がラク！💕

```text
src/
  MyApp.Api/            // HTTPの入口だけ
  MyApp.Application/    // Handler/UseCase（CQRSの中心）
  MyApp.Domain/         // 業務ルール（Entity/ValueObjectなど）
  MyApp.Infrastructure/ // EF Core, 外部APIなど
tests/
  MyApp.Tests/
```

### 依存の向き（これが“設計”の正体😎）

* Api → Application
* Application → Domain
* Infrastructure → Application/Domain（実装で依存してOK）
* Domain は誰にも依存しない（理想）✨

---

## 4. 命名規約：これだけ固定すれば迷子ほぼゼロ🏷️🐣

### ✅ Command / Query / Handler の命名テンプレ

* `CreateXxxCommand`（書く）✍️
* `GetXxxQuery`（読む）👀
* `CreateXxxHandler` / `GetXxxHandler`（さばく人）🧑‍🍳

### ✅ DTOの命名（読み側は“画面都合”でOK）

* 一覧：`XxxListItemDto`
* 詳細：`XxxDetailsDto`
* 検索条件：`XxxSearchDto`（または `XxxFilter`）

### ✅ フォルダ名とNamespaceは揃える

「ファイル場所」と「namespace」がズレると、後で地獄🔥なので揃えようね！😇

---

## 5. 責務ルール：Controller/Handler/DB の境界線を引く🚧✨

### ✅ Controller / Minimal API がやること

* リクエストを受け取る📨
* DTOを作る（or バインド）🧩
* Handler に渡す📮
* 結果をHTTPに変換して返す📤

**禁止：**

* 業務ルール判断をしない🙅‍♀️
* DBアクセスしない（基本）🙅‍♀️
* でっかいif地獄を作らない🙅‍♀️

### ✅ Handler がやること（ここが主役）

* 1ユースケースを完結させる🎯
* ルールチェック（必要ならDomainへ）🏛️
* DB更新（Write）or 取得（Read）を呼ぶ🧱
* “結果”を返す（成功/失敗/IDくらい）✅

---

## 6. 具体例：CreateOrder を「正しい置き場所」で置く📦✨

### 例：Command と Handler（形だけ覚えよう）

```csharp
// Features/Orders/Commands/CreateOrder/CreateOrderCommand.cs
public sealed record CreateOrderCommand(int CustomerId, IReadOnlyList<int> ProductIds);

// Features/Orders/Commands/CreateOrder/CreateOrderHandler.cs
public sealed class CreateOrderHandler
{
    private readonly AppDbContext _db;

    public CreateOrderHandler(AppDbContext db) => _db = db;

    public async Task<int> Handle(CreateOrderCommand command, CancellationToken ct)
    {
        // ここに「注文を作る」ユースケースを書く（必要ならドメインルールへ）
        var order = new Order(command.CustomerId);
        foreach (var productId in command.ProductIds)
            order.AddItem(productId);

        _db.Orders.Add(order);
        await _db.SaveChangesAsync(ct);

        return order.Id; // 返しすぎない（第11章で詳しくやるよ）
    }
}
```

この“置き場所”が大事で、`CreateOrder` 関連が**全部同じフォルダ**にあるだけで、探す時間が激減するよ⏱️💕

---

## 7. ミニ演習：あなたのプロジェクトを“迷わない形”に整える🛠️✨

所要：30〜60分くらい（じっくりでOK）😊☕️

### ステップ1：Featuresを作る📁

* `Features/Orders/Commands`
* `Features/Orders/Queries`

### ステップ2：今あるコードを「読む/書く」で振り分ける✂️

* 更新系 → `Commands` へ
* 参照系 → `Queries` へ

### ステップ3：命名をテンプレに合わせる🏷️

* `CreateOrder` / `GetOrderList` みたいに、**ユースケース名をフォルダ名に**するのがおすすめ！✨

### ステップ4：READMEに“ルール”を書く📄

あとで自分が忘れるからね！🤣（未来の自分を助けるやつ）

---

## 8. READMEに貼る「命名規約テンプレ」📄✨

そのままコピペしてOKだよ〜！

```text
## CQRS 命名・配置ルール

- 1ユースケース = 1フォルダ
  Features/<Feature>/(Commands|Queries)/<UseCase>/

- Command: 〜Command
- Query: 〜Query
- Handler: 〜Handler

- Read DTO:
  - 一覧: 〜ListItemDto
  - 詳細: 〜DetailsDto

- Api層は薄く（受け取って投げるだけ）
- 業務ルールはHandler or Domainへ
```

---

## 9. AI活用（Copilot/Codex向け）プロンプト例🤖💡

### ✅ フォルダ設計案を出させる

* 「ToDoアプリのCQRSで、Features単位のフォルダ構成案を出して。命名規約もセットで」

### ✅ 既存コードを移動する手順を作らせる

* 「このControllerのメソッドをCommand/Handlerに分けて、移動先フォルダも提案して」

### ✅ namespace整形を一括でやらせる

* 「このフォルダ構成に合わせてnamespaceを提案して。ズレが出ないように」

---

## 10. よくある事故と対策🚑💦

### 😵 事故1：Shared に何でも入れて巨大化

✅ 対策：Shared は **“本当に共通で変わりにくい物だけ”**（インターフェースやResult型くらい）

### 😵 事故2：Handlers フォルダに全部突っ込む

✅ 対策：**UseCaseごとのフォルダ**にする（探しやすさ最優先）

### 😵 事故3：Controller が肥大化

✅ 対策：Api層は“配送係”📦。判断はHandlerへ！

---

## 11. まとめ：第10章の合格ライン✅🎉

* ✅ 機能（Feature）ごとにまとまってる
* ✅ Command / Query / Handler の置き場が固定
* ✅ 命名がテンプレ化されてる
* ✅ READMEにルールが書いてある

ここまでできたら、次（第11章）の「Commandの戻り値を欲張らない」に進む準備バッチリだよ〜！😺💪✨

---

必要なら、今あるサンプル（ToDo/ミニEC）に合わせて「Orders/Products」のフォルダツリーを**具体的に完成形で**書き起こしてあげるよ📁💕

[1]: https://learn.microsoft.com/en-us/aspnet/core/tutorials/first-web-api?view=aspnetcore-10.0&utm_source=chatgpt.com "Create a controller-based web API with ASP.NET Core"
