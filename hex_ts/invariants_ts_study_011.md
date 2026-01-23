# 第11章 不変に近づく：readonly・イミュータブルの気持ち🧊✨

この章は「**不変条件を壊す“勝手な変更”ルートを減らす**」練習だよ〜🙂🛡️
TypeScriptでできるのは主に **コンパイル時のガード**（= 変な書き換えを“書けなくする”）✨

---

## 1) なんで「勝手に変わる」とヤバいの？😱💥

不変条件って、だいたいこういう形👇

* 「合計金額はマイナスにならない」💰
* 「在庫は0未満にならない」📦
* 「注文確定後は明細を変更できない」🧾🚫

でもオブジェクトが**どこからでも書き換え可能**だと…

* 途中の誰かが `items.push(...)` しちゃう
* どこかが `price = -1` しちゃう
* そして不変条件が静かに崩壊…😇🌀

だから方針はこれ👇

✅ **“変えていい場所”を少なくする**
✅ **“変える方法”を限定する（意図のある関数だけ）**
✅ **“外から勝手に触れない”を増やす** 🧊

---

## 2) まず整理！ const / readonly / immutable の違い🧠✨

### `const`：変数の再代入を禁止するだけ🪧

* `const x = ...` は `x = ...` を禁止
* でも **中身のオブジェクトは普通に変わる**（JSの仕様）🙂

### `readonly`：型として「書き換え禁止」を付ける🛡️

* `readonly prop` は **そのプロパティへの代入を禁止**
* ただし **完全な不変を保証するわけじゃない**（浅い/深い問題がある）
  TypeScript公式も「readonly=完全不変じゃないよ」と説明してるよ。([TypeScript][1])

### immutable（イミュータブル）：設計の姿勢🧊

* 「**変更は新しい値を返す**」
* 「元の値は触らない」
* これは言語機能というより“流儀”だよ🙂✨

---

## 3) readonly の基本セット（今日から使える）🎒✨

### 3-1) readonly プロパティ（オブジェクト）🔒

```ts
type User = {
  readonly id: string;
  readonly name: string;
};

const u: User = { id: "u1", name: "Aki" };
// u.name = "Mika"; // ❌ コンパイルで怒られる
```

### 3-2) readonly 配列（push禁止！）📦🚫

readonly配列は2種類の書き方があるよ👇（意味は同じ）

* `ReadonlyArray<T>`
* `readonly T[]`
  TypeScript公式の説明もあるよ。([TypeScript][2])

```ts
const xs: ReadonlyArray<number> = [1, 2, 3];
// xs.push(4); // ❌
xs.slice(); // ✅ 読むのはOK
```

---

## 4) “浅いreadonly”の落とし穴⚠️😵‍💫（ここ超大事！）

TypeScript公式の例に近い形でいくね👇
`resident` 自体は readonly でも、中の `age` は普通に変わっちゃう！

```ts
type Home = {
  readonly resident: { name: string; age: number };
};

const h: Home = { resident: { name: "Aki", age: 20 } };

h.resident.age++; // ✅ できちゃう（中身はreadonlyじゃない）
```

公式にも「readonlyは完全不変じゃない」って明言されてるよ。([TypeScript][1])

### 対策A：ネストもreadonlyにする🧊

```ts
type Resident = {
  readonly name: string;
  readonly age: number;
};

type Home = {
  readonly resident: Resident;
};
```

### 対策B：設定オブジェクトは `as const` で“カチカチ”にする🧊🧱

`as const` は「できるだけ細かい型」＋「readonly化」してくれる便利技！
（配列はreadonlyタプル、オブジェクトのプロパティもreadonly寄りになる）([typescriptbook.jp][3])

```ts
const PLAN = {
  Free: { maxProjects: 1 },
  Pro:  { maxProjects: 100 },
} as const;

// PLAN.Free.maxProjects = 2; // ❌
```

---

