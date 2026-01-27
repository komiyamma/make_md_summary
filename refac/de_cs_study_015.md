# 第15章 イベント名の付け方：過去形 + ドメイン語彙📝✨

([Past chat][1])([Past chat][2])([Past chat][3])([Past chat][4])([Past chat][5])

## 15.0 この章のゴール🎯✨

この章が終わると…

* ドメインイベント名を「読んだ瞬間に意味が伝わる」形で付けられる📣✨
* **命令（Command）っぽい名前**や **技術っぽい名前**を避けられる🙅‍♀️🧯
* 例題ミニEC（Order / Payment / Shipment）で、イベント名をスラスラ作れる🛒💳📦

---

## 15.1 なんで“イベント名”がそんなに大事なの？🤔💡

ドメインイベントは「起きた事実」🔔🕒
だから、イベント名がキレイだと…

* **ログ**を見た瞬間に「何が起きた？」が分かる🔭🧾
* 後から読み返しても「仕様そのもの」になってる📘✨
* 変な名前だと、イベントが“命令”や“処理メモ”に見えて事故る😵‍💫💥

.NET の DDD ガイドでも、ドメインイベントは **過去形（起きたこと）**として表現するのが自然だよ、と説明されてるよ。 ([Microsoft Learn][6])

---

## 15.2 命名の大原則 5つ🧩✨（これだけで8割勝てる）

### 原則①：イベント名は「過去形」🕒🔔

* ✅ **OrderPaid**（支払いが完了した）
* ✅ **OrderShipped**（発送された）
* ❌ **PayOrder**（命令っぽい）
* ❌ **Shipping**（状態？処理？曖昧）

「イベント＝すでに起きたこと」なので **過去形にする**のが王道だよ。 ([Microsoft Learn][6])

---

### 原則②：「ドメインの言葉（ユビキタス言語）」で付ける🗣️🎀

* ✅ **PaymentAuthorized**（与信が取れた）
* ✅ **OrderCancelled**（注文がキャンセルされた）
* ❌ **SavedToDb**（技術）
* ❌ **MessagePublished**（技術）

“DBに保存した”はドメインの事実じゃなくて実装の都合になりがち⚠️
ドメインイベントは業務の意味で命名しようね💕

---

### 原則③：「主語（だれ/なに）＋起きたこと」で作る🧠🧷

イベント名はだいたいこの形が強い💪✨

* **{集約/対象} + {過去形の動詞}**

  * Order + Paid → **OrderPaid**
  * Shipment + Dispatched → **ShipmentDispatched**

---

### 原則④：C#の型名は PascalCase🧼✨

イベントを **クラス/レコード**で表すなら、型名は PascalCase が基本だよ。 ([Microsoft Learn][7])

---

### 原則⑤：チーム内で“型名の流派”を固定する📏✨

よくある2つの流派👇（どっちもアリ！）

* **短い派**：OrderPaid / OrderPlaced
* **サフィックス派**：OrderPaidDomainEvent / OrderPlacedDomainEvent

Microsoft のガイド例では “〜DomainEvent” を付ける例が出てるよ。 ([Microsoft Learn][6])
教材では読みやすさ重視で **短い派（OrderPaid）**を主に使うね🩷（でもどっちでもOK、混ぜないのが大事！）

---

## 15.3 Completed / Failed の使い分け🙂⚖️

ここ、超つまずきポイント！🧠💥

### 15.3.1 まず結論：結果を表したいなら「成功」と「失敗」を対にする🎭✨

* ✅ **PaymentCompleted** / **PaymentFailed**
* ✅ **PaymentSucceeded** / **PaymentFailed**
* ✅ **PaymentAuthorized** / **PaymentAuthorizationFailed**

「Completed」って便利だけど、単体だと **成功なの？ただ終わったの？** が曖昧になりがち😵‍💫
だから **Failed とセット**で置くと安心だよ✨

---

### 15.3.2 「Requested」は命令じゃないの？🤔📝

**Requested** は「要求が発生した」という事実だから、イベントとして成立するよ👍

* ✅ **OrderCancellationRequested**（キャンセル要求が来た）
* ✅ **OrderCancelled**（注文がキャンセルされた）

この2つは **別の事実**だよね🧠✨
“要求が来た”段階と “キャンセル完了”段階を分けたいときに便利🎀

---

## 15.4 “やりがちNG命名”あるある集😱🧯

### NG①：技術用語を混ぜる🙅‍♀️🔌

* ❌ OrderSavedToDb
* ❌ OrderInserted
* ❌ EntityTracked

→ ✅ OrderPlaced（注文が確定した）
→ ✅ OrderUpdated（注文内容が更新された：ただし粒度は注意）

---

### NG②：メソッド名っぽい（命令っぽい）📣💦

* ❌ SendOrderPaidEmail
* ❌ UpdateStock
* ❌ CreateShipment

→ ✅ OrderPaid（支払いが完了した）
→ ✅ StockReserved（在庫が引き当てられた）
→ ✅ ShipmentCreated（発送が作成された）

---

### NG③：Before/After を付ける🕰️🚫

“BeforeX / AfterX” は避けよう、というルールが .NET の命名ルールにもあるよ。 ([Microsoft Learn][8])
順序を表したいなら…

* ✅ **OrderPaying**（支払い処理中：進行形・現在形）
* ✅ **OrderPaid**（支払い完了：過去形）

みたいに **時制**で表現するのがスッキリ✨ ([Microsoft Learn][8])

---

## 15.5 ミニEC：イベント名の作り方（具体例）🛒💳📦

「業務の会話」→「イベント名」へ変換してみよう🎀

### 注文（Order）

