# クリーンアーキテクチャ（C#）45章：中核に寄せた詳細アウトライン 🏗️💖

前提：Windows + Visual Studio（最新）＋ ASP.NET Core（最新）でOK。AIは「各章の補助」として使う🤖✨（※AI自体を“章テーマ”にはしない）

---

## Part 0：クリーンアーキの芯（1〜7）⭕🧠

### 1章：クリーンアーキで何が解決できるの？😌

* ねらい：変更が怖い原因を「依存」と「境界」で説明できる
* 中身：UI/DB/外部サービスに振り回される理由
* ミニ課題：過去のつらい修正を「どこ依存が原因か」分類
* AI：原因分類のたたき台を出させる🤖

### 2章：同心円の4層を覚える（Entities / Use Cases / Adapters / Frameworks）⭕

* ねらい：図を見て説明できるようにする
* 中身：各層の責務（Uncle Bobの定義）([blog.cleancoder.com][1])
* ミニ課題：題材（例：メモ管理）を4層に配置
* AI：配置がズレてたらツッコミ役にする😆

### 3章：Dependency Rule（依存は内側へ）を体に入れる➡️

* ねらい：設計判断の“憲法”を持つ
* 中身：内側は外側を知らない（名前すら出さない）([blog.cleancoder.com][1])
* ミニ課題：禁止参照リストを作る（例：DomainはEFを参照しない）
* AI：違反例をわざと作らせてクイズ化🎮

### 4章：境界（Boundary）とは何か？🚪

* ねらい：「どこで切るか」を言語化できる
* 中身：入力境界・出力境界・変換（adapter）の意味
* ミニ課題：境界候補を3つ宣言（API境界/DB境界/外部API境界）
* AI：境界が崩れやすいポイントを列挙させる

### 5章：Ports & Adapters を“処理の流れ”で理解する🔌

* ねらい：Controller→InputPort→Interactor→OutputPort→Presenter の流れを掴む
* 中身：Input/Output Port の役割、Controller/PresenterはAdapter側([Qiita][3])
* ミニ課題：1ユースケースの処理フロー図を描く
* AI：フロー図のレビュー係にする

### 6章：C#で層をどう置く？（プロジェクト/参照方向）🏠

* ねらい：構造で迷子にならない
* 中身：Core（Entities+UseCases）を中心に置く思想([Microsoft Learn][2])
* ミニ課題：Solutionに「Core」「Adapters」「Frameworks」的な配置を決める
* AI：参照方向チェック（逆参照を疑う）

### 7章：題材を決めて“クリーンに作る宣言”📣

* ねらい：学習スコープを固定して完走する
* 中身：機能を8〜10個に絞る（例：メモ作成/取得/更新/削除/検索）
* ミニ課題：ユースケース一覧＋優先順位
* AI：やり過ぎ機能を削る提案をさせる✂️

---

## Part 1：Entities（Enterprise Business Rules）を厚く（8〜16）👑💎

### 8章：Entityとは？（同一性＋振る舞い）🪪

* ねらい：Entityを“データ箱”にしない
* 中身：ID・状態・ルール・メソッド
* ミニ課題：Memo Entityに「Rename」「Archive」みたいな振る舞いを付ける
* AI：setter地獄を避ける設計案を出させる

### 9章：Value Objectとは？（不変＋等価）💎

* ねらい：string地獄から脱出する
* 中身：Title/TagName/DateRange など
* ミニ課題：VOを2つ作って比較（等価性）
* AI：VO候補の洗い出しをさせる

### 10章：不変条件（Invariants）を入口で守る🚧

* ねらい：壊れた状態を“作れない”設計
* 中身：生成時/更新時のチェック
* ミニ課題：タイトル空禁止・長さ制限・タグ重複禁止など
* AI：境界値と抜けを列挙させる

### 11章：EntityとVOの切り分け練習⚖️

* ねらい：判断基準を言える
* 中身：同一性が必要？値そのもの？
* ミニ課題：題材の項目を分類表にする
* AI：理由の弱い分類を指摘させる

