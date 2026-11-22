# PLATEAUランドマークモデル取り込み状況

## 東京タワー：実データを取り込み済み（2026-11-22）

ユーザー提供の2020年版PLATEAUデータ `533935894_bldg_6677.obj` と `materials(1).mtl` を解析し、東京タワーのマテリアル `tbfg2191` を分離しました。

- 出典：国土交通省 Project PLATEAU 3D都市モデルを加工して作成
- 元の塔体：4,847頂点 / 9,350三角形
- 原データの高度：17.098934〜350.546222m → 高さ約333.447m
- 元データの座標参照系：EPSG:6677（JGD2011／平面直角座標系第IX系）
- 出力：`assets/plateau_tokyo_tower.json`
- 表現方式：5cm位置量子化したオリジナルメッシュ（uint16）をBase64化
- 実装：`index.html` の `unpackVerifiedPlateau` と `addVerifiedPlateau`。JSONの検証に通れば従来モデルと差し替え
- 現在のWebGL表示は色帯を簡略化しており、添付された写真テクスチャ `tbfg2191.jpg` のUVマッピングは未実装です。
- 別途生成した `PLATEAU_Tokyo_Tower_textured.glb` は、元データのUVとテクスチャを含む完全な確認用ファイル。ユーザー向けファイルとして提供しています（GitHub Pages上には未配置）。

## 東京スカイツリー：未取得

墨田区のPLATEAUデータから塔体そのものの幾何形状は未検証です。現行アプリでは従来の自作スカイツリーモデルを表示します。

## 設定と出典

東京タワーの形状データはPLATEAUに由来しますが、インターナショナルオレンジと白の色分けはWeb表示用に簡略化したものです。元の写真テクスチャを使っていない表示を「完全な実測テクスチャモデル」と説明しないでください。

原本： https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku-obj4-2020
