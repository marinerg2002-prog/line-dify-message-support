# LINE文章作成・返信サポートAI

送信したい内容を入力すると、相手や目的に合わせた文章を作成する LINE Bot です。  
LINE Messaging API・Flask・Dify API を連携しています。

## 構成

```text
LINE アプリ
  → LINE Webhook (/webhook)
  → Flask (app.py)
  → Dify API
  → LINE へ返信
```

## 必要なもの

- Python 3.11+
- [Dify](https://dify.ai/) の API キーと Chat API URL
- [LINE Developers](https://developers.line.biz/console/) の Messaging API チャネル
- ローカル公開用の [ngrok](https://ngrok.com/)（開発時）

## セットアップ

1. リポジトリをクローンする

```bash
git clone https://github.com/marinerg2002-prog/line-dify-message-support.git
cd line-dify-message-support
```

2. 仮想環境を作成して依存関係を入れる

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. 環境変数を設定する

```powershell
copy .env.example .env
```

`.env` に実際の値を記入します。

| 変数名 | 内容 |
| --- | --- |
| `DIFY_API_KEY` | Dify の API キー |
| `DIFY_API_URL` | Dify Chat Messages API の URL（例: `https://api.dify.ai/v1/chat-messages`） |
| `LINE_CHANNEL_SECRET` | LINE チャネルシークレット |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE チャネルアクセストークン |
| `PORT` | サーバーポート（省略時は `5000`） |

4. アプリを起動する

```powershell
python app.py
```

5. ngrok で公開する（別ターミナル）

```powershell
ngrok http 5000
```

6. LINE Developers の Webhook URL に次を設定する

```text
https://（ngrokの公開URL）/webhook
```

Webhook の利用をオンにし、検証を成功させてください。  
応答メッセージ・あいさつメッセージはオフにします。

## 主なエンドポイント

| メソッド | パス | 説明 |
| --- | --- | --- |
| `GET` | `/` | ヘルスチェック |
| `POST` | `/webhook` | LINE Webhook 受信 |

## 注意

- `.env` は Git 管理しません。秘密情報をリポジトリに含めないでください。
- ngrok を再起動すると公開 URL が変わるため、その都度 LINE の Webhook URL を更新してください。
