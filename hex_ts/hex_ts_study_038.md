# 38. AI活用②：レビュー用プロンプト集（そのまま使える）📝🤖
（まず最新情報をWebで確認してから、教材本文＋コピペ用プロンプト集＋運用手順を作ります）


以下では「第38章：AI活用②：レビュー用プロンプト集（そのまま使える）」を、**いま使われているCopilotのコードレビュー機能や、VS CodeのCopilot/Agent機能、CodexのVS Code拡張**などの最新状況も踏まえてまとめるね😊📝🤖
（※GitHub上のPRに“Copilotをレビュアーとして付ける”公式導線や、月間クォータ（premium request）消費の話も含めて反映してるよ） ([GitHub Docs][1])

---

# 第38章：AI活用②：レビュー用プロンプト集（そのまま使える）📝🤖✅

## 1) まず結論：AIレビューは「質問の型」で9割決まる😆✨

AIにレビューを頼むとき、ふわっと「見て！」だと、返事もふわっとなりがち…🥺
だからこの章は **“チェック観点が漏れない質問テンプレ”** を用意して、**毎回コピペで安定したレビュー**が取れるようにするよ💪💕

---

## 2) 2026っぽいAIレビューのやり方（使い分け）🧭✨

### A. IDEのチャットで“手元レビュー”🧰💬

* 変更したファイルを開いて、**選択範囲 or 差分**を見せながらレビューさせる
* 小刻みに直して、すぐ再レビューできるのが強い💖

（VS CodeのCopilot Chatは公式ドキュメントとしてまとまってるよ） ([Visual Studio Code][2])

### B. GitHubのPRで“Copilotにレビュー依頼”👀✅

* PRのReviewersから **Copilotを選ぶ**とレビューしてくれる導線が公式にあるよ ([GitHub Docs][1])
* しかもこれ、**プレミアムリクエスト（月間クォータ）を消費**するタイプの機能なので、使いどころは大事🥺💸 ([GitHub Docs][3])

### C. Codex（VS Code拡張）で“エージェント的にレビュー/修正案”🛠️🤖

* Codexは「IDEで並走」も「タスクを任せる」もできる設計（VS Code拡張が公式にある） ([OpenAI Developers][4])

### D. Agent mode（やや自動化寄り）🚗💨

* VS Code側にも **Copilot agent mode** の流れがあって、タスクを“計画→実行”っぽく進められる（プレビューから安定版へも進んでる） ([Visual Studio Code][5])

---

## 3) クォータ節約のコツ（超だいじ）💰🥺

Copilotのコードレビューは **月間クォータ（premium requests）** が絡むので、順番はこれがオススメ👇 ([GitHub Docs][3])

1. **IDE内（チャット）で軽くレビュー**（構造・依存・命名）
2. 直してテスト
3. 最後に **PRでCopilotレビュー**（本番の最終チェック）

こうすると「PRレビュー1回」で済みやすいよ😊✨

---

## 4) AIレビューの“勝ちテンプレ”基本形（まずこれだけ覚える）🏆✨

レビュー依頼は、毎回この形に寄せると安定するよ👇

* **目的**：何を守りたいレビュー？（例：中心が外側を知らないか）
* **対象**：ファイル/差分/範囲
* **制約**：出力形式（箇条書き、重要度、修正案は最小差分など）
* **観点**：チェックしてほしい項目（Port/Adapter/依存/DTO/例外など）
* **期待**：最終的にどうしてほしい？（指摘 + 直し方 + テスト案）

---

# 5) コピペで使える：レビュー用プロンプト集 📝🤖✅

ここから全部、そのまま貼ってOKだよ😊
（※コードブロックは “プロンプトそのもの” だから、必要に応じて【差分】や【対象ファイル】を埋めてね）

---

## 5-1) まずは全体レビュー（万能）🌍✨

```text
あなたはシニアエンジニアです。次の差分（または選択範囲）をレビューしてください。

【目的】
ヘキサゴナル（Ports & Adapters）観点で、中心（domain/app）が外側（adapters/infra/HTTP/DB）に汚染されていないか確認したい。

【出力形式】
1) 重大度: High / Mid / Low
2) 指摘（なぜダメかを1〜2行）
3) 直し方（最小差分の方針）
4) 追加すると良いテスト（あれば）

【差分】
（ここにdiff or 選択範囲）
```

---

## 5-2) 「Adapter薄い？」チェック 🥗⚠️

```text
次のAdapterコードは「薄いAdapter」の原則を守れていますか？

【チェック観点】
- 変換（DTO/外部型→内部型）と呼び出しだけになっている？
- 業務ルール（判断/状態遷移/巨大if）を持っていない？
- エラーハンドリングが「外側の責務」に留まっている？

【出力】
- 太っている箇所（具体的に行/関数名）
- どこへ追い出すべきか（domain/app/別サービスなど）
- 最小のリファクタ手順（ステップで）

【コード】
（ここに貼る）
```

---

## 5-3) 「中心が外部型を参照してない？」チェック 🛡️😱

```text
次のコードで、中心（domain/app）が外側の型（HTTP Request/Response、DBモデル、ライブラリ型など）を参照していないか監査してください。

【出力】
- 参照している箇所の一覧（ファイル名・シンボル名）
- なぜ危険か（1行）
- 直し方：DTO/変換をどこに置くべきか
- 直した後に確認すべきテスト

【対象】
（ファイル or diff）
```

