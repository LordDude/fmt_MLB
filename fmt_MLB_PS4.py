from inc_noesis import *
import rapi


def registerNoesisTypes():
   handle = noesis.register("MLB The Show 23_PS4", ".PS4")
   noesis.setHandlerTypeCheck(handle, noepyCheckType)
   noesis.setHandlerLoadModel(handle, noepyLoadModel)
   handle = noesis.register("MLB The Show 24_NSW", ".MOD")
   noesis.setHandlerTypeCheck(handle, noepyCheckType)
   noesis.setHandlerLoadModel(handle, noepyLoadModel)
   return 1


def noepyCheckType(data):
    bs = NoeBitStream(data)
    if bs.readBytes(8) == b'IFF0MODL':
        return 1
    else:
        return 0

def noepyLoadModel(data, mdlList):
    Skin = 1
    if noesis.optWasInvoked("-NoSkin"):
        Skin = 0
    ctx = rapi.rpgCreateContext()
    bs = NoeBitStream(data)
    Size = bs.getSize()
    bs.seek(16, NOESEEK_REL)
    Root = GetFromRoot(bs, Size)
    Add = 0
    if rapi.getInputName().split(".")[1] == "MOD":
        Add = rapi.checkFileExists(rapi.getInputName().split(".")[0]+str(".0.MOD"))
    elif rapi.getInputName().split(".")[1] == "PS4":
        Add = rapi.checkFileExists(rapi.getInputName().split(".")[0]+str(".0.PS4"))
    if Add:
        if rapi.getInputName().split(".")[1] == "MOD":
            Add = rapi.loadIntoByteArray(rapi.getInputName().split(".")[0]+str(".0.MOD"))
        elif rapi.getInputName().split(".")[1] == "PS4":
            Add = rapi.loadIntoByteArray(rapi.getInputName().split(".")[0]+str(".0.PS4"))
        Add = NoeBitStream(Add)
        print("Loaded Add")
        bs = Add
        bs.seek(16)
        Size = bs.getSize()
        DRBLList = Root.DRBLList
        VBOSetCount = Root.VBOSetCount
        VMap = Root.VMap
        EBOList = []
        Faces = []
        EBOSet = int(0)
        VBOSet = int(0)
        Layouts = []
        VBOBlockList = []
        VBOList = Root.VBOList
        OldType = 0
        print("VBOLISTCOUNT", len(VBOList))
        for L in range(0, len(Root.Layout)):
            LL = LayoutSet()
            LL.Type = bytes(Root.Layout[L], 'utf-8')
            Layouts.append(LL)
        while bs.tell() < Size:
            ID = bs.readBytes(8)
            BlockCount = bs.readUInt()
            BlockSize = bs.readUInt()
            End = bs.tell() + BlockSize
            if ID == b'CLAS_VBO':
                VBOList, Stuff = CLAS_VBOFunc(bs, BlockCount, End, VBOList)
                # print(Stuff)
            elif ID == b'CLAS_EBO':
                for N in range(0, BlockCount):
                    Check = bs.readInt()
                    if Check < 0:
                        E = EBOClass()
                        E.FaceType = bs.readUInt()
                        E.FaceCount = bs.readUInt()
                        bs.seek(108, NOESEEK_REL)
                        EBOList.append(E)
                        OldType = 0
                    else:
                        print("Weird EBO Class", bs.tell())
                        E = EBOClass()
                        E.FaceCount = bs.readUInt()
                        E.FaceType = bs.readUInt()
                        bs.seek(20, NOESEEK_REL)
                        EBOList.append(E)
                        OldType = 1
                bs.seek(End)
            elif ID == b'VOID_EBO':
                Lay = Layouts[EBOSet]
                Layouts[EBOSet] = VOID_EBOFunc(bs, EBOList[EBOSet], Lay)
                bs.seek(End)
                EBOSet += 1
            elif ID == b'VOID_VBO':
                # print("VBOSET Layout/Index", Stuff[VBOSet])
                VBOList[Stuff[VBOSet][0]] = VOID_VBOFunc(bs, BlockSize, VBOList[Stuff[VBOSet][0]], Stuff[VBOSet][1])
                # print("VBOByteCount", len(VBOList[Stuff[VBOSet][0]].BytesList))
                VBOSet += 1
                bs.seek(End)
            else:
                print("Unrecognized ID: " + str(ID) + " " + str(BlockCount) + " " + str(BlockSize))
                bs.readBytes(BlockSize)
        texList = []
        for VV in range(0, len(Root.DGRPGroup)):
            # rapi.rpgReset()
            GroupName = Root.STRGDGRPList[VV]
            GroupStart = Root.DGRPGroup[VV].GroupCountStart
            GroupCount = Root.DGRPGroup[VV].GroupCount
            Bytes1 = bytearray()
            Bytes2 = bytearray()
            Bytes3 = bytearray()
            Bytes4 = bytearray()
            Bytes5 = bytearray()
            Bytes6 = bytearray()
            Bytes7 = bytearray()
            Bytes8 = bytearray()
            Bytes9 = bytearray()
            for Z in range(0, GroupCount):
                V = GroupStart+Z
                D = DRBLList[V]
                # print(D.__dict__)
                CurSetIndex = VMap[D.VMAP]
                CurLayout = Layouts[CurSetIndex].Type
                normals = None
                print(V,"CurLayout_", CurLayout)
                Root.MaterialList[Z].name = GroupName+"_"+str('%03d' % V)+"_mat"
                rapi.rpgSetName(GroupName+"_"+str('%03d' % V+"_mesh"))
                rapi.rpgSetMaterial(GroupName+"_"+str('%03d' % V)+"_mat")
                if CurLayout == b'"POS_TF_N_UVMAP1_UVLIGHTMAP"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_FLOAT, 20, 0)
                    rapi.rpgBindColorBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 20, 16, 4)
                    rapi.rpgBindNormalBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 12, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_FLOAT, 12, 3, 2, 4)
                elif CurLayout == b'"POS_TF_N_UVMAP1_UVLAYER"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_FLOAT, 20, 0)
                    rapi.rpgBindColorBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 20, 16, 4)
                    rapi.rpgBindNormalBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 8, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 8, 1, 2, 4)
                elif CurLayout == b'"POS_TF_N_UVMAP1_UVLAYER_UVLIGHTMAP"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_FLOAT, 20, 0)
                    rapi.rpgBindColorBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 20, 16, 4)
                    rapi.rpgBindNormalBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 16, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 16, 1, 2, 4)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_FLOAT, 16, 3, 2, 8)
                elif CurLayout == b'"POS_TF_N_UVMAP1_UVLAYER_UVMASK_UVLIGHTMAP"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_FLOAT, 20, 0)
                    rapi.rpgBindColorBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 20, 16, 4)
                    rapi.rpgBindNormalBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 20, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 20, 1, 2, 4)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 20, 3, 2, 8)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_FLOAT, 20, 2, 2, 12)
                elif CurLayout ==  b'"POS_2UV_N"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_FLOAT, 16, 0)
                    rapi.rpgBindNormalBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 8, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 12, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_FLOAT, 12, 3, 2, 4)
                elif CurLayout ==  b'"POS_2UV_TAN_N"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_FLOAT, 16, 0)
                    rapi.rpgBindNormalBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 12, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_FLOAT, 12, 3, 2, 4)
                elif CurLayout ==  b'"Simple_Pos_UV"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_FLOAT, 28, 0)
                    rapi.rpgBindNormalBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 28, 16)
                    rapi.rpgBindUVXBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 28, 0, 2, 24)
                elif CurLayout ==  b'"POS_3UV_N"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_FLOAT, 16, 0)
                    rapi.rpgBindNormalBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 8, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 16, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 16, 1, 2, 4)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_FLOAT, 16, 3, 2, 8)
                elif CurLayout ==  b'"POS_3UV_TAN_N"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_FLOAT, 16, 0)
                    rapi.rpgBindNormalBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 16, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 16, 1, 2, 4)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_FLOAT, 16, 2, 2, 8)
                elif CurLayout ==  b'"Bat"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 8, 0)
                    normals = bytearray()
                    for Q in range(0, D.VertexCount):
                        normals+= Bytes2[Q*8+0:Q*8+0+4]
                    norm = rapi.decodeNormals32(normals, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                    rapi.rpgBindNormalBuffer(norm, noesis.RPGEODATA_FLOAT, 12)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 8, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 8, 1, 2, 4)
                elif CurLayout ==  b'"Simple_Pos"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_FLOAT, 16, 0)
                elif CurLayout ==  b'"Cloth"':
                    if OldType:
                        Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                        Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                        rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                        rapi.rpgBindNormalBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 28, 0)
                        rapi.rpgBindUVXBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 28, 0, 2, 8)
                    else:
                        Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                        Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                        Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                        rapi.rpgBindBoneWeightBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 16, 4, 4)
                        rapi.rpgBindBoneIndexBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 16, 0, 4)
                        rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                        normals = bytearray()
                        for Q in range(0, D.VertexCount):
                            normals+= Bytes2[Q*12+0:Q*12+0+4]
                        norm = rapi.decodeNormals32(normals, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                        rapi.rpgBindNormalBuffer(norm, noesis.RPGEODATA_FLOAT, 12)
                        rapi.rpgBindUVXBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 12, 0, 2, 8)
                elif CurLayout ==  b'"SkinnedAndDecals"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindBoneWeightBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 16, 4, 4)
                    rapi.rpgBindBoneIndexBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 16, 0, 4)
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    normals = bytearray()
                    for Q in range(0, D.VertexCount):
                        normals+= Bytes2[Q*8+0:Q*8+0+4]
                    norm = rapi.decodeNormals32(normals, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                    rapi.rpgBindNormalBuffer(norm, noesis.RPGEODATA_FLOAT, 12)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 8, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 8, 1, 2, 4)
                elif CurLayout == b'"SimpleLitSkinned"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    rapi.rpgBindBoneWeightBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 16, 4, 4)
                    rapi.rpgBindBoneIndexBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 16, 0, 4)
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    normals = bytearray()
                    for Q in range(0, D.VertexCount):
                        normals+= Bytes2[Q*12+0:Q*12+0+4]
                    norm = rapi.decodeNormals32(normals, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                    rapi.rpgBindNormalBuffer(norm, noesis.RPGEODATA_FLOAT, 12)
                    rapi.rpgBindUVXBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 12, 0, 2, 0)
                    rapi.rpgBindColorBufferOfs(Bytes2, noesis.RPGEODATA_UBYTE, 12, 8, 4)
                elif CurLayout ==  b'"Jersey"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindBoneWeightBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 16, 4, 4)
                    rapi.rpgBindBoneIndexBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 16, 0, 4)
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    normals = bytearray()
                    for Q in range(0, D.VertexCount):
                        normals+= Bytes2[Q*20+0:Q*20+0+4]
                    norm = rapi.decodeNormals32(normals, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                    rapi.rpgBindNormalBuffer(norm, noesis.RPGEODATA_FLOAT, 12)
                    rapi.rpgBindUVXBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 20, 0, 2, 8)
                    rapi.rpgBindUVXBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 20, 1, 2, 12)
                    rapi.rpgBindUVXBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 20, 2, 2, 16)
                elif CurLayout ==  b'"Head"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    Bytes4 = VBOList[VMap[D.VMAP]].BytesList[3][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindBoneWeightBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 8, 4, 4)
                    rapi.rpgBindBoneIndexBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 8, 0, 4)
                    rapi.rpgBindPositionBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 8, 0)
                    normals = bytearray()
                    for Q in range(0, D.VertexCount):
                        normals+= Bytes3[Q*4+0:Q*4+0+4]
                    norm = rapi.decodeNormals32(normals, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                    rapi.rpgBindNormalBuffer(norm, noesis.RPGEODATA_FLOAT, 12)
                    rapi.rpgBindUVXBufferOfs(Bytes4, noesis.RPGEODATA_USHORT, 12, 0, 2, 4)
                    rapi.rpgBindUVXBufferOfs(Bytes4, noesis.RPGEODATA_USHORT, 12, 1, 2, 8)
                elif CurLayout ==   b'"ClothVPosF32"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_FLOAT, 20, 8)
                    normals = bytearray()
                    for Q in range(0, D.VertexCount):
                        normals+= Bytes2[Q*12+0:Q*12+0+4]
                    norm = rapi.decodeNormals32(normals, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                    rapi.rpgBindNormalBuffer(norm, noesis.RPGEODATA_FLOAT, 12)
                    rapi.rpgBindUVXBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 12, 0, 2, 8)
                elif CurLayout ==   b'"BumpRigid"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 8, 0)
                    normals = bytearray()
                    for Q in range(0, D.VertexCount):
                        normals+= Bytes2[Q*12+0:Q*12+0+4]
                    norm = rapi.decodeNormals32(normals, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                    rapi.rpgBindNormalBuffer(norm, noesis.RPGEODATA_FLOAT, 12)
                    rapi.rpgBindUVXBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 12, 0, 2, 8)
                elif CurLayout == b'"Crowd_Static"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 20, 0)
                    normals = bytearray()
                    UV = bytearray()
                    for Q in range(0, D.VertexCount):
                        normals+= Bytes1[Q*20+8:Q*20+8+4]
                    # for K in range(0, D.VertexCount):
                    #     UV += Bytes1[K*20+16:K*20+16+4]
                    norm = rapi.decodeNormals32(normals, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                    rapi.rpgBindNormalBuffer(norm, noesis.RPGEODATA_FLOAT, 12)
                    rapi.rpgBindUVXBufferOfs(Bytes1, noesis.RPGEODATA_SHORT, 20, 0, 2, 16)
                elif CurLayout == b'"POS_SW_TF_N_UVMAP1_UVLIGHTMAP"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_FLOAT, 28, 0)
                    rapi.rpgBindColorBufferOfs(Bytes1, noesis.RPGEODATA_UBYTE, 28, 24, 4)
                    rapi.rpgBindNormalBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 12, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_FLOAT, 12, 2, 2, 8)
                elif CurLayout == b'"ClothAndDecals"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    normals = bytearray()
                    for Q in range(0, D.VertexCount):
                        normals+= Bytes1[Q*16+0:Q*16+0+4]
                    norm = rapi.decodeNormals32(normals, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                    rapi.rpgBindUVXBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 16, 0, 2, 8)
                    rapi.rpgBindUVXBufferOfs(Bytes2, noesis.RPGEODATA_HALFFLOAT, 16, 1, 2, 12)
                elif CurLayout == b'"AccLayeredSkinned"' or CurLayout ==  b'"Shoes"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    normals = bytearray()
                    for Q in range(0, D.VertexCount):
                        normals+= Bytes1[Q*16+0:Q*16+0+4]
                    norm = rapi.decodeNormals32(normals, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 8, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 8, 1, 2, 4)
                elif CurLayout ==  b'"BatGlove"':
                    Bytes1 = VBOList[VMap[D.VMAP]].BytesList[0][D.VertTechList[0].VertBlockSkip:]
                    Bytes2 = VBOList[VMap[D.VMAP]].BytesList[1][D.VertTechList[1].VertBlockSkip:]
                    Bytes3 = VBOList[VMap[D.VMAP]].BytesList[2][D.VertTechList[2].VertBlockSkip:]

                    Bytes4 = VBOList[VMap[D.VMAP]].BytesList[3][D.VertTechList[2].VertBlockSkip:]
                    Bytes5 = VBOList[VMap[D.VMAP]].BytesList[4][D.VertTechList[2].VertBlockSkip:]
                    Bytes6 = VBOList[VMap[D.VMAP]].BytesList[5][D.VertTechList[2].VertBlockSkip:]
                    Bytes7 = VBOList[VMap[D.VMAP]].BytesList[6][D.VertTechList[2].VertBlockSkip:]
                    Bytes8 = VBOList[VMap[D.VMAP]].BytesList[7][D.VertTechList[2].VertBlockSkip:]
                    rapi.rpgBindPositionBufferOfs(Bytes1, noesis.RPGEODATA_HALFFLOAT, 16, 8)
                    normals = bytearray()
                    for Q in range(0, D.VertexCount):
                        normals+= Bytes2[Q*16+0:Q*16+0+4]
                    norm = rapi.decodeNormals32(normals, 4, -10, -10, -10, NOE_LITTLEENDIAN)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 16, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 16, 1, 2, 4)
                    rapi.rpgBindUVXBufferOfs(Bytes3, noesis.RPGEODATA_HALFFLOAT, 16, 2, 2, 4)

                    rapi.rpgBindUVXBufferOfs(Bytes4, noesis.RPGEODATA_HALFFLOAT, 16, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes4, noesis.RPGEODATA_HALFFLOAT, 16, 1, 2, 4)
                    rapi.rpgBindUVXBufferOfs(Bytes4, noesis.RPGEODATA_HALFFLOAT, 16, 2, 2, 4)

                    rapi.rpgBindUVXBufferOfs(Bytes5, noesis.RPGEODATA_HALFFLOAT, 16, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes5, noesis.RPGEODATA_HALFFLOAT, 16, 1, 2, 4)
                    rapi.rpgBindUVXBufferOfs(Bytes5, noesis.RPGEODATA_HALFFLOAT, 16, 2, 2, 4)

                    rapi.rpgBindUVXBufferOfs(Bytes6, noesis.RPGEODATA_HALFFLOAT, 16, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes6, noesis.RPGEODATA_HALFFLOAT, 16, 1, 2, 4)
                    rapi.rpgBindUVXBufferOfs(Bytes6, noesis.RPGEODATA_HALFFLOAT, 16, 2, 2, 4)

                    rapi.rpgBindUVXBufferOfs(Bytes7, noesis.RPGEODATA_HALFFLOAT, 16, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes7, noesis.RPGEODATA_HALFFLOAT, 16, 1, 2, 4)
                    rapi.rpgBindUVXBufferOfs(Bytes7, noesis.RPGEODATA_HALFFLOAT, 16, 2, 2, 4)

                    rapi.rpgBindUVXBufferOfs(Bytes8, noesis.RPGEODATA_HALFFLOAT, 16, 0, 2, 0)
                    rapi.rpgBindUVXBufferOfs(Bytes8, noesis.RPGEODATA_HALFFLOAT, 16, 1, 2, 4)
                    rapi.rpgBindUVXBufferOfs(Bytes8, noesis.RPGEODATA_HALFFLOAT, 16, 2, 2, 4)
                else:
                    raise ValueError("Unknown Layout: " + str(CurLayout))
                if Layouts[CurSetIndex].FaceType == 2:
                    rapi.rpgCommitTriangles(Layouts[CurSetIndex].Faces[D.FaceCountShift*Layouts[CurSetIndex].FaceType:], noesis.RPGEODATA_USHORT, D.FaceCount, noesis.RPGEO_TRIANGLE, 1)
                elif Layouts[CurSetIndex].FaceType == 4:
                    rapi.rpgCommitTriangles(Layouts[CurSetIndex].Faces[D.FaceCountShift*Layouts[CurSetIndex].FaceType:], noesis.RPGEODATA_UINT, D.FaceCount, noesis.RPGEO_TRIANGLE, 1)
                rapi.rpgClearBufferBinds()
                # rapi.rpgCommitTriangles(None, noesis.RPGEODATA_UINT, D.VertexCount, noesis.RPGEO_POINTS)
        mdl = rapi.rpgConstructModel()
        if Root.BoneList:
            mdl.setBones(Root.BoneList)
            # mdl.setBones(rapi.multiplyBones(Root.BoneList))
        mdl.setModelMaterials(NoeModelMaterials(Root.TEXN, Root.MaterialList))
        mdlList.append(mdl) 
    else:
        return 0            


    #BULLSHIT
 
    # rapi.rpgCommitTriangles(None, noesis.RPGEODATA_UINT, VC, noesis.RPGEO_POINTS)




        
    # mdl = NoeModel()
    # mdl.setBones(BoneList)
    return 1

