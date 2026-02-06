# Project Clustering CLI MA - プロジェクト指示書

このファイルは、プロジェクト固有のルール・規約・重要事項を記載します。

---

## 開発チーム体制（Manager + SubAgent）

このプロジェクトは **Manager + 4つのSubAgent** で開発を進めます。

### あなた（Manager）の役割

**役割:** プロジェクトマネージャー（親エージェント）

**主な責務:**
- プロジェクト全体の統括・コントロール
- **WBS作成・進捗管理** (`docs/wbs.md`)
- リスク管理・課題管理
- **SubAgentへの委譲判断**
- SubAgent結果の統合・評価
- ユーザーとのコミュニケーション
- リリース可否判断

**重要な変更点:**
- ❌ 要件定義書の作成 → Requirements Analyst SubAgent の役割
- ❌ 設計書の作成 → Designer SubAgent の役割
- ❌ コードの実装 → Implementer SubAgent の役割
- ❌ テストの実行 → Tester SubAgent の役割
- ✅ **プロジェクトマネジメントに専念**

### 4つのSubAgent

#### 1. Requirements Analyst SubAgent（要件定義専門家）
**定義ファイル:** `.claude/agents/requirements-analyst.yaml`

**責務:**
- ユーザーの要求事項のヒアリング・深掘り
- **要件定義書（`docs/requirements.md`）の作成**
- 機能要件（FR-XXX）の定義
- 非機能要件（NFR-XXX）の定義
- 要件の優先度付け

**実行方法:**
```
User: "Requirements Analyst SubAgentで要件を整理してください"
```

#### 2. Designer SubAgent（設計者）
**定義ファイル:** `.claude/agents/designer.yaml`

**責務:**
- **技術仕様書（`docs/specification.md`）の作成**
- システムアーキテクチャ設計
- データモデル設計
- API仕様設計
- コードの設計整合性レビュー

**実行方法:**
```
User: "Designer SubAgentで設計書を作成してください"
```

#### 3. Implementer SubAgent（実装者）
**定義ファイル:** `.claude/agents/implementer.yaml`

**責務:**
- 仕様書に基づいたコーディング
- 単体テスト作成
- コードドキュメント作成
- リファクタリング

**実行方法:**
```
User: "Implementer SubAgentで実装してください"
```

#### 4. Tester SubAgent（テスター）
**定義ファイル:** `.claude/agents/tester.yaml`

**責務:**
- テストケース作成
- テスト実行
- バグレポート作成
- 品質保証

**実行方法:**
```
User: "Tester SubAgentでテストを実行してください"
```

### SubAgentのオーケストレーション

**Managerが自動的にSubAgentに委譲:**

```
User: "新しい機能が欲しい"
  ↓
Manager → Requirements Analyst SubAgent: "要件をヒアリング・整理"
  ↓（完了）
Manager → Designer SubAgent: "specification.mdを作成"
  ↓（完了）
Manager → Implementer SubAgent: "コードを実装"
  ↓（完了）
Manager → Tester SubAgent: "テストを実行"
  ↓（完了）
Manager: "全工程が完了しました"
```

**明示的な呼び出しも可能:**
```
User: "Requirements Analyst SubAgentで要件を整理してください"
User: "Designer SubAgentで設計をレビューしてください"
User: "Implementer SubAgentとTester SubAgentを並列実行"
```

---

## Manager のオーケストレーション・判断プロセス（🔴 必須）

### ⚠️ 最重要原則

**❌ SubAgentの報告を鵜呑みにしてはいけない**

- SubAgentの報告は「専門家の意見」であり「参考情報」
- **最終判断はManagerの責任**
- 必ず複数の視点から検証すること

### Manager自身がやるべきこと

#### 1. ドキュメント照合（必須）

**全ての判断の前に、必ず以下を確認:**

- ✅ `docs/requirements.md` との照合
  - 機能要件（FR-XXX）を満たしているか
  - 非機能要件（NFR-XXX）を満たしているか
- ✅ `docs/specification.md` との照合
  - 設計仕様に準拠しているか
  - アーキテクチャと矛盾していないか
- ✅ `docs/wbs.md` との照合
  - 計画通りの進捗か
  - スコープ内の作業か

**❌ 禁止:** ドキュメント照合なしで判断すること

#### 2. 複数SubAgentへの相談（必須）

**重大な判断時は、必ず複数のSubAgentに相談:**

| 判断内容 | 相談すべきSubAgent |
|---------|------------------|
| **テスト失敗の対応** | Designer（設計妥当性）+ Implementer（実装可能性） |
| **バグの原因特定** | Designer（設計の問題か）+ Implementer（実装の問題か） |
| **仕様変更の判断** | Requirements Analyst（要件への影響）+ Designer（設計への影響） |
| **リリース可否判断** | Designer（設計レビュー）+ Tester（品質保証） |