---

## 5-4) 「Port大きすぎない？」チェック 🔌🐘

```text
次のPort（interface）設計をレビューしてください。

【観点】
- UseCaseが本当に必要とする最小の約束になっている？
- 1つのPortが多用途になっていない？（何でも屋になってない？）
- メソッドが増えすぎる未来が見えない？

【出力】
- 問題点（あれば）
- 分割案（例：Read系/Write系、目的別など）
- 命名改善案
- テストが楽になる理由（1〜2行で）

【Portコード】
（ここに貼る）
```

---

## 5-5) 「依存の向き」監査（importの方向）🧭🔥

```text
このプロジェクト構造で、依存の向きが正しいかレビューしてください。

【ルール】
- 中心（domain/app）は外側（adapters/infra）をimportしない
- 外側は中心をimportしてよい

【出力】
- ルール違反のimport一覧
- 直し方（どこにinterface/DTO/変換を移すか）
- 直した後に壊れやすい場所（注意点）

【対象】
（ツリー/主要ファイル/差分を貼る）
```

---

## 5-6) 「DTO漏れ」チェック（地味に効く）📮🛡️

```text
次のUseCase入出力が、domain型を漏らしていないか確認してください。

【観点】
- UseCaseの入力/出力が“外に見せる形（DTO）”として単純か
- domainの内部構造（Entity/ValueObject）が外に漏れてないか
- 将来API/永続化が変わっても耐えるか

【出力】
- 漏れている箇所
- DTO設計の提案（最小）
- 変換はどこに置くべきか（Inbound/Outbound Adapterなど）

【対象】
（UseCaseの型定義 + 呼び出し側）
```

---

## 5-7) 「エラー設計」チェック（中心と外側が混ざってない？）🧯😵‍💫

```text
次のエラー処理を、ヘキサゴナル観点でレビューしてください。

【観点】
- 中心のエラー（仕様）と外側のエラー（I/O失敗）が混ざってない？
- 例外の投げ方がバラバラになってない？
- 呼び出し側（Adapter）が適切に変換して返している？

【出力】
- 混ざっている箇所
- 分離方針（中心/外側でどう扱うか）
- 直す順番（安全な手順）
- 追加すべきテスト（エラー系）

【対象】
（コード or diff）
```

---

## 5-8) 「テスト追加」だけお願いするプロンプト 🧪💪

```text
次の差分に対して、ユースケース単体テストを追加したいです。

【要望】
- InMemory系を差し替えて高速テストにする前提で
- “仕様が文章みたいに読める”テスト名にして
- 失敗ケース（バリデーション/二重完了など）も必ず入れて

【出力】
- 追加すべきテストケース一覧
- そのうち重要Top3のテストコード例（TypeScript）

【差分 / 対象コード】
（ここに貼る）
```

---

## 5-9) “最小差分”で直してほしい（AI暴走防止）🧯🧩

```text
指摘ありがとう！ただし、修正は「最小差分」でお願い。

【条件】
- 公開APIやUseCaseのシグネチャは変えない（どうしても必要なら理由と代替案）
- フォルダ構成は変えない
- 既存テストが通る前提で、追加テストは歓迎

【出力】
- 変更点の要約
- パッチ案（変更箇所だけ）
- 追加テスト（必要なら）
```

---

# 6) “質問テンプレ”の小ワザ集（レビュー精度が上がる）🎯✨

* **範囲を絞る**：1ファイル/1責務ずつ頼むと当たりやすい😊
* **出力形式を固定**：High/Mid/Low + 直し方 + テスト案、が最強
* **「最小差分」縛り**：AIが大改造しがちなのを防げる🧯
* **差分→理由→直し方→確認テスト**：この順番を毎回要求する

---

# 7) 章のまとめ 🎁💖

* AIレビューは **“チェック観点つきテンプレ”** にすると安定する😊✅
* **IDEで軽く→PRで最終**にすると、クォータ節約にもなるよ💰✨ ([GitHub Docs][3])
* Copilot/Agent/Codexなど、2026は「レビューの入口」が増えてるので、うまく使い分けると強い🤖🛠️ ([Visual Studio Code][5])

---

* [theverge.com](https://www.theverge.com/news/808032/github-ai-agent-hq-coding-openai-anthropic?utm_source=chatgpt.com)
* [techradar.com](https://www.techradar.com/pro/openai-launches-gpt-5-codex-with-a-74-5-percent-success-rate-on-real-world-coding?utm_source=chatgpt.com)
* [theverge.com](https://www.theverge.com/command-line-newsletter/668251/chatgpt-is-getting-an-ai-coding-agent?utm_source=chatgpt.com)

[1]: https://docs.github.com/ja/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review?utm_source=chatgpt.com "GitHub Copilot コード レビューの使用"
[2]: https://code.visualstudio.com/docs/copilot/chat/copilot-chat?utm_source=chatgpt.com "Get started with chat in VS Code"
[3]: https://docs.github.com/en/copilot/concepts/agents/code-review?utm_source=chatgpt.com "About GitHub Copilot code review"
[4]: https://developers.openai.com/codex/ide/?utm_source=chatgpt.com "Codex IDE extension"
[5]: https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode?utm_source=chatgpt.com "Introducing GitHub Copilot agent mode (preview)"