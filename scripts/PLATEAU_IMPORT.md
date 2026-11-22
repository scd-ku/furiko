# PLATEAUランドマーク置換の状態

## 現在の状態

実測PLATEAUデータの抽出処理と、3Dアプリの条件付き読み込み処理を実装しました。ただし実際のOBJファイルはまだ取得できておらず、**アプリに表示される2塔は現行の手続き生成モデルのまま**です。元データなしでPLATEAUモデルに差し替えたと説明してはいけません。

## 公式ソースと対象

- 東京都23区 2020年度 OBJ 4次メッシュ: https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku-obj4-2020
- 東京タワー: 533935 配布ZIP内の LOD2 → 533935894 → 533935894_bldg_6677.obj（公開チュートリアルで確認）。
- 東京スカイツリー: 墨田区の年度別PLATEAUデータを調査中。塔体自体の実測3Dデータが収録されていることを確認できていません。塔体がないデータを、スカイツリーの実測モデルとして公開しないでください。

## 抽出ツール

準備: Pythonに numpy、trimesh、pyproj をインストール。

コマンド例:
  python scripts/plateau_obj_extract.py --obj path/to/533935894_bldg_6677.obj --landmark tower --output assets/plateau_tokyo_tower.json

出力先:
- 東京タワー: assets/plateau_tokyo_tower.json
- 東京スカイツリー: assets/plateau_tokyo_skytree.json

スクリプトはEPSG:6677の実際の位置と塔の高さを検証し、条件を満たさなければエラー停止します。元ファイルに含まれる周辺建築物を誤って抽出しないよう、完成モデルは3Dビューアで最終確認が必要です。現在は実測形状を検証するための抽出機能のみで、写真テクスチャは再現していません。

## アプリへの適用

index.html は対応するJSONファイルをGitHub Pages上に見つけ、source=PLATEAU、landmark、trianglesの最低限の検証に通った場合に限り自作タワーを置換します。読み込みに失敗した場合は自作モデルを維持します。登録したアセットの出典は「出典：国土交通省 Project PLATEAU 3D都市モデルを加工して作成」と明記してください。

## 制限

2020年度の配布ZIPはこの実行環境では直接ダウンロードできませんでした。現在のモデルは**PLATEAUを抽出したデータではありません**。必要な原データ取得と形状確認のあと、両タワーのモデルを正式に差し替える必要があります。
