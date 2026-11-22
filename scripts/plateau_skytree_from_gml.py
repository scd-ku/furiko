#!/usr/bin/env python3
"""Extract validated PLATEAU Tokyo Skytree CityGML and its original photo atlas.

Inputs are the user-provided 2023 Sumida CityGML and tk32216.jpg.
Output is an ASCII-only JSON consumed by scd-ku/furiko's PLATEAU loader.
"""
import argparse
from collections import Counter
from pathlib import Path
import base64
import io
import json
import math
import numpy as np
from lxml import etree
from PIL import Image
from pyproj import Transformer
from shapely import Polygon, constrained_delaunay_triangles

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--gml',type=Path,required=True)
ap.add_argument('--texture',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args()
SOURCE=args.gml
TEXTURE=args.texture
OUT=args.output
NS={"gml":"http://www.opengis.net/gml","app":"http://www.opengis.net/citygml/appearance/2.0","bldg":"http://www.opengis.net/citygml/building/2.0"}
GML_ID='{http://www.opengis.net/gml}id'
transformer=Transformer.from_crs('EPSG:6697','EPSG:6677',always_xy=False)
lon,lat=139.81070,35.71006
anchor_e,anchor_n=transformer.transform(lat,lon)

def vector3(source):
    v=np.asarray([float(x) for x in source.split()],dtype=float).reshape((-1,3))
    e,n=transformer.transform(v[:,0],v[:,1])
    return np.column_stack([e-anchor_e,v[:,2],-(n-anchor_n)])

def projected(vertices):
    # Project each planar polygon into 2-D using its dominant axis normal.
    a=vertices[:-1] if np.linalg.norm(vertices[-1]-vertices[0])<1e-7 else vertices
    normal=np.zeros(3)
    for i in range(len(a)):
        p,q=a[i],a[(i+1)%len(a)];normal+=np.cross(p,q)
    dominant=int(np.argmax(np.abs(normal)))
    axes=[i for i in range(3) if i!=dominant]
    return a[:,axes]

root=etree.parse(str(SOURCE))
buildings=root.xpath('//bldg:Building[gml:name="東京スカイツリー"]',namespaces=NS)
if len(buildings)!=1:raise RuntimeError('Cannot uniquely locate the named Tokyo Skytree building')
b=buildings[0]
height=float(b.xpath('./bldg:measuredHeight/text()',namespaces=NS)[0])
if not 630<=height<=640:raise RuntimeError('Unexpected measured height')
tex=root.xpath('//app:ParameterizedTexture[app:imageURI[contains(text(),"tk32216.jpg")]]',namespaces=NS)
if len(tex)!=1:raise RuntimeError('The uploaded atlas is not referenced exactly once')
textures={}
for target in tex[0].xpath('./app:target',namespaces=NS):
    pid=target.get('uri','').lstrip('#')
    rings={}
    for uv in target.xpath('./app:TexCoordList/app:textureCoordinates',namespaces=NS):
        rings[uv.get('ring','').lstrip('#')]=np.asarray([float(x) for x in uv.text.split()],dtype=float).reshape((-1,2))
    textures[pid]=rings

vertices=[];faces=[];uv_faces=[];index={};stats=Counter();min_height=1e9;max_height=-1e9

def index_for(point):
    key=tuple(np.round(point,3))
    if key not in index:
        index[key]=len(vertices);vertices.append(point)
    return index[key]

def ring_data(poly,kind):
    # Returning both 3D geometry and UV coordinates for every polygon ring.
    r=poly.xpath('./gml:'+kind+'/gml:LinearRing',namespaces=NS)
    if not r:return []
    out=[]
    pid=poly.get(GML_ID)
    for ring in r:
        raw=ring.xpath('./gml:posList/text()',namespaces=NS)
        if not raw:continue
        v=vector3(raw[0]);closed=np.linalg.norm(v[0]-v[-1])<1e-4
        if closed:v=v[:-1]
        coords=textures.get(pid,{}).get(ring.get(GML_ID))
        if coords is not None and len(coords)>0:
            coords=coords[:-1] if np.allclose(coords[0],coords[-1],atol=1e-5) else coords
            if len(coords)!=len(v):
                raise RuntimeError(f'UV count mismatch at {pid}: {len(coords)}, {len(v)}')
        out.append((v,coords))
    return out

for polygon in b.xpath('.//gml:Polygon',namespaces=NS):
    outer=ring_data(polygon,'exterior');holes=ring_data(polygon,'interior')
    if not outer:stats['missing exterior']+=1;continue
    ext,eu=outer[0]
    if len(ext)<3:continue
    # Convert to a 2D polygon in its own plane while keeping a 2D->3D mapping.
    all_rings=[(ext,eu)]+holes
    n=np.zeros(3)
    for i in range(len(ext)):n+=np.cross(ext[i],ext[(i+1)%len(ext)])
    axes=[j for j in range(3) if j!=int(np.argmax(np.abs(n)))]
    rings2d=[v[:,axes] for v,_ in all_rings]
    flat=np.concatenate(rings2d)
    polygon2d=Polygon(rings2d[0],rings2d[1:])
    if not polygon2d.is_valid:polygon2d=polygon2d.buffer(0)
    if polygon2d.is_empty:stats['degenerate polygons']+=1;continue
    xy_to_vertex={}
    for (pts,uv),xy in zip(all_rings,rings2d):
        for k,p in enumerate(xy):
            key=tuple(np.round(p,6))
            xy_to_vertex[key]=(pts[k],(None if uv is None else uv[k]))
    try:
        triangles=constrained_delaunay_triangles(polygon2d)
        polys=list(triangles.geoms)
    except Exception:
        from shapely.ops import triangulate
        polys=[p for p in triangulate(polygon2d) if polygon2d.covers(p)]
        stats['fallback triangulation']+=1
    for tri in polys:
        t=np.asarray(tri.exterior.coords)[:3]
        if len(t)!=3 or tri.area<1e-7:continue
        v3=[];tex_uv=[]
        for p in t:
            key=tuple(np.round(p,6))
            data=xy_to_vertex.get(key)
            if data is None:
                closest=min(xy_to_vertex, key=lambda k:(k[0]-p[0])**2+(k[1]-p[1])**2)
                if np.linalg.norm(np.asarray(closest)-p)>.01:raise RuntimeError(f'Triangulator added a vertex: {p}')
                data=xy_to_vertex[closest]
            v3.append(data[0]);tex_uv.append(data[1])
        if np.linalg.norm(np.cross(v3[1]-v3[0],v3[2]-v3[0]))<1e-5:continue
        faces.append(tuple(index_for(p) for p in v3))
        if all(p is not None for p in tex_uv):
            uv_faces.extend(tex_uv);stats['textured triangles']+=1
        else:
            uv_faces.extend([None]*3);stats['untextured triangles']+=1
        min_height=min(min_height,*(p[1] for p in v3));max_height=max(max_height,*(p[1] for p in v3))
    stats['source polygons']+=1
if len(faces)<500 or max_height<600:raise RuntimeError('Insufficient source geometry')
print('stats',stats,'vertices',len(vertices),'triangles',len(faces),'height',min_height,max_height)
verts=np.asarray(vertices)
faces=np.asarray(faces,dtype=np.uint16)
# Relocate mesh base to the world ground (0m). Keep horizontal coordinates relative to tower center.
verts[:,1]-=min_height
min_xyz=verts.min(axis=0)
unit=.05
quant=np.round((verts-min_xyz)/unit)
if quant.max()>65535:raise RuntimeError('Geometric range overflows q16')
quant=quant.astype('<u2')
if len(vertices)>65535:raise RuntimeError('Too many distinct vertices')
body=quant.tobytes()+faces.astype('<u2').tobytes()
print('binary geometry',len(body),'raw bytes')

# Resize atlas and append a narrow neutral-color edge for polygons without UV.
with Image.open(TEXTURE) as src:
    rgba=src.convert('RGB');rgba=rgba.resize((1024,1024),Image.Resampling.LANCZOS)
    atlas=Image.new('RGB',(1024,1040),(200,208,210))
    atlas.paste(rgba,(0,0))
    bio=io.BytesIO();atlas.save(bio,format='WEBP',quality=78,method=6)
    photo=bio.getvalue()
# Geo UV origins: V=0 bottom edge. New blank neutral strip at image bottom.
texq=np.zeros((len(uv_faces),2),dtype='<u2')
for i,p in enumerate(uv_faces):
    if p is None:
        uv=(.5,8/1040)
    else:
        uv=(float(p[0]),(float(p[1])*1024+16)/1040)
    texq[i]=np.round(np.clip(uv,0,1)*65535).astype('<u2')
assert len(uv_faces)==len(faces)*3

result={
 'source':'PLATEAU','landmark':'skytree','source_file':SOURCE.name,
 'source_material':'tk32216.jpg','source_citygml_building_id':b.get(GML_ID),
 'source_height_m':height,'height_m':round(max_height-min_height,3),
 'format':'q16-vf-v1','vertex_count':len(vertices),'face_count':len(faces),
 'unit_m':unit,'origin_m':[round(float(v),5) for v in min_xyz],
 'data':base64.b64encode(body).decode('ascii'),
 'uv_format':'q16-corner-uv-v1','uv_data':base64.b64encode(texq.tobytes()).decode('ascii'),
 'photographic_texture':'data:image/webp;base64,'+base64.b64encode(photo).decode('ascii'),
 'texture_source':TEXTURE.name,
 'license_note':'出典：国土交通省 Project PLATEAU 3D都市モデルを加工して作成',
 'stats':dict(stats)
}
OUT.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('final JSON',OUT.stat().st_size,'texture image',len(photo),'bytes','source bldg id',b.get(GML_ID));
print('bounds local:', verts.min(axis=0), verts.max(axis=0))
# Transfer as 1200-char lines for connector-safe read and publishing.
raw=OUT.read_text(encoding='utf-8')
chunked=Path('/mnt/data/plateau_tokyo_skytree_import_chunked.txt')
chunked.write_text('\n'.join(raw[i:i+1200] for i in range(0,len(raw),1200))+'\n',encoding='utf-8')
print('upload transport',chunked, 'lines',len(raw)//1200+1)