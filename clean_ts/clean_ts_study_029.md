# 第29章：Portを増やしすぎない運用（必要になったら）🌱🔌🧩

Port（ポート）って、ざっくり言うと「内側（UseCase）が外側（DB/外部API/時間など）にお願いする“窓口”」だよね😊
でもね…**窓口を増やしすぎると、逆に迷子になる**の🥺💦

この章は「Portは大事。でも“作りすぎ”は毒」って感覚を、ちょー実践的に身につける回だよ〜🌟

---

## 1) この章のゴール 🎯✨

* ✅ **Portを“作るべき時”と“作らない方がいい時”**を言える
* ✅ Port乱立（= 抽象の増殖）を防ぐ **判断基準**を持つ
* ✅ 後から必要になった時に **キレイにPortを増やす手順**が分かる
* ✅ TypeScriptらしく **薄いPort**で運用できるようになる 🧼💕

---

## 2) よくある「Port増やしすぎ事故」あるある 😇💥

### 事故A：1クラスにつき1Port（ほぼ同じ名前）量産 🤖📦📦📦

* 例：TaskServicePort / TaskServiceImpl みたいに **1:1で並ぶだけ**
* “差し替え”も“意味の違い”もなく、ただファイルが増えるだけ…🥲

Mark Seemannさんも「**Interfaceを作った＝抽象になった**ではないよ」って指摘してるよ。 ([Ploeh Blog][1])

### 事故B：Portが“ただの中継”になる 📞➡️📞

* UseCase → Port → Adapter → ライブラリ…
  なのに中身が1行で丸投げ、しかも二度と差し替えない😵‍💫

### 事故C：「いつか必要かも」でPortを先に作る（YAGNI違反）🔮❌

* 「将来DB変えるかも…」で先に抽象化
* でも変えないまま半年経って、誰も触れない“遺跡Port”爆誕🗿

YAGNI（You Aren’t Gonna Need It）は「必要になってから作ろうね」っていう有名な原則だよ。 ([martinfowler.com][2])

---

## 3) Portを作るべきタイミング ✅🔌（5つだけ覚えよ）

### ① 外部I/O・副作用がある（DB/HTTP/ファイル/通知）🌍⚡

* 内側は「方針（Policy）」
* 外側は「詳細（Details）」
  この分離がClean Architectureの王道だよ。 ([クリーンコーダーブログ][3])

### ② “差し替えたい理由”が今ある 🔁

* すでに実装が2つある（InMemoryとSQLite…みたいに）
* もしくは **次のスプリント**で増えるのが確定してる（妄想じゃなく予定！）📅

### ③ テストで“外側なし”にしたい 🧪

* DBやネットワークを切ってもUseCaseが回るようにしたい
* これはPortの強い理由になるよ💪✨

### ④ 非決定なもの（時間・乱数・UUID）を固定したい ⏰🎲

* Clock / IdGenerator みたいなやつ
* テストが安定する🌈

### ⑤ 外部ライブラリの変更が怖い（吸収したい）🧯

* 外部API・SDKがコロコロ変わるなら、Portで“防波堤”を作る価値あり🏖️

---

## 4) Portを作らない方がいいタイミング ❌🧹（こっちが超大事）

### ❌ 1:1でしか使わない（しかも差し替え予定なし）

* 「Interface置いたら疎結合！」って思いがちだけど
  **“役割が共通化されてない”なら抽象の価値が薄い**ことが多いよ。 ([Ploeh Blog][1])

### ❌ 内側の“純粋処理”にPortを当てる

* 例：タイトル文字数チェック、並び替え、変換、計算
  → それ、Entities / UseCaseの中でOK👌✨

### ❌ “設定（Config）”を何でもPort化しちゃう

* 「ConfigPort作って、そこからmaxLength取ろう」みたいなやつ
  → たいてい **値を注入**すれば足りる🥰（後で例やるね）

### ❌ 「テストのためだけ」にPortを作る（雑に）

* “Port=モックのため”だけになってると、設計が崩れやすい…🥺
  似た話として「Repositoryに必ずInterfaceが必要とは限らない」って議論もあるよ。 ([Enterprise Craftsmanship][4])

