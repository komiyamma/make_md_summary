# 第3章　なぜバグる？チェックが散ると事故る😱🌀

この章は「不変条件を守る前に、なんで守れなくなるのか？」を体感する回だよ〜🙂✨
いったん **“あるある地獄”** を見てから、次章以降の「入口で一回だけ保証する🚪🛡️」がスッと入るようにするね🫶🌸

---

## 1) この章でできるようになること🎯✨

* ✅ 「チェックが散る」と、なぜ漏れるのか説明できる🙂
* ✅ “if のコピペ増殖”が、バグと保守コストを増やす流れがわかる😵‍💫
* ✅ 「入口で一回だけ保証する」発想の気持ちよさをつかむ🚪🛡️
* ✅ TypeScriptの型だけでは守れない領域（実行時）も理解する👀💡
  ※ TypeScriptの型注釈はコンパイル後に消える＝実行中の安全は別で守る必要があるよ📌 ([typescriptlang.org][1])

---

## 2) まず結論：チェックが散ると “漏れ” が必ず出る😱

チェックが散るコードって、だいたいこうなるの👇

* 入口が複数（UI / API / DB / 外部API）🌍➡️
* それぞれの場所で「一応チェック」する😅
* でも **微妙に違うチェック** が混ざる（trimしてる/してない、上限が違う、条件が古い…）🌀
* 仕様変更で「全部探して直す」になって、どこか必ず直し忘れる💥

つまり…

> **“どこで保証されてるか分からない” = どこでも壊れる** 😇💣

---

## 3) あるある例：会員登録（Emailと年齢）✉️🎓

ここでは題材として「会員登録」を使うよ🙂
守りたい不変条件はこんな感じ👇

* Email：空じゃない、だいたいメールっぽい（例：@ がある）✉️
* 年齢：0〜120の範囲内👶➡️👵
* 表示名：空白だけはダメ🙅‍♀️

---

## 4) 悪い例：チェックが散って “漏れ” が出るコード😵‍💫🧨

「とりあえず動く」を積み重ねると、こうなりやすい…！

```ts
// どこからでも呼ばれる便利関数（のつもり）
function createUser(email: string, age: number, displayName: string) {
  // チェック①（ここではtrimしてない）
  if (!email.includes("@")) throw new Error("email invalid");
  if (age < 0) throw new Error("age invalid");

  return { email, age, displayName };
}

function handleUiSubmit(form: { email: string; age: string; displayName: string }) {
  // チェック②（ここではtrimしてる）
  const email = form.email.trim();
  if (email.length === 0) return { ok: false, message: "email required" };

  // ageを数値化（ここではNaNチェックしてない）
  const age = Number(form.age);

  return { ok: true, user: createUser(email, age, form.displayName) };
}

function importFromCsv(row: { email: string; age: string; displayName: string }) {
  // チェック③（ここではageの上限だけ見てる）
  const age = Number(row.age);
  if (age > 120) throw new Error("age too old");

  // emailのチェックを忘れた😇
  return createUser(row.email, age, row.displayName);
}
```

### 何が起きる？😱

* CSVから取り込むと、メールが空でも通る（チェック漏れ）💥
* UI経由だとtrimされるけど、別経由だと `"   a@b.com"` がそのまま残る（正規化の不一致）🌀
* `Number(form.age)` が `NaN` でも通って、後で計算が爆発する💣

そして一番つらいのがこれ👇

### 「直すとき」が地獄😵‍💫🧹

* 仕様変更：「年齢は 13歳以上」になった！
  → どこに age チェックがあるか探す
  → 直し忘れが出る
  → “特定ルートだけバグる” が発生😇

---

## 5) さらに重要：TypeScriptの型だけでは、入口は守れない🛡️❓

ここ、超だいじ🙂✨
TypeScriptは **開発中（コンパイル時）** に助けてくれるけど、

* 実行時には型注釈が消える
* “型があるから安全” にはならない

って公式ドキュメントでもハッキリ書かれてるよ📌
「型注釈は実行時の動きを変えない」ってやつ！ ([typescriptlang.org][1])

だから外部入力（フォーム、API、CSV、DB、外部API）は **実行時にチェック** が必要になるのね🙂

---

## 6) 良い考え方：入口で一回だけ保証する🚪🛡️✨

合言葉はこれ👇

### ✅ 「境界で検証して変換」→「中は信じる」🙂🏰

* 境界（入口）で
  unknown / string みたいな “信用できない値” を受け取る🕵️‍♀️
* そこでまとめて検証する🧪
* OKなら「検証済みの形」に変換してから中へ渡す💎
* ドメイン内部では “再チェックしない” を目指す（チェック散らばりを止める）🧼✨

この発想が、次章の「境界（Boundary）を見つけよう🚧📍」につながるよ〜🙂✨

---

