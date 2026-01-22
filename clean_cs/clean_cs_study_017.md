# 第17章：Use Caseとは？（アプリの手順書）🧾🎮✨

この章はね、**「Entity（ルールの核）」を、アプリとして“どう使うか”をまとめる場所**が Use Case だよ〜って話です😊
（いまの最新だと .NET 10 / C# 14 / Visual Studio 2026 が中心になってるよ〜🆕✨） ([Microsoft for Developers][1])

---

## 1) Use Caseをひとことで言うと？🧠💡

**Use Case = ユーザーの目的を叶えるための「手順書（レシピ）」**だよ🍳📖✨

* Entity：**正しい状態・正しいルール**を持つ（ドメインの核）💎
* Use Case：Entityたちを使って、**目的を達成するための“段取り”**を決める🧾✨

  * 例）「メモを作る」「メモを更新する」「アーカイブする」など📝

イメージはこんな感じ👇

* Entity：素材と調理ルール（生肉はちゃんと火を通す、みたいな）🥩🔥
* Use Case：今日の献立（カレー作る！→切る→炒める→煮る→盛る）🍛✨

---

## 2) なんでUse Caseが必要なの？😵‍💫➡️😌

もし Use Case が無いと、こんな事故が起きやすいよ💥

### ❌事故1：Controller（UI側）が太る🍔

「入力チェック」「Entity生成」「保存」「例外処理」「画面用整形」…が全部UIに集まりがち😇
→ 変更が怖いし、テストもつらい🥺

### ❌事故2：Entityが何でも屋になる🌀

「保存（DB）」「HTTPの都合」「画面表示の都合」まで背負うと、Entityが汚れちゃう🧼💦

### ✅Use Caseがいるとこうなる！✨

* UIは薄くできる（受け取って渡すだけ）🚪
* Entityは純粋なルールに集中できる💎
* 変更点が「手順（Use Case）」に集まり、影響範囲が読みやすい👀✨

---

## 3) Use Caseの“責務”はここまで！✋📦

Use Caseがやること（だいたいこの4つ）👇

1. **入力を受け取る**（ただし “外側の形” そのままは持ち込まない）📨
2. **Entityを使って処理を進める（段取り）**🧩
3. **保存や外部呼び出しは「インターフェース経由」**でお願いする🚪
4. **結果を外側へ返す**（表示用の形にするのは外側の役目）🎁

ここ大事〜！
Uncle Bob の図でも、**Use Caseは外側（Presenter）を直接呼べない**ので、**出力はインターフェース（Output Port）経由**にする、って説明されてるよ📌 ([blog.cleancoder.com][2])

---

## 4) Use Caseの“形”をざっくり掴もう✍️✨

「メモ作成（Create Memo）」を例に、超ざっくり流れ👇

1. UIが「メモ作りたい！」って来る🙋‍♀️
2. Use Caseが手順を進める🧾
3. 保存は “保存係（Repository/Gateway）” にお願いする🗄️
4. 結果は “結果係（Presenter など）” に渡す🎤

図にするとこんな感じ（雰囲気だけでOK）👇

* UI → **Use Case** →（保存インターフェース）→ DB実装
* **Use Case** →（出力インターフェース）→ Presenter → 画面/APIレスポンス

「内側は外側を知らない」って原則を守るための形だよ〜🛡️ ([blog.cleancoder.com][2])

---

## 5) ちいさなコードで“手順書感”を体験しよ🧪📝

ここでは **「Use Caseは“段取りを書く場所”」**って感覚だけ掴もうね😊
（ポートやモデル設計は次章以降でもっと丁寧にやるよ〜🔌✨）

```csharp
public sealed class CreateMemoUseCase
{
    private readonly IMemoRepository _repo;

    public CreateMemoUseCase(IMemoRepository repo)
    {
        _repo = repo;
    }

    public async Task<CreateMemoResult> ExecuteAsync(string title, string body)
    {
        // 1) Entityを作る（ルールはEntity側で守らせるのが基本）
        var memo = Memo.Create(title, body);

        // 2) 保存（DB直叩きじゃなくて、インターフェース越し）
        await _repo.SaveAsync(memo);

        // 3) 結果を返す（表示用の整形はまだしない）
        return new CreateMemoResult(memo.Id.Value);
    }
}

public interface IMemoRepository
{
    Task SaveAsync(Memo memo);
}

public sealed record CreateMemoResult(Guid MemoId);
```

ポイントはこれだけ覚えてね👇💡

* Use Caseは **Entityを使って段取りを書く**🧾
* 保存や外部I/Oは **インターフェースに逃がす**🚪
* “画面の都合の形” にしない（それはPresenter側）🎤

---

## 6) よくある勘違いあるある😇⚠️

### 😵「Use Case = ただのServiceでしょ？」

近いけど、**“何でも屋Service” になると危険**！
Use Caseはあくまで「ユーザーの目的」単位にするのがコツ🎯

### 😵「Use CaseにDTO（APIの形）をそのまま渡していい？」

やりがちだけど、**外側の都合が中に侵入**しやすいよ〜🥺
→ 入力モデルは “Use Case用” を用意する方向が安全（次章でやる）📨✨

### 😵「Use Caseで結果を直接 return すればOutput Portいらないのでは？」

小さいアプリでは return でも成立することあるよ👌
でも Clean Architecture の教科書的には、**外側に依存しないために Output Port を使う**説明がされてる（Presenterを直接知らないため）📌 ([blog.cleancoder.com][2])

---

## 7) ミニ課題🎮✍️（10〜20分）

題材：メモアプリ📝✨

### 課題A：手順書を書く🧾

「メモ作成」を文章で書いてみて👇

* 入力：タイトル、本文
* 手順：Entity生成 → 保存 → 結果返す
* 失敗：タイトル空、長すぎ…など（どこで止める？）

### 課題B：Use Case候補を8個出す🧠💡

例）Create / Get / Update / Delete / Search / Archive / Restore / AddTag …みたいに🎯

---

## 8) AI活用（Copilot / Codex）🤖✨：ここでの使い方が安全！

AIはめっちゃ便利だけど、**Use Caseの目的は「段取りをスッキリさせる」こと**なので、こう使うのがおすすめ😊

### ✅プロンプト例（そのまま投げてOK）💬

* 「メモ作成Use Caseの手順を書いて。入力・処理・出力・失敗ケースを箇条書きで」
* 「このUse Caseが“UI/DB寄り”になってないか、責務のはみ出しを指摘して」
* 「Use Caseのテスト観点（Given-When-Then）を5個出して」

### ⚠️AIがやりがちな地雷💣

* Use CaseにEF CoreやHttpContextを混ぜる提案（やめて〜！）🙅‍♀️
* “汎用Repository” を作りすぎて逆にわかりにくくする（最小でOK）🧩

---

## 9) まとめ✅✨（この章で持ち帰ること）

* Use Caseは **アプリの手順書（レシピ）**🧾🍳
* Entityは **ルールの核**、Use Caseは **段取り**💎➡️🧩
* I/O（DB・外部）は **インターフェース越し**にするのが基本🚪
* 結果の“見せ方”は外側（Presenter）へ🎤
* 「内側は外側を知らない」思想の延長で、Output Portが登場するよ📌 ([blog.cleancoder.com][2])

---

## 次章予告👀✨（第18章）

次は、**Use Caseの“入口”＝Input Port（入力境界）**をちゃんと設計して、UIとUse Caseの接続をキレイにするよ〜🔌⬅️💖

[1]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
[2]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
