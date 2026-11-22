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

## 東京スカイツリー：アプリ側の写真テクスチャ描画対応済み／実測元データは未取得

- スカイツリーがある3次地域メッシュは `53394654`（北緯約35.710°・東経約139.811°）。
- 国土交通省PLATEAUの墨田区2023年度CityGML・3D Tilesには建築物LOD2があり、スカイツリーの塔体の形状が収録されていると確認されています。
- データセット： https://www.geospatial.jp/ckan/dataset/plateau-13107-sumida-ku-2023
- Webアプリ `index.html` は、`assets/plateau_tokyo_skytree.json` に検証済み実測形状とUV座標が入り、`photographic_texture` に画像への相対パスが設定されていれば、東京タワーと独立した写真テクスチャをWebGL2で描画できます。
- ただし、2026-11-22現在、スカイツリーのOBJ/MTL/写真画像を**実際に取得・検証できていません**。`assets/plateau_tokyo_skytree.json` は `source: NOT_AVAILABLE` のままです。
- 写真テクスチャが元のLOD2モデルで提供されているかも未確認です。実測形状と写真テクスチャを混同しないでください。
- 実際のモデルを登録するには、地域メッシュ `53394654` に対応する建築物モデルからスカイツリーを抽出し、必要ならPLATEAU SDKでOBJ形式に変換します。OBJ/MTLとUVで参照される写真画像を合わせて確認してください。
- WebGL2非対応時には既存の色付きモデルが表示されます。元データ未取得時も既存の自作スカイツリーが表示されます。

## 設定と出典

東京タワーの形状・UV座標および画像は、ユーザー提供のPLATEAU由来OBJ・MTL・JPEGを基にしています。Web表示ではJPEGをWebPへ変換し、解像度を1024×512に落としています。オリジナルのテクスチャ色調を維持しますが、完全な原解像度ではありません。スカイツリーは未取得のため従来の自作モデルです。

原本： https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku-obj4-2020