## 7) 改善例：入口に “検問所” を作る🚓🚪✨

ポイントは **「ドメインの関数は、検証済みだけ受け取る」** だよ🙂

```ts
// 入口が作る「検証済みのデータ」
type SignupInput = {
  email: string;       // ここではまだプリミティブだけど「検証済み」の意味
  age: number;
  displayName: string;
};

// 入口の検問所（ここにチェックを集約する）
function parseSignup(raw: unknown): { ok: true; value: SignupInput } | { ok: false; errors: string[] } {
  const errors: string[] = [];

  if (typeof raw !== "object" || raw === null) {
    return { ok: false, errors: ["request must be an object"] };
  }

  const obj = raw as Record<string, unknown>;

  const email = typeof obj.email === "string" ? obj.email.trim() : "";
  if (email.length === 0) errors.push("email required");
  if (email.length > 0 && !email.includes("@")) errors.push("email invalid");

  const age = typeof obj.age === "number" ? obj.age : Number(obj.age);
  if (!Number.isFinite(age)) errors.push("age must be a number");
  if (Number.isFinite(age) && (age < 0 || age > 120)) errors.push("age out of range");

  const displayName = typeof obj.displayName === "string" ? obj.displayName.trim() : "";
  if (displayName.length === 0) errors.push("displayName required");

  if (errors.length > 0) return { ok: false, errors };

  return { ok: true, value: { email, age, displayName } };
}

// ドメイン側：もう「検証済み」しか来ない前提に寄せる
function createUser(input: SignupInput) {
  // ここでは基本、検証しない（散らばり防止）
  return { id: crypto.randomUUID(), ...input };
}
```

### 何が嬉しい？😍✨

* チェックが1箇所に集まる → 直す場所が明確🧭
* UIでもCSVでもAPIでも、入口が同じ検問所を通るようにできる🚪🚪🚪
* ドメイン側のコードがスッキリして “意図” が見える🙂💎

---

## 8) 今どきの流れ（最新の周辺事情）📰✨

この「入口で実行時検証」文化はますます強くなってるよ🙂
最近はスキーマ検証ライブラリも進化していて、たとえば Zod は v4 が安定版として案内されてるよ📦✨ ([Zod][2])
さらに、Zod/Valibot/ArkType などで共通インターフェースを作ろうという “Standard Schema” の流れもある（ライブラリ横断で扱いやすくする動き）🧩🤝 ([Zenn][3])

（この教材でも後半で「スキーマ→型が付く」気持ちよさをちゃんとやるよ〜😌✨）

※ TypeScript自体も高速化のためにネイティブ実装（TypeScript 7のプレビュー等）の話が進んでるけど、これは主に速度・開発体験の改善の方向だよ🚀 ([Microsoft Developer][4])

---

## 9) ミニ課題（15〜30分）📝✨

### 課題A：散ってるチェック探しゲーム🔍🌀

手元のコード（または想像の題材）で👇を探してみてね🙂

* 同じような if が複数箇所にある
* trimしてる場所としてない場所がある
* Number変換してるのに NaN チェックがない
* 例外/戻り値がバラバラ（UIだけ優しいメッセージ、他は即throw…）

### 課題B：入口関数を1個だけ作る🚪🛡️

* どこか1つ（例：フォーム送信）だけでいいから
  「parse〇〇」みたいな関数を作って、チェックを集約してみよう🙂✨

---

## 10) AI活用テンプレ（この章ver）🤖💡✨

そのままコピペで使えるよ〜😆💕

* 「このコードで入力チェックが散ってる箇所を列挙して。漏れそうな観点も追加して」🔍
* 「この不変条件（例：年齢0〜120）を破る入力パターンを20個出して」🧠
* 「バリデーションを入口の関数に集約したい。分離案と関数名案を出して」🚪✨
* 「“途中で検証” が残ってたら指摘して、削除していい根拠も説明して」🧹🙂

---

## まとめ✨

* チェックが散ると、**漏れる・直し忘れる・ルート限定バグが出る** 😱
* TypeScriptの型は実行時には消えるから、**入口は実行時チェックが必要** 🧪 ([typescriptlang.org][1])
* だから「入口で一回だけ保証する🚪🛡️」が効く！

次の第4章では、その「入口＝境界」を具体的に見つけていくよ〜🚧📍✨

[1]: https://www.typescriptlang.org/docs/handbook/2/basic-types.html "TypeScript: Documentation - The Basics"
[2]: https://zod.dev/v4 "Release notes | Zod"
[3]: https://zenn.dev/osushioichii/articles/816e8437569b1c "Standard Schema とは何か？その使用例と実装方法"
[4]: https://developer.microsoft.com/blog/typescript-7-native-preview-in-visual-studio-2026 "TypeScript 7 native preview in Visual Studio 2026 - Microsoft for Developers"