class EBOClass:
    def __init__(self) -> None:
        self.UNK = int()
        self.FaceType = int()
        self.FaceCount = int()

class EBO:
    def __init__(self) -> None:
        self.FaceCount = int()
        self.Faces = bytes()

class VBO:
    def __init__(self) -> None:
        self.ElmCount = int()
        self.Index = int()
        self.Stride = int()
        self.Layout = int()
        self.UNK = int()
        self.BytesList = []

class MREFClass:
    def __init__(self):
        self.ShaderHash = int()
        self.ParamCount = int()
        pad = bytes()
        self.ParamSkip = int()

class LayoutSet:
    def __init__(self) -> None:
        self.Type = str()
        self.Position = bytes()
        self.Norm = bytes()
        self.UV = bytes()
        self.Faces = bytes()
        self.FaceType = int()
        self.FaceCount = int()
        self.VertCount = int()

def VOID_VBOFunc(bs:NoeBitStream, Size:int, VBOList:VBO, LayoutIndex:int):
    VBOList.BytesList.append(bs.readBytes(Size))
    return VBOList

def VOID_EBOFunc(bs:NoeBitStream, EBO:EBOClass, F:LayoutSet):
    Type = 0
    print("Faces For" + str(F.Type))
    if EBO.FaceType == 0:
        F.FaceType = 2
        print("Faces Short")
    elif EBO.FaceType == 1:
        F.FaceType = 4
        print("Faces Int")
    F.FaceCount = EBO.FaceCount
    F.Faces = bs.readBytes(EBO.FaceCount*F.FaceType)
    return F

