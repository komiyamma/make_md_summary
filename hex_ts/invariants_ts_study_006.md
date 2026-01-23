# 第6章：「型で守れること」と「実行時に守ること」分けよう 🧩✅

この章はね、超重要な“分岐点”だよ〜！✨
ここを押さえると「不変条件を守る設計」が一気にスムーズになるよ🛡️💎

---

## 0. いまの最新状況ちょいメモ 🗞️✨（安心材料）

* TypeScript の安定版は「5.9.3」タグが最新として公開されてるよ（2025-10-01）📌 ([GitHub][1])
* TypeScript チームは「6.0 は 5.9 と 7.0 の橋渡し（bridge）」って位置付けを明言してるよ🧩（早めの 2026 を狙う話も） ([Microsoft for Developers][2])
* VS Code は「TypeScript の言語サービス」と「コンパイラ（tsc）」が別物って公式に説明してるよ（ページ更新 2026-01-08）✍️ ([Visual Studio Code][3])
* 実行時バリデーションの定番 Zod は v4 系が安定していて、GitHub では v4.3.5 が Latest（2026-01-04）だよ📦✨ ([GitHub][4])

---

## 1. この章でできるようになること 🎯✨

* 「型で守れること / 実行時に守ること」を仕分けできる🧺✅
* 外から来たデータを “まず unknown 扱い” して安全に中へ入れられる🚪🕵️‍♀️
* 「境界で実行時チェック → 中は型で固定」の二段構えが作れる🧪🔒

---

## 2. まず結論：二段構えモデルが最強 🛡️💎

不変条件を守る基本はこれ👇✨

**① 境界（入口）で実行時検証する** 🧪
**② ドメイン（中）では型を信じて進む** 🔒

イメージはこんな感じ👇

```text
外部入力（信用しない😤）
   ↓  unknown
境界で検証🧪（parse / validate）
   ↓  OKなら
ドメイン型💎（信用してOK🙂）
   ↓
業務ロジック（if地獄が減る✨）
```

---

## 3. TypeScriptの「型」で守れること（コンパイル時）🧠✅

TypeScript が得意なのは **“プログラムの書き方” のミス防止** だよ✨

たとえば👇

* プロパティ名の打ち間違いを防ぐ（user.emial みたいなやつ💥）
* ユニオンで選択肢を固定できる（"Free" | "Pro" みたいに🎫）
* 分岐を型で安全にできる（タグ付きユニオンの世界🏷️）
* null/undefined を扱うミスを減らす（ちゃんと意識できる🙂）

でもね…ここがポイント⚠️

**TypeScript の型は “実行時には存在しない”**
（コンパイルすると消える＝JavaScriptだけが動く）🫥

---

## 4. 型だけでは守れないこと（実行時の現実）😅🌪️

外から来るデータって、だいたいこう👇

* フォーム入力（文字列だらけ）⌨️
* APIリクエスト（JSON）📡
* DBからの復元（壊れた古いデータもありえる）🗄️
* 外部API（欠損・型違い・単位ズレ）🤯

ここで怖いのは…

**「型が付いてる“つもり”」で進むこと** 😱
（as で黙らせると、事故が起きた瞬間にドカーン💥）

---

## 5. 入口は unknown で受けるのが基本 🕵️‍♀️❓

「外から来た値」は、まず **unknown** 扱いにするのが王道だよ✨
（any は “何でもOK” になって、守りが崩壊しやすい😵‍💫）

### ✅ ありがちな事故：JSON.parse

```ts
// ⚠️ JSON.parse の戻りは「なんでもあり」になりがち
const raw = JSON.parse('{"id": 123, "email": "a@b.com"}');

// 😱 as で黙らせると、実行時に爆発するかも
type User = { id: string; email: string };
const user = raw as User;

// ここで user.id は「stringのはず」だけど実際は number かも…
console.log(user.id.toUpperCase()); // 💥 123 に toUpperCase はない！
```

**「型がある＝安全」じゃない**
**「検証してから型を与える＝安全」** だよ🛡️✨

---

## 6. じゃあどうする？入口の武器は3つ 🧰✨

### 武器A：型ガード関数（軽め）🛡️

「これは UserDTO っぽいよね？」を自分でチェックするやつ🙂

```ts
type UserDTO = { id: string; email: string };

function isUserDTO(x: unknown): x is UserDTO {
  if (typeof x !== "object" || x === null) return false;

  const o = x as Record<string, unknown>;
  return typeof o.id === "string" && typeof o.email === "string";
}

function parseUserDTO(x: unknown): UserDTO {
  if (!isUserDTO(x)) throw new Error("UserDTOの形じゃないよ🥲");
  return x;
}
```

👍 小規模ならこれでもOK
👀 でも項目が増えると手書きが大変になりがち💦

---

### 武器B：asserts（失敗したら止める宣言）🚨

「ここを通ったら型は確定！」って強く言い切るやつ✨