## 5) “イミュータブル更新”のコツ3選🔁✨（壊さずに変える）

### コツ①：オブジェクトはスプレッドでコピー🧼

```ts
type Profile = Readonly<{
  readonly name: string;
  readonly age: number;
}>;

function birthday(p: Profile): Profile {
  return { ...p, age: p.age + 1 };
}
```

### コツ②：配列は「新しい配列を作る」系を使う📦✨

```ts
type Todo = Readonly<{ readonly id: string; readonly title: string }>;
type State = Readonly<{ readonly todos: ReadonlyArray<Todo> }>;

function addTodo(s: State, todo: Todo): State {
  return { ...s, todos: [...s.todos, todo] };
}
```

最近のJSだと「コピーして変更」専用メソッド（例：`toSorted()`）もあるよ。([MDN Web Docs][4])
（“元の配列を壊さない”方向の味方🥰）

### コツ③：深い更新が多すぎるなら Immer を検討🤝🧊（任意）

Immerは「書き換えてる風なのに、結果は新しい値」ってやつ。
公式の説明（`produce`）はここが分かりやすいよ。([Immer.js][5])

---

## 6) 不変条件と相性がいい readonly の置き場所🎯✨

おすすめはこの順番👇

1. **関数の引数を readonly にする**（呼び出し側の破壊を防ぐ）🛡️
2. **戻り値を readonly にする**（受け取った側の破壊を防ぐ）🧊
3. **公開する型を readonly に寄せる**（外から触れない）🔒
4. **変更は“意図のある関数”だけに集める**（次の章以降で強化🔥）

---

## 7) ミニ課題🧩🧊（15〜25分）

### 課題A：readonly化ポイント探し🔍

自分の題材の型（DTOでもドメインでもOK）から、最低3つ👇

* `readonly` を付けられるプロパティ
* `ReadonlyArray` にできる配列
* `as const` にできる設定オブジェクト

### 課題B：「勝手に壊すコード」を書いて怒られてみる😆⚡

わざと `push` / 再代入 を書いて、TypeScriptに止めてもらう（体験が大事！）

---

## 8) AI活用テンプレ🤖✨（この章と相性よすぎ）

VS Codeでそのまま投げてOKだよ👇

* 「このコードで**破壊的変更**（push/splice/代入）してる箇所を列挙して」🔍
* 「公開APIの引数・戻り値を **ReadonlyArray / readonly** に直して」🧊
* 「`as const` を使うと良い“設定オブジェクト候補”を探して提案して」🧱
* 「浅いreadonlyの穴（ネスト変更できる箇所）を指摘して」⚠️

---

## まとめ🎁✨

* 不変条件を守るには「チェック」だけじゃなくて、**“勝手に変えられない形”**を増やすのが効く🛡️🧊
* `readonly` はまず **API境界（引数・戻り値）** から入れると、効果が見えやすいよ🙂
* ただし `readonly` は **完全不変ではない**（浅いreadonlyに注意！）([TypeScript][1])

次の章でいよいよ「ルール込みの値（Value Object）」に進むと、**“無効な値を作れない”**がもっと強くなるよ〜💎🚀

ちなみに本日時点だと、npmで配布されている TypeScript の最新は **5.9.3** だよ。([npmjs.com][6])

[1]: https://www.typescriptlang.org/docs/handbook/2/objects.html?utm_source=chatgpt.com "Documentation - Object Types"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-4.html?utm_source=chatgpt.com "Documentation - TypeScript 3.4"
[3]: https://typescriptbook.jp/reference/values-types-variables/const-assertion?utm_source=chatgpt.com "constアサーション「as const」 (const assertion)"
[4]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/toSorted?utm_source=chatgpt.com "Array.prototype.toSorted() - JavaScript - MDN Web Docs"
[5]: https://immerjs.github.io/immer/produce/?utm_source=chatgpt.com "Using produce | Immer"
[6]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
