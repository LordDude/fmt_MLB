import json
import sys

f = open(sys.argv[1], 'rb')
UE4 = dict({"Name": "None", 
           "LightName": "LightName", 
           "LightType": "LightType", 
           "Position": {'X': 0.0, 'Y': 0.0, 'Z': 0.0}, 
           "Direction": {'X': 0.0, 'Y': 0.0, 'Z': 0.0}, 
           "Color": {'X': 0.0, 'Y': 0.0, 'Z': 0.0}, 
           "Cone": 0.0, 
           "Penum": 0.0, 
           "AreaMatrix_A": {'X': 0.0, 'Y': 0.0, 'Z': 0.0}, 
           "AreaMatrix_B": {'X': 0.0, 'Y': 0.0, 'Z': 0.0}, 
           "AreaMatrix_C": {'X': 0.0, 'Y': 0.0, 'Z': 0.0}, 
           "AreaMatrix_D": {'X': 0.0, 'Y': 0.0, 'Z': 0.0}}
           )
Hold = []
data = json.load(f)
AreaMatrix_A = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
AreaMatrix_B = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
AreaMatrix_C = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
AreaMatrix_D = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
Root = "---,LightName,LightType,Position,Direction,Color,Cone,Penum,AreaMatrix_A,AreaMatrix_B,AreaMatrix_C,AreaMatrix_D\n"
w = open("test.csv", 'w')
w.write(Root)
for key in data:
    if data[key]["ClassLabel"]["label"] == "SpotLight":
        print(data[key]["Label"]["label"], data[key]["Object"]["Pos"]["X"], data[key]["Object"]["Dir"])
        w.write(str(data[key]["Label"]["label"])+",")
        w.write('"'+str(data[key]["Label"]["label"])+'",')
        w.write('"'+str(data[key]["ClassLabel"]["label"])+'",')
        w.write('"(X='+str(data[key]["Object"]["Pos"]["X"])+',Y='+str(data[key]["Object"]["Pos"]["Y"])+',Z='+str(data[key]["Object"]["Pos"]["Z"])+')",')
        w.write('"(X='+str(data[key]["Object"]["Dir"]["X"])+',Y='+str(data[key]["Object"]["Dir"]["Y"])+',Z='+str(data[key]["Object"]["Dir"]["Z"])+')",')
        w.write('"(X='+str(data[key]["Object"]["Color"]["X"])+',Y='+str(data[key]["Object"]["Color"]["Y"])+',Z='+str(data[key]["Object"]["Color"]["Z"])+')",')
        w.write('"'+str(data[key]["Object"]["Cone"])+'",')
        w.write('"'+str(data[key]["Object"]["Penum"])+'",')
        w.write('"(X='+str(0.0)+',Y='+str(0.0)+',Z='+str(0.0)+')",')
        w.write('"(X='+str(0.0)+',Y='+str(0.0)+',Z='+str(0.0)+')",')
        w.write('"(X='+str(0.0)+',Y='+str(0.0)+',Z='+str(0.0)+')",')
        w.write('"(X='+str(0.0)+',Y='+str(0.0)+',Z='+str(0.0)+')"')
        w.write('\n')
    elif data[key]["ClassLabel"]["label"] == "PointLight":
        print(data[key]["Label"]["label"])
        w.write(str(data[key]["Label"]["label"])+",")
        w.write('"'+str(data[key]["Label"]["label"])+'",')
        w.write('"'+str(data[key]["ClassLabel"]["label"])+'",')
        w.write('"(X='+str(data[key]["Object"]["Pos"]["X"])+',Y='+str(data[key]["Object"]["Pos"]["Y"])+',Z='+str(data[key]["Object"]["Pos"]["Z"])+')",')
        w.write('"(X='+str(0.0)+',Y='+str(0.0)+',Z='+str(0.0)+')",')
        w.write('"(X='+str(data[key]["Object"]["Color"]["X"])+',Y='+str(data[key]["Object"]["Color"]["Y"])+',Z='+str(data[key]["Object"]["Color"]["Z"])+')",')
        w.write('"'+str(0.0)+'",')
        w.write('"'+str(0.0)+'",')
        w.write('"(X='+str(0.0)+',Y='+str(0.0)+',Z='+str(0.0)+')",')
        w.write('"(X='+str(0.0)+',Y='+str(0.0)+',Z='+str(0.0)+')",')
        w.write('"(X='+str(0.0)+',Y='+str(0.0)+',Z='+str(0.0)+')",')
        w.write('"(X='+str(0.0)+',Y='+str(0.0)+',Z='+str(0.0)+')"')
        w.write('\n')
    elif data[key]["ClassLabel"]["label"] == "AreaLight":
        print(data[key]["Label"]["label"])
        w.write(str(data[key]["Label"]["label"])+",")
        w.write('"'+str(data[key]["Label"]["label"])+'",')
        w.write('"'+str(data[key]["ClassLabel"]["label"])+'",')
        w.write('"(X='+str(0.0)+',Y='+str(0.0)+',Z='+str(0.0)+')",')
        w.write('"(X='+str(0.0)+',Y='+str(0.0)+',Z='+str(0.0)+')",')
        w.write('"(X='+str(data[key]["Object"]["Color"]["X"])+',Y='+str(data[key]["Object"]["Color"]["Y"])+',Z='+str(data[key]["Object"]["Color"]["Z"])+')",')
        w.write('"'+str(0.0)+'",')
        w.write('"'+str(0.0)+'",')
        w.write('"(X='+str(data[key]["Object"]["Mat34"]["A"]["X"])+',Y='+str(data[key]["Object"]["Mat34"]["A"]["Y"])+',Z='+str(data[key]["Object"]["Mat34"]["A"]["Z"])+')",')
        w.write('"(X='+str(data[key]["Object"]["Mat34"]["B"]["X"])+',Y='+str(data[key]["Object"]["Mat34"]["B"]["Y"])+',Z='+str(data[key]["Object"]["Mat34"]["B"]["Z"])+')",')
        w.write('"(X='+str(data[key]["Object"]["Mat34"]["C"]["X"])+',Y='+str(data[key]["Object"]["Mat34"]["C"]["Y"])+',Z='+str(data[key]["Object"]["Mat34"]["C"]["Z"])+')",')
        w.write('"(X='+str(data[key]["Object"]["Mat34"]["D"]["X"])+',Y='+str(data[key]["Object"]["Mat34"]["D"]["Y"])+',Z='+str(data[key]["Object"]["Mat34"]["D"]["Z"])+')"')
        w.write('\n')