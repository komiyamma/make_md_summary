# 第14章 Shared地獄を回避②：契約（Contract）を中心に置く📜🎯

## この章でできるようになること💪✨

* 「Shared に何でも入れて崩壊😇」を **“契約”で防ぐ** 方法がわかる📦🚫
* **Contracts プロジェクト**を作って、依存の矢印をきれいに保てる🧭➡️
* 契約を **壊さず育てる**（バージョニング）方針が作れる🔁🧠
* 変更に強い「境界」の作り方が身につく🚪✨

---

## 1) そもそも「Shared」って何がダメなの？😵‍💫📦

Shared が育つと、だいたいこうなります👇😇

* 「便利だから」→ 何でも入る🌀
* みんな参照する → みんなが引っ張られる🧲
* 変更したら **全プロジェクトが壊れる**💥
* いつの間にか Shared が “中心” になる（本末転倒）🙃

そこで救世主がこれ👇✨

> **“共有”の正体は多くの場合「契約（Contract）」** 🤝📜
> 共有するなら「契約だけ」に絞ると、爆発しにくい💣➡️🧯

---

## 2) 「契約（Contract）」ってなに？🤝📜

一言でいうと👇

* **他の層・他のアプリとやり取りするための“約束”**✨
* たとえば

  * API のリクエスト/レスポンス DTO 🎁
  * メッセージ（イベント）📨
  * 外側が実装すべきインターフェース（Port）🧷
  * エラーコードや共通の結果型（ただし薄く！）⚠️

そして超重要な考え方👇

* 契約は “みんなが使う”＝**公開API** になりがち
* 公開APIは **雑に変えると事故る**😇
* だから契約は **中心寄り（安定側）に置く**🧭🎯

「安定してて長生きするルール」を守る発想は、SemVer（セマンティックバージョニング）でも前提として出てきます📌✨ ([Semantic Versioning][1])

---

## 3) Contracts に入れていいもの / 入れちゃダメなもの🚦✅❌

### ✅ 入れていい（= 契約っぽい）

* API 用 DTO（Request / Response）📦
* メッセージ契約（イベントの型）📨
* “境界”に必要な最小の型（ID・ページング・エラーコードなど）🧩
* Port（外側に実装してほしいIF）※ケース次第🧷🎯

### ❌ 入れちゃダメ（= Shared地獄の種）

* 業務ロジック（計算・判定）🧨
* “便利関数盛り合わせ”ユーティリティ🌀
* DB都合の型（Entity/EF設定/SQL直結）🪦
* Web都合の型（Controller依存、HTTPにベタ寄り）🌐💥
* ログ基盤・設定読み込み・外部SDKなどの詳細🔧🧱

Contracts は **「薄く、安定、詳細に依存しない」** が命です💖✨

---

## 4) 置き場所はどうする？🧭（おすすめ構成）

「契約は中心に置く」＝ **外側の都合（DB/UI）から遠ざける** ってことだよ😊

よくある形👇（例）

* `Shop.Domain` 🥚（中心）
* `Shop.Application` 🧠（ユースケース）
* `Shop.Contracts` 📜（約束だけ）
* `Shop.Infrastructure` 🧰（DB/外部）
* `Shop.WebApi` 🌐（UI/HTTP）

依存の矢印イメージ👇🧅➡️

* WebApi → Application → Domain
* Infrastructure → Application（※Application側にあるIFを実装するため）
* WebApi / Client → Contracts
* Contracts は **できるだけ単独で生きる**（他に依存しない）🌱✨

---

## 5) “壊れにくいContracts” の作り方（型設計のコツ）🧱✨

### コツ①：DTOは「後から足せる形」にする🧩➕

**位置引数の record**（`record X(a,b,c)`）は、項目を追加すると破壊的変更になりがち😇
なので、契約DTOはこういう形が強いよ👇（プロパティ init 方式）✨

```csharp
namespace Shop.Contracts.Orders;

public sealed record CreateOrderRequest
{
    public Guid UserId { get; init; }
    public List<CreateOrderItem> Items { get; init; } = new();
    public string? Note { get; init; }  // 後から項目が増えても壊れにくい✨
}

public sealed record CreateOrderItem
{
    public Guid ProductId { get; init; }
    public int Quantity { get; init; }
}

public sealed record CreateOrderResponse
{
    public Guid OrderId { get; init; }
    public string Status { get; init; } = "Created";
}
```

**「あとからフィールド追加」**は、互換性を保ちやすい王道ムーブだよ😊✨
（ただし“必須”にすると破壊になるので慎重にね⚠️）

---

### コツ②：契約に「ドメイン型」を漏らさない🫧

Domain の Entity/ValueObject をそのまま返すと、外側がドメインにベタ依存しちゃう😵
なので **契約DTOは契約DTOとして独立**させて、境界でマッピングするのが安全🧯✨

---

### コツ③：enum は増やすだけでも注意⚠️

「列挙値を増やす」は一見安全だけど、受け手が `switch` を網羅してたら **コンパイルや挙動に影響**が出ることもあるよ😇
破壊的変更の考え方は .NET の互換性ガイドにも整理されてるので、ルール作りの参考になるよ📚✨ ([Microsoft Learn][2])

---

## 6) 実装詳細は外側へ：WebApiで使う例🌐✨

Contracts の DTO を WebApi の入出力に使って、Application へ渡す（境界で変換）例👇

