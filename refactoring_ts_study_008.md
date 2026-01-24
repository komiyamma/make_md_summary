（第8章として「変更を小さく刻む＝1コミット1説明」を体で覚えるために、分割の考え方・手順・例題・ミニ課題・AI活用の型まで、教材ページとして完結する形で作ります。）


## 第8章 「小さく刻む」練習（1コミット1説明）👣📌

### ねらい🎯

「変更が大きすぎて怖い😱」を卒業して、**1コミット＝1つの説明**でスッキリ進められるようになるよ〜！✨

---

### この章でできるようになること🌸

* 「大きい変更」を、**安全な小分け**にできる🧩✨
* VS Codeで**部分的にステージ（hunk/行単位）**してコミットできる🧑‍💻📌
* コミットメッセージを「何したか」じゃなくて「何のため」を軸に書ける✍️💡
* AIに**分割案**や**メッセージ案**を出してもらって、比較して選べる🤖🔍

---

### 用語ミニ辞典📚

* **diff（差分）**：何が変わったかの見える化👀
* **stage（ステージ）**：今回コミットする変更だけを「選ぶ」こと📌
* **hunk（ハンク）**：差分のかたまり（まとまった変更の塊）🧱
* **partial commit（部分コミット）**：同じファイル内でも、必要な行だけコミットすること✂️

---

## 1. なんで「小さく刻む」と勝てるの？🏆✨

### 小さいコミットの良いところ💖

* **レビューが秒速で読める**👀⚡（差分が少ない＝理解が早い）
* **戻すのが簡単**🔙（1コミットだけ取り消しやすい）
* **バグった時の犯人がすぐ見つかる**🕵️‍♀️（変更点が少ないから）
* **AIの提案を検証しやすい**🤖✅（1回で直す量が少ないほど安全）

### 逆に「大きいコミット」のつらさ😵‍💫

* 「どこで壊れた？」が分からない
* 変更理由が説明できない
* 直したい場所が増えて、さらにカオス化🌪️

---

## 2. 「1コミット1説明」の合格ライン✅📌

次の3つが満たせたら合格だよ〜！🌟

1. **目的が1つ**（例：命名だけ、抽出だけ）🎯
2. **確認ポイントが1つ**（型チェック通る、テスト通る、動作同じ）✅
3. **1文で説明できる**（レビューに貼れる文章）📝

---

## 3. 分割の基本ルール（迷ったらこれ）🧭✨

### ルールA：混ぜない🧼

* **見た目（フォーマット）**と**中身（ロジック）**は別コミット🎀⚙️
* **リネーム**と**処理の移動**はできれば別コミット🏷️➡️📦
* **振る舞い変更**（仕様変更・バグ修正）は、リファクタと別コミット🚧

### ルールB：依存の順番を守る👣

よくある安全順はこれ👇

1. **名前を整える**🏷️
2. **定数化・式の整理**🔢
3. **関数を抽出**✂️
4. **分岐や流れを整理**🚦
5. **最後に見た目**（必要なら）🎀

---

## 4. 実演：1つの「大きい変更」を5コミットに分ける🧩➡️📌

ここからは、ありがちなコードを例に「どう刻むか」を見せるね👀✨
（※あくまで例なので、実務では状況に合わせてね🌷）

### ビフォー（臭いが混ざってる）👃💦

```ts
type Item = { price: number; qty: number; category?: "food" | "other" };

export function calcTotal(items: Item[], coupon?: string) {
  let s = 0;

  for (const it of items) {
    if (it.category === "food") {
      s += it.price * it.qty * 1.08;
    } else {
      s += it.price * it.qty * 1.1;
    }
  }

  if (coupon) {
    if (coupon === "OFF10") {
      s = s - 10;
    } else if (coupon === "OFF20") {
      s = s - 20;
    }
  }

  return Math.round(s);
}
```

このコードの「やりたい改善」はいっぱいあるよね👇

* 変数`s`が意味不明😵‍💫
* 税率のマジックナンバーが散らばってる🔢💦
* クーポンのifが伸びそう🌿
* 1つの関数がいろいろやってる🍱

---

### ✅ 分割コミット案（5つに刻む）👣📌

#### Commit 1：命名だけ直す🏷️✨

* `s` → `total` とか、読みやすくする
* **ロジックは絶対にいじらない**
* 説明：*「意味が伝わる名前にした」*

```ts
export function calcTotal(items: Item[], coupon?: string) {
  let total = 0;

  for (const it of items) {
    if (it.category === "food") {
      total += it.price * it.qty * 1.08;
    } else {
      total += it.price * it.qty * 1.1;
    }
  }

  if (coupon) {
    if (coupon === "OFF10") {
      total = total - 10;
    } else if (coupon === "OFF20") {
      total = total - 20;
    }
  }

  return Math.round(total);
}
```

