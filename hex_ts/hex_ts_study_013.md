# 第13章：TypeScript設定①：strict最小セット 🛡️✨

この章は「**strict を“怖い先生”から“頼れる相棒”にする**」回だよ〜😊💖
ヘキサゴナル的にも、**Port（interface）で“約束”を守る**のが大事だから、ここで型の守りを作っておくと後がめちゃ楽になるよ🔌✨

---

## 1) まず strict って何？🧠💡

`"strict": true` を入れると、TypeScript が **いろんな“厳しめチェック”をまとめて ON** にしてくれるよ✅
つまり、**バグになりやすい所を、実行前にツッコんでくれる**感じ🫶

しかもポイントはこれ👇

* strict は「厳しめチェックのセット」🎁
* **必要なら、個別に OFF にできる**（つらい所だけ緩められる）😊
* 将来の TS では strict の中身が増えることもある（＝アップデートで新しいエラーが出ることがある）🔁⚠️ ([typescriptlang.org][1])

---

## 2) 2026の “今どき tsconfig” 事情（超重要）📌✨

最近の TypeScript は、`tsc --init` がけっこう“最初から強い”設定を作るよ💪
TypeScript 5.9 の release notes では、`tsc --init` が **より“推奨寄り”の設定**（例：`noUncheckedIndexedAccess` や `exactOptionalPropertyTypes` まで）を出すようになったって明言されてるよ🧾 ([typescriptlang.org][2])

そして公式 Download ページでも「最新は（当時点で）5.9」って案内されてるよ📦 ([typescriptlang.org][3])

---

## 3) 今日作るのは「strict最小セット」✂️🛡️

`tsc --init` の“強め全部入り”は後で育てればOK！🌱
この章では、初心者が詰まりやすい設定（`noUncheckedIndexedAccess` とか）をいったん後回しにして、**“まず気持ちよく回る strict”**にするよ😊

* **絶対入れる（最小）**：`strict`
* **チーム開発・Windowsで効く**：`forceConsistentCasingInFileNames`
* **依存パッケージで詰まりにくくする**：`skipLibCheck`

`forceConsistentCasingInFileNames` は、OSの大文字小文字の扱い差で事故るのを防ぐためのやつだよ🪟🧯 ([typescriptlang.org][4])
`skipLibCheck` は、依存ライブラリ側の `.d.ts` チェックでハマりにくくする定番だよ🧹✨ ([typescriptlang.org][5])

---

## 4) 実際の tsconfig.json（この章の完成形）✅🎉