---

## 5) 3分で決める！Port追加の判断フロー 🧭✨

1. その依存先は **外部I/O / 副作用**？（DB/HTTP/通知/時間など）

   * ✅ Yes → 2へ
   * ❌ No → Portいらない可能性大（まず内側に置こ？）

2. **差し替えの必要**がある？（今ある/予定が確定/テストで切りたい）

   * ✅ Yes → Port作る価値あり💡
   * ❌ No → 3へ

3. “今”の開発速度が落ちる？（ファイル増える/注入増える/追跡しづらい）

   * ✅ Yes → いったん作らない（YAGNI）🌱 ([martinfowler.com][2])
   * ❌ No → Port作ってもOK（ただし最小で！）

---

## 6) TypeScriptで「Portを薄く保つ」テク 🧼💕

TypeScriptは **構造的型付け**（形が合えばOK）だから、Port運用がラクだよ〜😊
「implementsしなくても、形が合えば渡せる」って世界観ね。 ([typescriptbook.jp][5])

だからPortはこういう“薄い形”がめっちゃ相性いい✨

### ✅ Portを「関数型」にしちゃう（超おすすめ）🧠⚡

* Clock：現在時刻を返すだけ
* IdGenerator：IDを返すだけ

```ts
// usecases/ports/Clock.ts
export type Clock = () => Date;

// usecases/ports/IdGenerator.ts
export type IdGenerator = () => string;
```

これならテストでこうできる👇

```ts
const fixedClock: Clock = () => new Date("2026-01-01T00:00:00.000Z");
const fixedId: IdGenerator = () => "task-0001";
```

“Interface + class”より、かなりスッキリするよ🥹💖

---

## 7) Taskアプリでの具体例：Portを増やす？増やさない？📌✨

### 例1：タイトル最大長（maxTitleLength）を追加したい ✍️📏

**悪い寄り**（やりがち🥺）：ConfigPortを作る

* maxTitleLengthだけ取るPortが増える
* 将来の設定が増えるたびにPort/Adapterも増える…増殖コース🐛

**おすすめ**：値をUseCaseに注入する（Port不要）🌟

```ts
export class CreateTaskInteractor {
  constructor(
    private readonly taskRepo: TaskRepository,
    private readonly idGen: IdGenerator,
    private readonly maxTitleLength: number,
  ) {}

  execute(request: CreateTaskRequest) {
    if (request.title.length > this.maxTitleLength) {
      return { ok: false, error: "TitleTooLong" as const };
    }
    // ...
  }
}
```

設定読み込みは外側でやって、数値だけ渡せばOK👌✨
これ、Clean Architecture的にも「詳細は外側」って考え方と合うよ。 ([クリーンコーダーブログ][3])

---

### 例2：タスク完了時に通知したい 📣✅（Portを増やす価値あり）

これは **外部I/O（通知）** だから、Portがキレイにハマるよ🔌💕

```ts
// usecases/ports/Notifier.ts
export interface Notifier {
  notifyTaskCompleted(taskId: string): Promise<void>;
}
```

UseCaseはNotifierにお願いするだけ：

```ts
export class CompleteTaskInteractor {
  constructor(
    private readonly taskRepo: TaskRepository,
    private readonly notifier: Notifier,
  ) {}

  async execute(request: CompleteTaskRequest) {
    const task = await this.taskRepo.findById(request.taskId);
    if (!task) return { ok: false, error: "NotFound" as const };

    task.complete();
    await this.taskRepo.save(task);

    await this.notifier.notifyTaskCompleted(task.id);

    return { ok: true };
  }
}
```

外側でSlack通知でも、メールでも、ダミーでも差し替え自由🕊️✨
まさにPorts & Adaptersの狙いだね。 ([Alistair Cockburn][6])

---

### 例3：Repositoryが太り始めた（Port増やす？）🗄️🍔

TaskRepositoryにメソッドが増えすぎて
「何でも屋Port」になったら、それはそれで臭い😵‍💫💦

でも！ここでも極端はダメで、分けすぎるとまた乱立地獄🌀

