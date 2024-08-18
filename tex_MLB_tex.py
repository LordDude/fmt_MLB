from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("MLB The Show 23_PS4", ".tex")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    handle = noesis.register("MLB The Show 24_NSW", ".tex")
    noesis.setHandlerTypeCheck(handle, noepyCheckType_24NSW)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA_24NSW)
    #noesis.logPopup()
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    if bs.readBytes(8) == b'IFF0TX00':
        return 1
    else:
        return 0
def noepyCheckType_24NSW(data):
    bs = NoeBitStream(data)
    if bs.readBytes(8) == b'TXSTNSW\x00':
        return 1
    else:
        return 0
    
def getTextureFormat(format):
    bpp = 8
    switchbpp = 16
    if format == 2:
        return "r8g8b8a8", 2, "r8g8b8a8", switchbpp
    elif format == 6:
        return noesis.FOURCC_DXT3, bpp, "DXT3", switchbpp
    elif format == 7:
        return noesis.FOURCC_DXT5, bpp, "DXT5", switchbpp
    elif format == 13:
        return noesis.FOURCC_DXT1, 4, "DXT1", 8
    elif format == 14:
        print("UNCERTAIN FORMAT")
        return "r8g8b8a8", bpp, "r8g8b8a8", switchbpp
    elif format == 19:
        return noesis.FOURCC_BC4, 4, "BC4", switchbpp
    elif format == 21:
        return noesis.FOURCC_BC6H, bpp, "BC6H", switchbpp
    elif format == 22:
        return noesis.FOURCC_BC7, bpp, "BC7", switchbpp
    else:
        raise(ValueError("Unsupported Texture format: " + str(format)))

def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    bs.seek(16)
    size = bs.getSize()
    Platform = bs.readBytes(4)
    if Platform != b'PS4\x00':
        raise(ValueError("Unsupported platform type: " + Platform))
    TextureCount = bs.readUInt64()
    UNKMIP = bs.readUInt()
    CompressionAt = size - bs.readUInt()
    UncompressTotal = bs.readUInt()
    Hash = bs.readBytes(8)
    for Z in range(0, TextureCount):
        TexName = bs.readBytes(64).decode("ASCII").rstrip("\0")
        print(TexName)
        TexHash = bs.readBytes(16)
        TexCompSize = bs.readUInt()
        TexCompAdd = bs.readUInt()
        TexUnCompUNK = bs.readUInt()
        TexUnCompSize = bs.readUInt()
        bs.seek(16, NOESEEK_REL)
        width,height = bs.readUShort(),bs.readShort()
        UNK2 = bs.readUInt()
        Type, bpp, TypeName, switchbpp = getTextureFormat(bs.readUShort())
        bs.seek(38, NOESEEK_REL)
        ret = bs.tell()
        bs.seek(CompressionAt+TexCompAdd, NOESEEK_ABS)
        print(bs.tell(), TypeName)
        textureData = bs.readBytes(TexCompSize)
        if TexCompSize != TexUnCompSize:
            textureData = rapi.decompLZ4(textureData, TexUnCompSize)
        
        if type(Type) == int:
            textureData = rapi.callExtensionMethod("untile_1dthin", textureData, width,height, bpp, 1)
            textureData = rapi.imageDecodeDXT(textureData,width,height,Type)
        else:
            textureData = rapi.callExtensionMethod("untile_1dthin", textureData, width,height, bpp, 0)
            textureData = rapi.imageDecodeRaw(textureData,width,height,Type)
        texList.append(NoeTexture(TexName, width, height, textureData, noesis.NOESISTEX_RGBA32))
        bs.seek(ret, NOESEEK_ABS)

    return 1

def noepyLoadRGBA_24NSW(data, texList):
    bs = NoeBitStream(data)
    bs.seek(12)
    size = bs.getSize()
    CompressionAt = size - bs.readUInt()
    UncompressSize = bs.readUInt()
    TextureCount = bs.readUInt()
    MIPCount = bs.readUInt64()
    Hash = bs.readBytes(8)
    Blank = bs.readBytes(8)
    TexNames = []
    TexSizes = []
    TexDimensions = []
    MIPCounts = []
    for Z in range(0, TextureCount):
        TexName = bs.readBytes(64).decode("ASCII").rstrip("\0")
        print(TexName)
        TexNames.append(TexName)
        bs.seek(43, NOESEEK_REL)
        MIPCounts.append(bs.readUInt())
        bs.seek(57, NOESEEK_REL)
        TexOffsetAdd = bs.readUInt()
        TexUncompressed = bs.readUInt()
        TexSize = bs.readUInt()
        TexSizes.append([TexOffsetAdd, TexUncompressed, TexSize])
        UNK = bs.readUInt()
        Blakn = bs.readUInt()
        Type, bpp, TypeName, switchbpp = getTextureFormat(bs.readUShort())
        width,height = bs.readUShort(),bs.readShort()
        UNKS1, UNKS2 = bs.readUShort(),bs.readUShort()
        TexDimensions.append([width, height, UNKS1, UNKS2])
        bs.seek(10, NOESEEK_REL)
        ret = bs.tell()
        bs.seek(CompressionAt+TexSizes[Z][0], NOESEEK_ABS)
        print(bs.tell(), TypeName)
        textureData = bs.readBytes(TexSizes[Z][2])
        if TexSizes[Z][2] != TexSizes[Z][1]:
            textureData = rapi.decompLZ4(textureData, TexSizes[Z][1])
        
        if type(Type) == int:
            blockWidth = blockHeight = 4
            blockSize = switchbpp
            WidthInBlocks = (TexDimensions[Z][0] + (blockWidth - 1)) // blockWidth
            HeightInBlocks = (TexDimensions[Z][1] + (blockHeight - 1)) // blockHeight
            mbH = 4 
            if TexDimensions[Z][0] < 512:
                mbH = 3
            if TexDimensions[Z][1] < 256:
                mbH = 2
            # maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", TexDimensions[Z][1])
            pix = textureData
            pix = rapi.callExtensionMethod("untile_blocklineargob", textureData, WidthInBlocks, HeightInBlocks, blockSize)
            pix = rapi.imageDecodeDXT(pix, TexDimensions[Z][0], TexDimensions[Z][1], Type)
        else:
            pix = rapi.callExtensionMethod("untile_1dthin", textureData, width,height, bpp, 0)
            pix = rapi.imageDecodeRaw(textureData,width,height,Type)
        texList.append(NoeTexture(TexName, width, height, pix, noesis.NOESISTEX_RGBA32))
        bs.seek(ret, NOESEEK_ABS)

    return 1