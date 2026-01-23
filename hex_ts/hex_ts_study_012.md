# 第12章：AI拡張の準備 🤖💖

〜「AIは相棒✨ でも“設計の芯”はあなたが握る🛡️」〜

---

## 12-1. この章のゴール 🎯✨

この章が終わる頃には、こんな状態になってます😊

* VS Codeで **AIを呼び出せる**（補完・チャット・編集）🤝
* AIに渡す“ルール”を **ファイルで固定**できる（ブレ防止）📌
* AIの使いどころ／使っちゃダメどころが **感覚で分かる**⚠️
* すぐ使える **レビュー質問テンプレ**を手元に持てる🧾✨

---

## 12-2. まず知っておく：AI支援は3段階あるよ 🪜🤖

VS CodeまわりのAI支援はだいたいこの3つに分かれるよ〜😊

1. **自動補完**（コードを書いてる横で候補が出る）✍️💡
2. **チャット**（質問→回答、設計相談、説明、テスト案）💬🧠
3. **エージェント**（複数ステップで編集・コマンド実行までやる）🤖🔧

エージェントは便利だけど、最初は暴走しやすいので「制限付き」で触るのが安心だよ〜🧯✨（VS Code側にもエージェント設定があるよ） ([Visual Studio Code][1])

---

## 12-3. GitHub Copilot を VS Code に入れる（いちばん王道）🐙✨

### 12-3-1. セットアップ手順（最短ルート）🚀

VS Code右下（ステータスバー）にいる **Copilotアイコン**にマウスを乗せて、**Use AI Features**（または Set up Copilot）を選ぶ → サインイン、が一番スムーズだよ😊 ([Visual Studio Code][2])

> ここで初回セットアップすると、必要な拡張が自動で入る流れになってるよ〜✨ ([GitHub Docs][3])

---

### 12-3-2. “安全設定”を先に押さえる（個人でも超大事）🔒🧷

CopilotはGitHub側の設定で、いくつか重要なポリシーを変えられるよ👇

* **Public codeに一致する提案を許可するか**（オン/オフ）
* **プロンプト収集**（改善用に収集するか）
* **Web検索**や **別モデル利用**が見える場合もある（プラン等で変動）

このへんはGitHubの「Copilot policy（個人設定）」画面で管理できるよ🧯 ([GitHub Docs][4])

---

## 12-4. 「AIに守らせるルール」をファイルで固定する 📌🗂️

ここが今日のメイン💖
ヘキサゴナルは“依存の向き”が命だから、AIにそこを崩されないように**ルールを文章化して渡す**のが超効くよ🛡️✨

### 12-4-1. Copilot Instructions（推奨）📝✨

最近のVS Codeでは、設定値で文章を直書きするより **instructionsファイル**が推奨だよ（`codeGeneration`/`testGeneration`の設定は非推奨になって、ファイル方式が推奨に寄ってる）📌 ([Visual Studio Code][5])

* 置き場所（定番）：`.github/copilot-instructions.md`
* これを自動で使う設定：`github.copilot.chat.codeGeneration.useInstructionFiles` がON（既定でONのことが多い） ([Visual Studio Code][1])

#### ✅ テンプレ：`.github/copilot-instructions.md`（ヘキサゴナル守る版）🛡️🔌🧩

（そのままコピペでOK！）

```md
# Copilot Instructions (Hexagonal / Ports & Adapters)

## Architecture rules (must)
- Keep the center clean:
  - domain/ and app/ must NOT import from adapters/ nor depend on frameworks (fs, http, express, prisma, etc).
- Ports live in the center:
  - Outbound ports are interfaces/types defined under app/ (or domain/ if truly domain-level).
  - Adapters implement ports under adapters/.
- Adapters are thin:
  - No business rules, invariants, or state transitions in adapters.
  - Adapters do mapping/validation/logging and call the use case.

## Folder conventions
- domain/: entities/value objects/invariants (pure TS)
- app/: use cases + ports + DTOs (pure TS)
- adapters/: inbound (HTTP/CLI) and outbound (DB/File/API) implementations

## Naming
- Ports: *Port, *Repository, *Gateway
- Adapters: *Adapter, *Controller, *Presenter

## Testing preference
- Prioritize unit tests for app/ (use cases) using in-memory adapters.
- Avoid testing adapters first.

## Style
- TypeScript strict-friendly code.
- Small functions, explicit types on public boundaries.
```

