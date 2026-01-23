# 第8章　型の武器①：リテラル型・ユニオン型で選択肢を固定🎫✨

第7章で「`string` とか `number` だけだと、意味が混ざって事故る〜！😱」を体験したよね。
この章は、その“事故りやすい自由さ”を **「そもそも選べる値を固定する」** ことで止める話だよ🛡️💕

ちなみに本日時点のTypeScriptは **5.9 系**のリリースノートが最新として参照できる状態で（2026年1月更新）、今日やる型テクはぜんぶ現役バリバリで使えるよ〜😊✨ ([typescriptlang.org][1])

---

## この章でできるようになること🎯🌸

* 「この値は **この中からしか選べない**」を型で表現できる🎫✨
* `switch` の分岐漏れを **コンパイルで怒らせる** 感覚がわかる⚡
* `as const` を使って「定義した選択肢」から型を自動生成できる🤖💡
* `satisfies` で「辞書（マップ）のキー漏れ・スペルミス」を叩ける🔨✨ ([typescriptlang.org][2])

---

## まずは“事故”を見てみよっか😇➡️💥

「プラン」は Free / Pro しかないのに、`string` だと何でも入るよね。

```ts
type User = {
  plan: string; // 😇 なんでも入っちゃう
};

const u: User = { plan: "Fre" }; // typoでも通る…🥲
```

この時点で **不変条件**（プランは決められた候補のどれか）を破ってるのに、型が止めてくれないのがつらいところ😵‍💫

---

## 1) リテラル型ってなに？🧠✨

TypeScriptには「文字列そのもの」を型にできる仕組みがあるよ🙂
たとえば `"Free"` は `string` の一種だけど、もっと具体的に **"Free そのもの"** を指す型なんだ〜！ ([typescriptlang.org][3])

* 文字列リテラル型: `"Free"`
* 数値リテラル型: `0`, `1`, `100`
* 真偽値リテラル型: `true`, `false` ([typescriptlang.org][3])

---

## 2) ユニオン型で「選択肢の集合」を作る🎫✨

じゃあ「プランは Free か Pro」って型にしちゃおう！

```ts
type Plan = "Free" | "Pro";

type User = {
  plan: Plan;
};

const ok: User = { plan: "Free" }; // ✅
const ng: User = { plan: "Fre" };  // ❌ コンパイルで怒られる⚡
```

これだけで
**「無効な値が入るルート」**が一気に減るよ〜〜〜🛡️✨

---

## 3) どんな場面に効く？（めちゃ効くやつ）💪😊

ユニオン型で固定しやすいのはこういうの👇✨

* ステータス: `"Draft" | "Paid" | "Shipped"` 🚚
* 種類（Kind）: `"Personal" | "Business"` 🧾
* 区分（Category）: `"Food" | "Book" | "Other"` 🛍️
* UIのタブ: `"Home" | "Settings"` 🧭
* エラーコード（軽め）: `"NotFound" | "Unauthorized"` 🚫

---

## 4) “定義した配列”から型を作る（Single Source of Truth）📌✨

ここからが超大事！
**値の一覧（配列）**と**型定義**を別々に書くと、更新漏れが起きがち🥲

そこでよく使うのが **`as const`** ✨
`as const` は「できるだけリテラルとして扱ってね」ってお願いするやつだよ🙂
（const assertion と呼ばれてて、TypeScript公式の機能として説明されてるよ） ([typescriptlang.org][4])

```ts
const PLANS = ["Free", "Pro"] as const;
//    ^^^^^ readonly ["Free", "Pro"] みたいに超カチカチになる✨

type Plan = typeof PLANS[number];
//            ^^^^^^^^^^^^^^^^^^^ "Free" | "Pro"
```

これで…

* 値の追加は `PLANS` に足すだけ✅
* 型 `Plan` も自動で増える✅

最高〜〜〜😆✨

---

## 5) 境界から来る入力を「Planにする」🕵️‍♀️➡️💎

UIやAPIから来る入力は、だいたい `string` とか `unknown` だよね。
ユニオン型は **実行時には存在しない**から、ここは **実行時チェック**が必要🙂

シンプル版いくよ👇✨

```ts
const PLANS = ["Free", "Pro"] as const;
type Plan = typeof PLANS[number];

function parsePlan(input: unknown): Plan | null {
  if (typeof input !== "string") return null;

  // includes の型都合を軽く調整🙂
  const ok = (PLANS as readonly string[]).includes(input);
  return ok ? (input as Plan) : null;
}
```

使う側はこう👇

```ts
const raw = "Pro"; // ほんとは外部入力想定

const plan = parsePlan(raw);
if (plan === null) {
  console.log("プランが不正です🥲");
} else {
  // plan は Plan 型（"Free" | "Pro"）になってる💎
  console.log("OK:", plan);
}
```