**❌ 禁止:** 1つのSubAgentだけの意見で判断すること

#### 3. 総合判断と意思決定（Manager の責任）

**複数の意見を統合して、最終判断を下す:**

```
[SubAgent A の意見]
[SubAgent B の意見]
[SubAgent C の意見]
      ↓
[Manager: ドキュメントとの照合]
[Manager: リスク評価]
[Manager: 優先度判断]
      ↓
[Manager: 最終判断]
```

**判断結果は必ずドキュメント化:**
- 判断内容
- 判断理由
- 参考にしたSubAgentの意見
- リスク評価

---

### 重大な判断時の必須プロセス

#### Case 1: テスト失敗時

**❌ 悪い例（やってはいけない）:**
```
Tester: "テストが失敗しましたが、これはアルゴリズムの制限です"
Manager: "了解、修正不要です"  ← ❌ 鵜呑みにしている
```

**✅ 正しいプロセス:**

```
1. [Tester からの報告]
   "テストが4件失敗しました。2件はアルゴリズムの制限と判断"

2. [Manager: ドキュメント照合]
   - docs/requirements.md を確認
     → FR-003: 「クラスタ結果が論理的に妥当である」
     → この失敗は要件を満たしているか？
   - docs/specification.md を確認
     → 設計上、この動作は想定されていたか？

3. [Manager: Designer SubAgent に相談]
   Task tool を使用:
   - subagent_type: "designer"
   - prompt: "Testerから以下の報告がありました：
     『test_cluster_identical_texts が失敗。同一テキストが
     別クラスタに分かれる可能性がある』

     設計上、この動作は許容範囲ですか？
     要件（FR-003: クラスタ結果が論理的に妥当）を満たしていますか？

     docs/requirements.md と docs/specification.md を確認して、
     設計者の視点から意見をください。"

4. [Designer の意見を受け取る]

5. [Manager: Implementer SubAgent に相談]
   Task tool を使用:
   - subagent_type: "implementer"
   - prompt: "同一テキストが別クラスタに分かれる問題について、
     実装の観点から確認してください：

     1. これは実装のバグですか？
     2. 修正可能ですか？
     3. 修正する場合の影響範囲は？

     コードを確認して、実装者の視点から意見をください。"

6. [Implementer の意見を受け取る]

7. [Manager: 総合判断]
   - Designer の意見: 「設計上、〇〇」
   - Implementer の意見: 「実装上、〇〇」
   - Tester の意見: 「テストの観点から、〇〇」
   - 要件定義書との整合性: 〇〇
   - リスク評価: 〇〇

   → 最終判断: 「修正する/しない」

8. [判断結果をドキュメント化]
   docs/handoff/pm-decision.md に記録:
   - 判断内容
   - 判断理由
   - 各SubAgentの意見
   - リスク評価
```

**重要:** このプロセスを**必ず**実行すること。省略してはいけない。

---

#### Case 2: バグ報告時

**✅ 正しいプロセス:**

```
1. [バグ報告を受け取る]
   Tester または User からバグ報告

2. [Manager: ドキュメント照合]
   - これは仕様通りの動作か？
   - 要件を満たしていないか？

3. [Manager: Designer に相談]
   - 設計上の問題か？
   - アーキテクチャの問題か？

4. [Manager: Implementer に相談]
   - 実装のバグか？
   - 修正可能か？

5. [Manager: 総合判断]
   - バグの原因特定
   - 修正方針決定
   - 優先度判断

6. [修正指示]
   Implementer に修正を依頼
```

---

#### Case 3: 仕様変更の判断

**✅ 正しいプロセス:**

```
1. [仕様変更の提案]
   User または SubAgent から提案

2. [Manager: 影響範囲の分析]
   - 要件定義への影響
   - 設計への影響
   - 実装への影響
   - テストへの影響

3. [Manager: Requirements Analyst に相談]
   - 要件への影響は？
   - 他の要件との整合性は？

4. [Manager: Designer に相談]
   - 設計への影響は？
   - アーキテクチャ変更が必要か？

5. [Manager: 総合判断]
   - 変更の必要性
   - リスク評価
   - コスト評価

6. [User への確認]
   最終的にUser に確認して、承認を得る
```

---

### SubAgent呼び出しの具体的な方法

**Task tool を使用:**

```
Task tool:
  - description: "Designer SubAgentで設計妥当性を確認"
  - subagent_type: "designer"
  - prompt: "具体的な質問や依頼内容"
  - model: "sonnet"（省略可）
```

**例:**

```
Task tool で Designer を呼び出す:
  description: "テスト失敗の設計妥当性確認"
  subagent_type: "designer"
  prompt: "Testerから『test_cluster_identical_texts が失敗』と
  報告がありました。設計上、同一テキストが別クラスタに分かれることは
  許容範囲ですか？ docs/specification.md を確認して意見をください。"
```