### ✅ 推奨：学習しやすい “strict最小セット” tsconfig

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "CommonJS",
    "moduleResolution": "Node",

    "rootDir": "src",
    "outDir": "dist",

    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,

    "esModuleInterop": true,
    "sourceMap": true
  },
  "include": ["src/**/*.ts", "test/**/*.ts"]
}
```

> ここでの狙いは「**strict は ON**、でも余計な難所は増やさない」だよ😊🛡️

---

## 5) “最小セット”各項目の意味をふわっと理解しよう ☁️💕

### ✅ strict 🛡️

**型チェックを強化して、バグを未然に止める**。
strict は“まとめON”で、必要なら個別OFFもできるよ🔧 ([typescriptlang.org][1])

### ✅ forceConsistentCasingInFileNames 🔤

`./FileManager` と `./fileManager` みたいな **大文字小文字ブレ**をエラーにしてくれる。
人によって環境が違うと起こる事故を防ぐよ🧯 ([typescriptlang.org][4])

### ✅ skipLibCheck 🧹

外部ライブラリの型定義（`.d.ts`）まで細かく検査すると、学習段階では詰まりがち。
そこをスキップして、**自分のコードに集中**できるよ🎯 ([typescriptlang.org][5])

---

## 6) strict で最初に出がちなエラー3兄弟 👀💥（怖くない！）

### ① `Object is possibly 'undefined'.` 😵

「それ、`undefined` かもだよ？」って警告。
**入口（Adapter）でチェック**してから中心に渡す、が相性いいよ🧩🔌
（`strictNullChecks` 系のノリ） ([typescriptlang.org][6])

よく使う形👇

* `if (!x) return;`
* `x?.foo`
* `x ?? "default"`

---

### ② `Parameter 'x' implicitly has an 'any' type.` 🫠

引数に型がなくて、TypeScript が困ってるやつ。
**Port（interface）**から型が流れてくる設計にすると、この系の事故が激減するよ🔌✨ ([typescriptlang.org][7])

---

### ③ `Type 'A | B' is not assignable to type 'A'.` 😭

Union 型（`string | undefined` とか）を、そのまま `string` に入れようとして怒られるやつ。
**“境界で整える”**（validate/変換）をやると一気に減るよ🚪🔁

---

## 7) 動作確認（この章のゴールチェック）✅🎯

### package.json に typecheck を追加しよ 🧪

```json
{
  "scripts": {
    "typecheck": "tsc -p tsconfig.json --noEmit"
  }
}
```

実行👇

```bash
npm run typecheck
```

* エラーゼロなら 🎉
* エラーが出たら「入口で整える」「型を足す」で直せばOK😊

---

## 8) “あとで強くする”候補（今日は入れない）🧊➡️🔥

TypeScript 5.9 の `tsc --init` は最初からこれ系を入れてくるよ👇

* `noUncheckedIndexedAccess`
* `exactOptionalPropertyTypes`
* `isolatedModules`
* `verbatimModuleSyntax`
  …などなど 📚 ([typescriptlang.org][2])

でもこれ、学習初期は「え、なんで？😳」が増えやすいのも事実。
だから次章以降で、**目的を持って**少しずつ入れるのが気持ちいいよ🌱✨

（例えば `noUncheckedIndexedAccess` は「配列/辞書アクセスが常に安全とは限らない」を厳密にする設定だよ📦） ([typescriptlang.org][8])
（`exactOptionalPropertyTypes` は「optional の意味」をより正確にするやつだよ🎯） ([typescriptlang.org][9])

---

## 9) AIに投げると捗る“質問テンプレ”🤖📝

そのまま貼れるやつ置いとくね🎁✨（短くて強い！）

* 「この TypeScript のエラーを、初心者向けに1〜2行で説明して。直し方を3つ出して」
* 「ヘキサゴナル前提で、**中心に if/例外処理を持ち込まない**修正案にして」
* 「Port（interface）側に型を寄せる直し方を優先して提案して」

---

## まとめ 🎁💖

今日の合言葉はこれ！🗣️✨

* strict は **まとめて守ってくれる盾** 🛡️ ([typescriptlang.org][1])
* でも最初は **最小セット**で気持ちよく回す😊
* エラーは敵じゃなくて「境界をきれいにするヒント」🚪🧩

次章では、ここに **Lint / Format / Test** を乗せて、「機械に任せる量」を増やしていくよ🤖✨

[1]: https://www.typescriptlang.org/tsconfig/strict.html "TypeScript: TSConfig Option: strict"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html "TypeScript: Documentation - TypeScript 5.9"
[3]: https://www.typescriptlang.org/download "TypeScript: How to set up TypeScript"
[4]: https://www.typescriptlang.org/tsconfig/forceConsistentCasingInFileNames.html "TypeScript: TSConfig Option: forceConsistentCasingInFileNames"
[5]: https://www.typescriptlang.org/tsconfig/skipLibCheck.html "TypeScript: TSConfig Option: skipLibCheck"
[6]: https://www.typescriptlang.org/tsconfig/strictNullChecks.html "TypeScript: TSConfig Option: strictNullChecks"
[7]: https://www.typescriptlang.org/tsconfig/noImplicitAny.html "TypeScript: TSConfig Option: noImplicitAny"
[8]: https://www.typescriptlang.org/tsconfig/noUncheckedIndexedAccess.html "TypeScript: TSConfig Option: noUncheckedIndexedAccess"
[9]: https://www.typescriptlang.org/tsconfig/exactOptionalPropertyTypes.html "TypeScript: TSConfig Option: exactOptionalPropertyTypes"