def CLAS_VBOFunc(bs:NoeBitStream, Count:int, End:int, VBOList:list):
    Stuff = []
    for Z in range(0, Count):
        ElmCount = bs.readUInt()
        Index = bs.readUInt()
        Stride = bs.readUShort()
        Layout = bs.readUShort()
        UNK = bs.readUInt()
        Zero = bs.readBytes(48)
        VBOList[Layout].ElmCount = ElmCount
        VBOList[Layout].Index = Index
        VBOList[Layout].Stride = Stride
        VBOList[Layout].Layout = Layout
        VBOList[Layout].UNK = UNK
        Stuff.append([Layout, Index])
    bs.seek(End, NOESEEK_ABS)
    return VBOList, Stuff

class VOIDSOFSClass:
    def __init__(self) -> None:
        self.UNK1 = []

class RootClass:
    def __init__(self) -> None:
        self.BoneList = []
        self.BoneNames = []
        self.TEXN = []
        self.VBOSetCount = int()
        self.VMap = []
        self.Root = []
        self.DRBLList = []
        self.Layout = []
        self.VBOList = []
        self.STRGDGRPList = []
        self.DGRPGroup = []
        self.MaterialList = []

class INT0DGRPClass:
    def __init__(self) -> None:
        self.GroupCount = int()
        self.GroupCountStart = int()