### 12章：「貧血ドメイン」にならないコツ🩸

* ねらい：ルールがUseCaseやControllerに散るのを防ぐ
* 中身：Entityに置くべきルールの見極め
* ミニ課題：散ってるルールをEntityに戻すリファクタ
* AI：どのルールがEntity向きか提案させる

### 13章：Domain Serviceは“最後の手段”🧩

* ねらい：Serviceに逃げすぎない
* 中身：複数Entityに跨るときだけ
* ミニ課題：Serviceで1つ作り、Entityに戻せるか検討
* AI：Service/Entityどっちに置くべきか議論させる

### 14章：エラーもドメインの一部（失敗＝仕様）⚠️

* ねらい：例外が暴れない土台
* 中身：ドメインエラーの種類と表現
* ミニ課題：失敗ケースを10個→ドメイン起因だけ抽出
* AI：文言をユーザー目線に整形

### 15章：Entitiesは“フレームワーク非依存”🧼

* ねらい：中心にEF属性やHTTP型を入れない
* 中身：中心は純粋なC#で保つ（外の都合を持ち込まない）([blog.cleancoder.com][1])
* ミニ課題：Entitiesに外部参照がないか確認
* AI：参照一覧から“外側っぽい依存”を検出させる

### 16章：Entities層の完成チェック✅

* ねらい：中心が“方針”になっているか確認
* 中身：用語・不変条件・振る舞い・依存ゼロ
* ミニ課題：Entitiesだけで動く簡易テスト（後の章で本格化）
* AI：レビュー観点チェックリストを生成

---

## Part 2：Use Cases（Application Business Rules）を厚く（17〜28）🎮📦

### 17章：Use Caseとは？（アプリの手順書）🧾

* ねらい：Entitiesの“使い方”を分離する
* 中身：入力→処理→出力（副作用の扱い）
* ミニ課題：「メモ作成」手順を文章で書く
* AI：手順の抜け漏れを指摘させる

### 18章：Input Port（入力境界）を設計する🔌⬅️

* ねらい：外側が呼ぶ窓口を固定する
* 中身：InputPort（interface）＋RequestModel
* ミニ課題：CreateMemoInputPort を定義
* AI：メソッド名・入出力の粒度を提案させる

### 19章：Request Model（入力データ）を整える📨

* ねらい：外の形を中に持ち込まない
* 中身：API DTOとは分ける（UseCase用の入力）
* ミニ課題：RequestModelを“必要最小限”にする
* AI：不要フィールドを削る提案

### 20章：Interactor（UseCase実装）の骨格🧱

* ねらい：UseCaseが何をするか明確に
* 中身：Entities呼び出し／出力境界へ渡す
* ミニ課題：CreateMemoInteractor を実装（まずはインメモリでOK）
* AI：Interactorの責務が膨らんでないか指摘させる

### 21章：Output Port（出力境界）を設計する🔌➡️

* ねらい：UseCaseが“表示やHTTP”を知らない状態にする
* 中身：OutputPort（interface）＋ResponseModel([m3tech.blog][4])
* ミニ課題：CreateMemoOutputPort を定義
* AI：ResponseModelの設計レビュー

### 22章：Presenter（出力のAdapter）を理解する🎤

* ねらい：出力整形は外側でやる
* 中身：PresenterがOutputPortを実装し、ViewModel/DTOへ変換([blog.cleancoder.com][1])
* ミニ課題：Presenterが作る“表示用モデル”を定義
* AI：表示モデルの命名案を出させる

### 23章：Gateway/Repository（外部依存の出口）🚪

* ねらい：DBや外部サービスをUseCaseから切る
* 中身：UseCase内にinterface、外側が実装([Microsoft Learn][2])
* ミニ課題：MemoRepository interface をCore側に定義
* AI：過剰に汎用化してないか監査

### 24章：UseCase内の“読み書き”の考え方📚✍️

* ねらい：UseCaseが「手順」に集中できる
* 中身：保存/取得の責務分離、必要最小のI/O
* ミニ課題：GetMemo/UpdateMemo のUseCaseを追加
* AI：I/Oが増えすぎてないか指摘

