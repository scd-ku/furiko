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
- **2026-11-22更新：** 写真テクスチャ `tbfg2191.jpg` を軽量化した `assets/tbfg2191.webp`（1024×512、約129KB）を配置し、OBJの全9,350面・28,050頂点コーナーのUV座標を16-bit量子化してJSONに保存しました。
- WebGL2表示では実測メッシュをUVで写真テクスチャにマッピングします。画像またはWebGLが利用できない場合には従来の単色描画へ自動的にフォールバックします。
- 別途生成した `PLATEAU_Tokyo_Tower_textured.glb` は、元データのUVとテクスチャを含む完全な確認用ファイル。ユーザー向けファイルとして提供しています（GitHub Pages上には未配置）。

## 東京スカイツリー：実測CityGML＋写真テクスチャを組み込み済み（2026-11-22）

ユーザー提供の墨田区PLATEAU CityGML `53394654_bldg_6697_op.gml` と専用写真 `tk32216.jpg` を解析し、正式な `gml:name=東京スカイツリー` の建物を分離しました。

- CityGML建物ID：`bldg_58ab8c46-8369-49c4-86cf-6912bbc4efe1`
- 建物属性 `bldg:measuredHeight`：634.9m
- 最も高い形状頂点：約635.141m
- 元の形状：693ポリゴン（うち616ポリゴンにUV写真テクスチャ）
- 描画用に三角形分割：1,304頂点／2,525三角形
- 地理座標：EPSG:6697 → JGD2011 平面直角第IX系（EPSG:6677）を経由し、アプリ局所座標に変換
- Web用幾何形状：`q16-vf-v1`（頂点5cm量子化、16bit面インデックス）
- UV：`q16-corner-uv-v1`（三角形コーナーごとの元テクスチャUV）
- 写真：元の2048×2048pxのJPEGから、1024×1024pxへリサイズしてWebP化しJSON内に埋め込み
- データ：`assets/plateau_tokyo_skytree.json`
- 未テクスチャ面は同アトラス内の中間色で表示
- 描画：`index.html` の `unpackVerifiedPlateau` / `uploadLandmarkPhoto` / `drawLandmarkPhotos` が利用
- 出典表示：国土交通省 Project PLATEAU 3D都市モデルを加工して作成

スカイツリーの元データと写真を検証したため、手作業で作成したスカイツリーモデルは通常時の背景に使われません。読み込みまたはWebGL2による写真描画に失敗した場合は簡易色付き表示にフォールバックします。

写真のUVマッピングの値はユーザー提供CityGML内の`app:textureCoordinates`に基づくものです。実ブラウザでの外観・色味の目視検証は別途必要です。

## 設定と出典

東京タワーの形状・UV座標および画像は、ユーザー提供のPLATEAU由来OBJ・MTL・JPEGを基にしています。Web表示ではJPEGをWebPへ変換し、解像度を1024×512に落としています。オリジナルのテクスチャ色調を維持しますが、完全な原解像度ではありません。スカイツリーは未取得のため従来の自作モデルです。

原本： https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku-obj4-2020