def GetFromRoot(bs:NoeBitStream, Size:int):
    BoneList = []
    TextureList = []
    VBOSetCount = 0
    VMap = []
    Root = RootClass()
    VBOList = []
    DRBLList = []
    while bs.tell() < Size:
        ID = bs.readBytes(8)
        BlockCount = bs.readUInt()
        BlockSize = bs.readUInt()
        # print(ID, bs.tell())
        End = bs.tell() + BlockSize
        if ID == b'VOIDSOFS':
            End = bs.tell() + BlockSize
            FuckList = []
            Fuck = bs.readUInt64()
            FuckStride = bs.readUInt64()
            for Z in range(0, Fuck):
                FuckList.append(bs.readUInt64())
            print(FuckList)
            if len(FuckList) == 1:
                Root.VBOList.append(VBO())
            else:
                for N in range(0, FuckList[1]):
                    Root.VBOList.append(VBO())
            bs.seek(End)
        elif ID == b'CLAS_VBO':
            CLAS_VBO = bs.readBytes(BlockSize)
        elif ID == b'CLAS_EBO':
            CLAS_EBO = bs.readBytes(BlockSize)
        elif ID == b'STRGINLA':
            STRGINLA = NoeBitStream(bs.readBytes(BlockSize))
            LayoutCount = STRGINLA.readUInt()
            STRGINLA.seek(12, NOESEEK_REL)
            STRGINLA.seek(8* LayoutCount, NOESEEK_REL)
            for Z in range(0, LayoutCount):
                Hold = STRGINLA.readString().splitlines()[0].split('=')[1].rstrip('>')
                Root.Layout.append(Hold)
            # print("Layouts", Root.Layout)
        elif ID == b'VOIDDNFO':
            VOIDDNFO = bs.readBytes(BlockSize)
        elif ID == b'VOIDDFLG':
            VOIDDFLG = bs.readBytes(BlockSize)
        elif ID == b'VOIDVMAP':
            Count = bs.readUInt64()
            UNK = bs.readUInt64()
            for B in range(0, Count):
                Root.VMap.append(bs.readUInt64())
            bs.seek(End)
        elif ID == b'STRGTEXN':
            Grey = bytes.fromhex('7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF7F7F7FFF')
            GreyDummy = rapi.imageDecodeRaw(Grey,int(4),int(4),"r8g8b8a8")
            TexNames = []
            for T in range(0, BlockCount):
                TexNames.append(bs.readString())
                Root.TEXN.append(NoeTexture(TexNames[T], int(4), int(4), GreyDummy, noesis.NOESISTEX_RGBA32))
                print(str(T), Root.TEXN[T].name)
            bs.seek(End)
        elif ID == b'SPHRNONE':
            SPHRNONE = bs.readBytes(BlockSize)
        elif ID == b'INT0TEXL':
            INT0TEXL = bs.readBytes(BlockSize)
        elif ID == b'INT0MREF':
            MREFList = []
            for M in range(0, BlockCount):
                MREF = MREFClass()
                MREF.ShaderHash = bs.readUInt64()
                MREF.ParamCount = bs.readUInt()
                bs.readBytes(4)
                MREF.ParamSkip = bs.readUInt64()
                MREFList.append(MREF)
            bs.seek(End)
        elif ID == b'VOIDPRMS':
            CountAgain = bs.readUInt64()
            fuck = bs.readUInt64()
            RET = bs.tell()
            for N in range(0, len(MREFList)):
                bs.seek(RET+MREFList[N].ParamSkip*40, 0)
                Material = NoeMaterial("Material_"+str(N), None)
                for NN in range(0, MREFList[N].ParamCount):
                    Move = bs.tell()+40
                    ParamHash = bs.readUInt()
                    Pad = bs.readBytes(4)
                    if ParamHash == int(3587957853):
                        Material.setTexture(Root.TEXN[bs.readUInt64()].name)
                        bs.readUInt64()
                    elif ParamHash == int(446307371):
                        Root.TEXN[bs.readUInt64()]
                        bs.readUInt64()
                    elif ParamHash == int(914446448):
                        Material.setNormalTexture(Root.TEXN[bs.readUInt64()].name)
                        bs.readUInt64()
                    elif ParamHash == int(1230949056):
                        TexID1 = bs.readUInt64()
                        TexID2 = bs.readUInt64()
                        Check = bs.readUInt64()
                    elif ParamHash == int(4175593205):
                        TexID1 = bs.readUInt64()
                        TexID2 = bs.readUInt64()
                        Check = bs.readUInt64()
                        if Check == int(12514849900987264429):
                            pass
                        elif Check == int(74565):
                            Material.setOcclTexture(Root.TEXN[bs.readUInt64()].name)
                    elif ParamHash == int(215568845):
                        TexID1 = bs.readUInt64()
                        TexID2 = bs.readUInt64()
                        Check = bs.readUInt64()
                    elif ParamHash == int(2939592902):
                        Root.TEXN[bs.readUInt64()]
                        bs.readUInt64()
                    elif ParamHash == int(4092909716):
                        Root.TEXN[bs.readUInt64()]
                        bs.readUInt64()       
                    elif ParamHash == int(1642070157):
                        Material.setTexture(Root.TEXN[bs.readUInt64()].name)
                        bs.readUInt64()
                    elif ParamHash == int(1642070158):
                        Root.TEXN[bs.readUInt64()]
                        bs.readUInt64() 
                    elif ParamHash == int(1050113430):
                        Root.TEXN[bs.readUInt64()]
                        bs.readUInt64()
                    elif ParamHash == int(2689292475):
                        TexID1 = bs.readUInt64()
                        TexID2 = bs.readUInt64()
                        Check = bs.readUInt64()
                    elif ParamHash == int(3862171190):
                        TexID1 = bs.readUInt64()
                        TexID2 = bs.readUInt64()
                        Check = bs.readUInt64()
                    bs.seek(Move)
                Root.MaterialList.append(Material)
            bs.seek(End)
        elif ID == b'STRGDGRP':
            Count = bs.readUInt64()
            Pad = bs.readUInt64()
            bs.readBytes(8*Count)
            # print("String Group")
            for C in range(0, Count):
                Root.STRGDGRPList.append(bs.readString())
                print(Root.STRGDGRPList[C])
            bs.seek(End)
        elif ID == b'INT0DGRP':
            # print("INT0DGRP", BlockCount)
            for C in range(0, BlockCount):
                Root.DGRPGroup.append(INT0DGRPClass())
                Root.DGRPGroup[C].GroupCount = bs.readUInt()
                pad = bs.readBytes(4)
                Root.DGRPGroup[C].GroupCountStart = bs.readUInt()
                pad = bs.readBytes(4)
                # print(str(C), Root.DGRPGroup[C].GroupCount, Root.DGRPGroup[C].GroupCountStart)
            bs.seek(End)
        elif ID == b'INT0DRBL':
            DRBLList = GetINT0DRBL(bs, BlockCount, BlockSize)
        elif ID == b'VOIDDRBL':
            End = bs.tell() + BlockSize
            Root.DRBLList = GetVOIDDRBL(bs, DRBLList)
            bs.seek(End)
        elif ID == b'VOIDHIER': #Bones?
            VOIDHIER = NoeBitStream(bs.readBytes(BlockSize))
            BoneList = []
            UNKList = []
            Parents = []
            Bone = []
            Parent = int(-2)
            HOLD = []
            Stored = int(-2)
            Returned = 0
            Return = 0
            for Z in range(0, BlockCount):
                Bone.append(NoeMat44.fromBytes(VOIDHIER.readBytes(64)).toMat43().inverse())
            for N in range(0, BlockCount):
                UNKList.append(NoeVec4.fromBytes(VOIDHIER.readBytes(16)))
            for M in range(0, BlockCount):
                Test = VOIDHIER.readByte()
                # print(M, Test, HOLD)
                Stored += 1
                Parent += 1
                if Returned:
                    Stored = Return
                    Returned = 0
                if Test == 0:
                    Parents.append(Stored)
                elif Test == 1:
                    HOLD.append(Stored)
                    Parents.append(Stored)
                elif Test == 2:
                    Parents.append(Stored)
                    if len(HOLD) <= 0:
                        pass
                    else:
                        Returned = 1
                        Return = HOLD.pop()
                elif Test == 3:
                    Returned = 1
                    Return = Parents[M-1]
                    Parents.append(Parents[M-1])
                else:
                    print("FUCK Parent fuckery", Test)
                Stored = Parent

            # print(Parents)
            for L in range(0, BlockCount):
                Root.BoneList.append(NoeBone(L, "Bone"+str(L), Bone[L], None, Parents[L]))
            # Root.BoneList = rapi.multiplyBones(BoneList)
            bs.seek(End)
        elif ID == b'STRGHIER':
            Count = bs.readUInt64()
            Blank = bs.readBytes(8)
            Blank = bs.readBytes(8*Count)
            for Z in range(0, Count):
                Root.BoneNames.append(bs.readString())
            for F in range(0, len(Root.BoneList)):
                Root.BoneList[F].name = Root.BoneNames[F]
            bs.seek(End)
        elif ID == b'NURBVOID':
            NURBVOID = bs.readBytes(BlockSize)
        else:
            print("Unrecognized ID: " + str(ID) + " " + str(BlockCount) + " " + str(BlockSize))
            bs.readBytes(BlockSize)
    return Root


