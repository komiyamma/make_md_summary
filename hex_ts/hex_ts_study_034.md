# 34. エラー設計②：外側のエラー（I/O失敗）😵‍💫

> この章は「ファイル読めない」「ネット落ちた」みたいな **外側（I/O）の事故**を、ヘキサゴナル的に“きれいに”扱えるようになる回だよ〜🧸✨
> いきなり結論：**中心（ドメイン/ユースケース）は静かに🧠**、**外側（Adapter）で受け止めて、必要な形に翻訳する🧩**！

---

## 0. 2026-01-23時点の前提メモ（超ミニ）🗓️✨

* Node は **v24 が Active LTS**（安定して使うならここが軸）だよ〜 ([Node.js][1])
* TypeScript は **5.9.x 系が安定版ライン**（5.9 のアナウンスあり）で、**6/7 は進行中**って流れ ([Microsoft for Developers][2])
* Node の `fetch()` は **undici で動く内蔵 fetch**（Node 18〜） ([Node.js][3])
* 例外を包むなら `new Error(msg, { cause })` の **cause** が超便利 ([Node.js][4])

---

## 1. この章のゴール 🎯💖

この章が終わったら、こんなことができるようになるよ〜😊✨

* I/O失敗を **「中心の仕様エラー」と混ぜない**で整理できる🧠🧼
* Adapter で起きた例外を **アプリ用のエラー型に翻訳**できる🧩
* ログに **状況（コンテキスト）**を残して、デバッグしやすくできる🪪📌
* 「リトライしていい失敗/ダメな失敗」を分けられる🔁✅

---

## 2. I/O失敗ってどんなやつ？あるある😵‍💫💥

### ファイル系（FileRepository）📄💾

* ファイルが無い（初回起動とか）😳
* 権限がない（EACCES）🔒
* JSONが壊れてる（途中で手で編集しちゃった…）🫠
* 同時書き込みで壊れる（並列処理）💥

### ネット系（外部API）🌐⚡

* 回線が落ちる / DNSが死ぬ📡💀
* タイムアウトする⌛
* 503（相手が死んでる）🧯
* 401/403（認証エラー）🔑

---

## 3. 超重要：中心のエラーと、外側のエラーは“別もの”🧠🧩

### ✅ 中心（仕様）のエラー（第33章の範囲）

* 「タイトル空はダメ」
* 「完了の二重適用はダメ」
  → これは **仕様**だから、中心が判断してOK🙆‍♀️

### ✅ 外側（運用/I/O）のエラー（第34章）

* 「ファイル読めない」
* 「ネット落ちた」
  → これは **環境の事故**だから、中心が抱えると世界が汚れる😱

なので、ヘキサゴナルのノリでこうするよ👇

* **Adapterで受け止める**🧤
* **アプリが理解できる形に翻訳して返す**🧩
* **ログは外側で残す**📝
* **中心は外部例外の種類を知らない**🙅‍♀️

---

## 4. 外側エラー設計の型：おすすめの最小セット🧩✨

「アプリ的に意味がある」情報だけ持つのがコツだよ✂️💖

* 何が起きた？（kind）
* リトライしていい？（retryable）
* ユーザーに見せるメッセージ（publicMessage）
* デバッグ用の情報（cause / details）

### 例：InfraError（外側の翻訳結果）🧱

```ts
export type InfraErrorKind =
  | "STORAGE_NOT_FOUND"
  | "STORAGE_PERMISSION_DENIED"
  | "STORAGE_CORRUPTED"
  | "STORAGE_IO_FAILED"
  | "NETWORK_TIMEOUT"
  | "NETWORK_UNAVAILABLE"
  | "REMOTE_BAD_STATUS";

export class InfraError extends Error {
  constructor(
    public readonly kind: InfraErrorKind,
    message: string,
    public readonly options: {
      retryable: boolean;
      publicMessage: string;
      details?: Record<string, unknown>;
      cause?: unknown;
    }
  ) {
    super(message, { cause: options.cause }); // causeで「根っこ」を保持✨
    this.name = "InfraError";
  }

  get retryable() {
    return this.options.retryable;
  }

  get publicMessage() {
    return this.options.publicMessage;
  }

  get details() {
    return this.options.details;
  }
}
```

