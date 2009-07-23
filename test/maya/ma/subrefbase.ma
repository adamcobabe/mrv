//Maya ASCII 8.5 scene
//Name: subrefbase.ma
//Last modified: Mon, Aug 11, 2008 03:09:56 PM
//Codeset: UTF-8
file -rdi 1 -ns "cube" -rfn "cubeRN" "$MAYAFILEBASE/ma/cube.ma";
file -rdi 1 -ns "cylinder" -rfn "cylinderRN" "$MAYAFILEBASE/ma/cylinder.ma";
file -rdi 1 -ns "sphere" -rfn "sphereRN" "$MAYAFILEBASE/ma/sphere.ma";
file -rdi 1 -ns "subsubrefbase" -rfn "subsubrefbaseRN" "$MAYAFILEBASE/ma/subsubrefbase.ma";
file -rdi 2 -ns "cube" -rfn "subsubrefbase:cubeRN" "$MAYAFILEBASE/ma/cube.ma";
file -rdi 2 -ns "cylinder" -rfn "subsubrefbase:cylinderRN" "$MAYAFILEBASE/ma/cylinder.ma";
file -rdi 2 -ns "sphere" -rfn "subsubrefbase:sphereRN" "$MAYAFILEBASE/ma/sphere.ma";
file -r -ns "cube" -dr 1 -rfn "cubeRN" "$MAYAFILEBASE/ma/cube.ma";
file -r -ns "cylinder" -dr 1 -rfn "cylinderRN" "$MAYAFILEBASE/ma/cylinder.ma";
file -r -ns "sphere" -dr 1 -rfn "sphereRN" "$MAYAFILEBASE/ma/sphere.ma";
file -r -ns "subsubrefbase" -dr 1 -rfn "subsubrefbaseRN" "$MAYAFILEBASE/ma/subsubrefbase.ma";
requires maya "8.5";
currentUnit -l centimeter -a degree -t pal;
fileInfo "application" "maya";
fileInfo "product" "Maya Unlimited 8.5";
fileInfo "version" "8.5 Service Pack 1 x64";
fileInfo "cutIdentifier" "200706070006-700509";
fileInfo "osv" "Linux 2.6.24-19-generic #1 SMP Fri Jul 11 21:01:46 UTC 2008 x86_64";
createNode transform -s -n "persp";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -31.95016359459364 18.554497376576727 25.356805381179811 ;
	setAttr ".r" -type "double3" -21.93835272960407 -51.400000000000539 -5.0980264433060312e-15 ;
createNode camera -s -n "perspShape" -p "persp";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 44.82186966202994;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 100.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 100.1 ;
createNode camera -s -n "frontShape" -p "front";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "pSphere1";
createNode mesh -n "pSphereShape1" -p "pSphere1";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "pCube1";
createNode mesh -n "pCubeShape1" -p "pCube1";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "pCylinder1";
createNode mesh -n "pCylinderShape1" -p "pCylinder1";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode lightLinker -n "lightLinker1";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
createNode displayLayer -n "defaultLayer";
createNode renderLayerManager -n "renderLayerManager";
createNode renderLayer -n "defaultRenderLayer";
	setAttr ".g" yes;
createNode polySphere -n "polySphere1";
createNode polyCube -n "polyCube1";
	setAttr ".cuv" 4;
createNode polyCylinder -n "polyCylinder1";
	setAttr ".sc" 1;
	setAttr ".cuv" 3;
createNode script -n "sceneConfigurationScriptNode";
	setAttr ".b" -type "string" "playbackOptions -min 1.041667 -max 25 -ast 1.041667 -aet 50 ";
	setAttr ".st" 6;
createNode reference -n "cubeRN";
	setAttr ".ed" -type "dataReferenceEdits" 
		"cubeRN"
		"cubeRN" 0
		"cubeRN" 1
		2 "|cube:pCube1" "translate" " -type \"double3\" -2.304798 7.174361 -6.119084";
	setAttr ".ptag" -type "string" "";
lockNode;
createNode reference -n "cylinderRN";
	setAttr ".ed" -type "dataReferenceEdits" 
		"cylinderRN"
		"cylinderRN" 0
		"cylinderRN" 1
		2 "|cylinder:pCylinder1" "translate" " -type \"double3\" 6.361194 7.314121 1.441397";
	setAttr ".ptag" -type "string" "";
lockNode;
createNode reference -n "sphereRN";
	setAttr ".ed" -type "dataReferenceEdits" 
		"sphereRN"
		"sphereRN" 0
		"sphereRN" 1
		2 "|sphere:pSphere1" "translate" " -type \"double3\" 1.849112 7.081187 -2.403839";
	setAttr ".ptag" -type "string" "";
lockNode;
createNode reference -n "subsubrefbaseRN";
	setAttr ".fn[0]" -type "string" "/home/sebastian/whitesharkstd/trunk/ext/byronimo/py/byronimo/maya/test/ma/subsubrefbase.ma";
	setAttr ".ed" -type "dataReferenceEdits" 
		"subsubrefbaseRN"
		"subsubrefbaseRN" 0
		"subsubrefbase:sphereRN" 0
		"subsubrefbase:cubeRN" 0
		"subsubrefbase:cylinderRN" 0;
	setAttr ".ptag" -type "string" "";
lockNode;
createNode reference -n "sharedReferenceNode";
	setAttr ".ed" -type "dataReferenceEdits" 
		"sharedReferenceNode";
lockNode;
select -ne :time1;
	setAttr ".o" 1.0416666666666667;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 2 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :lightList1;
	setAttr -s 8 ".ln";
select -ne :initialShadingGroup;
	setAttr -s 12 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :defaultHardwareRenderGlobals;
	setAttr ".fn" -type "string" "im";
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
connectAttr "polySphere1.out" "pSphereShape1.i";
connectAttr "polyCube1.out" "pCubeShape1.i";
connectAttr "polyCylinder1.out" "pCylinderShape1.i";
connectAttr ":defaultLightSet.msg" "lightLinker1.lnk[0].llnk";
connectAttr ":initialShadingGroup.msg" "lightLinker1.lnk[0].olnk";
connectAttr ":defaultLightSet.msg" "lightLinker1.lnk[1].llnk";
connectAttr ":initialParticleSE.msg" "lightLinker1.lnk[1].olnk";
connectAttr ":defaultLightSet.msg" "lightLinker1.slnk[0].sllk";
connectAttr ":initialShadingGroup.msg" "lightLinker1.slnk[0].solk";
connectAttr ":defaultLightSet.msg" "lightLinker1.slnk[1].sllk";
connectAttr ":initialParticleSE.msg" "lightLinker1.slnk[1].solk";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "sharedReferenceNode.sr" "subsubrefbaseRN.sr";
connectAttr "lightLinker1.msg" ":lightList1.ln" -na;
connectAttr "pSphereShape1.iog" ":initialShadingGroup.dsm" -na;
connectAttr "pCubeShape1.iog" ":initialShadingGroup.dsm" -na;
connectAttr "pCylinderShape1.iog" ":initialShadingGroup.dsm" -na;
// End of subrefbase.ma
