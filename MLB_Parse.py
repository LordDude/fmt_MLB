#from MPIREStuff import MStream, MStreamBuffer
import sys
import os
import struct
dir_path = os.getcwd()+'\\'

def readUInt(f):
    return struct.unpack('I', f.read(4))[0]

def readInt(f):
    return struct.unpack('i', f.read(4))[0]

def readUInt64(f):
    return struct.unpack('Q', f.read(8))[0]

def readUShort(f):
    return struct.unpack('H', f.read(2))[0]

def readFloat(f) -> float:
    return struct.unpack('f', f.read(4))[0]

def getSize(f):
    t = f.tell()
    f.seek(0, 2)
    Size = f.tell()
    f.seek(t)
    return Size

def readString(f) -> str:
    '''Read Terminated String'''
    H = f.read(1)
    P = H
    while H != b'\x00':
        H = f.read(1)
        P += H
    return P.decode("ASCII").rstrip("\x00")

def LoadFile():
    bs = open(sys.argv[1], 'rb')
    Check = bs.read(8)
    if b'IFF0MODL' in Check:
        bs.seek(0)
        return bs
    else:
        raise ValueError()
    
def ReturnShaderName(ID):
    if ID == int(963085113):
        return "PBRShader"
    elif ID == int(3050143925):
        return "stadiumgrass"
    elif ID == int(3451704346):
        return "Simple"
    elif ID == int(997365454):
        return "PBRLayeredMask_Dirt"
    elif ID == int(751546760):
        return "PBRLayeredMask"
    elif ID == int(3336866762):
        return "GrassPattern"
    elif ID == int(3429282042):
        return "stadiumwater"
    elif ID == int(870750588):
        return "PBRLayered"
    elif ID == int(1821963899):
        return "PBRAnimated"
    elif ID == int(3126041189):
        return "StadiumBase_Bink"
    else:
        return "Unknown Shader"+"_"+str(ID)
    
class DRBLINT:
    def __init__(self):
        self.Index = int()
        self.Pad = bytes()
        self.Offset = int()

class DRBLVertClass:
    def __init__(self, bs) -> None:
        self.VertClassBlank = readInt(bs)
        self.VertCountSkip = readUInt(bs)
        self.VertClassUNK1 = readUInt(bs)
        self.LODCount = readUInt(bs)
        self.VertClassUNK3 = readUInt64(bs)

class DRBLVertTechClass:
    def __init__(self, bs) -> None:
        RET = bs.tell()
        self.VertBlockSkip = readUInt(bs)
        self.VertTechClassUNK = readUInt(bs)
        self.VertTechClassUNK1_1 = readUShort(bs)
        self.VertTechClassUNK1_2 = readUShort(bs)
        self.VertTechClassUNK2 = readUInt64(bs)
        bs.seek(RET+self.VertTechClassUNK)
        self.VertexCount = readUInt(bs)
        self.VertTechClassUNK3 = readUInt(bs)
        bs.seek(RET)

class DRBLClass:
    def __init__(self, bs):
        self.VertClassList = []
        self.VertTechList = []
        Add = bs.tell()
        self.UNK1 = readInt(bs)
        self.UNK2 = readUShort(bs)
        self.VMAP = readUShort(bs)
        self.LODCount = readUShort(bs)
        self.UNK4 = readUShort(bs)
        self.VertexCount = readUInt(bs)
        self.UNK6 = readUShort(bs)
        self.UNK6_1 = readUShort(bs)
        self.UNK7 = readUInt(bs)
        self.UNK8 = readUInt(bs)
        self.UNK9 = readUInt(bs)
        self.UNK10 = readUInt(bs)
        self.UNK11 = readUInt(bs)
        self.VertBlockCount = readUShort(bs)
        self.UNK13 = readUShort(bs)
        self.UNK14 = readUShort(bs)
        self.UNK15 = readUShort(bs)
        bs.seek(Add+self.UNK14)
        self.FaceCount = readUInt(bs)
        self.FaceCountShift = readUInt(bs)
        bs.seek(self.UNK13+Add)
        for Z in range(0, self.VertBlockCount):
            RET1 = bs.tell()
            self.VertClassList.append(DRBLVertClass(bs))
            RET2 = bs.tell()
            bs.seek(self.VertClassList[Z].VertClassUNK1+RET1)
            self.VertTechList.append(DRBLVertTechClass(bs))
            bs.seek(RET2)
            