---

#### Commit 2：マジックナンバーを定数化🔢🪄

* 税率や割引額を「名前つき」にする
* 説明：*「数値の意味を名前で表した」*

```ts
const TAX_FOOD = 1.08;
const TAX_OTHER = 1.1;

const COUPON_OFF10 = 10;
const COUPON_OFF20 = 20;

export function calcTotal(items: Item[], coupon?: string) {
  let total = 0;

  for (const it of items) {
    if (it.category === "food") {
      total += it.price * it.qty * TAX_FOOD;
    } else {
      total += it.price * it.qty * TAX_OTHER;
    }
  }

  if (coupon) {
    if (coupon === "OFF10") total = total - COUPON_OFF10;
    else if (coupon === "OFF20") total = total - COUPON_OFF20;
  }

  return Math.round(total);
}
```

---

#### Commit 3：税計算を関数に抽出✂️📦

* forループ内の「計算」を切り出す
* 説明：*「税計算の意図を関数名にした」*

```ts
function calcItemTotalWithTax(item: Item): number {
  const base = item.price * item.qty;
  return item.category === "food" ? base * TAX_FOOD : base * TAX_OTHER;
}

export function calcTotal(items: Item[], coupon?: string) {
  let total = 0;

  for (const it of items) {
    total += calcItemTotalWithTax(it);
  }

  if (coupon) {
    if (coupon === "OFF10") total = total - COUPON_OFF10;
    else if (coupon === "OFF20") total = total - COUPON_OFF20;
  }

  return Math.round(total);
}
```

---

#### Commit 4：クーポン処理を小さく整理🧾➡️🏷️

* 「クーポン → 割引額」を関数化 or テーブル化
* 説明：*「クーポン判定を1か所に集めた」*

```ts
function discountByCoupon(coupon?: string): number {
  if (!coupon) return 0;
  if (coupon === "OFF10") return COUPON_OFF10;
  if (coupon === "OFF20") return COUPON_OFF20;
  return 0;
}

export function calcTotal(items: Item[], coupon?: string) {
  let total = 0;

  for (const it of items) {
    total += calcItemTotalWithTax(it);
  }

  total -= discountByCoupon(coupon);
  return Math.round(total);
}
```

---

#### Commit 5：最後に見た目を整える🎀🧹

* ここで初めて「書き方の好み」を入れてOK（必要な場合だけ）
* 説明：*「読みやすい形に整形した」*

---

## 5. VS Codeで「部分ステージ」して刻む（超重要）🧑‍💻📌

### 5.1 どんな時に必要？🤔

同じファイルでこうなった時👇

* 上の方でリネーム
* 下の方で関数抽出
* さらに別の所で整形
  …みたいに「混ざっちゃった」時😵‍💫

### 5.2 やり方（UI）👣✨

1. 左の **Source Control**（ソース管理）を開く📂
2. 変更ファイルをクリックして **diff表示**にする👀
3. コミットしたい行（範囲）を選択する🖱️
4. エディタ右上の「…」から **Stage Selected Ranges** を選ぶ📌✨
5. ステージされた差分だけコミットする💾

この「選んだ範囲だけステージ」が、刻む力の正体だよ〜！✂️✨
（VS Codeでは差分画面から範囲選択→Stage Selected Ranges ができるよ） ([Stack Overflow][1])

---

## 6. ターミナルで刻む（慣れると超便利）⌨️✨

### `git add -p`（変更を対話で選ぶ）🧩

* hunkごとに「これ入れる？入れない？」って聞いてくれるやつ💡
* ざっくりコマンド：

```bash
git add -p
```

もっと細かく「行単位」にしたいときは、編集モード（`e`）で調整する方法もあるよ✂️ ([git-tower.com][2])

---

## 7. コミットメッセージのコツ（1コミット1説明の文章化）✍️💖

### 書き方テンプレ🧁

* **目的を書く**：何のため？
* **範囲を書く**：どこ？
* **短く**：1行で伝える

例👇

* `Rename variables for readability` 🏷️
* `Extract tax calculation into function` ✂️
* `Centralize coupon discount mapping` 🧾

### NG例😵

* `fix`（何を？どこを？なぜ？が不明）
* `update`（更新って何！？）
* `many changes`（絶対だめ😂）

---

## 8. ミニ課題✍️（実戦っぽく刻もう）👣🔥

### 課題A：分割設計（紙に書くだけOK）📝

次の「大きい変更」を、**3〜6コミット**に分けてみてね👇

* 変数名が曖昧なのでリネームしたい🏷️
* 長い関数を3つに分けたい✂️
* マジックナンバーを定数化したい🔢
* ネストifをガード節にしたい🚦
* ついでに整形もしたい🎀