---

### 12-4-2. AGENTS.md（エージェント時代の“追加ルール”）🤖📘

VS Codeでは **`AGENTS.md` を読ませる**設定もあるよ（複数エージェント/作業指示に強い）🧠✨ ([Visual Studio Code][5])

* `chat.useAgentsMdFile` をONにすると `AGENTS.md` を使う構成になるよ ([Visual Studio Code][5])

---

## 12-5. VS Codeの「見える化」設定（初心者に超おすすめ）👀✨

AIが編集した結果を「ちゃんと目で追える」ようにしておくと安心感が段違いだよ〜😊

### ✅ おすすめ：Chatの“チェックポイント”で差分を見る 🧾

* `chat.checkpoints.enabled`（既定ON）
* **`chat.checkpoints.showFileChanges` を true** にすると、リクエスト後に「どのファイルが変わったか」見やすいよ✨ ([Visual Studio Code][1])

例（`settings.json`）：

```json
{
  "chat.checkpoints.showFileChanges": true
}
```

---

## 12-6. OpenAI Codex（VS Code拡張）も使う場合 🧠⚡

「Copilotだけ」でも全然OKだけど、Codex系の拡張を併用したい人向けに要点だけまとめるね😊

### 12-6-1. まず大事：Windowsは“実験的サポート”寄り 🪟🧪

Codex IDE拡張は、Windowsだと **サポートが実験的**と明記されていて、安定重視なら **WSL上で動かすのが推奨**になってるよ💡 ([OpenAI Developers][6])

---

### 12-6-2. “勝手に進む度合い”を選べる（Approval Modes）🧯

Codex拡張では、作業の自動化度が選べるよ👇

* **Chat**：相談だけ（いちばん安全）
* **Agent**：複数ファイル編集など（途中で承認が必要）
* **Agent (Full Access)**：より強い（最初はおすすめしない）

まずは **Chat or Agent** くらいが安心だよ😊 ([OpenAI Developers][6])

---

### 12-6-3. “考える強さ”も調整できる（Reasoning effort）🧠🔧

Codex側には「速さ ↔ 深さ」のつまみがあるよ✨
IDE上では low/medium/high みたいに選べる説明があるし ([OpenAI Developers][6])、
設定ファイルだと **minimal / low / medium / high / xhigh** まであるよ（※xhighはモデル次第で非対応のこともある）⚠️ ([OpenAI Developers][7])

---

### 12-6-4. Codexの設定ファイル（知ってると強い）🧾

Codexは `~/.codex/config.toml` で設定できるよ（`model` や `model_reasoning_effort` など）🛠️ ([OpenAI Developers][8])

---

### 12-6-5. Codex用の AGENTS.md も書ける 📘🤖

Codexも `AGENTS.md` で“作業ルール”を渡せるよ。どの指示が優先されるか（グローバル/プロジェクトなど）も整理されてる🧠✨ ([OpenAI Developers][9])

---

## 12-7. AIの「使いどころ」「使っちゃダメ」🥰⚠️

### ✅ 使いどころ（めっちゃ相性いい）💖

* Adapterの雛形（入出力の変換、例外ラップ）🧩
* 命名案（Port名、UseCase名、DTO名）🏷️
* テストの観点出し（正常/異常/境界）🧪
* “レビュー役”としての指摘（依存の向き・肥大化チェック）🔍

### ❌ 使っちゃダメ（事故りやすい）😵‍💫

* Portの粒度・責務をAIに丸投げ（すぐ巨大Port化しがち）🐘
* ドメインの不変条件をAIに勝手に増やさせる（仕様が変わる）🧨
* 依存方向（中心→外）を破る提案を無批判に採用する🙅‍♀️

