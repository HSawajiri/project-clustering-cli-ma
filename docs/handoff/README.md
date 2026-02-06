# エージェント間引き継ぎ（Handoff）

このディレクトリは、4人のClaude Codeエージェント間で情報を引き継ぐための共有ドキュメント置き場です。

---

## 基本原則

⚠️ **全ての引き継ぎは文書化すること**

- 口頭説明は禁止
- 暗黙の前提は禁止
- ドキュメントに書かれていないことは「存在しない」と見なす

---

## 引き継ぎフロー

### Phase 1: 要件定義フェーズ

```
Manager → Designer: pm-to-designer.md
  （要件定義のレビュー依頼）

Designer → Manager: designer-to-pm.md
  （技術的実現可能性のフィードバック）
```

---

### Phase 2: 設計フェーズ

```
Designer → Manager: designer-to-pm.md
  （仕様書の承認依頼）

Designer → Implementer: designer-to-implementer.md
  （実装可能性の確認依頼 + 実装指示）

Manager → Designer: pm-to-designer.md
  （承認 or フィードバック）

Implementer → Designer: implementer-to-designer.md
  （実装可能性のフィードバック）
```

---

### Phase 3: 実装フェーズ

```
Implementer → Designer: implementer-to-designer.md
  （コードレビュー依頼）

Implementer → Tester: implementer-to-tester.md
  （テスト引き継ぎ）

Designer → Implementer: designer-to-implementer.md
  （レビューコメント or 承認）
```

---

### Phase 4: テストフェーズ

```
Tester → Designer: tester-to-designer.md
  （バグ報告）

Tester → Manager: tester-to-pm.md
  （リリース判断依頼）

Designer → Implementer: designer-to-implementer.md
  （バグ修正指示）
```

---

## ファイル一覧

| ファイル名 | 方向 | 目的 |
|-----------|------|------|
| `pm-to-designer.md` | Manager → Designer | レビュー依頼、承認/フィードバック |
| `designer-to-pm.md` | Designer → Manager | レビュー結果、承認依頼 |
| `designer-to-implementer.md` | Designer → Implementer | 実装指示、レビューコメント |
| `implementer-to-designer.md` | Implementer → Designer | 実装可能性確認、コードレビュー依頼 |
| `implementer-to-tester.md` | Implementer → Tester | テスト引き継ぎ |
| `tester-to-designer.md` | Tester → Designer | バグ報告 |
| `tester-to-pm.md` | Tester → Manager | リリース判断依頼 |

---

## 使い方

### 1. 引き継ぎドキュメントを作成

担当エージェントが該当ファイルに追記：

```markdown
---
## [日付] [作成者] → [受取者]

### 依頼内容 / 報告内容
...

### 期待するアクション
...

### 期限
...
```

### 2. 相手エージェントが確認

受取者が引き継ぎドキュメントを読み、対応：

```markdown
---
## [日付] [受取者] からの返信

### 対応内容
...

### フィードバック
...

### 次のアクション
...
```

### 3. クローズ

対応が完了したら、その旨を記載：

```markdown
### ステータス
✅ 完了 / ⏳ 対応中 / ❌ ブロック中
```

---

## テンプレート

各ファイルに以下のテンプレートを使用：

```markdown
# [送信者] → [受信者] 引き継ぎ

---

## [YYYY-MM-DD] [送信者名]

### 依頼内容 / 報告内容
...

### 関連ドキュメント
- docs/requirements.md
- docs/specification.md

### 期待するアクション
...

### 期限
...

### ステータス
⏳ 対応待ち

---

## [YYYY-MM-DD] [受信者名] からの返信

### 対応内容
...

### フィードバック
...

### 次のアクション
...

### ステータス
✅ 完了
```

---

## 注意事項

- ⚠️ 引き継ぎドキュメントは**追記型**です。上書きしないでください。
- ⚠️ 日付とステータスを必ず記載してください。
- ⚠️ 関連するドキュメントへのリンクを必ず記載してください。
- ⚠️ 曖昧な表現は避け、具体的に記載してください。

---

## 例

### pm-to-designer.md の例

```markdown
# Manager → Designer 引き継ぎ

---

## 2025-02-01 Manager

### 依頼内容
docs/requirements.md v0.9 を作成しました。
技術的実現可能性の観点でレビューをお願いします。

### 関連ドキュメント
- docs/requirements.md

### 期待するアクション
- 技術的に実現不可能な要件がないか確認
- アーキテクチャへの影響を評価
- フィードバックを designer-to-pm.md に記載

### 期限
2025-02-03

### ステータス
⏳ レビュー待ち

---

## 2025-02-02 Designer からの返信

### レビュー結果
全体的に実現可能です。以下の点を確認させてください：

1. NFR-003「1秒以内のレスポンス」について
   - データ量が多い場合、キャッシュ機構が必要
   - requirements.md に追記をお願いします

2. FR-005「エクセルファイルアップロード」について
   - ファイルサイズの上限を明記してください

### 次のアクション
Manager: 上記2点を requirements.md に反映

### ステータス
✅ レビュー完了、フィードバック提供済み
```

---