* 「注文が確定した」→ **OrderPlaced** 🧾✨
* 「注文内容が変更された」→ **OrderUpdated** ✍️
* 「注文がキャンセルされた」→ **OrderCancelled** 🛑

### 支払い（Payment）

* 「支払いが完了した」→ **OrderPaid** 💳✅
* 「支払いに失敗した」→ **PaymentFailed** 💥❌
* 「与信が取れた」→ **PaymentAuthorized** 🏦✅
* 「返金が完了した」→ **RefundCompleted** 💸✅

### 発送（Shipment）

* 「発送が作られた」→ **ShipmentCreated** 📦✨
* 「発送した（出荷した）」→ **ShipmentDispatched** 🚚💨
* 「配達完了した」→ **DeliveryCompleted** 🏠✅

---

## 15.6 C#でイベント型を作ってみる🧩✨

イベントは「変えない事実」なので、**不変（イミュータブル）**にすると安心だよ🔒✨
C#なら record が相性いい🌸

```csharp
public interface IDomainEvent
{
    DateTimeOffset OccurredAt { get; }
}
```

```csharp
public sealed record OrderPaid(
    Guid OrderId,
    decimal Amount,
    DateTimeOffset OccurredAt
) : IDomainEvent;
```

```csharp
public sealed record PaymentFailed(
    Guid OrderId,
    string Reason,
    DateTimeOffset OccurredAt
) : IDomainEvent;
```

ポイント🎀

* 型名は **PascalCase**（C#の基本） ([Microsoft Learn][7])
* 名前は **過去形** ＋ **ドメイン語彙** ([Microsoft Learn][6])
* データは「必要最小限」になりやすい（太らせないの大事！）📦✂️

---

## 15.7 リライト練習✍️✨（悪い例→良い例）

### 問題：次のイベント名、どこが微妙？どう直す？🧠🖍️

1. OrderSavedToDb
2. SendOrderPaidEmail
3. BeforeOrderPaid
4. UpdateInventory
5. PublishMessageToRabbit
6. OrderPaymentProcessing
7. PaymentCompleted（単体）
8. CreateShipment
9. OrderStateChanged
10. SyncToExternalApi

---

### 解答例（ひとつの正解じゃないよ🙂✨）

1. ❌ OrderSavedToDb → ✅ **OrderPlaced** / **OrderUpdated**（業務の意味に寄せる）
2. ❌ SendOrderPaidEmail → ✅ **OrderPaid**（メールは“反応”でやる）
3. ❌ BeforeOrderPaid → ✅ **OrderPaying** / **OrderPaid**（時制で表す） ([Microsoft Learn][8])
4. ❌ UpdateInventory → ✅ **StockReserved** / **StockAdjusted**（何が起きた？）
5. ❌ PublishMessageToRabbit → ✅ **OrderPaid** / **ShipmentDispatched**（技術を捨てる）
6. ❌ OrderPaymentProcessing → ✅ **PaymentProcessingStarted**（開始の事実ならOK）
7. ❌ PaymentCompleted → ✅ **PaymentCompleted** ＋ **PaymentFailed**（失敗とペアにする）🙂⚖️
8. ❌ CreateShipment → ✅ **ShipmentCreated**（命令→事実へ）
9. ❌ OrderStateChanged → ✅ **OrderCancelled** / **OrderPaid** など（具体的に）
10. ❌ SyncToExternalApi → ✅ **CustomerAddressUpdated** など（外部同期は“結果”じゃなく“事実”に戻す）

---

## 15.8 AI（Copilot/Codex）で命名を爆速にするプロンプト例🤖✨

命名はAIが得意😌💖
ただし「採用するか」は人間の役目🎯

### 例：ユビキタス言語から候補を出す📝

* 伝える情報：用語集（Order/Payment/Shipment）、起きた事実、NGワード（DB/HTTPなど）

```text
ミニECのドメインイベント名を提案して。
条件：
- ドメイン語彙を使う（Order/Payment/Shipment）
- 過去形の事実として命名する
- 技術用語（DB/HTTP/MessageQueueなど）は入れない
欲しい：イベント名候補10個と、それぞれ「何の事実か」の説明
```

---

## 15.9 章末チェック✅✨（これで命名ミス激減）

次の質問に全部「うん！」って言えたら合格💮🎀

* イベント名は **過去形**になってる？🕒 ([Microsoft Learn][6])
* 技術用語じゃなくて **業務の言葉**になってる？🗣️
* “命令”っぽくない？（PayOrder / SendEmail になってない？）📣🚫
* **主語＋起きたこと**が読める？🧠
* Completed を使うなら **Failed とペア**で考えた？🙂⚖️
* 型名は PascalCase で統一できてる？🧼 ([Microsoft Learn][7])

---

[1]: https://chatgpt.com/c/697750de-9d24-8321-881a-3920eb2a59e7 "第8章 VS Code環境"
[2]: https://chatgpt.com/c/697754a7-065c-8322-985f-2bb801b7bc5c "第10章 ソリューション構成"
[3]: https://chatgpt.com/c/69774769-dc5c-8320-a7ba-48763dfb429a "ドメインイベント入門"
[4]: https://chatgpt.com/c/69774d16-4fb0-8323-baaa-53ed08d30404 "ドメインイベント用語集"
[5]: https://chatgpt.com/c/6977494d-fa28-8320-ac52-c5a05101866b "関心の分離理解"
[6]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-events-design-implementation?utm_source=chatgpt.com "Domain events: Design and implementation - .NET"
[7]: https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names?utm_source=chatgpt.com "C# identifier naming rules and conventions"
[8]: https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/naming-warnings?utm_source=chatgpt.com "Naming rules (code analysis) - .NET"
