# 40. アンチパターン②：巨大Port／太いAdapter 🐘🍔


# 第40章：アンチパターン②「巨大Port／太いAdapter」🐘🍔🔌🧩

この章は **「ヘキサゴナルにしたのに、全然ラクにならない…😭」** って時の原因TOPクラス、
**巨大Port** と **太いAdapter** をスパッと直せるようになる回だよ〜！✂️✨

---

## 1) まず結論：何がダメで、どう直すの？😵‍💫➡️😊

### ✅ ダメな状態（ありがち）

* Port（interface）が **なんでも詰め合わせ** になってる🐘💦
* Adapterが **変換係のくせに判断もルールもやってる** 🍔💦

### ✅ 正しい状態（気持ちいい）

* Portは **「ユースケースが本当に必要な最小の約束」だけ** 🔌✨
* Adapterは **「変換して呼ぶ」「I/O失敗を包む」だけ** 🧩✨

  * つまり **薄い＝正義** 🥗✨

---

## 2) 巨大Portってなに？（症状でわかる）🐘🔌

巨大Portはこういうやつ👇

* `RepositoryPort` が **CRUD全部＋検索＋集計＋バッチ＋…** みたいに肥大化😇
* メソッド名が **技術寄り**（`executeQuery`, `beginTransaction` とか）になってる⚙️
* ユースケース側が「とりあえずPortに足す」が習慣化してる🧟‍♀️
* 実装（Adapter）を差し替えたいのに、**契約がデカすぎて差し替えられない** 🔁💥

### 💡なぜ起きる？

* 「将来いるかも」で先に盛る🍱
* 「Repositoryは何でも屋」でまとめたくなる🧹
* “境界”より“便利”が勝っちゃう😵

---

## 3) 太いAdapterってなに？（こっちの方が致命傷）🍔🧩

Adapterが太ると、こうなる👇

* Adapterの中に **業務ルール（禁止事項・状態遷移・分岐の山）** がいる🏔️😱
* 例外処理やログだけじゃなく、**判断までAdapterが握る** 🔥
* テストしようとしても、I/Oが絡んで **テスト地獄** 🧪💀
* “中心を守る”つもりが、中心が空っぽになる🥺

> Adapterは **外の都合を吸収する翻訳係** なのに、
> 翻訳係が勝手に意思決定したらダメ〜！🙅‍♀️📚

---

## 4) まずは「地雷チェックリスト」💣✅

### 🔌 Portが巨大化してるサイン（5つ）

* [ ] メソッドが **10個超え** が当たり前
* [ ] **使ってないメソッド** がゴロゴロある
* [ ] “保存”なのに “検索条件の組み立て” までPortにある
* [ ] 戻り値に **外部ライブラリの型**（ORMモデル等）が混ざる
* [ ] ユースケースの言葉じゃなく、**DB/HTTPの言葉** で話してる

### 🧩 Adapterが太ってるサイン（5つ）

* [ ] `if` がやたら多い（ルールがいる匂い）😱
* [ ] Adapter内で **状態遷移**（二重完了禁止など）を判断してる
* [ ] Adapter内で **入力バリデーション**（空文字NG等）をやってる
* [ ] 「データ取得→整形→判断→保存」まで1ファイルにいる
* [ ] Adapterのテストが “ファイル/ネットワーク必須” になる

---

## 5) 悪い例（わざと太らせる）😈🍔

ToDoミニで、ありがちな悪例いくよ〜👇

```ts
// ❌ 巨大Port：なんでもRepositoryPort😇
export interface TodoRepositoryPort {
  // 書き込み
  save(todo: Todo): Promise<void>;
  update(todo: Todo): Promise<void>;
  delete(id: string): Promise<void>;

  // 読み取り
  findById(id: string): Promise<Todo | null>;
  findAll(): Promise<Todo[]>;
  search(keyword: string): Promise<Todo[]>;

  // 便利機能（増えがち）
  countCompleted(): Promise<number>;
  exportCsv(): Promise<string>;
  importCsv(csv: string): Promise<void>;

  // 技術寄り（境界が死ぬ…）
  beginTransaction(): Promise<void>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
}
```