`cause` は **「翻訳前の元エラー」**を残すための公式ルートだよ🧠✨ ([Node.js][4])

---

## 5. FileRepositoryでやってみる：例外→InfraErrorに翻訳🧩📄

ここでは `fs/promises` を使うよ（Node公式） ([Node.js][5])

### 5.1 Nodeのエラーコードを安全に見る小ワザ🔍

```ts
type NodeErrnoException = Error & { code?: string };

function isNodeErrno(e: unknown): e is NodeErrnoException {
  return e instanceof Error;
}
```

### 5.2 JSONロード（壊れてた/無い/権限ない…を分岐）📥😵‍💫

```ts
import fs from "node:fs/promises";

export class FileTodoRepositoryAdapter {
  constructor(private readonly filePath: string) {}

  async loadAll(): Promise<unknown[]> {
    try {
      const text = await fs.readFile(this.filePath, "utf-8");
      try {
        const parsed = JSON.parse(text);
        if (!Array.isArray(parsed)) throw new Error("JSON is not an array");
        return parsed;
      } catch (cause) {
        // JSON壊れてる系
        throw new InfraError(
          "STORAGE_CORRUPTED",
          "Failed to parse storage JSON",
          {
            retryable: false,
            publicMessage: "保存データが壊れているみたい…🥺（JSONの形式を確認してね）",
            details: { filePath: this.filePath },
            cause,
          }
        );
      }
    } catch (cause) {
      if (isNodeErrno(cause)) {
        if (cause.code === "ENOENT") {
          // 初回起動：ファイル無しは「正常系」扱いにして空配列でもOK🙆‍♀️
          return [];
        }
        if (cause.code === "EACCES" || cause.code === "EPERM") {
          throw new InfraError(
            "STORAGE_PERMISSION_DENIED",
            "No permission to read storage file",
            {
              retryable: false,
              publicMessage: "保存先にアクセス権がないみたい…🔒（フォルダ権限を見てね）",
              details: { filePath: this.filePath, code: cause.code },
              cause,
            }
          );
        }
      }

      throw new InfraError("STORAGE_IO_FAILED", "Failed to read storage file", {
        retryable: true, // 一時的なI/Oなら再試行の余地あり
        publicMessage: "保存データの読み込みに失敗したよ…😵‍💫 もう一度試してね",
        details: { filePath: this.filePath },
        cause,
      });
    }
  }
}
```

**ポイント**💡

* `ENOENT`（無い）は「初回なら普通」なので、エラーにしない選択もアリ😊
* JSON壊れは **retryしても直らない** → `retryable: false`
* `cause` に元の例外を刺しておくと、あとでログで追える✨ ([Node.js][4])

---

## 6. ネットワークAdapter：fetch失敗を翻訳🌐🧩

Nodeの `fetch()` は **undiciベースの内蔵 fetch** だよ ([Node.js][3])

### 6.1 タイムアウトは AbortController で止める⌛🛑

```ts
export async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs: number
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } catch (cause) {
    // Abort はタイムアウトの可能性が高い
    throw new InfraError("NETWORK_TIMEOUT", "Request timed out", {
      retryable: true,
      publicMessage: "通信がタイムアウトしたよ…⌛ 電波いいとこで再試行してね",
      details: { url, timeoutMs },
      cause,
    });
  } finally {
    clearTimeout(timer);
  }
}
```

（この形は定番！） ([Stack Overflow][6])

### 6.2 HTTPステータスは「通信成功だけど結果NG」🚦

```ts
export async function callRemoteApiExample(url: string): Promise<unknown> {
  let res: Response;
  try {
    res = await fetchWithTimeout(url, { method: "GET" }, 5000);
  } catch (cause) {
    // ここはすでに InfraError が投げられてる想定（再スローでOK）
    if (cause instanceof InfraError) throw cause;

    throw new InfraError("NETWORK_UNAVAILABLE", "Network failure", {
      retryable: true,
      publicMessage: "ネットワークに問題があるみたい…📡 少し待って再試行してね",
      details: { url },
      cause,
    });
  }

  if (!res.ok) {
    throw new InfraError("REMOTE_BAD_STATUS", "Remote returned bad status", {
      retryable: res.status >= 500, // 5xxだけ再試行候補、4xxは基本NG
      publicMessage:
        res.status >= 500
          ? "相手サーバーが混雑してるかも…😵‍💫 少し待って再試行してね"
          : "リクエストが拒否されたよ…🔒（設定や認証を確認してね）",
      details: { url, status: res.status },
    });
  }

  return await res.json();
}
```

