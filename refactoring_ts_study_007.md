第7章（ブランチで安全に実験する）の教材ページとして、コマンド手順・VS Code操作・よくある事故回避・ミニ課題・AI活用プロンプトまで、実戦で迷わない形にまとめます。最新のGit/VS Code動向もWebで確認して反映します。


## 第7章 Gitの超基本②（ブランチで実験する）🌿🧪

### ねらい🎯

* 壊すのが怖い変更を、**安全に試せる場所（ブランチ）**でやれるようになる🙆‍♀️✨
* 「作業 → いつでも戻れる → 良かったら取り込む」を、手で回せるようになる🔁✅

---

### 今日できるようになること✅

* ブランチを作る🌱
* ブランチを切り替える🔀
* main（またはデフォルトブランチ）に戻って「何も起きてない」状態を確認する🔙
* 良かった変更だけを取り込む（merge）🧩
* いらないブランチを消す🧹

---

## 1) ブランチって何？🧠🌿

ブランチはざっくり言うと、**「コミットを指してるしおり📌」**みたいなもの。
main の“しおり”とは別の“しおり”を作れば、main を汚さずに実験できるよ😌🧪

---

## 2) まずは最短ルート（ターミナルでやる）⌨️✨

### 2-1. 今の状態チェック👀

変更が途中に残ってると、切り替えがややこしくなることがあるよ〜💦
まずは状況確認！

```sh
git status
```

---

### 2-2. ブランチを作って、そのまま移動する🌱➡️🚶‍♀️

いちばんよく使う形：**作る + 移動（checkout）を一発**✨
`git switch -c <branch名>` が便利！
（`switch` は「ブランチ切り替えの専用コマンド」だよ） ([Git][1])

```sh
git switch -c feature/try-refactor
```

💡豆知識：切り替え時に、未コミットの変更が消えちゃいそうな場合は **安全のために中断**してくれるよ🛟 ([Git][1])

---

### 2-3. ブランチ上で、遠慮なく変更する🧪🔥

ここは大胆にいってOK！
ファイルをいじったら、いつも通りコミットまで作るよ💾

```sh
git add .
git commit -m "refactor: rename variables in calc"
```

---

### 2-4. 「やっぱ戻る」も秒速🔙⚡

main に戻る：

```sh
git switch main
```

「直前のブランチに戻る」ショートカットもあるよ（行ったり来たりに超便利）：

```sh
git switch -
```

この `-` は「ひとつ前のブランチへ」って意味だよ🪄 ([Git][1])

---

### 2-5. うまくいったら取り込む（merge）🧩✨

main に戻ってから merge するのが基本！

```sh
git switch main
git merge feature/try-refactor
```

⚠️merge の前に、作業中の変更が残っているなら **コミットするか stash するのがおすすめ**（トラブル回避）🛟 ([Git][2])

---

### 2-6. 取り込み後、ブランチを掃除する🧹

取り込み終わったブランチは消してOK（片付け大事）🧼✨

```sh
git branch -d feature/try-refactor
```

`-d` は **「マージ済み（取り込み済み）」のときだけ消してくれる安全モード**。
未マージだと止めてくれるよ🛑 ([Git][3])

どうしても「この実験は全部いらない！」って時だけ（慎重に！）：

```sh
git branch -D feature/try-refactor
```

`-D` は強制削除だよ⚠️（未マージでも消える） ([Git][3])

---

### 2-7. 履歴がごちゃついたら“地図”を見る🗺️👀

ブランチの流れが一発で見えるコマンド👇

```sh
git log --oneline --graph --decorate --all
```

---

## 3) VS Codeでやる（クリック操作）🧑‍💻🖱️

### 3-1. ブランチの場所はここ！⬇️🌿

画面左下（ステータスバー）に **現在のブランチ名**が出るよ。
そこをクリックすると、ブランチの作成・切り替えができる🙌 ([Visual Studio Code][4])

### 3-2. コマンドパレット派ならこれ🪄

`Ctrl + Shift + P` → `Git: Create Branch...` で作れるよ✨
同じく `Git: Checkout to...` で切り替えもできる🙆‍♀️ ([Visual Studio Code][4])

### 3-3. Source Controlビューも便利📦

`Ctrl + Shift + G` で Source Control を開けるよ（差分確認がラク！）👀✨ ([Visual Studio Code][5])

---

## 4) ありがち事故と、回避ワザ集🛟💡

### 4-1. 「切り替えできない😭」→ 未コミット変更が原因かも

ブランチ切り替えで、変更が上書きされそうだと **Gitが止める**よ（安全装置）🛑 ([Git][1])
対処はこのどれか👇

