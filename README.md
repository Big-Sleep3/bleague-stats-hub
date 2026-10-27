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