今から「第11章：TypeScriptの型チェックを味方にする」を、初心者でも手を動かしながら理解できるように、例→手順→課題→AI活用の順で“教材ページ”として作ります（2026年の型チェック周辺ツール情報も確認して反映します）。


## 第11章 TypeScriptの型チェックを味方にする🧷✨

### ねらい🎯

型チェックを「うるさい先生」じゃなくて「守ってくれる味方」にして、リファクタ中に壊れた場所をすぐ見つけられるようになるよ〜🛟😊
特に **関数を分割したり名前を変えたり**するとき、型エラーは「ここ直して！」って教えてくれる超便利アラーム🔔✨

---

### この章でできるようになること🌸

* 型チェックを **いつでも1発で回す**（＝安全確認の習慣化）🏃‍♀️💨
* VS Codeで **型の情報を読む**（ホバー／Problems）👀🧠
* `strict`系を **怖がらずに使う**（段階的に強くする）🛡️
* 型エラーを **リファクタの道しるべ**として使う🗺️✨

---

## 1) まず「型チェック」をワンボタン化しよう🔘✅

### ✅ やること：`typecheck` コマンドを用意する

`tsc`（TypeScriptコンパイラ）が型チェックの本体だよ。VS Codeは型の支援をしてくれるけど、`tsc`自体は別で入れる必要があるよ〜🧑‍💻🧷 ([Visual Studio Code][1])

#### ① TypeScriptの導入（まだなら）

```bash
npm i -D typescript
```

#### ② バージョン確認（「入ってる！」の安心）

```bash
npx tsc -v
```

※ 2026年1月時点だと、安定版は 5.9.3 が最新として配布されてるよ（npm表示）📦✨ ([npm][2])

#### ③ `package.json` に `typecheck` を追加

```json
{
  "scripts": {
    "typecheck": "tsc --noEmit"
  }
}
```

`--noEmit` は「型チェックだけして、JSは出力しない」って意味。リファクタ中はこれが最高に便利💡✨

#### ④ 走らせる！

```bash
npm run typecheck
```

---

## 2) VS Codeで「型」を読む練習👀🧷

### ① Problems パネルは「型エラーの地図」🗺️

* 赤い波線が出たら、まず **Problems** を開く🔎
* エラー文は長くてもOK！大事なのはここ👇

  * **どのファイルの何行目？**
  * **期待してる型は何？**（`string`が欲しいのに`number`来てる…みたいな）
  * **原因になってる変数はどれ？**

### ② ホバー（マウスを乗せる）で「推論された型」を見る🪄

「え、これ何型なの？」って迷ったら、変数や関数にマウス置くだけでだいぶ解決するよ〜😊✨

### ③ VS Codeが使ってるTypeScriptのバージョンを合わせる🔧

VS Codeは「内蔵のTypeScript」と「プロジェクトに入ってるTypeScript」を切り替えられるよ。プロジェクト側（workspace）を使うと、チームで挙動が揃いやすい🙆‍♀️✨ ([Stack Overflow][3])

* コマンドパレットで
  **TypeScript: Select TypeScript Version** → **Use Workspace Version**（があればそれ）✅

---

## 3) `strict` は「安全ネットのまとめスイッチ」🛟✨

`tsconfig.json` の `strict: true` は、型チェックを強くしてバグを早めに見つけやすくするスイッチだよ🔛
しかも **strictは“strict系のオプション全部まとめてON”**って意味（後から個別にOFFもできる）🧷✅ ([TypeScript][4])

### まずはこの形がおすすめ（入門だけど強い）🌱🛡️

```json
{
  "compilerOptions": {
    "strict": true
  }
}
```

> もしエラーが多すぎて心が折れそうなら😵‍💫
> `strict: true` のまま、困ってる項目だけ一時的に調整してOK（ただし“戻す予定”で！）🗓️✨
> どのオプションが何をするかは公式のTSConfigリファレンスがいちばん確実だよ📚 ([TypeScript][4])

---

## 4) コード例（ビフォー/アフター）🧩➡️✨

### 例1：型チェックが「壊れた接続」を教えてくれる🔌⚡

#### ❌ Before：引数の型ミスが混ざる

```ts
function formatPrice(price: number) {
  return `${price.toFixed(0)}円`;
}

const input = "1000";           // string
console.log(formatPrice(input)); // ここで型エラー！
```

型エラーはだいたいこういう感じ👇

* `Argument of type 'string' is not assignable to parameter of type 'number'.`

#### ✅ After：直し方はいろいろ（安全にいこう）🛟

パターンA：呼び出し側で変換する