class VBO:
     def __init__(self):
          self.ElmCount = int()
          self.ElmBuffer = int()
          self.ElmStride = int()
          self.ElmLayout = int()
          self.UNK = int()
          self.Bytes = list()

class MREFClass:
    def __init__(self):
        self.ShaderHash = int()
        self.ParamCount = int()
        pad = bytes()
        self.ParamSkip = int()

class INT0DGRPClass:
    def __init__(self) -> None:
        self.GroupCount = int()
        self.GroupCountStart = int()
        
#VOIDSOFS
# SOFS Count, CountStride
# UNKCount, Layout Count
# UNKCount2, Blank  

#VOIDPRMS Material Paramaters
# Paramater Count, Stride (40 Bytes)
# Paramater hash, Blah Balh Bullshit
        
    
def main():
    bs = LoadFile()
    bs.seek(16)
    DRBLIntList = []
    VBOList = []
    FuckList = []
    DGRPGroup = []
    STRGDGRPList = []
    STRGHIER = []
    while bs.tell() < getSize(bs):
        ID = bs.read(8)
        print(ID)
        Count = readUInt(bs)
        Size = readUInt(bs)
        End = bs.tell()+Size
        if ID == b'STRGDGRP':
            Count = readUInt64(bs)
            Pad = readUInt64(bs)
            bs.read(8*Count)
            for C in range(0, Count):
                STRGDGRPList.append(readString(bs))
                print(STRGDGRPList[C])
            bs.seek(End)
        elif ID == b'INT0DGRP':
            for C in range(0, Count):
                DGRPGroup.append(INT0DGRPClass())
                DGRPGroup[C].GroupCount = readUInt(bs)
                pad = bs.read(4)
                DGRPGroup[C].GroupCountStart = readUInt(bs)
                pad = bs.read(4)
                print(str(C), DGRPGroup[C].GroupCount, DGRPGroup[C].GroupCountStart)
            bs.seek(End)
        elif ID == b'INT0DRBL':
            for C in range(0, Count):
                DRBLIntList.append(DRBLINT())
                DRBLIntList[C].Index = readUInt(bs)
                DRBLIntList[C].Pad = bs.read(4)
                DRBLIntList[C].Offset = readUInt64(bs)
                print(DRBLIntList[C].Index, DRBLIntList[C].Offset)
            bs.seek(End)
        elif ID == b'VOIDSOFS':
            Fuck = readUInt64(bs)
            FuckStride = readUInt64(bs)
            for Z in range(0, Fuck):
                FuckList.append(readUInt64(bs))
            for N in range(0, FuckList[1]):
                VBOList.append(VBO())
            bs.seek(End)
        elif ID == b'CLAS_VBO':
            VBOCount = FuckList[1]
            CurVBOI = -1
            for Q in range(0, Count):
                CurVBOI += 1
                ElmCount = readUInt(bs)
                ElmBuffer = readUInt(bs)
                ElmStride = readUShort(bs)
                ElmLayout = readUShort(bs)
                UNK = readInt(bs)
                bs.seek(48, 1)
                VBOList[ElmLayout].ElmCount = ElmCount
                VBOList[ElmLayout].ElmBuffer = ElmBuffer
                VBOList[ElmLayout].ElmStride = ElmStride
                VBOList[ElmLayout].ElmLayout = ElmLayout
                VBOList[ElmLayout].UNK = UNK
            bs.seek(End)
        elif ID == b'VOIDDRBL':
            DRBL = bs.read(Size)
            bs.seek(End)
        elif ID == b'STRGTEXN':
            TEXN = []
            for T in range(0, Count):
                TEXN.append(readString(bs))
                print(str(T), TEXN[T])
            bs.seek(End)
        elif ID == b'VOIDHIER':
            VOIDHIER = []
            for M in range(0, Count):
                bs.read(64)
            for M in range(0, Count):
                bs.read(16)
            for M in range(0, Count):
                VOIDHIER.append(bs.read(1))
            print("VOID END", bs.tell())
            bs.seek(End)
        elif ID == b'STRGHIER':
            
            Count = readUInt64(bs)
            Blank = readUInt64(bs)
            bs.read(8*Count)
            print(bs.tell())
            for M in range(0, Count):
                STRGHIER.append(readString(bs))
            bs.seek(End)
        elif ID == b'INT0MREF':
            MREFList = []
            ShaderCount = []
            for M in range(0, Count):
                MREF = MREFClass()
                MREF.ShaderHash = ReturnShaderName(readUInt64(bs))
                if MREF.ShaderHash not in ShaderCount:
                    ShaderCount.append(MREF.ShaderHash)
                MREF.ParamCount = readUInt(bs)
                bs.read(4)
                MREF.ParamSkip = readUInt64(bs)
                MREFList.append(MREF)
            bs.seek(End)
        elif ID == b'VOIDPRMS':
            CountAgain = readUInt64(bs)
            fuck = readUInt64(bs)
            RET = bs.tell()
            for N in range(0, len(MREFList)):
                bs.seek(RET+MREFList[N].ParamSkip*40, 0)
                print("Material Number", str('%03d' % N), "ParamCount", MREFList[N].ParamCount, "Shader", MREFList[N].ShaderHash, bs.tell(), "--------------------------------")
                for NN in range(0, MREFList[N].ParamCount):
                    Move = bs.tell()+40
                    ParamHash = readUInt(bs)
                    Pad = bs.read(4)
                    if ParamHash == int(3587957853):
                        print('BaseColorTexture', TEXN[readUInt64(bs)])
                        readUInt64(bs)
                    elif ParamHash == int(446307371):
                        print('RoughnessTexture', TEXN[readUInt64(bs)])
                        readUInt64(bs)
                    elif ParamHash == int(914446448):
                        print('NormalTexture', TEXN[readUInt64(bs)])
                        readUInt64(bs)
                    elif ParamHash == int(1230949056):
                        TexID1 = readUInt64(bs)
                        TexID2 = readUInt64(bs)
                        Check = readUInt64(bs)
                        if Check == int(12514849900987264429):
                            print('EmissiveTexture', str("Null"))
                        elif Check == int(74565):
                            print('EmissiveTexture', TEXN[TexID1])
                    elif ParamHash == int(4175593205):
                        print('CavityTexture', TEXN[readUInt64(bs)])
                        readUInt64(bs)
                    elif ParamHash == int(215568845):
                        TexID1 = readUInt64(bs)
                        TexID2 = readUInt64(bs)
                        Check = readUInt64(bs)
                        if Check == int(12514849900987264429):
                            print('MetalnessTexture', "Null")
                        elif Check == int(74565):
                            print('MetalnessTexture', TEXN[TexID1])
                    elif ParamHash == int(2939592902):
                        print('LayerBaseColorTexture', TEXN[readUInt64(bs)])
                        readUInt64(bs)
                    elif ParamHash == int(4092909716):
                        print('LayerRoughnessTexture', TEXN[readUInt64(bs)])
                        readUInt64(bs)       
                    elif ParamHash == int(1642070157):
                        print('Texture0', TEXN[readUInt64(bs)])
                        readUInt64(bs)
                    elif ParamHash == int(1642070158):
                        print('Texture1', TEXN[readUInt64(bs)])
                        readUInt64(bs) 
                    elif ParamHash == int(1050113430):
                        print('LayerMaskTexture', TEXN[readUInt64(bs)])
                        readUInt64(bs)
                    elif ParamHash == int(2689292475):
                        TexID1 = readUInt64(bs)
                        TexID2 = readUInt64(bs)
                        Check = readUInt64(bs)
                        if Check == int(12514849900987264429):
                            pass
                        elif Check == int(74565):
                            print('LayerNormalTexture', TEXN[TexID1])
                    elif ParamHash == int(3862171190):
                        TexID1 = readUInt64(bs)
                        TexID2 = readUInt64(bs)
                        Check = readUInt64(bs)
                        if Check == int(12514849900987264429):
                            pass
                        elif Check == int(74565):
                            print('LayerMetalnessTexture', TEXN[TexID1])
                    elif ParamHash == int(1578719808):
                        print("EmissiveBaseColorMultiplier", str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)))
                    elif ParamHash == int(2991596545):
                        print("GammaDefogAlbedoBumpScale", str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)))
                    elif ParamHash == int(3084957816):
                        print("DirtColor", str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)))
                    elif ParamHash == int(2435778631):
                        print("HighlightColor", str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)))
                    elif ParamHash == int(1480436005):
                        print("MaxReflect", str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)))
                    elif ParamHash == int(1846334721):
                        print("FresnelReflectMipBiasDist", str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)))
                    elif ParamHash == int(1629137955):
                        print("GlassColor", str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)))
                    elif ParamHash == int(2861591377):
                        print("TextureXForm", str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)))
                    elif ParamHash == int(1802854312):
                        print("materialAlphaMultiplier", str(readFloat(bs)))
                        readFloat(bs)
                        readFloat(bs)
                        readFloat(bs)
                    elif ParamHash == int(1871041587):
                        print("instanced", str(readFloat(bs)))
                        readFloat(bs)
                        readFloat(bs)
                        readFloat(bs)
                    elif ParamHash == int(1961375049):
                        print("layer", str(readFloat(bs)))
                        readFloat(bs)
                        readFloat(bs)
                        readFloat(bs)
                    elif ParamHash == int(2449754611):
                        print("animated", str(readFloat(bs)))
                        readFloat(bs)
                        readFloat(bs)
                        readFloat(bs)
                    elif ParamHash == int(4095162411):
                        print("LayermaterialAlphaMultiplier", str(readFloat(bs)))
                        readFloat(bs)
                        readFloat(bs)
                        readFloat(bs)
                    elif ParamHash == int(3329228236):
                        print("EmissiveColor", str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)))
                    elif ParamHash == int(956843584):
                        print("materialColor", str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)),str(readFloat(bs)))
                    elif ParamHash == int(4135697372):
                        print("UseAlphaBlending", str(readFloat(bs)))
                        readFloat(bs)
                        readFloat(bs)
                        readFloat(bs)
                    elif ParamHash == int(2012471668):
                        print("EmissiveIntensity", str(readFloat(bs)))
                        readFloat(bs)
                        readFloat(bs)
                        readFloat(bs)
                    elif ParamHash == int(1530441199):
                        print("normalScale", str(readFloat(bs)))
                        readFloat(bs)
                        readFloat(bs)
                        readFloat(bs)
                    elif ParamHash == int(821046512):
                        print("CollisionType", str(readFloat(bs)))
                        readFloat(bs)
                        readFloat(bs)
                        readFloat(bs)
                    elif ParamHash == int(819023593):
                        print("UseEmissiveTexture", str(readFloat(bs)))
                        readFloat(bs)
                        readFloat(bs)
                        readFloat(bs)
                    elif ParamHash == int(3551900449):
                        print("EmissiveCategory", str(readFloat(bs)))
                        readFloat(bs)
                        readFloat(bs)
                        readFloat(bs)
                    elif ParamHash == int(1888208725):
                        print("lightmaps", str(readFloat(bs)))
                        readFloat(bs)
                        readFloat(bs)
                        readFloat(bs)
                    elif ParamHash == int(1642070159):
                        print('Texture2', TEXN[readUInt64(bs)])
                        readUInt64(bs)
                    else:
                        print("Unknown Hash", ParamHash, "at", bs.tell(), bs.read(4).hex(), bs.read(4).hex(), bs.read(4).hex(), bs.read(4).hex())
                    bs.seek(Move)
            bs.seek(End)
        else:
            bs.seek(Size, 1)
    print(len(ShaderCount))
    if len(STRGHIER) >= 1:
        for Q in range(0, len(STRGHIER)):
            print(VOIDHIER[Q], STRGHIER[Q])
    # w = open(sys.argv[1].split('.')[0]+".txt", 'w')
    # for Z in range(0, len(DRBLIntList)):
    #     DRBL.seek(DRBLIntList[Z].Offset, 0)
    #     I = DRBLIntList[Z].Index
    #     HH = DRBLClass(DRBL)
    #     H = HH.__dict__
    #     w.write(str('%03d' % I)+' ')
    #     for q in range(0, len(HH.VertClassList)):
    #                    w.write(str(HH.VertClassList[q].__dict__))
    #     for qq in range(0, len(HH.VertClassList)):
    #                    w.write(str(HH.VertTechList[qq].__dict__))
    #     w.write(str(H)+'\n')

    

main()