# 第4章　境界（Boundary）を見つけよう🚧📍✨

この章は **「どこで不変条件チェックをやるべきか？」の地図を作る章**だよ〜🗺️💎
境界さえ見つかれば、次から「入口でまとめて検証して、内側は信じる🛡️」ができるようになるよ😊✨

---

## この章のゴール🎯✨

章末までに、あなたができるようになること👇

* 「境界ってどこ？」を自分の題材で **3つ以上** 言える🗣️✨
* それぞれの境界で「何が入ってきて」「何を保証するか」を書ける📝
* 「検証→変換→ドメイン」へ流すための **入口の形** をイメージできる🚪➡️🏰

---

## 1) 境界ってなに？（めっちゃやさしく）🚧🙂

**境界 = 外の世界と、あなたのプログラム（ドメイン）の境目** だよ〜🌍➡️🏰

外の世界って、だいたいこんな感じ👇

* ユーザーが入力した文字（空欄・誤字・絵文字・変な値…なんでも来る😇）
* APIで飛んできたJSON（欠けてたり、型違ったり、古い仕様だったり😇）
* DBから読んだ値（過去のバグで壊れてる可能性もゼロじゃない😇）
* 外部サービスのレスポンス（仕様変更・欠損・単位違い😇）

だから境界は、イメージ的にこう👇

* **境界 = 門番さん** 🧍‍♀️🛡️
* 門番さんは「怪しい荷物（入力）」をチェックして
* OKなら「中で使える安全な形（型）」にして中に通す✨

---

## 2) 境界が見つかると何が嬉しいの？🥹💖

境界が曖昧だと、コードのあちこちにこういうのが散る👇

* `if (!x) return ...`
* `if (typeof x !== "string") ...`
* `if (x < 0) ...`

散るとどうなる？😱

* どこかでチェック漏れして事故る💥
* 仕様変更のたびに「全部探して直す」地獄🧟‍♀️
* 「この値って安全？」がずっと不安😵‍💫

境界が決まると、こうなる👇✨

* **境界で1回だけ検証して保証する** ✅🚪
* ドメイン内では **“安全な型しか存在しない”** ので、安心してロジックを書ける💎😊

---

## 3) 境界はどこにある？代表パターン集📌✨

### A. 「入ってくる境界」🚪⬅️

* 画面フォーム（入力欄）🧾
* APIのリクエスト（JSON）📨
* URL/クエリパラメータ 🔗
* Cookie / LocalStorage / Session 🍪💾
* CLI引数、環境変数 🖥️
* ファイル入力（CSV/画像/テキスト）📄
* メッセージキュー / webhook 📩

### B. 「出ていく境界」➡️🚪

* APIレスポンスを返す（外向けのDTO）📤
* DBへ保存する（保存形式へ変換）🗄️
* 外部APIに送る（相手仕様へ変換）📡
* ログ/監視に出す（情報の出し方を決める）📈

✅ コツ：**「I/Oしてる場所 = 境界の候補」** だよ〜👀✨
（I/O = 入出力ね！）

---

## 4) 境界を見つける5ステップ🗺️➡️✅

### Step1: まず「機能1個」を選ぶ🎯

例：

* 会員登録🌸
* 注文作成🛒
* パスワード変更🔑
* 在庫引当📦

### Step2: 入力→処理→出力を1本線で描く🧵✨

ざっくりでOKだよ！👀

例（会員登録）👇

* UIフォーム🧾 → API受信📨 → 検証✅ → VO生成💎 → 登録処理🏰 → DB保存🗄️ → レスポンス📤

### Step3: 「外から来るデータ」を全部列挙する📝

* 画面：`email`, `password`, `nickname`
* API：`req.body` の JSON
* DB：既存ユーザーの検索結果

### Step4: その場で“信じちゃダメな理由”を一言で書く😇

* email：空欄や変な形式が来る
* password：短すぎ、長すぎ、スペースだけなど
* DB：過去データが壊れてる可能性

### Step5: 境界ごとに「検証→変換」の責任を置く📦➡️💎

境界ごとにこう決める👇

* **受け取る形**（だいたい `unknown` / 生JSON / string）
* **最低限の検証**（必須、型、範囲、形式）
* **正規化**（trim、小文字化など）
* **ドメイン型へ変換**（Email, UserIdみたいな “混ざらない型”）

---

## 5) ミニ例：会員登録の「境界」を切ってみる🌸🚧

ここでは“雰囲気”をつかもう〜🙂✨
（実行時バリデーションのガチ実装は後の章で深掘りするよ🧪）

### 5-1. 境界関数は「外→中」の門にする🚪🛡️

* 入力は **unknown**（信用しない）🕵️‍♀️
* 成功したら **ドメインで使える型** に変換して渡す💎

