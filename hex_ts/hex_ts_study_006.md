## 第6章：Adapterってなに？（変換器＝実装）🧩✨

### この章のゴール 🎯💖

* 「Adapterって結局なに？」を**自分の言葉で説明**できるようになる😊
* Adapterがやる仕事（＝**変換**）と、やっちゃダメな仕事（＝**業務ルール**）を見分けられるようになる🛡️
* “薄いAdapter”の感覚がつかめる🥗✨

---

## 1) Adapterは「外の世界」と「中心」をつなぐ通訳さん 🧩🗣️

ヘキサゴナル（Ports & Adapters）では、中心（ドメイン／ユースケース）は**技術の詳細を知らない**のが理想だよね🧠🛡️
でも現実には、外側にはDB、HTTP、ファイル、外部API…いろんな“都合”がある😵‍💫

そこで登場するのが Adapter！
Adapterは、Port（約束・インターフェース）を通して、外部のデータや呼び出しを**中心が扱える形に変換**する役だよ🔁✨
「ポート経由でアプリに接続して、データを受け渡し・変換する」って説明されることも多いよ🌐🧩 ([AWS ドキュメント][1])

---

## 2) Adapterがやることは、だいたいこの4つだけ！🧩📌

### ✅ (A) データの変換（最重要）🔁✨

* 外部の形 → 中心の形（DTO/ドメインに近い形）
* 中心の結果 → 外部が欲しい形（HTTPレスポンス、DB行、JSONなど）

### ✅ (B) 外部への「呼び出し」📞💾

* DBに保存/取得する
* HTTPで外部APIを叩く
* ファイルを読む/書く

### ✅ (C) エラーの変換（翻訳）🚑🧯

* 外部エラー（例：ネット落ち、ファイル壊れた）
  → アプリ側で扱いやすい失敗にまとめる（例：`InfraError` とか）😌

### ✅ (D) ログや計測（必要なら）📊🪪

* 「いつ」「何が」「失敗した？」を外側で記録する
* 中心は静かにルールを実行🧠✨（ここがキレイだと強い）

---

## 3) Adapterが“やっちゃダメ”なこと 😱🚫（ここが超大事！）

Adapterが太る原因は、だいたいこれ👇

* ❌ **業務ルールを書く**（例：タイトル空なら保存しない、完了済みなら弾く、など）
  → それ、中心（ドメイン／ユースケース）の仕事！🛡️
* ❌ **状態遷移を持つ**（例：`Pending→Done` の判断をAdapterでやる）
* ❌ **巨大if・巨大for・巨大switch**で「なんでも処理」しはじめる🐘🍔

AWSの解説でも「ポートはドメインが定義し、アダプターがそれを実装する。ドメインはアダプター実装を知らないから差し替えやすい」って整理されてるよ🧠✨ ([AWS ドキュメント][2])
つまり Adapterがルールを持ち始めると、中心が汚れて差し替えが崩れるの…😵‍💫

---

## 4) “薄いAdapter”ってどのくらい？🥗✨（目安あるよ）

薄いAdapterの感覚はこれで掴める😊👇

### 🥗薄いAdapterの特徴

* メソッドが短い（数十行以内が多い）📏
* 「変換」→「呼び出し」→「変換」みたいな流れが見える🔁
* ルールっぽい判断がほぼない（あっても“外部都合”だけ）👌

### 🍔太いAdapterのニオイ

* if文が増殖してる（特に業務用語のif）😇
* DBのテーブル構造に引っ張られて、中心の形まで歪む😵
* 「ここでやるのが一番早いから…」が口ぐせになる（危険）⚠️

---

## 5) TypeScriptミニ例：Outbound Adapter（Repositoryの実装）💾🧩

### 🌟中心側：Port（約束）を定義する🔌

※中心に置くイメージ（`app` や `domain` 側）

```ts
// TodoRepositoryPort.ts（中心側）
export type TodoDTO = {
  id: string;
  title: string;
  completed: boolean;
};

export interface TodoRepositoryPort {
  save(todo: TodoDTO): Promise<void>;
  findAll(): Promise<TodoDTO[]>;
}
```

