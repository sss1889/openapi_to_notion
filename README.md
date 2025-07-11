# OpenAPI to Notion Converter

OpenAPI の YAML ファイルを読み込んで、Notion ページに見やすい API 仕様書を自動生成するツールです。

## 機能

- OpenAPI 3.0 仕様の YAML ファイルをパース
- エンドポイントごとに以下の情報を Notion ページに出力：
  - エンドポイント名（HTTP メソッド + パス）
  - 説明とタグ
  - パラメータ（シンプルな JSON 形式）
  - リクエストボディ（シンプルな JSON 形式）
  - レスポンス（成功レスポンスのみ、シンプルな JSON 形式）
- 大量のエンドポイントに対応（プログレスバー表示、バッチ処理）
- Pydantic風のシンプルなスキーマ表示（Optional表記付き）

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

4. Notion API トークンを設定

   - [Notion Integrations](https://www.notion.so/my-integrations)でインテグレーションを作成
   - `.env.example`を`.env`にコピーして、トークンを設定

   ```bash
   cp .env.example .env
   # .envファイルを編集してNOTION_TOKENを設定
   ```

5. Notion ページでインテグレーションを Share（重要！）
   - 右上の「...」メニューから「connections」を選択
   - 作成したインテグレーションを選択

## 使い方

### 基本的な使い方

```bash
python main.py --openapi path/to/openapi.yaml --notion-page-id YOUR_PAGE_ID
```

### オプション

- `--openapi`: OpenAPI YAML ファイルのパス（必須）
- `--notion-page-id`: Notion ページの ID（必須）
- `--notion-token`: Notion インテグレーショントークン（環境変数で設定している場合は不要）
- `--include-errors`: エラーレスポンス（4xx、5xx）をドキュメントに含める（デフォルト：含めない）
- `--batch-size`: 一度に処理するエンドポイント数（デフォルト：5）

### Notion ページ ID の取得方法

1. Notion でドキュメントを作成したいページを開く
2. ブラウザの URL から以下の部分をコピー：
   ```
   https://www.notion.so/Page-Title-{ページID}
   ```
   ハイフンで区切られた最後の部分がページ ID です

## 出力例

各エンドポイントは以下のような形式で Notion ページに出力されます：

### GET /users/{userId} - ユーザー情報取得

**Parameters**

```json
{
  "userId": "string (path)"
}
```

**Responses**

**Status Code: 200**
成功時のレスポンス

Content-Type: application/json

```json
{
  "id": "string",
  "name": "string",
  "email": "string"
}
```

## トラブルシューティング

### Notion API エラー

- トークンが正しく設定されているか確認
- ページ ID が正しいか確認
- インテグレーションがページに追加されているか確認

### OpenAPI ファイルのパースエラー

- YAML ファイルの形式が正しいか確認
- OpenAPI 3.0 仕様に準拠しているか確認

## ライセンス

MIT License