### 25章：トランザクション境界はUseCaseに置く💳

* ねらい：整合性の単位をUseCaseで語れる
* 中身：1ユースケース＝1トランザクションの感覚
* ミニ課題：保存＋イベント（後で）などの順序を決める
* AI：失敗時の分岐（どこまで戻す？）を列挙

### 26章：例外/エラーの流し方（Core→外）🌊

* ねらい：エラーが層を汚さない
* 中身：Domainエラー→UseCase結果→Presenterで表現
* ミニ課題：主要エラー3種の流れを決める
* AI：HTTPに落とす案は“外側担当”として提案させる

### 27章：UseCaseを増やしても崩れない“型”を作る📐

* ねらい：毎回同じ迷いを減らす
* 中身：InputPort/Request/Interactor/OutputPort/Presenter/Repository のテンプレ
* ミニ課題：テンプレで2ユースケース追加
* AI：テンプレ雛形を生成→人がレビューして確定

### 28章：UseCases層の完成チェック✅

* ねらい：UseCaseが“UI/DB/Framework”を知らない状態を確認
* 中身：参照禁止の再点検（依存が内側へ）([blog.cleancoder.com][1])
* ミニ課題：UseCasesプロジェクトの参照一覧を確認
* AI：依存チェックの自動化案を出させる

---

## Part 3：Interface Adapters（変換層）を厚く（29〜38）🔄🧩

### 29章：Controllerの責務（“受け取って呼ぶだけ”）🚪

* ねらい：Controller肥大化を防ぐ
* 中身：HTTP→InputPort への変換だけ
* ミニ課題：CreateMemoController（またはMinimal API）を薄く実装
* AI：Controllerが判断してないかレビュー

### 30章：API DTO と UseCase Request を分ける🍱

* ねらい：“外の形”で中を汚さない
* 中身：API DTO → RequestModel 変換の置き方
* ミニ課題：DTO↔Request の変換関数を作る
* AI：変換漏れをテスト観点で指摘

### 31章：Presenterが作る“出力モデル”の設計📦

* ねらい：UseCase結果を外の都合へ変換
* 中身：ResponseModel→ViewModel→API Response DTO
* ミニ課題：成功/失敗のレスポンス形をPresenter側で統一
* AI：返し方の一貫性チェック

### 32章：Validationの責務（Adapterで止める/Domainで守る）🛑

* ねらい：検証を散らさない
* 中身：形式はAdapter、ルールはDomain（不変条件）
* ミニ課題：どこで止めるかルール表を作る
* AI：置き場所ミスを指摘させる

### 33章：Persistence Adapterの考え方（DBは“詳細”）🗄️

* ねらい：DB都合がCoreに入らない
* 中身：Repository実装はAdapter側（外側）([Microsoft Learn][2])
* ミニ課題：InMemory実装→DB実装へ差し替え計画を書く
* AI：差し替えポイントの漏れチェック

### 34章：DBモデルとDomainモデルは分けてOK（変換で吸収）🔁

* ねらい：DomainをDB形状に合わせない
* 中身：DB Entity（永続化用）↔ Domain Entity のマッピング
* ミニ課題：永続化用モデルを別に用意してマップする
* AI：マッピングの地雷（null/既定値/ID）を列挙

### 35章：Queryの置き場所（検索/一覧の扱い）🔎

* ねらい：読み取りが肥大化しても境界を守る
* 中身：読み取り用のアダプタ（最適化は外側でOK）
* ミニ課題：検索UseCaseを作り、Repositoryの責務を最小化
* AI：Repositoryが巨大化してないか指摘

### 36章：外部サービスAdapter（HTTP等）🌍

* ねらい：外部API変更をCoreに波及させない
* 中身：Client interface（Core）＋実装（Adapter）([blog.cleancoder.com][1])
* ミニ課題：外部呼び出しを差し替え可能にする
* AI：タイムアウト/失敗時の分岐を列挙

### 37章：Adapter層の完成チェック（変換が一箇所に集約されてる？）✅