---

## 7. リトライ方針：**「何でも再試行」はダメ**⚠️🔁

* ✅ 再試行してOK：ネット一時不調、5xx、瞬断
* ❌ 再試行しても無駄：JSON壊れ、権限不足、4xx（大半）

一番ミニな指数バックオフ（雰囲気だけでもOK）👇

```ts
function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  maxAttempts = 3
): Promise<T> {
  let last: unknown;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (e) {
      last = e;

      // InfraErrorだけ判定する（それ以外は即死でもOK）
      if (!(e instanceof InfraError) || !e.retryable || attempt === maxAttempts) {
        throw e;
      }

      const backoff = 200 * Math.pow(2, attempt - 1);
      await sleep(backoff);
    }
  }

  throw last;
}
```

---

## 8. ログ：外側で「状況」を残す📝🪪

最低限でも **「どの操作」「どのファイル/URL」「どの失敗種別」**があると救われるよ〜🙏

### 8.1 まずは最小：consoleでもOK😊

```ts
function logInfraError(e: InfraError) {
  console.error("[infra-error]", {
    kind: e.kind,
    message: e.message,
    publicMessage: e.publicMessage,
    details: e.details,
    cause: e.cause, // Node/JSの標準機能✨
  });
}
```

### 8.2 ちゃんと構造化するなら pino も定番（任意）🧰✨

pino は Node 向け JSON ロガーとして広く使われてるよ ([getpino.io][7])

---

## 9. 入口（CLI/HTTP）では「表示用」に整形する🎀🧩

外側エラーは、ユーザーにそのまま生で見せないで、**優しい文**にするのが吉🥹💕

```ts
export function formatForUser(e: unknown): string {
  if (e instanceof InfraError) return e.publicMessage;
  if (e instanceof Error) return "予期しないエラーが起きたよ…🥺（詳細はログを見てね）";
  return "よくわからない失敗が起きたよ…😵‍💫";
}
```

---

## 10. AIに頼るときの“安全プロンプト”🤖✅（そのままコピペOK）

* 「この Adapter の責務は“変換と呼び出しだけ”になってる？業務ルール混ざってない？」🧩🥗
* 「I/O失敗を、InfraError(kind/retryable/publicMessage/cause) に翻訳できてる？」🧱✨
* 「retryable の判定は妥当？4xx をリトライしてない？」🔁⚠️
* 「ログに filePath / url / kind が残る？」📝📌

---

## 11. 自主課題📝🎀

1. **壊れたJSON**をわざと作って起動 → `STORAGE_CORRUPTED` が出るか確認🫠
2. `fetchWithTimeout` を使って、超遅いURLに当てて **timeout** を観測⌛
3. `withRetry` を噛ませて、**retryableだけ再試行**されるか確認🔁✅

---

## まとめ🎁💖

* 外側の失敗（I/O）は **Adapterで受け止めて翻訳**🧩
* 中心は仕様だけに集中して **静かに保つ**🧠🛡️
* `cause` を残すと、あとで絶対助かる✨ ([Node.js][4])
* リトライは「やっていい失敗」だけ！🔁⚠️

次の章（Composition Root）で、**本番はFileRepo／テストはInMemory**みたいな切替を“気持ちよく”やるよ〜🧩🏗️✨

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/?utm_source=chatgpt.com "Announcing TypeScript 5.9"
[3]: https://nodejs.org/en/learn/getting-started/fetch?utm_source=chatgpt.com "Node.js Fetch"
[4]: https://nodejs.org/api/errors.html?utm_source=chatgpt.com "Errors | Node.js v25.4.0 Documentation"
[5]: https://nodejs.org/api/fs.html?utm_source=chatgpt.com "File system | Node.js v25.4.0 Documentation"
[6]: https://stackoverflow.com/questions/46946380/fetch-api-request-timeout?utm_source=chatgpt.com "Fetch API request timeout? - javascript"
[7]: https://getpino.io/?utm_source=chatgpt.com "Pino"