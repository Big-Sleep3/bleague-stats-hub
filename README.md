# B.PREMIER STATS HUB (2026-27)

B.LEAGUE公式のクラブ詳細18項目（1試合平均・累計）、クラブ基本26項目、個人成績29項目、クラブ同士の比較を1ページにまとめた非公式スカウティングツール。

## 公開方法

GitHub → Settings → Pages → Build and deployment → Deploy from a branch → main → /(root) → Save。

有効化後のURL（公開確認前）: https://big-sleep3.github.io/bleague-stats-hub/

## データ状態

初期版のクラブ詳細は2026-10-26 02:24 JST更新の保存済み26クラブ。クラブ基本は初期0クラブ、個人成績は9選手の抜粋。全データを取得したという意味ではない。

## 自動更新と通知

GitHub Actionsの `Update B.PREMIER Stats` は**日本時間17:00〜翌02:45に15分ごと**、昼13:17・15:17にも公式データを確認する。早朝04:33は登録選手の変更も拾うため全選手の再取得を強制する。

- 通常の確認では26クラブのデータのみ取得。数値に変化があったときに限り全選手の再取得を行い、クラブ成績は先に公開する。
- GitHub Actionsの起動はGitHub側で遅れることがある。更新が検出されても、選手データの反映には時間がかかる場合がある。
- `data/last-data-change.json` に実データ更新の履歴・改訂番号を保持。単なるチェック成功だけでは改訂番号を増やさない。
- ChatGPT側の独立したタスクは**1時間ごと**に改訂番号をチェックし、新しい更新だけ通知する。通知済み番号は `data/notification-watermark.json` に保存して重複を防ぐ。
- 必要なら Actions → Update B.PREMIER Stats → Run workflow から手動更新できる。

- `scripts/update_stats.py`: 公式サイト取得・検証。Playwright使用
- `data/stats.json`: ページが読み込むデータ
- `data/sync-status.json`: 取得の成功・失敗・更新日時
- `tests/test_update_stats.py`: テスト

26クラブ揃わない結果や、個人成績200人未満・23クラブ未満の不完全なデータは更新に採用しない。失敗時には前回の値を保持する。2026年10月28日の初回実行では26クラブの基本・詳細成績と332選手分の成績を取得できた。新しい高速更新モードはGitHub上での検証が必要。

PITP / FBPS / 2NDPTS / PTSOFFTO / POSS は累計÷試合数、%・PACE・RTGは割らずに表示。

出典: https://www.bleague.jp/stats/?year=2026&tab=1&target=club-b1&value=sPointsInThePaint&o=desc&e=2&dt=dtl

公式サイトの利用条件とアクセス負荷に配慮して使用すること。
## 日本語 / English の切り替え

画面右上の「日本語」「English」から表示言語を切り替え可能。ランキング、指標名、フィルタ、比較画面、状態表示、CSVの列見出し、クラブ名は英語UIにも対応。順位と数値は言語にかかわらず同一の公式データを使用し、選手名は公式プロフィールの英語表記を取得できたものから英語へ切り替える。未取得選手は誤訳を避けて日本語のまま表示する。選択した言語はブラウザに保存される（保存が許可される環境のみ）。

UIのブラウザ動作テスト: `tests/test_i18n_ui.py`。

選手名の英語収集は公式選手詳細ページの実在するローマ字表記を使用。初期の主要選手名は表示側に登録済み。全選手の英語名は完全な選手データ再取得後に `data/stats.json` の `name_en` に反映し、数値に変更がない名前補完だけでは更新通知を発火させない。

## 公式英語選手名の一括補完

英語選手名は `scripts/enrich_english.py` で、公式の英語版・日本語版選手プロフィールの同一選手名を照合して収集する。専用 GitHub Actions `Verify English Player Names` はコード変更時、手動実行時、および日本時間05:43に実行する。全選手の名前は `data/player-names-en.json` に選手ID単位で保存し、`index.html` の英語表示・検索・CSVに反映する。取得失敗・未確認の場合は名前を推測しない。

GitHub Actionsの処理が終わるまでは `data/player-names-en.json` の `verified` が 0 のままのことがある。全選手の名前が確認できたかは `verified` と `total_players` を比較すること。

英語名のみの更新はスタッツの変更番号 `data/last-data-change.json` に影響せず、数値更新通知を発火させない。