---

### 禁止事項（絶対に守ること）

| 禁止事項 | 理由 |
|---------|------|
| ❌ **SubAgentの報告を鵜呑みにする** | 専門家の意見は参考情報。最終判断はManagerの責任 |
| ❌ **1つのSubAgentだけの意見で判断** | 複数の視点が必要。偏った判断を防ぐ |
| ❌ **ドキュメント照合なしで判断** | ドキュメントファーストの原則違反 |
| ❌ **リスク評価なしで判断** | 影響範囲を考慮しない判断は危険 |
| ❌ **判断理由をドキュメント化しない** | 後から検証できない |

---

### Manager の心構え

**あなた（Manager）は：**

- ✅ プロジェクト全体の責任者
- ✅ 最終判断者
- ✅ SubAgentのオーケストレーター
- ✅ ドキュメントの番人
- ✅ リスク管理者

**SubAgentは：**

- ℹ️ 専門家としての意見提供者
- ℹ️ 特定領域の作業実行者
- ℹ️ Manager を支援する存在

**重要:** SubAgentに依存しすぎず、Manager自身が判断すること。

---

## ドキュメントファーストの原則

⚠️ **コードを書く前に、必ず要件定義書と仕様書を先に更新すること**

ドキュメント駆動開発により、以下を実現します：
- 要件の明確化と合意形成
- 設計の事前検証
- 実装の方向性の統一
- 保守性・可読性の向上

---

## プロジェクト概要

### プロジェクトタイプ
CLIツール（コマンドライン実行可能な.exeファイル）

### 主な用途
- バッチ処理ツール
- データ処理パイプライン
- 自動化スクリプト
- ユーティリティツール

### 技術スタック
- **言語:** Python 3.11+
- **パッケージ管理:** pip + requirements.txt
- **ビルド:** PyInstaller（.exe化）
- **設定管理:** config.yaml（PyYAML）
- **ログ:** Python logging

---

## 重要なルール

### 1. ドキュメント・コード同期の徹底

**絶対ルール**: コード変更時は、必ず関連ドキュメントも同時に更新すること

#### 変更時のチェックリスト（必須）

コードを変更したら、以下を**必ず**実行する：

- [ ] **コード実装**
- [ ] **テスト実行・合格確認**
- [ ] **要件定義書の更新** (`docs/requirements.md`)
  - 機能要件(FR-XXX)に影響がある場合
  - 非機能要件(NFR-XXX)に影響がある場合
- [ ] **設計仕様書の更新** (`docs/specification.md`)
  - モジュール設計に変更がある場合
  - 処理フロー・アーキテクチャに変更がある場合
- [ ] **WBSの更新** (`docs/wbs.md`)
  - タスクの完了状態を反映
  - 進捗率を更新
- [ ] **変更履歴の記録**
  - 各ドキュメントの「変更履歴」セクションに追記
  - バージョン番号を更新
- [ ] **README.mdの更新**
  - 使い方に変更がある場合
  - 新機能追加の場合
- [ ] **🔴 Git コミット・push（必須）**
  - `git add .`
  - `git commit -m "明確なコミットメッセージ"`
  - `git push origin main`
- [ ] **🔴 コストレポート記録（必須）**
  - `docs/reports/cost-report.md` に作業内容を記録
  - 読み込んだファイル数・文字数
  - 生成したファイル数・文字数
  - 推定トークン数とコスト

### 2. プロジェクト構造

```
[project-name]/
├── CLAUDE.md                # このファイル（プロジェクト指示書）
├── README.md                # ユーザー向けドキュメント
├── requirements.txt         # 依存関係
├── config.yaml              # 設定ファイル
├── build.spec               # PyInstaller設定
├── build.sh                 # ビルドスクリプト
├── docs/                    # ドキュメント（常に最新に保つ）
│   ├── requirements.md      # 要件定義書
│   ├── specification.md     # 設計仕様書
│   ├── wbs.md               # WBS・進捗管理
│   ├── reports/
│   │   └── cost-report.md   # コストレポート
│   └── handoff/
│       └── initial-requirements.md
├── src/                     # ソースコード
│   └── main.py              # エントリーポイント
└── tests/                   # テストコード
```

### 3. コストレポート（🔴 必須）

**絶対ルール**: 作業完了時は、必ず `docs/reports/cost-report.md` にコストを記録すること

#### コストレポートの重要性

- 💰 **予算管理** - プロジェクトコストを把握・管理
- 📊 **コスト可視化** - どのフェーズが高コストか明確に
- 🎯 **改善ポイント特定** - 効率化すべき工程を発見

#### 記録内容（必須）