そして実装Adapterが、さらに最悪になる👇

```ts
// ❌ 太いAdapter：I/Oだけじゃなくルールも判断も持っちゃう🍔
export class FileTodoRepositoryAdapter implements TodoRepositoryPort {
  async save(todo: Todo): Promise<void> {
    // ルール：タイトル空NG（←本当は中心側！）
    if (todo.title.trim() === "") throw new Error("Title is empty");

    // ルール：二重完了禁止（←中心側！）
    if (todo.completed) throw new Error("Cannot save completed todo at creation");

    // I/O：ファイル読み書き
    const list = await this.readAll();
    if (list.some(x => x.id === todo.id)) throw new Error("Duplicate id");

    list.push(todo);
    await this.writeAll(list);
  }

  // …他の巨大メソッド山盛り…
}
```

これ、見た目は「Port/Adapterあるからヘキサゴナルっぽい」けど、
**実質：Adapterにドメインが埋まってる** ので終わってます😇💥

---

## 6) 直し方テンプレ（この順でやると失敗しない）🔧📌✨

### 手順①：Portを「ユースケースの言葉」に戻す🗣️🔌

ポイントはこれ👇
**Portは “外の都合” じゃなく “中心が欲しいこと” を書く** 🛡️✨

* 「CSV export」みたいな都合は、基本 **Portに入れない**
* 「検索」も、ユースケースで必要になった時に **最小で足す**

### 手順②：Portを小さく割る（必要なら）✂️🔌

Interface Segregation（分離）で、よくある割り方👇

* 読み取り系：`TodoQueryPort`
* 書き込み系：`TodoStorePort`

### 手順③：Adapterから「判断」を追放🏃‍♀️💨

Adapterに残していいのは基本これだけ👇

* 変換（DTO ↔ domain）🔁
* 呼び出し（fs/db/httpなど）📞
* 例外を “I/O失敗” として包む🎁

---

## 7) 良い例（スリムにする）🥗✨

### ✅ Port：必要最小限にする🔌

```ts
export interface TodoStorePort {
  save(todo: Todo): Promise<void>;
  findById(id: TodoId): Promise<Todo | null>;
  list(): Promise<Todo[]>;
}
```

> 「更新」「削除」「検索」「集計」…は、**ユースケースで必要になったら** 足すでOK👌✨
> 先に盛ると、ほぼ確実に巨大化するよ〜🐘💦

### ✅ Adapter：I/Oと変換だけ🧩

```ts
export class FileTodoStoreAdapter implements TodoStorePort {
  async save(todo: Todo): Promise<void> {
    // ✅ ここではルール判断しない（中心でやる）
    const list = await this.readAll();          // I/O
    list.push(this.toRecord(todo));            // 変換
    await this.writeAll(list);                 // I/O
  }

  async findById(id: TodoId): Promise<Todo | null> {
    const list = await this.readAll();
    const rec = list.find(x => x.id === id.value);
    return rec ? this.toDomain(rec) : null;
  }

  async list(): Promise<Todo[]> {
    const list = await this.readAll();
    return list.map(x => this.toDomain(x));
  }

  // ---- 変換だけ（薄い！）----
  private toRecord(todo: Todo): TodoRecord { /* ... */ }
  private toDomain(rec: TodoRecord): Todo { /* ... */ }

  // ---- I/Oだけ（薄い！）----
  private async readAll(): Promise<TodoRecord[]> { /* ... */ }
  private async writeAll(list: TodoRecord[]): Promise<void> { /* ... */ }
}
```

---

## 8) 「でも、ルールはどこに置くの？」🤔🧠