**分割の合図**（どれか当てはまったら検討）✅

* UseCaseごとに使うメソッド群が完全に別
* “Query（参照）”と“Command（更新）”で性質が違う
* メソッドの追加が止まらず、命名が苦しくなってきた🥺

→ そういう時だけ
TaskQueryPort / TaskCommandPort みたいに分けるのはアリ🌟

---

## 8) Port追加ルール（短文メモ）📌🧠✨

運用ルール、これだけでOKだよ👇🥰

* ✅ Portは「外部I/O・副作用」を境界で止めるために作る
* ✅ “差し替え・テスト・外部変更吸収”のどれかが**今**必要なら作る
* ❌ “いつか必要かも”だけでは作らない（YAGNI）🌱 ([martinfowler.com][2])
* ❌ 1:1のInterface量産は避ける（抽象の価値が薄い） ([Ploeh Blog][1])
* ✅ Portのメソッドは「UseCaseが必要な最小」だけにする
* ✅ Port名は技術名じゃなく、**能力の名前**にする（例：Notifier）
* ✅ 迷ったら「値の注入」で済まないか先に考える（ConfigPort作りがち注意）
* ✅ 追加する時は「今のユースケースに必要か」で判断する

---

## 9) AI相棒に投げるプロンプト集 🤖✨（コピペOK）

* 🤖「この依存はPort化すべき？ 判断理由を3つ、不要なら代案も」
* 🤖「このPort、メソッド多すぎ？ 分割するなら候補名を出して」
* 🤖「1:1のInterfaceになってない？ “役割”として再設計案を」
* 🤖「ConfigPortを作らずに済ませる注入設計を提案して」
* 🤖「このUseCaseを外部I/OなしでテストするためのFake案を作って」

---

## 10) ミニ演習 ✍️🎀

### 演習A：Portいらないパターンを見抜こ！👀

* 「タスクを一覧表示するとき、完了済みを上に出す並び替え」を追加
  → Port作る？作らない？理由は？😊

### 演習B：Portがいるパターンを作ろ！🔌

* 「タスク完了時に、外部にログ送信したい」
  → LogSender Portを最小で設計してみて✨

### 演習C：Repository肥大化チェック 🗄️

* TaskRepositoryに10メソッド増えた前提で、分割の必要性を判断してみよ🧠

---

## 11) 理解チェック（1問）✅📝

**Q.** 「将来DBをPostgreSQLにするかもしれない」だけを理由に、今すぐRepository Portを細かく分割して増やすのは正しい？

* A：正しい（将来に備えるほど良い）
* B：状況次第だが、多くの場合やりすぎ（必要になってからでOK）

**答え：B**🎉
理由：YAGNI的に、必要が確定してからの方が“ムダな抽象”を抱えにくいからだよ🌱 ([martinfowler.com][2])

---

## 12) この章の提出物 📦✨

* ✅ 「Port追加判断フロー」自分用メモ（箇条書きでOK）📝
* ✅ Taskアプリで「ConfigPortを作らない注入設計」コード1つ 💉
* ✅ Notifier（またはLogSender）Port + Fake実装 🧪🔌

---

必要なら、次は「第30章：Inbound Adapter（Controller）は責務3つだけ🧻🚪」を、このテンションでいくよ〜😆💕

[1]: https://blog.ploeh.dk/2010/12/02/Interfacesarenotabstractions/?utm_source=chatgpt.com "Interfaces are not abstractions - ploeh blog"
[2]: https://martinfowler.com/bliki/Yagni.html?utm_source=chatgpt.com "Yagni"
[3]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "Clean Architecture by Uncle Bob - The Clean Code Blog"
[4]: https://enterprisecraftsmanship.com/posts/interfaces-for-repositories/?utm_source=chatgpt.com "Interfaces for repositories: do or don't?"
[5]: https://typescriptbook.jp/reference/values-types-variables/structural-subtyping?utm_source=chatgpt.com "TypeScriptと構造的型付け"
[6]: https://alistair.cockburn.us/hexagonal-architecture?utm_source=chatgpt.com "hexagonal-architecture - Alistair Cockburn"
