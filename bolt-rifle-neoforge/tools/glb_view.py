import struct, json, math, sys, numpy as np
from PIL import Image
p="/mnt/user-data/attachments/f7704eef-62d6-5370-832a-86ddeef93d7b/be7dcb82-ak-47_low-poly.glb"
d=open(p,"rb").read(); off=12; js=None; bn=b""
while off<len(d):
    n,t=struct.unpack_from("<II",d,off); c=d[off+8:off+8+n]; off+=8+n
    if t==0x4E4F534A: js=json.loads(c)
    elif t==0x004E4942: bn=c
def acc(i):
    a=js["accessors"][i]; bv=js["bufferViews"][a["bufferView"]]
    dt={5126:np.float32,5123:np.uint16,5125:np.uint32,5121:np.uint8}[a["componentType"]]; k={"SCALAR":1,"VEC3":3,"VEC2":2,"VEC4":4}[a["type"]]
    st=bv.get("byteStride")
    o=bv.get("byteOffset",0)+a.get("byteOffset",0)
    if st and st!=k*np.dtype(dt).itemsize:
        arr=np.ndarray((a["count"],k),dt,bn,o,(st,np.dtype(dt).itemsize)); return arr.copy()
    return np.frombuffer(bn,dt,a["count"]*k,o).reshape(-1,k)
def local(nd):
    if "matrix" in nd: return np.array(nd["matrix"]).reshape(4,4).T
    M=np.eye(4)
    if "scale" in nd: M=np.diag(list(nd["scale"])+[1])@M
    if "rotation" in nd:
        x,y,z,w=nd["rotation"]; R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
        T=np.eye(4);T[:3,:3]=R;M=T@M
    if "translation" in nd:
        T=np.eye(4);T[:3,3]=nd["translation"];M=T@M
    return M
parts=[]  # (name, V(world), F, color)
def walk(i,P):
    nd=js["nodes"][i]; M=P@local(nd)
    if "mesh" in nd:
        for pr in js["meshes"][nd["mesh"]]["primitives"]:
            V=acc(pr["attributes"]["POSITION"]).astype(float); V=(M[:3,:3]@V.T).T+M[:3,3]
            F=acc(pr["indices"]).reshape(-1,3).astype(int) if "indices" in pr else np.arange(len(V)).reshape(-1,3)
            mat=js["materials"][pr["material"]] if "material" in pr else {}
            col=mat.get("pbrMetallicRoughness",{}).get("baseColorFactor",[.6,.6,.6,1])[:3]
            parts.append((nd.get("name","?"),V,F,np.array(col),pr.get("material")))
    for c in nd.get("children",[]): walk(c,M)
for r in js["scenes"][js.get("scene",0)]["nodes"]: walk(r,np.eye(4))
allv=np.concatenate([p[1] for p in parts]); lo,hi=allv.min(0),allv.max(0)
print("bounds",lo.round(3),hi.round(3),"size",(hi-lo).round(3))
for nm,V,F,c,mi in parts:
    if "Round" in nm or "Bullet" in nm: continue
    print("%-48s tris %5d  min %s max %s mat %s col %s"%(nm[:48],len(F),V.min(0).round(2),V.max(0).round(2),mi,c.round(2)))
if len(sys.argv)>1:
    yaw,pitch,out=float(sys.argv[1]),float(sys.argv[2]),sys.argv[3]
    ya,pa=math.radians(yaw),math.radians(pitch)
    Ry=np.array([[math.cos(ya),0,math.sin(ya)],[0,1,0],[-math.sin(ya),0,math.cos(ya)]])
    Rp=np.array([[1,0,0],[0,math.cos(pa),-math.sin(pa)],[0,math.sin(pa),math.cos(pa)]])
    R=Rp@Ry; ctr=(lo+hi)/2; ext=np.linalg.norm(hi-lo); S=1500/ext; W,H=1600,900
    img=np.zeros((H,W,3),np.uint8)+235; zb=np.full((H,W),1e9); L=np.array([-.4,.7,.6]);L/=np.linalg.norm(L)
    for nm,V,F,c,mi in parts:
        P=(R@(V-ctr).T).T
        sx=W/2+P[:,0]*S; sy=H/2-P[:,1]*S; z=-P[:,2]
        for f in F:
            a,b,cc=P[f[0]],P[f[1]],P[f[2]]; n=np.cross(b-a,cc-a); ln=np.linalg.norm(n)
            if ln<1e-12: continue
            n/=ln; sh=0.35+0.65*abs(float(n@L)); col=(c**(1/2.2)*255*sh).clip(0,255)
            xs=sx[f];ys=sy[f];x0,x1=int(max(xs.min(),0)),int(min(xs.max()+1,W-1));y0,y1=int(max(ys.min(),0)),int(min(ys.max()+1,H-1))
            if x1<x0 or y1<y0: continue
            gx,gy=np.meshgrid(np.arange(x0,x1+1),np.arange(y0,y1+1))
            dd=(ys[1]-ys[2])*(xs[0]-xs[2])+(xs[2]-xs[1])*(ys[0]-ys[2])
            if abs(dd)<1e-9: continue
            l0=((ys[1]-ys[2])*(gx+.5-xs[2])+(xs[2]-xs[1])*(gy+.5-ys[2]))/dd; l1=((ys[2]-ys[0])*(gx+.5-xs[2])+(xs[0]-xs[2])*(gy+.5-ys[2]))/dd; l2=1-l0-l1
            m=(l0>=0)&(l1>=0)&(l2>=0)
            if not m.any(): continue
            zz=l0*z[f[0]]+l1*z[f[1]]+l2*z[f[2]]; up=m&(zz<zb[gy,gx]); zb[gy[up],gx[up]]=zz[up]; img[gy[up],gx[up]]=col
    Image.fromarray(img).save(out); print("saved",out)