この「境界でチェックして、ドメイン内は信じる」方針は、ロードマップ後半（境界・DTO・バリデーション）で超効いてくるよ〜🛡️✨

---

## 6) `switch` の分岐漏れを “型で” 潰す🚦⚡

Planが増えたときに、分岐を書き忘れるのも事故ポイント😱
ここも型でガードできるよ！

```ts
type Plan = "Free" | "Pro";

function assertNever(x: never): never {
  throw new Error("Unexpected value: " + x);
}

function planLabel(plan: Plan): string {
  switch (plan) {
    case "Free":
      return "無料プラン🆓";
    case "Pro":
      return "プロプラン⭐";
    default:
      return assertNever(plan); // ここが効く⚡
  }
}
```

`Plan` に `"Enterprise"` を足したら、**コンパイルが「switch足りないよ！」って教えてくれる**感じになるよ🎉

（この“絞り込み（narrowing）”の考え方は公式ハンドブックでも詳しく説明されてるよ） ([typescriptlang.org][5])

---

## 7) `satisfies` で「辞書のキー」を安全にする🗂️✨

「プランごとの価格表」みたいな辞書、スペルミスしがちじゃない？🥺

`satisfies` は **型を満たしてるか検証しつつ、推論はなるべく保つ** 便利オペレータだよ✨（TypeScript 4.9で入ったよ） ([typescriptlang.org][2])

```ts
const PLANS = ["Free", "Pro"] as const;
type Plan = typeof PLANS[number];

const PRICE_BY_PLAN = {
  Free: 0,
  Pro: 980,
  // Por: 980, // ←こういうミスを即発見できる💥
} satisfies Record<Plan, number>;
```

これ、地味だけど **運用でめちゃ効く** やつ〜〜〜🥰✨

---

## 8) enum とユニオン、どっち使う？🤔💡

サクッと結論だけ言うね🙂

* **ユニオン型（おすすめ）**

  * 型だけで完結（実行時の余計なものが増えない）
  * “候補が少ない” “ドメインの選択肢” に強い🎫✨
* **enum**

  * 実行時にもオブジェクトとして残る
  * 外部との取り決め（SDK/設定値）で「実体がほしい」時に便利なこともある🙂
  * enum自体も「各メンバーがリテラルになって、全体がユニオンっぽく扱える」流れがあるよ ([typescriptlang.org][6])

この教材ではまず **ユニオン型**をメイン武器にするのが気持ちいいよ🛡️✨

---

## ミニ課題（手を動かすやつ）🧪🌟

### 課題A：固定できる選択肢を3つ探す🔍✨

あなたの題材から、次のどれかを3つ選んで「候補を列挙」してね🙂
（例：ステータス、種別、カテゴリ、画面タブ、支払い方法…）

### 課題B：`as const` 配列 → ユニオン型を作る🎫✨

* `const XXX = [...] as const`
* `type Xxx = typeof XXX[number]`

### 課題C：`satisfies` で辞書を作る🗂️✨

* `Record<Xxx, ...>` を使って「キー漏れゼロ」を体験してね😊

### 課題D：境界の `parseXxx()` を1個作る🚪✅

* `unknown` を受けて
* OKなら型付きで返す / ダメなら `null`

---

## AI活用テンプレ（この章向け）🤖💬✨

コピペで使ってOK〜〜😆🌸

* 「この機能で“固定できる選択肢”を10個候補出して。ステータス、カテゴリ、種別など」🔍
* 「`as const` 配列からユニオン型を作るパターンを、私の題材向けに例で出して」🧩
* 「`satisfies Record<...>` で辞書のキー漏れを防ぐ例を作って」🗂️
* 「switchの分岐漏れをコンパイルで検知する `assertNever` パターンを、初心者向けに説明して」🚦

---

## まとめ💎✨

* **リテラル型**で「この値そのもの」を型にできる🙂 ([typescriptlang.org][3])
* **ユニオン型**で「選択肢の集合」を固定できる🎫✨
* **`as const` + `typeof XXX[number]`**で、値リストから型を自動生成できる🪄 ([typescriptlang.org][4])
* **`satisfies`**で辞書のスペルミス・キー漏れを潰せる🔨✨ ([typescriptlang.org][2])

次の第9章は、このユニオン型をさらに強くする **「タグ付きユニオン（Discriminated Union）」**で、状態や結果（Success/Failure）を安全に表現していくよ〜🏷️🧠✨

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html?utm_source=chatgpt.com "Documentation - TypeScript 4.9"
[3]: https://www.typescriptlang.org/docs/handbook/literal-types.html?utm_source=chatgpt.com "Handbook - Literal Types"
[4]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-4.html?utm_source=chatgpt.com "Documentation - TypeScript 3.4"
[5]: https://www.typescriptlang.org/docs/handbook/2/narrowing.html?utm_source=chatgpt.com "Documentation - Narrowing"
[6]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html?utm_source=chatgpt.com "Documentation - TypeScript 5.0"
