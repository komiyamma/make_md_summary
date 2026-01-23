# 第10章　型の武器③：Branded / Opaque 風の型で「混ぜない」🏷️😎✨

この章は「**同じ `string` なのに意味が違うもの（UserId / OrderId / Email…）を絶対に混ぜない**」を、TypeScriptの型だけでガッチリ守る回だよ〜🛡️💎
（2026-01-23 時点で TypeScript の最新版は 5.9 が案内されています📌） ([typescriptlang.org][1])

---

## 0. 今日のゴール🎯✨

* `UserId` と `OrderId` を **コンパイルで混ぜられない**ようにする⚡
* 「**ブランド（タグ）付きの型**」の作り方が分かる🙂
* 「`as` をどこで使ってOKか（どこで使うと事故るか）」が分かる🚨

---

## 1. まず“事故”を体験しよ😱💥（string地獄）

例えば、IDをぜんぶ `string` にしてると…こうなる👇

```ts
// 😇 ありがちな設計（危ない）
type UserId = string;
type OrderId = string;

function loadUser(id: UserId) {
  /* ... */
}

const orderId: OrderId = "order_123";

// 💥 コンパイルは通る（UserId も OrderId もただの string だから）
loadUser(orderId);
```

この事故、めちゃくちゃ起きる🥹
「ちゃんと気をつける」だと、人間は負ける…😇

---

## 2. Branded / Opaque 型ってなに？🏷️🧠

**Branded Type（ブランド型）**は、ざっくり言うと👇

* 見た目（構造）は同じでも
* 型に“目に見えないタグ”を付けて
* **別物として扱わせる**テクニック✨

TypeScriptは「構造的型付け」だから、普通は“形が同じなら同じ型っぽく扱える”んだけど、ブランド型はそこに“タグ”を足して区別するよ〜🙂 ([Zenn][2])

---

## 3. いちばん実用的なブランド型の作り方（unique symbol 版）🧷✨

「ブランド名を文字列で書く」やり方もあるんだけど、**うっかり同じ名前を使う事故**が起きやすい🥹
そこで、**unique symbol** を使うと安全度が上がるよ💪（この方向性は実例でもよく紹介されてる） ([Mitsuyuki.Shiiba][3])

まずは共通パーツを作る👇

```ts
// brand.ts
declare const __brand: unique symbol;

// T = 実体（string/number/…）
// B = ブランド（区別したいタグ）
export type Brand<T, B> = T & { readonly [__brand]: B };
```

ポイントは👇

* `declare const` なので **実行時には存在しない**（型チェック専用）🫥✨
* でも型としては「タグが付いた別物」になる🏷️

---

## 4. UserId / OrderId を “混ざらない型” にする🧪✨

次に、ID型を定義する👇

```ts
// ids.ts
import type { Brand } from "./brand";

export type UserId = Brand<string, "UserId">;
export type OrderId = Brand<string, "OrderId">;
```

これだけでもう、`UserId` と `OrderId` は別物になる💎

---

## 5. でも結局どこかで“ブランド付け”が必要だよね？🏭🙂

そう！
外から来た `string` を `UserId` にするには、**どこかで変換**が必要。

ここで大事なルールはこれ👇

### ✅ ルール：`as UserId` は “工場（factory）” の中だけ！🏭🔒

アプリのあちこちで `as UserId` し始めると、結局なんでも通せちゃう世界に逆戻り😇

なので、こうする👇

```ts
// ids.ts
import type { Brand } from "./brand";

export type UserId = Brand<string, "UserId">;
export type OrderId = Brand<string, "OrderId">;

// ✅ 「信頼できる文字列」からだけ作る（境界で検証済み、DBの主キーなど）
export const UserId = {
  fromTrusted(value: string): UserId {
    return value as UserId;
  },
};

export const OrderId = {
  fromTrusted(value: string): OrderId {
    return value as OrderId;
  },
};
```

### 「Trustedっていつ？」🤔

* APIリクエストをスキーマ検証してOKだった✅
* DBから読み出して、形式チェックしてOKだった✅
* UUID生成関数が自前で保証してる✅

みたいに、**境界で“OK”って言えた瞬間**だよ🚧✨

---

## 6. “混ぜたら怒られる”を確認しよ⚡😆