* いったんコミットする💾
* 変更を捨てる🗑️（この教材ではまだ非推奨。焦ると事故る😵‍💫）
* **stashする**（一時的にしまう）📦

### 4-2. stash（いったんしまう）📦✨

`git stash` は「作業中の変更をいったん退避」できる機能だよ🧳 ([Visual Studio Code][4])

```sh
git stash push -m "wip"
git switch main
# 用事が終わったら戻す
git switch feature/try-refactor
git stash pop
```

---

### 4-3. mergeしたらコンフリクト（衝突）した😱💥

これは「同じ場所を別々に変更してて、どっち採用？」って状態。
merge の前に **コミット or stash 推奨**なのは、こういう混乱を減らすためだよ🛟 ([Git][2])

VS Codeは衝突解消UIが強いので、落ち着いて👇

1. どっちを採用するか選ぶ（または両方を手で統合）🧩
2. 保存する💾
3. もう一度コミットする✅

---

## 5) ミニ課題✍️🌸（20〜30分）

### お題：安全に“大胆リネーム”して戻れるようになろう🏷️🌿

#### 手順👣

1. ブランチ作成＆移動

```sh
git switch -c feature/rename-cleanup
```

2. どこでもいいので、変数名を3つリネームする（例：`tmp`→`totalPrice` みたいに）🏷️✨
3. コミットする💾

```sh
git add .
git commit -m "refactor: rename vars for readability"
```

4. main に戻って、「そのリネームが存在しない」ことを確認する🔙👀

```sh
git switch main
```

5. 差分の地図を見る🗺️

```sh
git log --oneline --graph --decorate --all
```

6. mergeして取り込む🧩

```sh
git merge feature/rename-cleanup
```

7. ブランチ削除🧹

```sh
git branch -d feature/rename-cleanup
```

#### 合格ライン✅

* main を汚さずに実験できた🌿
* 「戻れる」安心感を体で覚えた🛟
* 取り込んだ後に片付けまでできた🧹✨

---

## 6) AI活用ポイント🤖📝（ブランチ運用が一気にラクになる）

### 6-1. ブランチ名・コミット文を整える🏷️💬

AIにこう頼むと便利👇

* 「この変更内容を見て、ブランチ名を `feature/` で3案ください」
* 「コミットメッセージを、短く・意味が伝わる形で5案ください（英語でもOK）」

チェック観点✅

* 変更内容が想像できる？👀
* “何をしたか” が入ってる？🧩
* 長すぎない？✂️

---

### 6-2. PR説明文をAIに下書きさせる📝🤖

PRは「ブランチで作った変更を、デフォルトブランチに入れていいか相談する」仕組み。
PRは **トピックブランチとベースブランチの差分（diff）**を見せるよ👀 ([GitHub Docs][6])
PR作成時には **タイトルと説明**を書くよ📝 ([GitHub Docs][7])

AIへのお願いテンプレ👇（そのまま貼ってOK）

* タイトル案（1行）
* 変更の目的（なぜ）
* 変更内容（何を）
* 影響範囲（どこが変わる）
* 動作確認（どう確認した）
* スクショ/ログ（あれば）

さらに、GitHub上のPR説明欄では Copilot の提案（インライン補完）も使えるよ✍️✨ ([GitHub Docs][8])

---

## 7) 環境チェック（困ったらここ）🧰🪟

* VS CodeのGit機能は、PCに入ってるGitを使うよ（Git 2.0.0以上が必要）🧷 ([Visual Studio Code][4])
* Git for Windows の最新版として、Git公式の配布ページでは **2.52.0（2025-11-17）**が案内されているよ🆕 ([Git][9])

バージョン確認はこちら👇

```sh
git --version
```

[1]: https://git-scm.com/docs/git-switch "Git - git-switch Documentation"
[2]: https://git-scm.com/docs/git-merge "Git - git-merge Documentation"
[3]: https://git-scm.com/docs/git-branch "Git - git-branch Documentation"
[4]: https://code.visualstudio.com/docs/sourcecontrol/overview "Source Control in VS Code"
[5]: https://code.visualstudio.com/docs/sourcecontrol/intro-to-git "Quickstart: use source control in VS Code"
[6]: https://docs.github.com/articles/about-comparing-branches-in-pull-requests "About comparing branches in pull requests - GitHub Docs"
[7]: https://docs.github.com/articles/creating-a-pull-request "Creating a pull request - GitHub Docs"
[8]: https://docs.github.com/en/copilot/how-tos/get-code-suggestions/write-pr-descriptions "Writing pull request descriptions with GitHub Copilot text completion - GitHub Docs"
[9]: https://git-scm.com/install/windows "Git - Install for Windows"