✅ 出力はこれだけでOK：

* Commit 1：目的（1文）
* Commit 2：目的（1文）
* …

---

### 課題B：VS Code部分ステージ練習🧑‍💻📌

1つのファイルで、わざと「混ぜた変更」を作るよ👇

* 上：リネーム
* 中：空行や整形
* 下：関数抽出

そして、**部分ステージで「リネームだけ」を先にコミット**してみてね✂️✨
成功したら、次は抽出、最後に整形🎀

---

### 課題C：コミットメッセージ3案勝負🥊✍️

同じ変更に対して、メッセージを3案出してみて👇

* かたい（真面目）
* やさしい（初心者にも伝わる）
* ルールっぽい（統一感重視）

---

## 9. AI活用ポイント🤖✨（お願い方＋チェック観点✅）

### 9.1 分割案を出してもらうプロンプト🧩

```text
この変更内容を「1コミット1説明」になるように、3〜6コミットに分割した案を3パターン出して。
各コミットごとに：
- 目的（1文）
- 触る範囲（ファイルや関数）
- 確認ポイント（型チェック/テスト/動作確認）
も書いて。
「整形だけのコミット」は最後に回して。
```

### 9.2 コミットメッセージ案を出してもらう📝

VS CodeのCopilot系機能では、変更内容からコミットメッセージ生成の導線が用意されてるよ（ソース管理の入力欄あたりのキラキラ✨） ([Visual Studio Code][3])
ただし…👇

### 9.3 AIの提案チェック✅（ここ超大事）

* そのコミット、**目的1つ**になってる？🎯
* そのコミットだけで、**動く状態**？（途中で壊れてない？）🛟
* 「整形」と「中身」が混ざってない？🎀⚙️
* 差分を自分の目で読んで説明できる？👀📝

---

## 10. よくあるつまずき😵‍💫 → 解決ワザ🛟✨

### つまずき①：混ざりすぎて分けられない🌪️

✅ 解決：

* まず **リネームだけ**に戻せるところを戻す（Undo活用）🔙
* それでも無理なら、**「やり直し用ブランチ」**で一度落ち着く🌿
* 次からは「触る前に分割設計（コミット計画）」🗺️

### つまずき②：部分ステージが怖い😱

✅ 解決：

* **ステージ済み差分だけ**を必ず確認してからコミット（staged diffを見る）👀
* 「今コミットする分」と「残る分」を頭で分ける🧠📌

### つまずき③：コミットが細かすぎて多すぎる📚💦

✅ 解決：

* 目安は「レビューで1分で読める」くらい👀⏱️
* “意味の塊”が1つなら、細かくしすぎなくてOK🙆‍♀️

---

## 11. まとめ：この章のお守りフレーズ🧿✨

* **1コミット＝1つの説明**📌
* **混ぜない（整形は最後）**🎀🚫
* **部分ステージで刻めるようになる**✂️
* **AIは案出し係、採用判断は人間**🤖✅

---

### おまけ：TypeScriptの「いま」と「近い未来」👀🧷

* npm上での最新安定版は **5.9.3** として案内されているよ（2025年秋時点で公開、現在も最新として表示） ([npm][4])
* その先の **6.0/7.0（ネイティブ化の流れ）** も進捗が共有されていて、開発体験の高速化が大きなテーマになってるよ 🚀 ([GitHub][5])

- [The Verge](https://www.theverge.com/news/808032/github-ai-agent-hq-coding-openai-anthropic?utm_source=chatgpt.com)
- [IT Pro](https://www.itpro.com/technology/artificial-intelligence/openai-says-gpt-5-2-codex-is-its-most-advanced-agentic-coding-model-yet-heres-what-developers-and-cyber-teams-can-expect?utm_source=chatgpt.com)
- [techradar.com](https://www.techradar.com/pro/openai-launches-gpt-5-codex-with-a-74-5-percent-success-rate-on-real-world-coding?utm_source=chatgpt.com)

[1]: https://stackoverflow.com/questions/34730585/vs-code-how-to-stage-and-commit-individual-changes-in-a-single-file?utm_source=chatgpt.com "How to stage and commit individual changes in a single file?"
[2]: https://www.git-tower.com/learn/git/faq/staging-single-lines?utm_source=chatgpt.com "How to Stage a Single Line in Git"
[3]: https://code.visualstudio.com/docs/copilot/copilot-smart-actions?utm_source=chatgpt.com "AI smart actions in Visual Studio Code"
[4]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[5]: https://github.com/microsoft/TypeScript/issues/62785?utm_source=chatgpt.com "Iteration Plan for Typescript 5.10/6.0 ? · Issue #62785 ..."
