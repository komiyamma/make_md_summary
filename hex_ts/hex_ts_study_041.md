# 41. アンチパターン③：Repositoryが何でも屋になる 🧹😵


([Past chat][1])([Past chat][2])([Past chat][3])([Past chat][4])([Past chat][5])

# 第41章：アンチパターン③「Repositoryが何でも屋になる」🧹😵‍💫💥

## 1) この章のゴール 🎯✨

この章が終わったら、こんなことができるようになるよ〜！😊🌸

* 「あ、これ **何でも屋Repository** だ…！」って気づける👀⚡
* Repository（＝Outbound Port🔌）を **ちょうど良いサイズ** に保てる✂️✨
* 肥大化したRepositoryを **手順どおりに分解** して直せる🔧🧩
* 結果として、中心（UseCase/Domain）が守られてテストも楽になる🧪💕

※いまのTypeScriptは npm の “latest” が **5.9.3** になってるよ（2026-01時点の表示）。([NPM][6])
Node.js は **v24（LTS: Krypton）** がActive LTSで、2026-01にも更新が出てる感じ。([Node.js][7])

---

## 2) 何でも屋Repositoryって、どんな状態？ 🐘🍔💦

### ありがちなストーリー📖💭

最初はこうだったのに…

* `TodoRepository` に `save()` と `findById()` くらいしか無い✨

だんだん要望が増えて、こうなる👇😇

* `completeTodoAndNotifySlack()`
* `addTodoIfTitleUniqueOtherwiseThrow()`
* `findTodosWithUserAndTagsAndLatestComments()`
* `bulkUpdateStatusesAndLogAndRetry()`

……もう、**DB担当なのか業務担当なのか通知担当なのか** わかんないやつ😵‍💫💥

---

## 3) 何が困るの？（地味に致命傷）🧨😱

### 困りごと①：中心（UseCase/Domain）が汚れる 🥲

Repositoryが強くなりすぎると、UseCaseが薄くなって
「中心はルール置き場🏠」が崩れちゃうの💦

### 困りごと②：テストが急にしんどい 🧪😭

Repositoryが “何でも” やってると、テストで差し替えたい範囲が広すぎて
モックが地獄になる…（そしてテストを書かなくなる…）😇

### 困りごと③：変更が怖い（影響範囲がでかい）😵

「一覧画面の表示をちょい変えるだけ」なのに Repository 触ることになって
**別のUseCaseが壊れる** みたいな事故が起きがち⚠️💥

---

## 4) 症状チェックリスト✅（3つ当てはまったら黄色信号🚦）

* Repositoryのメソッド数が **10個超えてる**（しかも増え続ける）📈😇
* メソッド名に **業務動詞** が入ってる

  * `complete`, `notify`, `validate`, `reopen`, `assign`, `approve` など👀
* 返り値が **画面用DTO** とか **JOIN結果の盛り合わせ** になってる🍱
* Repositoryの中に `if (title === "") throw ...` みたいな **ルール判定** がある🚫
* 「とりあえずRepositoryに置いとくか」って空気がある（最重要）🫠

---

## 5) ダメな例：巨大Repository（何でも屋）🐘🍔

「うわ…あるある…」ってなるやつ置いとくね😇💦

```ts
// ❌ 何でも屋Repository（アンチパターン）
export interface TodoRepository {
  // 永続化っぽい
  save(todo: any): Promise<void>;
  findById(id: string): Promise<any>;

  // いつの間にか業務ルール
  addTodoIfTitleUnique(title: string): Promise<void>;
  completeTodoAndPreventDoubleApply(id: string): Promise<void>;

  // いつの間にか外部I/O
  completeTodoAndNotifySlack(id: string): Promise<void>;

  // いつの間にか画面都合（JOIN盛り盛り）
  findTodosWithUserAndTagsAndLatestComments(): Promise<any[]>;
}
```

これ、何がヤバいかというと…
**Port（約束🔌）が “中心の言葉” じゃなくなってる** のが一番キツいの😵‍💫

---

## 6) 正しい感覚：Repositoryは「永続化の都合」を隠す係 💾🧩

Repository（＝Outbound Port🔌）の役割は、ざっくりこれ👇

* ✅ **保存する**
* ✅ **取り出す**
* ✅ **永続化の都合（ファイル/DB/HTTPなど）を隠す**
* ❌ ルールを決める（例：タイトル空禁止）
* ❌ 状態遷移を判断する（例：二重完了禁止）
* ❌ 通知する（Slack/メール等）
* ❌ 画面都合の集計やJOIN盛り合わせを背負う

---

## 7) 直し方のコツ：UseCaseの言葉に寄せて「分割」✂️✨

### コツ①：まず「ユースケースの台本」を思い出す🎬✨

ToDoなら中心はだいたいこれだったよね📝

* AddTodo
* CompleteTodo
* ListTodos

Repositoryが何でも屋になったら、いったん
**「台本に必要な道具だけ」** に戻すのが最短ルート🚀

---

### コツ②：Portは “使う側（UseCase）” が欲しい最小だけ🔌✂️

たとえば、読みと書きを分けるだけでも一気にスッキリするよ😊

```ts
// ✅ 読み取り専用（Query寄り）
export interface TodoReaderPort {
  findById(id: TodoId): Promise<Todo | null>;
  findAll(): Promise<Todo[]>;
}

// ✅ 書き込み専用（Command寄り）
export interface TodoWriterPort {
  save(todo: Todo): Promise<void>;
}
```

UseCaseは「必要な方だけ」受け取れるから、依存が細くなる✨🧠

---