```ts
const input = "1000";
console.log(formatPrice(Number(input)));
```

パターンB：受け取り側を「現実に合わせる」（ただし責務に注意）

```ts
function formatPrice(price: number | string) {
  const n = typeof price === "string" ? Number(price) : price;
  return `${n.toFixed(0)}円`;
}
```

---

### 例2：`strictNullChecks` が「落ちる未来」を止めてくれる🧯🫧

#### ❌ Before：`undefined`が混ざるかもなのにそのまま使う

```ts
type User = { name?: string };

function greet(user: User) {
  return `Hello, ${user.name.toUpperCase()}!`; // nameがないと落ちる😱
}
```

#### ✅ After：ガードして安全にする🚦✨

```ts
function greet(user: User) {
  if (!user.name) return "Hello!";
  return `Hello, ${user.name.toUpperCase()}!`;
}
```

こういう「最初に危険を処理してスッキリする」形は、後の章のガード節（Guard Clauses）にもつながるよ〜🚦😊

---

## 5) リファクタでの「型チェックの使い方」👣🧷✨

型チェックは、リファクタ中にこう使うとめちゃ強いよ💪

### 黄金ムーブ🏆

1. **小さく変更**する（関数を少し切り出す／名前を変える）✂️🏷️
2. **すぐ `npm run typecheck`** ✅
3. エラーが出たら、**その場で直す**（放置しない）🧯
4. 直ったら次の一歩👣✨

### 便利ポイント📌

* 関数の引数や戻り値を変えたとき、**呼び出し箇所ぜんぶ教えてくれる**📣
* 使われなくなった変数・到達しない分岐が見つかりやすい👀
* 「このリネーム、漏れてない？」をかなり潰せる✅

---

## 6) よくあるつまずき & 安全な考え方🧠🛟

### 🌀 つまずきA：`any` で全部黙らせたくなる

気持ちは分かるけど、`any`は「安全ネットを自分で切る」感じ😱✂️
困ったらまずは `unknown` にして、**チェックしてから使う**が安全✨
（これは後の章の “any卒業” にもつながるよ🎓）

### 🧨 つまずきB：`as`（型アサーション）を多用しすぎる

`as` は「本当は違うかも」を“無理やりOKにする”ボタンになりがち⚠️

* どうしても必要なときだけ
* できれば **チェック（narrowing）**で安全に寄せる🔍✅

---

## 7) ミニ課題✍️🎀（手を動かすほど身につく！）

### 課題1：型チェックをルーティン化🔁✅

* `typecheck` スクリプトを入れて
* `npm run typecheck` を実行
* エラー0を確認してスクショ…じゃなくて「OKを確認」📌✨

### 課題2：型エラーを3つ直す🔧🔧🔧

わざとミスを作ってOK！

* `string` と `number` を混ぜる
* `undefined` の可能性を作る
* 関数の戻り値を間違える
  → 3つ直して、最後に `typecheck` が通ること✅

### 課題3：`any` を1個だけ減らす🎓🧷

* `any` を `unknown` に変える
* `typeof` や `in` で判定してから使う
* `typecheck` が通るようにする✅✨

---

## 8) AI活用ポイント🤖💡（お願い方＋チェック観点✅）

### お願い方テンプレ📝

* 「このTypeScriptエラーを、**1行ずつ**やさしく説明して」🥺✨
* 「**安全な直し方を3案**出して。メリット/デメリットも」⚖️
* 「`strict`で増えたエラーを、**段階的に減らす作戦**を提案して」🗺️
* 「このコード、`as`を減らして **narrowing** で直せる？」🔍

### AIの提案を採用する前のチェック✅🤖⚠️

* `npm run typecheck` が通る？🧷
* `as any` が増えてない？😇
* 例外ケース（`undefined`/空文字/0/空配列）に弱くなってない？🫧
* “型が通るだけ”で、処理の意味が変わってない？🔁👀

---

### まとめ🌷

型チェックは「怒られてる」じゃなくて「守られてる」だよ🛟✨
リファクタのたびに **型チェック→直す→次へ** を繰り返すと、壊れにくくて気持ちよく進められるようになるよ〜😊💖

[1]: https://code.visualstudio.com/docs/languages/typescript?utm_source=chatgpt.com "TypeScript in Visual Studio Code"
[2]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[3]: https://stackoverflow.com/questions/39668731/what-typescript-version-is-visual-studio-code-using-how-to-update-it?utm_source=chatgpt.com "What TypeScript version is Visual Studio Code using? How ..."
[4]: https://www.typescriptlang.org/tsconfig/?utm_source=chatgpt.com "TSConfig Reference - Docs on every TSConfig option"
