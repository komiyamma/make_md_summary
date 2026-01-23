# 第4章：まず覚える合言葉3つ 🗣️✨（Ports & Adapters の“最短暗記セット”）

この章はね、細かい図とか理屈より先に、**一生モノの3つの合言葉**を体に入れる回だよ〜😊💕
この3つさえ覚えておくと、あとでPort/Adapterを作るときに迷子になりにくいの！🧭✨

---

## 1) 合言葉その①「中心を守る🛡️」🏰💖

### ✅ 意味（超ざっくり）

**アプリの中心（ルール）に、外の都合を入れない**ってことだよ🙂✨

* 中心：ルール（「空タイトル禁止」「完了は二重適用禁止」みたいな決まり）🧠
* 外側：UI/HTTP/DB/ファイル/日時/UUID…などの“入出力”🌐💾⏰

中心が外側の仕組み（Expressとかfsとか）を知り始めると、急に壊れやすくなる😵‍💫💥
だから **中心は静かに・強く**が正義✨🛡️

### ✅ すぐ使えるチェックリスト ✅

中心のコードを見て、これが出てきたら黄色信号🚥😳

* `express` / `Request` / `Response`（HTTPの匂い）🌐
* `fs` / `path`（ファイルの匂い）📄
* DBのクライアント（sqlite/prisma/…）💾
* `new Date()`（時間の匂い）⏰
* 外部API SDK（Stripeとか）💳

出てきても即アウトじゃないけど、**「外に追い出せないかな？」**って考えるクセが大事だよ😊✨

---

## 2) 合言葉その②「約束はPort🔌」📌✨

### ✅ 意味（超ざっくり）

**中心が“外側にお願いしたいこと”を、インターフェースとして宣言する**のが Port だよ🔌💕

ポイントはここ👇
**Portは中心側の言葉で書く**（外側の技術の言葉に寄せない）🧠✨

たとえば「ToDoを保存したい」って中心が思ったら、中心はこう言うの👇

```ts
// core（中心）側：外にお願いする“約束”＝Port 🔌
export interface TodoRepositoryPort {
  save(todo: { id: string; title: string; completed: boolean }): Promise<void>;
  findAll(): Promise<Array<{ id: string; title: string; completed: boolean }>>;
}
```

これが **「約束はPort🔌」** の正体だよ😊✨

### 🌿 Portを“最小の約束”にするコツ ✂️

* メソッド数を増やしすぎない（増えると管理地獄👻）
* 「今必要なこと」だけに絞る（未来の妄想で盛らない🙅‍♀️）
* 名前は **中心の目的**に寄せる（`PrismaTodoRepository`みたいな技術名はPortに入れない）🧠✨

---

## 3) 合言葉その③「変換はAdapter🧩」🔁✨

### ✅ 意味（超ざっくり）

Adapterは、**外側の世界を“中心に合わせる”変換係**だよ🧩💕

* 外側の面倒（JSON/DB行/HTTP入力/例外/型の違い）を吸収する
* 中心の約束（Port）を満たすように実装する

例：さっきの `TodoRepositoryPort` を、メモリ配列で実装するAdapter👇

```ts
import { TodoRepositoryPort } from "../core/ports/TodoRepositoryPort";

// 外側（adapters）側：Portを満たす“実装”＝Adapter 🧩
export class InMemoryTodoRepositoryAdapter implements TodoRepositoryPort {
  private todos: Array<{ id: string; title: string; completed: boolean }> = [];

  async save(todo: { id: string; title: string; completed: boolean }): Promise<void> {
    const index = this.todos.findIndex(t => t.id === todo.id);
    if (index >= 0) this.todos[index] = todo;
    else this.todos.push(todo);
  }

  async findAll(): Promise<Array<{ id: string; title: string; completed: boolean }>> {
    return [...this.todos];
  }
}
```

### 🥗 Adapterは「薄い」が正義！

Adapterが太り始めると、中心が汚れていくの😱💦

AdapterにいてOK ✅

* 変換（外→中心のDTO、中心→外のレスポンス）🔁
* 外部呼び出し（DB/HTTP/FS）📡
* 外部の例外を“中心向けの形”に包む（ラップ）🎁

Adapterに入れちゃダメ🙅‍♀️

* 業務ルール（「タイトル空は禁止」みたいなやつ）🧠
* 状態遷移の判断（「完了を二重適用禁止」みたいなやつ）🚫

---

## まとめ：今日の3語だけ覚えて帰ってね🎁💖

* **中心を守る🛡️**（ルールは中心、外の都合を入れない）
* **約束はPort🔌**（中心が欲しい外部機能を“契約”にする）
* **変換はAdapter🧩**（外側を中心に合わせる“変換・実装係”）

この3つが頭にあるだけで、次の章以降（Port設計・Adapter実装）がめちゃラクになるよ😊✨

---

## ミニ練習クイズ🎀（すぐ解けるやつ）

次のうち **Port** はどれ？ **Adapter** はどれ？🧐✨

A. `interface TodoRepositoryPort { ... }`
B. `class InMemoryTodoRepositoryAdapter implements TodoRepositoryPort { ... }`
C. `AddTodoUseCase`（ユースケース）

✅ 答え

* Port：**A** 🔌
* Adapter：**B** 🧩
* 中心（アプリのルール側）：**C** 🛡️

---

## AI拡張の使いどころ（安全運転版）🤖🧠✨

AIに頼むときは、**「中心を守る🛡️」を壊さない指示**がコツだよ🙂✨

### ✅ そのままコピペで使えるプロンプト3つ📌

1. Port案を出してもらう（でも最終判断は自分！）

* 「ToDoの保存と一覧に必要な最小のPortを、メソッド2〜3個までで提案して。技術名は禁止。中心の言葉で。」

2. Adapter雛形を作ってもらう

* 「このPortを満たす InMemory のAdapter実装を作って。業務ルールは絶対に入れないで。変換と保存だけにして。」

3. 汚染チェックをさせる

* 「この core フォルダのコードに、fs/express/DBクライアント/new Date が混ざってないかレビューして。混ざってたら移動案を出して。」

---

## 小ネタ：最近のTypeScript事情（知ってると気分が上がるやつ）✨

この教材で使う“Port＝interface”みたいな基本はずっと安定だけど、TypeScript自体も進化中だよ〜🚀
たとえば **TypeScript 5.9 系**のリリース情報が出ていて、さらに **TypeScript 7（ネイティブ化の流れ）**の進捗も公式ブログで共有されてるよ🧑‍💻✨ ([Microsoft for Developers][1])
（「へぇ今そんな感じなんだ〜」くらいでOK😉💓）

---

次の章では、この合言葉を使って **「Portをどう切るか」**を実際にやっていくよ🔌✨
この3つ、今のうちに口に出して言えるようにしとこっ😊🛡️🔌🧩💕

[1]: https://devblogs.microsoft.com/typescript/?utm_source=chatgpt.com "TypeScript"