```ts
// 境界：APIハンドラのイメージ
type RegisterInputDto = {
  email: string;
  password: string;
  nickname: string;
};

type BoundaryError =
  | { kind: "Validation"; messages: string[] }
  | { kind: "Unexpected"; message: string };

type Result<T> =
  | { ok: true; value: T }
  | { ok: false; error: BoundaryError };

// ドメインに渡す「安全な形」(ここでは仮)
type RegisterCommand = {
  email: string;     // 本当は Email VO にしたい（後の章でやる💎）
  password: string;  // 本当は Password VO にしたい
  nickname: string;  // 本当は Nickname VO にしたい
};

export function parseRegisterCommand(raw: unknown): Result<RegisterCommand> {
  // 1) 形チェック（超ざっくり）
  if (typeof raw !== "object" || raw === null) {
    return { ok: false, error: { kind: "Validation", messages: ["入力がオブジェクトじゃないよ😢"] } };
  }

  const r = raw as Partial<Record<string, unknown>>;

  // 2) 1個ずつ取り出して検証（次章以降はスキーマでまとめる🧪）
  const email = typeof r.email === "string" ? r.email.trim() : "";
  const password = typeof r.password === "string" ? r.password : "";
  const nickname = typeof r.nickname === "string" ? r.nickname.trim() : "";

  const errors: string[] = [];
  if (!email) errors.push("emailが空だよ📩");
  if (!email.includes("@")) errors.push("emailの形が変かも…🤔");
  if (password.length < 8) errors.push("passwordは8文字以上がいいな🔑");
  if (!nickname) errors.push("nicknameが空だよ🙂");

  if (errors.length > 0) {
    return { ok: false, error: { kind: "Validation", messages: errors } };
  }

  // 3) OKなら「中で使える形」へ
  return { ok: true, value: { email, password, nickname } };
}
```

ここで大事なのはコレ👇✨

* **境界が raw を受けて**
* **境界で検証＆整形して**
* **中へは “安心な形” だけ通す** 🛡️💎

---

## 6) ミニ課題：あなたの題材の境界を3つ以上書こう🗺️📝✨

下の表を埋めてみてね〜😊
（最初は雑でOK！後でどんどん良くなるよ🌱）

| 境界の名前     | 入/出 | 具体例（何が来る/出る？）  | 信じちゃダメな理由😇 | その境界で保証したいこと✅      |
| --------- | --- | -------------- | ----------- | ------------------ |
| 例：会員登録API | 入   | req.body(JSON) | 欠損/型違い/空文字  | 必須項目OK、形式OK、trim済み |
|           |     |                |             |                    |
|           |     |                |             |                    |

### お手本（例：ToDoアプリ）🧸✨

* UIフォーム（タイトル入力）🧾：空、長すぎ、スペースだけ
* LocalStorage読み込み💾：古い形式、壊れてるJSON
* APIレスポンス📨：`done` が boolean じゃない、項目欠け

---

## 7) よくある「境界ミス」あるある😵‍💫💥

### あるある1：ドメイン内で毎回チェックしてる🌀

**症状**：あちこちに `if` が散っていく
**治し方**：入口（境界）にチェックを寄せる🚪✅

### あるある2：DTOとドメインが混ざる🍲

**症状**：画面都合の `snake_case` や欠損許容がドメインに侵入
**治し方**：境界で **DTO→ドメイン** に変換する📦➡️💎

### あるある3：「DBの値は正しいよね？」って信じる🗄️😇

**症状**：過去データが原因で突然落ちる
**治し方**：**読み込みも境界**。読み込み時にも変換・検証を意識する🧼

---

## 8) 1分チェックリスト✅⏱️✨

* [ ] その機能の「外から入る値」を全部言える？📝
* [ ] I/Oしてる場所を境界として意識できた？🚪
* [ ] 境界で「検証→正規化→変換」をやる方針になってる？🛡️
* [ ] ドメイン内では「安全な型だけが存在する」未来が見えた？💎✨

---

## 9) AI活用コーナー🤖💡✨（境界探しが爆速になるやつ）

そのままコピペで使える質問テンプレだよ〜📋💕

* 「この機能の境界（入力・出力）候補を全部列挙して。UI/API/DB/外部API/ストレージ/ファイル/環境変数まで！」🗺️
* 「この入力が壊れるパターンを20個出して（欠損・型違い・境界値・悪意ある入力も）」😈🧪
* 「DTOとドメインの分離ポイントを提案して。変換関数の責務もセットで！」📦➡️🏰
* 「境界で返すべきエラーメッセージを初心者向けに整えて」🫶✨

---

## 10) 2026-01-20時点の“最新動向メモ”🧭✨

* TypeScript は **5.9 系**が最新リリースとして案内されていて、パッケージの最新も **5.9.3** が表示されてるよ📦✨。([Microsoft for Developers][1])
* いっぽうで、コンパイラ等をネイティブ化して高速化する **TypeScript 7 のプレビュー**（Visual Studio 2026向け）も進んでるみたい🧨⚡（大規模コードだとコンパイルがかなり速くなる狙い）。([Microsoft Developer][2])
* Node.js は **v24 “Krypton” が Active LTS** で、リリース表は 2026-01-19 更新になってる📅。([Node.js][3])
* 直近だと Node.js のセキュリティリリースで **24.13.0 / 25.3.0 など**が出てるので、開発環境も定期的にアップデート意識あると安心だよ〜🔒✨。([Node.js][4])

（この教材の本筋は「境界で検証して型で守る」だから、バージョンは目安として“いまはこう”って覚え方でOKだよ🙂）

---

## 次章予告チラ見せ👀✨

次の第5章で「最小のTypeScriptプロジェクトの型安全な土台」を作って、ここで見つけた境界を **実装しやすい形** に整えていくよ〜🧰💕

---

必要なら、あなたの題材（アプリ/機能名だけでOK）を1つ投げてくれたら、**その題材の“境界マップ”を一緒に作る**ところまで、この章の内容で即やっちゃうよ🗺️💪✨

[1]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/?utm_source=chatgpt.com "Announcing TypeScript 5.9"
[2]: https://developer.microsoft.com/blog/typescript-7-native-preview-in-visual-studio-2026?utm_source=chatgpt.com "TypeScript 7 native preview in Visual Studio 2026"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://nodejs.org/en/blog/vulnerability/december-2025-security-releases?utm_source=chatgpt.com "Tuesday, January 13, 2026 Security Releases"