### 🌟外側：AdapterがPortを実装する🧩

（例：まずは超シンプルなメモリ版）

```ts
// InMemoryTodoRepositoryAdapter.ts（外側）
import { TodoRepositoryPort, TodoDTO } from "../app/TodoRepositoryPort";

export class InMemoryTodoRepositoryAdapter implements TodoRepositoryPort {
  private todos: TodoDTO[] = [];

  async save(todo: TodoDTO): Promise<void> {
    // ✅ Adapterの仕事：保存先の都合で保持するだけ
    // ❌ ここで「title空は禁止」みたいな業務ルールを書かない！
    this.todos = this.todos.filter(t => t.id !== todo.id).concat(todo);
  }

  async findAll(): Promise<TodoDTO[]> {
    return [...this.todos];
  }
}
```

ここでのポイントは超シンプル💖
Adapterは「保存の仕組み」を持つけど、**Todoの正しさ**（タイトル空NGとか）には口を出さない🛡️✨

---

## 6) Adapterは“差し替え”で気持ちよさが出る🔁🎉

たとえば Repository を、

* InMemory（テスト用）🧠
* File（開発用）📄
* DB（本番用）🗄️

みたいに差し替えできるのがヘキサゴナルの強さだよね✨
AWSの説明でも「ドメインはアダプター実装を知らないから、SQL→NoSQLみたいな変更でもドメインを変えずに済む」って言い方をしてるよ🔁([AWS ドキュメント][2])

---

## 7) ありがち失敗：Adapterが“中心を侵食”する例 😱🧨

### 😵ダメ例のイメージ

* Adapter内で「タイトル空なら例外」「完了済みなら弾く」などの**業務判断**をする
* すると「UIから呼んだときだけ挙動が違う」みたいな事故が起きる😇

### ✅直し方（第6章の範囲でできる改善）

* ルール判断は中心（ユースケース／ドメイン）へ移動🛡️
* Adapterには「変換」と「呼び出し」と「外部エラーの翻訳」だけ残す🥗✨

---

## 8) AI拡張の使いどころ（安全運転）🤖🧰

### ✅頼ってOK（めっちゃ相性いい）🎉

* 「このPortを実装するAdapterの雛形つくって」
* 「例外をまとめるラッパー関数つくって」
* 「DTO変換関数を生成して」

### ⚠️頼りすぎ注意（崩れやすい）😵‍💫

* 「業務ルールまで書かせる」→ Adapterが太りがち🍔
* 「Portの設計そのものを丸投げ」→ 変な責務が混ざりやすい🧨

#### コピペで使えるお願いテンプレ📝🤖

* 「このAdapterは **変換と呼び出しだけ** にして。**業務ルールは書かない**で」
* 「中心（domain/app）側の型を汚さないで。外部型はAdapter内で閉じて」
* 「if文が増えそうなら、変換関数に分けて薄くして」

---

## 9) ちいさな理解チェック（5分）✅💖

1. Adapterの主な仕事を2つ言える？（ヒント：🔁📞）
2. 「title空は禁止」は Adapter？それとも中心？どっち？😊
3. Adapterが太ってるサインを1つ言える？🐘🍔

---

## まとめ：Adapterは“変換係”で、薄いほど強い 🧩🥗✨

* Adapter = 外部の都合を吸収して、Port越しに中心へ届ける通訳さん🗣️
* 仕事は「変換」「呼び出し」「外部エラーの翻訳」くらいに絞る🔁
* ルールを書き始めたら太る！中心を守る！🏰🛡️

（補足）「Ports & Adapters（ヘキサゴナル）」は2005年にAlistair Cockburnが提唱した、とAWSの解説にも書かれてるよ📚✨ ([AWS ドキュメント][1])

[1]: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html "Hexagonal architecture pattern - AWS Prescriptive Guidance"
[2]: https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/hexagonal-architectures/hexagonal-architectures.pdf "AWS Prescriptive Guidance - Building hexagonal architectures on AWS"
