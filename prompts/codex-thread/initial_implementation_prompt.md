# 初回Codexプロンプト: DockForWindowsCodexSender

このリポジトリは `DockForWindowsCodexSender` です。

目的:
Windowsローカル環境で、Codex / Codex CLI に対してプロンプトを送信するための send-only bridge を作ります。

v0.1では、受信・解析・自動運用・WindowsアプリUI自動操作は実装しません。
まずは「プロンプトを安全に生成し、dry-runし、Codex CLIへ送信できること」を優先します。

## 背景

私は複数の Timeline / Dock / Tool 製品を管理しています。
手作業で各Codexスレッドへ指示を貼り続けるのは避けたいです。

このリポジトリでは、以下を最初の到達点にします。

- repo一覧を設定できる
- 製品ごとのプロンプトを生成できる
- dry-runで送信予定を確認できる
- Codex CLIへ1 repo単位で送信できる
- send-all は dry-run first とし、実送信には明示フラグを要求する
- 送信済みプロンプトと送信ログを保存する

## v0.1でやること

1. リポジトリ構成を確認する
2. 既存ファイルがあれば尊重する
3. CLIを実装または補強する
4. `config/repos.example.yaml` を読み込めるようにする
5. `config/prompts.yaml` を読み込めるようにする
6. prompt templateをrenderできるようにする
7. `data/outbox` へrendered promptを保存できるようにする
8. Codex CLI transportを実装する
9. `--dry-run` で実行予定コマンドとprompt pathを表示する
10. 実送信時は送信内容を `data/sent` に保存する
11. `data/logs/send-log.jsonl` にログを保存する
12. pytestで最低限のテストを追加する
13. READMEに使い方を書く

## CLIとして欲しいコマンド

```powershell
dock-windows-codex-sender repos list
dock-windows-codex-sender prompt render --repo timeline_for_chatgpt --kind bootstrap
dock-windows-codex-sender prompt render-all --kind bootstrap
dock-windows-codex-sender send --repo timeline_for_chatgpt --kind bootstrap --dry-run
dock-windows-codex-sender send --repo timeline_for_chatgpt --kind bootstrap
dock-windows-codex-sender send-all --kind bootstrap --dry-run
dock-windows-codex-sender send-all --kind bootstrap --confirm-send-all
```

## 安全ルール

- デフォルトは安全側に倒す
- send-allの実送信は `--confirm-send-all` がなければ拒否する
- Windows Codex app UI automationは実装しない
- 受信・解析は実装しない
- deployしない
- secretを扱わない
- raw inputを削除・移動・リネームしない
- 外部投稿しない
- 大規模アーキテクチャ変更はしない

## Codex CLI transport

まずは以下のような方式を想定します。

```powershell
codex exec --cd <repo_path> -
```

prompt本文はstdinで渡してください。

`codex` binary pathは環境変数またはオプションで差し替え可能にしてください。

## 実装の優先順位

1. 設定読み込み
2. prompt rendering
3. outbox保存
4. dry-run
5. send one repo
6. send log
7. send-all dry-run
8. send-all confirmed
9. tests
10. README整備

## 報告形式

最後に以下の形式で報告してください。

```md
## Current state

## Completed

## Changed files

## Commands implemented

## Dry-run behavior

## Actual send behavior

## Tests

## Risks

## Next safe tasks

## Human decisions needed
```