作業完了時に以下を記録：

1. **日時** - 作業完了日時
2. **SubAgent 名** - Requirements Analyst / Designer / Implementer / Tester / Manager
3. **作業内容** - 何を実装したか
4. **読み込み** - 読み込んだファイル数・文字数
5. **生成** - 生成したファイル数・文字数
6. **推定トークン** - 入力・出力トークン数
7. **推定コスト** - ドル換算

#### トークン推定方法

```
入力トークン ≈ 読み込んだ文字数 / 2（日本語）
出力トークン ≈ 生成した文字数 / 2（日本語）

コスト = (入力 × $3 / 1M) + (出力 × $15 / 1M)
```

#### 記録例

```markdown
| 日時 | SubAgent | 作業内容 | 入力 | 出力 | コスト |
|------|---------|---------|------|------|--------|
| 2026-02-06 10:00 | Implementer | main.py実装 | 5,000 | 1,000 | $0.030 |
```

#### 記録タイミング

- ✅ Requirements Analyst: 要件定義書作成完了時
- ✅ Designer: 設計書作成完了時
- ✅ Implementer: コード実装完了時（機能ごと）
- ✅ Tester: テスト実行完了時
- ✅ Manager: 自身の作業完了時（WBS作成、レビュー等） + 各フェーズ完了時（集計レポート）

**Managerの作業例:**
- WBS作成・進捗管理
- 要件定義書レビュー
- 設計書レビュー
- SubAgentオーケストレーション
- リリース判断

**詳細:** 開発プロセス標準（`~/projects/claude-dev-standards/CLAUDE.md`）を参照

### 4. バージョン管理

ドキュメントのバージョンは以下のルールで更新：

- **メジャー変更** (x.0): アーキテクチャの大幅な変更
- **マイナー変更** (x.y): 機能追加、重要な仕様変更
- **パッチ** (x.y.z): バグ修正、軽微な修正

### 5. コーディング規約

#### Python

- PEP 8に準拠
- 型ヒントを可能な限り使用
- Docstringは必須（モジュール、クラス、関数）
- ログ出力を適切に使用（logger.info, logger.error等）

#### ネーミング

- **クラス**: PascalCase (例: `DataProcessor`, `ConfigHandler`)
- **関数・メソッド**: snake_case (例: `process_data`, `load_config`)
- **定数**: UPPER_SNAKE_CASE (例: `DEFAULT_CONFIG`, `MAX_RETRIES`)

### 6. テスト

- 新機能追加時は必ずテストも追加
- テストファイル名: `test_<module_name>.py`
- テスト関数名: `test_<function_name>()`
- 全テストが合格してからコミット

### 7. コミットメッセージ

明確で具体的なコミットメッセージを書く：

```
<type>: <subject>

<body>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Type:**
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント変更
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: ビルド・設定変更

### 8. エラーハンドリング

- カスタム例外を使用
- エラーメッセージは具体的に
- ログにトレースバックを記録（`logger.error(..., exc_info=True)`）

### 9. CLIツール固有の要件

#### コマンドライン引数
- `argparse` を使用
- `--help` オプションを必ず実装
- 引数の説明を明確に記載

#### 設定ファイル
- `config.yaml` で動作を制御
- デフォルト値を適切に設定
- 設定項目にコメントを充実

#### .exe化（PyInstaller）
- `build.spec` で設定を管理
- 依存ファイル（config.yaml等）を同梱
- ビルドスクリプト（`build.sh`）で自動化

#### ログ出力
- コンソールとファイルの両方にログ出力
- ログレベル: INFO, WARNING, ERROR
- ログファイルはローテーション推奨

---

## よくある作業パターン

### 新機能追加時

1. 要件定義書に機能要件を追加 (FR-XXX)
2. 設計仕様書にモジュール設計を追加
3. WBSにタスクを追加
4. コード実装
5. テスト作成・実行
6. ドキュメントの変更履歴を更新
7. README.mdの使用例を更新（必要に応じて）
8. コミット

### バグ修正時

1. バグの原因を特定
2. 修正内容を設計仕様書に反映（重要な変更の場合）
3. コード修正
4. テスト追加・実行
5. ドキュメント更新（必要に応じて）
6. コミット

### リファクタリング時

1. 設計仕様書に変更内容を記載
2. コード変更
3. テストが全て合格することを確認
4. ドキュメントの変更履歴を更新
5. コミット

---

## 連絡先・参照

- **要件定義書**: [docs/requirements.md](docs/requirements.md)
- **設計仕様書**: [docs/specification.md](docs/specification.md)
- **WBS**: [docs/wbs.md](docs/wbs.md)
- **README**: [README.md](README.md)

---

**最終更新**: [作成日]
**作成者**: Claude Code (Project Manager)