* ねらい：変換の散乱を防ぐ
* 中身：Controller/Presenter/Repository実装の責務確認
* ミニ課題：変換処理の所在を一覧化
* AI：散らばりポイントを指摘させる

### 38章：違反パターン診断（よくある崩れ方）🩺

* ねらい：事故を早期に見抜く
* 中身：ControllerがDbContext直叩き、DomainがEF参照、UseCaseがHTTP型を持つ等
* ミニ課題：わざと1つ違反を作り、直す
* AI：違反の自動検出アイデアを出させる

---

## Part 4：Frameworks & Drivers（外側）を“外に閉じる”（39〜42）🧷🧱

### 39章：Webフレームワークは最外周（Coreは知らない）🌐

* ねらい：フレームワーク交換に耐える発想
* 中身：ASP.NET Coreは外側、入口はAdapterで吸収([blog.cleancoder.com][1])
* ミニ課題：Core参照が最小になっているか確認
* AI：参照グラフの点検案を出させる

### 40章：DI（依存の差し込み）で依存向きを守る🪄

* ねらい：実行時に外側実装を内側へ注入する
* 中身：Coreがinterface定義、外側が実装、DIで合体([Microsoft Learn][2])
* ミニ課題：Repository実装をDI登録して差し替え
* AI：DIの配線ミス（循環/ライフタイム）を疑わせる

### 41章：Composition Root（組み立て場所は1箇所）🧵

* ねらい：配線が散らばって崩れるのを防ぐ
* 中身：起動時に全部組み立てる（Coreはnewしない）
* ミニ課題：DI登録を1ファイルに集約
* AI：登録漏れを洗い出させる

### 42章：DB/ライブラリの“詳細”は外側で完結させる🧰

* ねらい：EF Coreや設定はCoreに入れない
* 中身：マイグレーション・接続・設定はFramework側へ
* ミニ課題：CoreがDB接続情報を知らない状態を確認
* AI：設定値の漏れや直書きを検出させる

---

## Part 5：テストと“依存ルール強制”は中核の一部（43〜45）🧪🛡️

### 43章：Entitiesのテスト（速い・堅い・気持ちいい）🍰

* ねらい：中心ルールを最速で守る
* 中身：VO不変条件、Entity振る舞い
* ミニ課題：重要ルールを3つテスト化
* AI：境界値テスト案を出させる

### 44章：UseCaseのテスト（Port差し替えで外部なし）🎭

* ねらい：DBなし・HTTPなしでUseCaseを検証できる
* 中身：Fake Repository / Fake Presenter でInteractorを叩く([m3tech.blog][4])
* ミニ課題：Create/UpdateのUseCaseをテスト
* AI：Given-When-Then形式のテスト案を生成

### 45章：Dependency Ruleを“自動で守る”（アーキテクチャテスト）🔒✅

* ねらい：人の注意力に頼らず崩れない
* 中身：Coreが外側参照してないかをCIで落とす（依存は内側へ）([blog.cleancoder.com][1])
* ミニ課題：禁止参照チェックをプロジェクトに組み込む
* AI：違反しがちなパターンを列挙→チェック項目化

---

## 変更点（あなたの要望どおり）😊✨

* **外した（関係が薄い）**：Swagger/OpenAPI、契約設計、観測性、状態機械、AI運用ルール“それ自体”
* **厚くした（中核）**：Dependency Rule、4層、Boundary、Input/Output Port、Interactor、Presenter/Controller、Gateway/Repository、DI/Composition Root、Port差し替えテスト、依存ルールの自動強制

---

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
[2]: https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures?utm_source=chatgpt.com "Common web application architectures - .NET"
[3]: https://qiita.com/arkuchy/items/874656b33d2e5acdf281?utm_source=chatgpt.com "Go言語とClean ArchitectureでAPIサーバを構築する"
[4]: https://www.m3tech.blog/entry/2020/02/07/110000?utm_source=chatgpt.com "Clean Architectureなにもわからないけど実例を晒して人類に ..."