答え：**中心（Domain/UseCase）** だよ🛡️✨

* **タイトル空NG** → Todo生成時 or AddTodoユースケース
* **二重完了禁止** → 完了ユースケース or Todoのメソッド
* **重複ID禁止** → ID発行をPort化する（UUID Port）などで回避 ⏰🔌

---

## 9) 便利テク：`satisfies` で「変換だけ」を安全にする🧩✅

Adapterは変換係だから、マッピングが増えるよね？
そんな時 `satisfies` が便利✨（型のチェックだけして、値の型推論は壊さないやつ）
公式でも説明されてるよ📚✨ ([typescriptlang.org][1])

```ts
const errorMap = {
  E_READ: "ファイル読めない😭",
  E_WRITE: "ファイル書けない😭",
} satisfies Record<string, string>;
```

---

## 10) AIレビュー用プロンプト集（そのままコピペOK）🤖📝✨

### 🔌 巨大Portチェック

* 「このPortの全メソッドを、ユースケースからの呼び出し箇所と紐づけて一覧化して。未使用メソッドも教えて」
* 「このPortを “読み取り” と “書き込み” に分割する案を出して。分割後の命名も」

### 🧩 太いAdapterチェック

* 「このAdapter内の処理を `変換 / 呼び出し / 例外ラップ / それ以外` に分類して。“それ以外” を中心へ移す案を出して」
* 「このAdapterが業務ルールを含んでいる箇所を指摘して。UseCaseかDomainに移動する形にリライトして」

---

## 11) ミニ演習（超効くやつ）📝🎀

1. わざと `TodoStorePort` に `search / count / exportCsv` を足してみる🐘
2. 「これ、どのユースケースが本当に使う？」って言葉に戻す🗣️
3. 使うものだけ残して削る✂️
4. Adapterから `if（判断）` を追放して、UseCaseに移す🏃‍♀️💨
5. ユースケース単体テストがラクになったか確認🧪✨

---

## 12) 2026年1月時点の “最近のTypeScriptまわり” メモ🔎✨

* TypeScript は npm 上の安定版として **5.9 系** が案内されてるよ（ダウンロードページでも “currently 5.9” 表記）([typescriptlang.org][2])
* TypeScript チームは **6.0 を最後の “JavaScript実装のメジャー”** とし、**6.1 は出さない予定** と明言してるよ([Microsoft for Developers][3])
* 進行中の TypeScript 7 は **Goによるネイティブ移植**＋言語サービスが **LSP** へ移行していく流れ（VS Code周りの体験も変わり得る）([Microsoft for Developers][3])
* Node.js 側は **v24 が Active LTS** などのラインが公式に整理されてるよ([Node.js][4])
* さらに Node.js では `.ts` を “型を剥がして実行する” 方向（Type Stripping）の話も進んでる（※型チェックは別）([publickey1.jp][5])

> ここ大事：ツールが速くなっても、**巨大Port／太いAdapterは普通に苦しい** 😭
> だからこそ「薄く保つ」がずっと効くよ〜🥗✨

---

## 13) まとめ（今日の合言葉）🎁💖

* Portは **必要最小** 🔌✨（ユースケースの言葉で！）
* Adapterは **薄く** 🧩🥗（変換・呼び出し・例外ラップだけ！）
* 太ったら、**判断を中心へ追放** 🏃‍♀️💨🛡️

---

次の章で「Repositoryが何でも屋になる」問題（41章）に繋がるから、
もし今「Repositoryが万能すぎるかも…😵」って匂いがしてたら、めちゃくちゃいい流れだよ〜！🧹✨

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html?utm_source=chatgpt.com "Documentation - TypeScript 4.9"
[2]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
[3]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[5]: https://www.publickey1.jp/blog/25/nodejstypescripttype_strippingnodejs_v2520.html?utm_source=chatgpt.com "Node.jsでネイティブにTypeScriptを実行できる「Type ..."