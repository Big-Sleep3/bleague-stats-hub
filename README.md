# B.PREMIER STATS HUB (2026-27)

B.LEAGUE公式のクラブ詳細18項目（1試合平均・累計）、クラブ基本26項目、個人成績29項目、クラブ同士の比較を1ページにまとめた非公式スカウティングツール。

## 公開方法

GitHub → Settings → Pages → Build and deployment → Deploy from a branch → main → /(root) → Save。

有効化後のURL（公開確認前）: https://big-sleep3.github.io/bleague-stats-hub/

## データ状態

初期版のクラブ詳細は2026-10-26 02:24 JST更新の保存済み26クラブ。クラブ基本は初期0クラブ、個人成績は9選手の抜粋。全データを取得したという意味ではない。

## 自動更新

GitHub Actionsの `Update B.PREMIER Stats` は日本時間 10:18 / 17:18 / 22:18 の3回実行する設定。初回は Actions → Update B.PREMIER Stats → Run workflow から手動で実行可能。

- `scripts/update_stats.py`: 公式サイト取得・検証。Playwright使用
- `data/stats.json`: ページが読み込むデータ
- `data/sync-status.json`: 取得の成功・失敗・更新日時
- `tests/test_update_stats.py`: テスト

26クラブ揃わない結果や、個人成績200人未満・23クラブ未満の不完全なデータは更新に採用しない。失敗時には前回の値を保持する。更新は未だライブ環境での成功確認を要する。

PITP / FBPS / 2NDPTS / PTSOFFTO / POSS は累計÷試合数、%・PACE・RTGは割らずに表示。

出典: https://www.bleague.jp/stats/?year=2026&tab=1&target=club-b1&value=sPointsInThePaint&o=desc&e=2&dt=dtl

公式サイトの利用条件とアクセス負荷に配慮して使用すること。