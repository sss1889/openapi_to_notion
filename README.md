# OpenAPI to Notion Converter

OpenAPIのYAMLファイルを読み込んで、Notionページに見やすいAPI仕様書を自動生成するツールです。

## 機能

- OpenAPI 3.0仕様のYAMLファイルをパース
- エンドポイントごとに以下の情報をNotionページに出力：
  - エンドポイント名（HTTPメソッド + パス）
  - 説明とタグ
  - パラメータ（JSON形式）
  - リクエストボディ（JSON形式）
  - レスポンス（ステータスコードごと、JSON形式）

## セットアップ

1. リポジトリをクローン
```bash
git clone <repository-url>
cd openapi-to-notion
```

2. 仮想環境を作成して有効化
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

3. 依存関係をインストール
```bash
pip install -r requirements.txt
```

4. Notion APIトークンを設定
   - [Notion Integrations](https://www.notion.so/my-integrations)でインテグレーションを作成
   - `.env.example`を`.env`にコピーして、トークンを設定
   ```bash
   cp .env.example .env
   # .envファイルを編集してNOTION_TOKENを設定
   ```

5. NotionページでインテグレーションをShare
   - 対象のNotionページを開く
   - 右上の「...」メニューから「Add connections」を選択
   - 作成したインテグレーションを選択

## 使い方

### 基本的な使い方
```bash
python main.py --openapi path/to/openapi.yaml --notion-page-id YOUR_PAGE_ID
```

### オプション
- `--openapi`: OpenAPI YAMLファイルのパス（必須）
- `--notion-page-id`: NotionページのID（必須）
- `--notion-token`: Notionインテグレーショントークン（環境変数で設定している場合は不要）

### NotionページIDの取得方法
1. Notionでドキュメントを作成したいページを開く
2. ブラウザのURLから以下の部分をコピー：
   ```
   https://www.notion.so/Page-Title-{ページID}
   ```
   ハイフンで区切られた最後の部分がページIDです

## 出力例

各エンドポイントは以下のような形式でNotionページに出力されます：

### GET /users/{userId} - ユーザー情報取得

**Parameters**
```json
[
  {
    "name": "userId",
    "in": "path",
    "required": true,
    "description": "ユーザーID",
    "schema": {
      "type": "string"
    }
  }
]
```

**Responses**

**Status Code: 200**
成功時のレスポンス

Content-Type: application/json
```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "email": {
      "type": "string"
    }
  }
}
```

## トラブルシューティング

### Notion APIエラー
- トークンが正しく設定されているか確認
- ページIDが正しいか確認
- インテグレーションがページに追加されているか確認

### OpenAPIファイルのパースエラー
- YAMLファイルの形式が正しいか確認
- OpenAPI 3.0仕様に準拠しているか確認

## ライセンス

MIT License