```csharp
using Shop.Contracts.Orders;

app.MapPost("/orders", async (
    CreateOrderRequest req,
    IOrderAppService appService,
    CancellationToken ct) =>
{
    var result = await appService.CreateOrderAsync(req, ct);

    return result.IsSuccess
        ? Results.Created($"/orders/{result.Value.OrderId}", result.Value)
        : Results.BadRequest(result.Error);
});
```

ポイントはこれ👇😊

* WebApi は Contracts を知ってOK（外側だから）🌐
* Domain は Contracts を知らない（中心は純粋に）🥚✨

---

## 7) 契約のバージョニング方針🔁📦（ここ超大事！）

Contracts は “みんなが使う” から、雑に変えると地獄😇
そこで **SemVer（メジャー/マイナー/パッチ）** を味方につけよう💖

### ✅ まずはルール（NuGet も基本はSemVer）📌

* **Major**：破壊的変更💥
* **Minor**：後方互換な機能追加➕
* **Patch**：後方互換なバグ修正🐛

これは NuGet のドキュメントにも、そのまま書いてあるよ📚✨ ([Microsoft Learn][3])
SemVer の原典も「公開APIを宣言して、互換性で番号を変えよう」って話だよ📜✨ ([Semantic Versioning][1])

---

### ✅ 「何が破壊的？」の具体例集💥😇

**Major（破壊）**になりやすい👇

* DTO のプロパティ名変更 / 削除✂️
* 型変更（`int`→`string` とか）🔁💥
* 必須項目を増やす（受け手が作れなくなる）🚫
* interface のメソッド変更/削除🧷💔

**Minor（互換追加）**になりやすい👇

* DTO に **任意（nullable）項目を追加**➕✨
* 新しいAPI/新しいメッセージ型を追加🆕📨
* 新しい型を追加（既存を壊さない）🌱

---

### ✅ “破壊が必要になった時”の逃げ道🧯

破壊が必要なら、現場でよく使うのはこのへん👇

* **名前/名前空間で V2 を作る**

  * `Shop.Contracts.V2.Orders` みたいに分ける📦
* **古い契約を残しつつ、新しい契約を追加**

  * 並行運用して移行期間を作る⏳
* **APIのバージョンを分ける（/v1, /v2 など）**

  * 公開APIならよくあるやつ🛣️

「API設計ベストプラクティス」系のガイドも、変更の扱い・互換性の考え方の参考になるよ📚✨ ([Microsoft Learn][4])

---

## 8) 演習：Contractsプロジェクトを作って、Sharedを成仏させよう🙏📦✨

### 🎯 お題：Shared の中身を「契約」と「詳細」に分離する

やることはシンプルだよ😊

1. `Shop.Contracts` を追加📜
2. Shared にいる型を、3つに分類する🧺

   * A：契約（DTO/IF/イベント）📜
   * B：実装詳細（DB/HTTP/SDK）🧰
   * C：便利寄せ集め（要整理）🌀
3. A だけ Contracts に移動🚚✨
4. B は元の場所（Infra/WebApi等）へ戻す🏠
5. C は各プロジェクトに散らすか、そもそも消す🧹😇
6. 参照関係を整える（Contracts が詳細に依存しない状態にする）🧭➡️

### ✅ 仕上げチェック（3秒）👀✨

* Contracts が EF / ASP.NET / 外部SDK を参照してない？🚫
* Contracts に “便利関数” 入ってない？🌀
* Domain が Contracts を参照してない？🥚🚫
* 追加はできても「変更・削除」は慎重になってる？🔁⚠️

---

## 9) AI活用コーナー🤖💖（Copilot/Codex想定）

そのままコピって使える指示例だよ〜🧁✨

* 「この Shared フォルダの型を、**契約/実装詳細/ユーティリティ**に自動分類して、移動案を出して」🤖📦
* 「Contracts に入れてOKな依存/NGな依存をチェックして、NG参照があったら一覧化して」🤖🔍
* 「Contracts の **SemVer運用ルール**（破壊変更の定義、移行方針、例）を README にまとめて」🤖📝
* 「DTOの設計を、**後方互換でフィールド追加しやすい形**にリファクタ案出して」🤖🧱

---

## 10) まとめ：Sharedの代わりに「契約」を中心へ📜🎯✨

* Shared に何でも入れると、だいたい爆発する😇💥
* 共有するなら「契約だけ」に絞ると強い🤝
* Contracts は **薄く・安定・詳細に依存しない** が正義🧼✨
* 契約は公開APIになりやすいから **SemVerで丁寧に育てる**🔁📦 ([Microsoft Learn][3])
* .NET の最新世代（.NET 10 / C# 14）でも、この考え方は超重要だよ🧭✨ ([Microsoft Learn][5])

---

## おまけ：この章の“合格ライン”チェック✅💮

* 「Shared を減らして、Contracts に“契約だけ”置けた」📜✨
* 「Contracts の依存が薄い（詳細に引っ張られてない）」🧼
* 「破壊変更をしたくなった時の手がある（V2/並行運用/ルール）」🧯🔁

次の第15章では、ログ・設定・例外みたいな“横断関心”を中心に混ぜない整理術に進むよ〜📈🧩✨

[1]: https://semver.org/?utm_source=chatgpt.com "Semantic Versioning 2.0.0 | Semantic Versioning"
[2]: https://learn.microsoft.com/en-us/dotnet/core/compatibility/library-change-rules?utm_source=chatgpt.com "NET API changes that affect compatibility"
[3]: https://learn.microsoft.com/en-us/nuget/concepts/package-versioning?utm_source=chatgpt.com "NuGet Package Version Reference"
[4]: https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design?utm_source=chatgpt.com "Web API Design Best Practices - Azure Architecture Center"
[5]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