```ts
type UserDTO = { id: string; email: string };

function assertUserDTO(x: unknown): asserts x is UserDTO {
  if (typeof x !== "object" || x === null) throw new Error("objectじゃない🥲");

  const o = x as Record<string, unknown>;
  if (typeof o.id !== "string") throw new Error("idがstringじゃない🥲");
  if (typeof o.email !== "string") throw new Error("emailがstringじゃない🥲");
}

function parseUserDTO(x: unknown): UserDTO {
  assertUserDTO(x);
  return x; // ここでは UserDTO として扱える✨
}
```

---

### 武器C：スキーマ（Zod など）📐✅（この教材の“定番ルート”）

スキーマの良いところは👇

* 検証ルールがまとまる🧱
* エラーメッセージを組み立てやすい🫶
* “検証したら型が付く” を体験しやすい✨

Zod v4 は安定してて、最新版は v4.3.5 が Latest だよ📦 ([GitHub][4])

```ts
import { z } from "zod";

const UserDTOSchema = z.object({
  id: z.string().min(1),
  email: z.string().email(),
});

type UserDTO = z.infer<typeof UserDTOSchema>;

export function parseUserDTO(input: unknown): UserDTO {
  return UserDTOSchema.parse(input); // 失敗したら例外（後でResult型にもできるよ✨）
}
```

---

## 7. 「どこまでをスキーマで？どこからをドメインで？」線引きルール 🧵✨

ここ、迷いやすいから “ざっくり基準” を置くね🙂

### ✅ スキーマ（境界）でやること 📐

* 必須かどうか
* 型（string/number/boolean）
* だいたいの範囲（min/max）
* メール形式、UUID形式…みたいな “一般形” ✉️

### ✅ ドメイン型（中）でやること 💎

* ビジネス固有のルール
  例：

  * 価格は「税計算後に端数ルールがある」💰
  * 在庫は「引当中は減らせない」📦
  * 会員ランクは「ある条件でしか上がらない」👑

スキーマは “入口の門番” 👮‍♀️
ドメイン型は “城のルール” 🏰
って覚えるとラクだよ〜😊✨

---

## 8. VS Codeで起きがちな混乱：言語サービスと tsc は別 🧠💡

VS Code は賢く補完してくれるけど、それは **TypeScript の言語サービス** の仕事。
一方で **コンパイル（tsc）** は別で、ワークスペースに入れたバージョンとズレることもあるよ〜🙂

公式も「言語サービスとコンパイラは別」って説明してる📌 ([Visual Studio Code][3])

この教材では、**「境界で unknown → 検証」** ができてれば、ツール差分で崩れにくい設計になるよ🛡️✨

---

## 9. AI活用コーナー 🤖💖（この章でめちゃ効く！）

コピペで使える質問テンプレ置いとくね👇✨

* 「この入力仕様から、不変条件を列挙して。型で守れるもの/実行時検証が必要なものに分類して」🧠🧺
* 「unknown を受け取って UserDTO に変換する関数を書いて。型ガード版と Zod版の両方」🛠️
* 「Zod スキーマの境界値テスト観点を10個出して」🧪📋
* 「as を使わずに型安全にする書き方に直して」🚫➡️✅

---

## 10. ミニ課題 🎲✨（手を動かすと一発で体に入る！）

### 課題A：仕分けクイズを自分で作る🧺

あなたの題材（例：会員登録、注文、投稿…）で
不変条件を **10個** 書いて、こう分類してみて👇

* 型で守れる✅
* 実行時チェックが必要🧪
* ドメイン固有（VOで守る予定）💎

### 課題B：境界関数を1本作る🚪

* 入力：unknown
* 出力：UserDTO（検証済み）
* 失敗：エラー（メッセージはやさしめに🫶）

Zod版が作れたら最高だよ〜🎉

---

## 11. よくある落とし穴 🕳️😱

* 「as」で黙らせて、静かに爆弾を運ぶ💣
* any を入口で使ってしまい、境界の意味が消える🫥
* 検証後もずっと if チェックし続けてしまう（“中は信じる”ができてない）🌀
* スキーマに全部詰め込みすぎて、ドメインのルールが迷子になる🧳💦

---

## 12. まとめ ✅✨（この章の合言葉）

* **型は“書き方”を守る🧠**
* **実行時検証は“現実のデータ”を守る🧪**
* **境界で unknown → 検証 → 型付け** 🚪🔒
* **中では型を信じて、if を減らす** 🧹✨

次の章からは、この考え方を使って「string/number地獄」をわざと体験して、抜け出す準備をしていくよ〜🧟‍♀️➡️😇✨

[1]: https://github.com/microsoft/typescript/releases?utm_source=chatgpt.com "Releases · microsoft/TypeScript"
[2]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[3]: https://code.visualstudio.com/docs/typescript/typescript-compiling "Compiling TypeScript"
[4]: https://github.com/colinhacks/zod/releases "Releases · colinhacks/zod · GitHub"