class DRBLVertClass:
    def __init__(self, bs:NoeBitStream) -> None:
        self.Blank = bs.readInt()
        self.VertCountSkip = bs.readUInt()
        self.UNK1 = bs.readUInt()
        self.UNK2 = bs.readUInt()
        self.UNK3 = bs.readUInt64()

class DRBLVertTechClass:
    def __init__(self, bs:NoeBitStream) -> None:
        RET = bs.tell()
        self.VertBlockSkip = bs.readUInt()
        self.UNK = bs.readUInt()
        self.UNK1_1 = bs.readUShort()
        self.UNK1_2 = bs.readUShort()
        self.UNK2 = bs.readUInt64()
        bs.seek(RET+self.UNK)
        self.VertexCount = bs.readUInt()
        self.UNK3 = bs.readUInt()
        bs.seek(RET)

class DRBLClass:
    def __init__(self, bs:NoeBitStream):
        self.VertClassList = []
        self.VertTechList = []
        Add = bs.tell()
        self.UNK1 = bs.readInt()
        self.UNK2 = bs.readUShort()
        self.VMAP = bs.readUShort()
        self.UNK4 = bs.readUInt()
        self.VertexCount = bs.readUInt()
        self.UNK6 = bs.readUShort()
        self.UNK6_1 = bs.readUShort()
        self.UNK7 = bs.readUInt()
        self.UNK8 = bs.readUInt()
        self.UNK9 = bs.readUInt()
        self.UNK10 = bs.readUInt()
        self.UNK11 = bs.readUInt()
        self.VertBlockCount = bs.readUShort()
        self.UNK13 = bs.readUShort()
        self.UNK14 = bs.readUShort()
        self.UNK15 = bs.readUShort()
        bs.seek(Add+self.UNK14)
        self.FaceCount = bs.readUInt()
        self.FaceCountShift = bs.readUInt()
        bs.seek(self.UNK13+Add)
        for Z in range(0, self.VertBlockCount):
            RET1 = bs.tell()
            self.VertClassList.append(DRBLVertClass(bs))
            RET2 = bs.tell()
            bs.seek(self.VertClassList[Z].UNK1+RET1)
            self.VertTechList.append(DRBLVertTechClass(bs))
            bs.seek(RET2)

class INT0DRBLClass:
    def __init__(self) -> None:
        self.Index = int()
        self.Offset = int()

def GetINT0DRBL(bs:NoeBitStream, BlockCount:int, BlockSize:int):
    DRBLList = []
    End = bs.tell() + BlockSize
    for Z in range(0, BlockCount):
        D = INT0DRBLClass()
        D.Index = bs.readUInt()
        Pad = bs.readBytes(4)
        D.Offset = bs.readUInt64()
        DRBLList.append(D)
        # print(D.__dict__)
    bs.seek(End)
    return DRBLList

def GetVOIDDRBL(DRBL:NoeBitStream, DRBLIntList:list):
    DRBLList = []
    Ret = DRBL.tell()
    for Z in range(0, len(DRBLIntList)):
        DRBL.seek(Ret+DRBLIntList[Z].Offset, 0)
        DRBLList.append(DRBLClass(DRBL))
    return DRBLList






