//Maya ASCII 8.5 scene
//Name: meshtweaks.ma
//Last modified: Wed, Jan 28, 2009 09:47:53 PM
//Codeset: 1252
requires maya "8.5";
currentUnit -l centimeter -a degree -t pal;
fileInfo "application" "maya";
fileInfo "product" "Maya Unlimited 8.5";
fileInfo "version" "8.5 Service Pack 1";
fileInfo "cutIdentifier" "200706062232-700503";
fileInfo "osv" "Microsoft Windows XP Service Pack 3 (Build 2600)\n";
createNode transform -s -n "persp";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 10.19459243354064 3.7064566758636888 -0.52950241753306848 ;
	setAttr ".r" -type "double3" -11.138352729587302 94.599999999996413 0 ;
createNode camera -s -n "perspShape" -p "persp";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 9.6589154299862994;
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
createNode transform -n "pCube1";
createNode mesh -n "mesh_with_history" -p "pCube1";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 5 ".pt";
	setAttr ".pt[2:5]" -type "float3" 0 2.9802322e-008 0  0 2.9802322e-008 
		0  1.1920929e-007 1.0000001 -1.0000004  1.1920929e-007 1.0000001 -1.0000004 ;
createNode transform -n "pCube2";
createNode mesh -n "mesh_without_history" -p "pCube2";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 -1 0.625 -1 
		0.375 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 
		0 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 4 ".pt[2:5]" -type "float3"  5.9604645e-008 2.3841858e-007 
		2.3841858e-007 5.9604645e-008 2.3841858e-007 2.3841858e-007 0 1 -1 0 1 -1;
	setAttr -s 8 ".vt[0:7]"  -1 -1 1 1 -1 1 -1 1 1 1 1 1 -1 1 -1 1 1 
		-1 -1 -1 -1 1 -1 -1;
	setAttr -s 12 ".ed[0:11]"  0 1 0 2 3 0 
		4 5 0 6 7 0 0 2 0 1 3 0 
		2 4 0 3 5 0 4 6 0 5 7 0 
		6 0 0 7 1 0;
	setAttr -s 6 ".fc[0:5]" -type "polyFaces" 
		f 4 0 5 -2 -5 
		mu 0 4 0 1 3 2 
		f 4 1 7 -3 -7 
		mu 0 4 2 3 5 4 
		f 4 2 9 -4 -9 
		mu 0 4 4 5 7 6 
		f 4 3 11 -1 -11 
		mu 0 4 6 7 9 8 
		f 4 -12 -10 -8 -6 
		mu 0 4 1 10 11 3 
		f 4 10 4 6 8 
		mu 0 4 12 0 2 13 ;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
createNode lightLinker -n "lightLinker1";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
createNode displayLayer -n "defaultLayer";
createNode renderLayerManager -n "renderLayerManager";
createNode renderLayer -n "defaultRenderLayer";
	setAttr ".g" yes;
createNode script -n "sceneConfigurationScriptNode";
	setAttr ".b" -type "string" "playbackOptions -min 1.041667 -max 25 -ast 1.041667 -aet 50 ";
	setAttr ".st" 6;
createNode polyCube -n "polyCube1";
	setAttr ".w" 2;
	setAttr ".h" 2;
	setAttr ".d" 2;
	setAttr ".cuv" 4;
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
select -ne :initialShadingGroup;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :defaultHardwareRenderGlobals;
	setAttr ".fn" -type "string" "im";
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
connectAttr "polyCube1.out" "mesh_with_history.i";
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
connectAttr "lightLinker1.msg" ":lightList1.ln" -na;
connectAttr "mesh_with_history.iog" ":initialShadingGroup.dsm" -na;
connectAttr "mesh_without_history.iog" ":initialShadingGroup.dsm" -na;
// End of meshtweaks.ma