```ts
import { UserId, OrderId } from "./ids";

function loadUser(id: UserId) {
  console.log("load user", id);
}

const u = UserId.fromTrusted("user_1");
const o = OrderId.fromTrusted("order_1");

loadUser(u); // ✅ OK
loadUser(o); // ❌ コンパイルエラー！最高！🎉
```

この「**最高！🎉**」が味わえたら勝ち😎✨

---

## 7. Branded型の“よくある落とし穴”🚧😵‍💫

### 落とし穴①：どこでも `as UserId` しちゃう

```ts
const id = "user_1" as UserId; // 😇 これを各所でやると崩壊
```

✅ 対策：**fromTrusted / parse / create** みたいな“入口”だけに閉じ込める🏰

---

### 落とし穴②：ブランド型＝実行時の安全、だと勘違いする

ブランド型は **コンパイル時の安全**だよ🙂
実行時の値はただの `string`（だから境界で検証が必要）🧪

---

### 落とし穴③：ブランドを付けたのに「メール形式」とかは守れてない

`Email` をブランドにしても、
`"aaa"` を trusted と言い張ったら作れちゃう😇

✅ 対策：**“形式チェックは境界で”**（第17章以降で本格的にやる流れ🚀）

---

## 8. ちょい応用：Emailも「ただのstringじゃない！」📩💎

```ts
import type { Brand } from "./brand";

export type Email = Brand<string, "Email">;

export const Email = {
  // ここではまだ「trusted」扱いにしとく（検証は後の章で強化）
  fromTrusted(value: string): Email {
    return value as Email;
  },
};
```

これで `Email` と `UserId` を混ぜたら怒られる👍✨

---

## 9. ミニ課題🎲✨（手を動かすと一気に身につく！）

### 課題①：3種類のIDを作って混ぜてみる🧨😆

* `ProductId`
* `CategoryId`
* `CartId`

それぞれ `fromTrusted` を用意して、わざと混ぜてコンパイルエラーを見よう👀⚡

---

### 課題②：「IDが必要な関数」を3つ作る📦

例：

* `loadUser(UserId)`
* `loadOrder(OrderId)`
* `addToCart(CartId, ProductId)`

間違った型を渡して、ちゃんと怒られるか確認😎✨

---

### 課題③：`fromTrusted` を “1ファイルに集約” する📁🔒

プロジェクト全体で `as XxxId` が出てくるのを防ぐために、
「**ids.ts 以外では `as UserId` 禁止**」みたいな自分ルールを作ろう🙂

---

## 10. AI活用コーナー🤖✨（この章と相性めちゃ良い！）

AIに聞くと強いのは「漏れ探し」「事故ルート探し」だよ🔍💪

### コピペで使える質問テンプレ👇

* 「`UserId` と `OrderId` が混ざるバグが起きるパターンを10個出して🥹」
* 「`as UserId` をアプリ全体で禁止したい。代替パターン案を出して🧠」
* 「Branded型を導入するときの落とし穴チェックリスト作って✅」
* 「境界でtrustedにしていい条件を文章で定義して🧾✨」

---

## まとめ🎁✨

* `string` は便利だけど、意味が違う `string` を混ぜる事故が多い💥
* **Branded/Opaque 型**で「混ざらない」をコンパイルで守れる🏷️😎 ([Zenn][2])
* `unique symbol` 系の作り方だと、タグ衝突の事故も減らせて堅い🧷✨ ([Mitsuyuki.Shiiba][3])
* `as` は **工場（fromTrusted など）に隔離**するのがコツ🏭🔒
* そして次は…「trustedにする前の **境界での unknown → 検証 → 変換**」が本番になってくるよ🚧🔥

---

次の章（第11章）の「readonly・イミュータブルの気持ち🧊✨」に繋げるなら、
「**混ざらない**」に加えて「**勝手に変わらない**」も揃ってくる感じだよ〜😆💎

[1]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
[2]: https://zenn.dev/ourly_tech_blog/articles/branded_type_20240726?utm_source=chatgpt.com "意味のタグ付けする Branded Typeで型の一意性を守る ..."
[3]: https://bufferings.hatenablog.com/entry/2025/01/12/171721?utm_source=chatgpt.com "TypeScriptのBranded TypeとZodの.brand - Mitsuyuki.Shiiba"