---

## 12-8. “AIレビュー質問テンプレ”配布 🎁🤖✅

このままコピペでOKだよ〜💖（チャットに貼るだけ！）

### テンプレ1：Adapter薄い？🥗

「この変更で、adapters/ に業務ルールや状態遷移が入ってないかチェックして。入ってたら app/ or domain/ に移す提案をして。」

### テンプレ2：依存の向き守れてる？🧭

「domain/ と app/ が adapters/ や fs/http 等の外部依存を import してないか確認して。違反があれば修正案を。」

### テンプレ3：Portが巨大化してない？🔌🐘

「Outbound Port（Repository等）が“何でもできる”形になってない？最小化の分割案を出して。」

### テンプレ4：DTOの漏れチェック📮

「外部I/Oの型（Request/ResponseやDBモデル）が中心に漏れてない？漏れてたらDTOと変換位置を提案して。」

### テンプレ5：UseCaseの単体テスト優先🧪

「このUseCaseに対して“文章みたいに読める”単体テストを先に作りたい。観点とテストケース案を列挙して。」

### テンプレ6：例外の扱い分離🧯

「I/O失敗（ファイル読めない等）と仕様エラー（バリデーション等）を分けて整理できてる？分離案を提案して。」

---

## 12-9. ミニ課題（5分）⌛🎀

**目的：AIを“安全に”1回使ってみる**😊

1. `.github/copilot-instructions.md` を作る（上のテンプレをコピペ）📝
2. AIにこう頼む💬

   * 「Todoの InMemoryRepository の雛形だけ作って。業務ルールは絶対に入れないで。Portは実装し、DTO変換は不要。」
3. 出てきたコードをテンプレ1（Adapter薄い？）でレビューさせる🔍✨

できたら勝ち〜〜🎉💖

---

## 12-10. よくあるトラブル 🧯😵‍💫（すぐ直るやつ）

* **Copilotアイコンが出ない** → 拡張が無効/未ログインのことが多いので、ステータスバーのCopilotからセットアップをやり直すのが早いよ ([Visual Studio Code][2])
* **instructionsが効いてない気がする** → `.github/copilot-instructions.md` の場所と、`github.copilot.chat.codeGeneration.useInstructionFiles` がONか確認してね ([Visual Studio Code][5])
* **CodexがWindowsで怪しい** → 公式に「Windowsは実験的」寄りなので、安定重視ならWSLに寄せるのが安全だよ ([OpenAI Developers][6])

---

## 12-11. 次章へのつなぎ 🌈✨

次は **TypeScriptのstrict最小セット**で「型のエラー＝味方🥹💖」の環境を作るよ！
今日作った instructions に「strict-friendly」って書いてあるから、次章からAIの出力も良い感じに締まってくるはず〜🎀✨

[1]: https://code.visualstudio.com/docs/copilot/reference/copilot-settings "GitHub Copilot in VS Code settings reference"
[2]: https://code.visualstudio.com/docs/copilot/setup?utm_source=chatgpt.com "Set up GitHub Copilot in VS Code"
[3]: https://docs.github.com/ja/copilot/how-tos/set-up/install-copilot-extension?utm_source=chatgpt.com "環境への GitHub Copilot 拡張機能のインストール"
[4]: https://docs.github.com/copilot/how-tos/manage-your-account/managing-copilot-policies-as-an-individual-subscriber "Managing GitHub Copilot policies as an individual subscriber - GitHub Docs"
[5]: https://code.visualstudio.com/docs/copilot/customization/custom-instructions?utm_source=chatgpt.com "Use custom instructions in VS Code"
[6]: https://developers.openai.com/codex/ide "Codex IDE extension"
[7]: https://developers.openai.com/codex/config-reference/ "Configuration Reference"
[8]: https://developers.openai.com/codex/config-basic/ "Basic Configuration"
[9]: https://developers.openai.com/codex/guides/agents-md "Custom instructions with AGENTS.md"