### コツ③：画面向けの “盛り合わせ” は Query 用のPortに逃がす🍱➡️🧩

「一覧で、ユーザー名もタグもコメントも全部ほしい！」みたいなのは
**Repositoryに押し込まない** のが大事💦

代わりにこうする👇

```ts
// ✅ 画面用の取得は、別Portにする（Read Model / Query Service）
export interface TodoListQueryPort {
  listForDisplay(): Promise<Array<{
    id: string;
    title: string;
    completed: boolean;
    // 表示に必要な分だけ
    // userName?: string; tags?: string[]; ...
  }>>;
}
```

これでRepositoryは「ドメインの保管庫」っぽさを保てるし、
画面は画面で最適化できるよ🌸✨

---

## 8) 「ルールはどこへ行くの？」→ 中心だよ🛡️❤️

たとえば「二重完了禁止」はRepositoryに入れたくなるけど…
**それはドメイン or ユースケースが担当** だよ😊

```ts
export class CompleteTodoUseCase {
  constructor(
    private readonly reader: TodoReaderPort,
    private readonly writer: TodoWriterPort,
  ) {}

  async execute(id: TodoId): Promise<void> {
    const todo = await this.reader.findById(id);
    if (!todo) throw new Error("Todo not found"); // ※実際は章33/34のエラー設計に合わせてね🧯

    // ✅ ルールは中心で判断（例：二重完了禁止）
    const completed = todo.complete(); // domainの状態遷移
    await this.writer.save(completed);
  }
}
```

Repositoryは「保存したり取り出したり」だけ。
判断（ルール）は中心でやる。これが気持ちいい分担💕🧠

---

## 9) “Port増えすぎ問題” を防ぐ小ワザ🧯✨

「分割は大事」だけど、増やしすぎても迷子になるよね😵‍💫
判断基準を置いとくね👇

* ✅ **同じ集まり（同じAggregate）** を扱ってるなら、まとめてもOK
* ✅ 同じUseCaseが毎回セットで使うなら、まとめてもOK
* ❌ 画面都合のJOINや集計が混ざるなら、分ける
* ❌ 通知・時間・UUIDが混ざるなら、分ける（Clock/IdGenerator/Notifierなど）

---

## 10) Adapter側はどうなる？（実装は “薄い” まま）🥗✨

Adapterは、Portを実装するだけ🧩
読み書き2つのPortを同じAdapterが実装しても全然OKだよ〜😊

```ts
export class FileTodoRepositoryAdapter implements TodoReaderPort, TodoWriterPort {
  async findById(id: TodoId): Promise<Todo | null> {
    // JSON読み取り → domainへ変換（変換だけ！）
    return null;
  }

  async findAll(): Promise<Todo[]> {
    return [];
  }

  async save(todo: Todo): Promise<void> {
    // domain → JSONへ変換して保存（変換だけ！）
  }
}
```

ここに `if (title==="")` とか `二重完了チェック` を入れたくなったら、
「それ中心の仕事だよ〜！🛡️」って自分に言って止めよ😂✨

---

## 11) AI拡張での “事故防止” プロンプト集🤖📝✅

コピペで使えるやつ置いとくね💕

* 「この `TodoRepository` は何でも屋になってない？理由も添えて、分割案を3つ出して」
* 「Repository内に業務ルールが混ざってたら指摘して。どこへ移すべきか（UseCase/Domain/Adapter）も提案して」
* 「このPortは大きすぎる？ ‘ユースケースが本当に必要な最小’ に削った場合のインターフェース案を作って」
* 「Query（画面用）とCommand（更新用）が混ざってたら、分離案（Reader/Writer or QueryPort）を出して」

---

## 12) ミニ実習：今あるRepositoryを分解してみよ🧩🔧✨

### お題📝

あなたの `TodoRepository`（または想定）に、次のメソッドが混ざってるとする👇

* `completeTodoAndNotifySlack`
* `findTodosWithUserAndTags...`
* `addTodoIfTitleUnique`

### やること（3ステップ）🚀

1. **「保存/取得」だけ残す**（Repository本体）💾
2. 通知は `NotifierPort` にする📨
3. 画面用一覧は `TodoListQueryPort` にする🍱

終わったら、UseCase側の依存がスッキリしてるのを眺めてニヤニヤしよ😊💕

---

## まとめ：Repositoryが何でも屋になったらこう思って🧠💡

* Repositoryは **永続化の都合を隠す係** 💾🧩
* ルールは **中心（UseCase/Domain）** 🛡️❤️
* 画面都合の盛り合わせは **Query用Port** 🍱✨
* Portは **ユースケースが欲しい最小** に寄せる🔌✂️

次の章では、こういう “分解” をもっと手早くやるための
「直し方テンプレ」🔧📌 をガッツリ使っていくよ〜！😊🎀

[1]: https://chatgpt.com/c/6972e69a-8e08-8321-b4f6-596e652a4f69 "Adapterの役割と注意点"
[2]: https://chatgpt.com/c/6970458f-7110-8321-8e2c-01eb1ab5a08b "ヘキサゴナル設計の略語"
[3]: https://chatgpt.com/c/6972bb61-5e8c-8321-b99c-acbecfed6646 "Portとは何か🔌"
[4]: https://chatgpt.com/c/696c6433-c6d4-8321-820c-cf446b14327d "第12章 Portの逆転技"
[5]: https://chatgpt.com/c/6972bd45-8bf4-8321-bc32-af6a9d796240 "ヘキサゴナル設計入門"
[6]: https://www.npmjs.com/package/typescript?activeTab=versions&utm_source=chatgpt.com "typescript"
[7]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"