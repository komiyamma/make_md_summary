# 第7章　プリミティブ地獄（string/numberだらけ）を体験する🧟‍♀️➡️😇

この章はあえて「うわ〜…こわっ😱」ってなる体験をします✨
**“意味のある型” を作りたくなる気持ち**を、ちゃんと作る章だよ🫶💕

---

## 0) 今日のゴール🎯✨

* `string` や `number` だらけだと、**混ぜ事故**が簡単に起きるのを体験する💥
* TypeScriptがいても、**プリミティブ同士は守れない穴**があると分かる🕳️😵
* 次章以降でやる「混ぜられない型」に期待できる状態になる😆🌸

---

## 1) まず結論：`string` は「全部入りカゴ」🧺😇

`string` って便利だけど、こういう “別物” を全部受け入れちゃうんだよね👇

* ユーザーID（例：`u_123`）🪪
* メールアドレス（例：`komi@example.com`）📧
* 郵便番号（例：`100-0001`）🏣
* URL（例：`https://...`）🌍
* 住所（例：`東京都...`）🏠

**全部 `string` ってことは、全部混ぜられる**ってこと…😱💦

---

## 2) 最新環境メモ（サクッと）🗒️✨

* TypeScript の npm 最新は **5.9.3**（2026-01時点でも “Latest” 表示）だよ📦✨ ([NPM][1])
* VS Code は TypeScript の言語機能は持ってるけど、`tsc` 自体は **npm で入れる**形だよ🧰 ([Visual Studio Code][2])
* Node.js は **v24 が Active LTS**、**v25 が Current**（2026-01時点）って整理になってるよ🟢 ([Node.js][3])

（ここは深掘りしないでOK！今日は “混ぜ事故” 体験が主役😆）

---

## 3) ハンズオン：わざと事故るミニコード🧨🙂

### 3-1) まずは最小プロジェクト📁✨

ターミナルで👇（フォルダ名は自由でOK）

```bash
mkdir ch07-primitive-hell
cd ch07-primitive-hell
npm init -y
npm i -D typescript
npx tsc --init
```

---

## 4) 事故①：UserId と Email が混ざる💥🪪📧

`index.ts` を作って貼ってね👇

```ts
// index.ts

// 「意味の名前」を付けたくなるよね…！ってことで型別名を作る
type UserId = string;
type Email = string;

function sendWelcomeEmail(email: Email) {
  console.log("Welcome mail sent to:", email);
}

const userId: UserId = "u_12345";

// 😱 ここで事故！ userId を email のつもりで渡してしまった
sendWelcomeEmail(userId);
```

### ✅ 起きること

* **コンパイルが通る**（えっ…通るの！？😱）
* 実行すると、**ユーザーIDにメール送ったことになる**（ログ上だけでも十分ヤバい💥）

> ポイント：`type UserId = string` は “ただの別名” だから、TypeScript的には同じ `string` 扱いなんだよね🫠

---

## 5) 事故②：お金の単位が混ざる💴🪙💥

「円」と「ポイント」とか、「税込」と「税抜」とか…
**number は全部混ざる**のが怖い😇

```ts
// money.ts
type Yen = number;
type Point = number;

function pay(price: Yen, usePoint: Point) {
  // ほんとはポイントを円換算する必要があるのに、引いちゃった😱
  const after = price - usePoint;
  return after;
}

console.log(pay(1200, 5000)); // ありえない結果になっても型は止めない…💀
```

### ✅ 何が怖い？

* `number` は「単位」が消える
* だから **“意味” の取り違え**が起きても止められない🥲

---

## 6) 事故③：秒とミリ秒が混ざる⏱️💥

地味だけど、実務でめちゃ多い😵‍💫

```ts
// time.ts
type Seconds = number;
type Milliseconds = number;

function wait(ms: Milliseconds) {
  console.log("wait:", ms, "ms");
}

const timeoutSeconds: Seconds = 5;

// 😱 秒をそのままmsに入れてしまった（本当は 5000ms）
wait(timeoutSeconds);
```

これも **通る** のが怖いよね…🫣💦

---

## 7) 「プリミティブ地獄」って結局なに？🧠🌀

今日の体験をまとめると👇

* プリミティブ（`string/number/boolean`）は **意味が乗らない**
* “意味が違うのに型が同じ” だと **混ぜ事故が防げない**
* その結果、チェックがいろんな場所に増えていって…

  * if が散る🌪️
  * 直し漏れが出る😱
  * 仕様変更が怖くなる🫠

これが「プリミティブ地獄」🧟‍♀️💦

---

## 8) ミニ課題：わざと混ぜて事故を再現🧨🙂

あなたの題材（アプリ/機能）で、次を作ってみてね👇✨

### ✅ ミニ課題A（超おすすめ💖）

* `userId: string`
* `email: string`
* `sendMail(to: string)`
  この3つを作って、**userId を誤って渡しても通る**のを確認する😆💥

### ✅ ミニ課題B（実務っぽい🔥）

* `price: number`（税込）
* `price: number`（税抜）
* `calcTaxIncluded(x: number)`
  どこかで混ぜて、変な値になっても止まらないのを確認する🧾😱

---

## 9) AI活用コーナー🤖✨（観点出しが最強🫶）

AIにこう聞くとめちゃ捗るよ👇💡

* 「`string` が混ざって事故る例を10個出して。実務でありがちなやつで！」🧠✨
* 「`number` が混ざって起きるバグを “単位違い” で10個出して！」⏱️💴📦
* 「このコードの危険ポイントをレビューして。不変条件の観点で！」🔍🛡️

👉 出てきた例から「自分の題材に近いやつ」だけ採用すればOKだよ🥰

---

## 10) この章のまとめ🧁✨

* `string/number` だけで設計すると、**TypeScriptがいても混ぜ事故は止まらない**😱
* “意味のある型” を作りたくなるのは自然な流れ💎
* 次章から、そのための **型の武器** を順番に増やしていくよ🪄✨

---

## 次章予告🎫✨

次は **リテラル型・ユニオン型**で「選択肢を固定」して、まずは混乱を減らすよ〜😆🏷️

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[2]: https://code.visualstudio.com/docs/languages/typescript?utm_source=chatgpt.com "TypeScript in Visual Studio Code"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
