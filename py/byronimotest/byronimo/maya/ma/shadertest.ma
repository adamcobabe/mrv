//Maya ASCII 8.5 scene
//Name: shadertest.ma
//Last modified: Wed, Oct 08, 2008 10:03:29 PM
//Codeset: UTF-8
requires maya "8.5";
currentUnit -l centimeter -a degree -t pal;
fileInfo "application" "maya";
fileInfo "product" "Maya Unlimited 8.5";
fileInfo "version" "8.5 Service Pack 1 x64";
fileInfo "cutIdentifier" "200706070006-700509";
fileInfo "osv" "Linux 2.6.24-19-generic #1 SMP Wed Aug 20 17:53:40 UTC 2008 x86_64";
createNode transform -s -n "persp";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 17.725966205864758 22.526538858035718 25.709581386565013 ;
	setAttr ".r" -type "double3" -36.338352729604793 27.800000000001546 1.7977747490500895e-15 ;
createNode camera -s -n "perspShape" -p "persp";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 38.825960077493761;
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
createNode transform -n "p1trans";
	setAttr ".t" -type "double3" -5.3569975829081891 0.62794501257321755 0.82710818812904918 ;
	setAttr ".s" -type "double3" 6.9529314473320136 6.9529314473320136 6.9529314473320136 ;
createNode mesh -n "p1" -p "p1trans";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "p2trans";
	setAttr ".t" -type "double3" 2.9070527736880427 0.058072725182974239 -0.53314097442556119 ;
	setAttr ".s" -type "double3" 6.8920372632154603 6.8920372632154603 6.8920372632154603 ;
createNode mesh -n "p2" -p "p2trans";
	setAttr -k off ".v";
	setAttr -s 6 ".iog[0].og";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "s1trans";
	setAttr ".t" -type "double3" 10.398419683552465 0 0 ;
	setAttr ".s" -type "double3" 2.1669258266465281 2.1669258266465281 2.1669258266465281 ;
createNode subdiv -n "s1" -p "s1trans";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 206 ".uvst[0].uvsp[0:205]" -type "float2" 0.375 0 0.625 0 0.625 0.25 
		0.375 0.25 0.625 0.5 0.375 0.5 0.625 0.75 0.375 0.75 0.625 1 0.375 1 0.875 0 0.875 
		0.25 0.125 0 0.125 0.25 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
		0 0 0 0.375 0 0.5 0 0.5 0.125 0.375 0.125 0.625 0 0.625 0.125 0.5 0.125 0.5 0 0.625 
		0.25 0.5 0.25 0.5 0.125 0.625 0.125 0.375 0.25 0.375 0.125 0.5 0.125 0.5 0.25 0 0 
		0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.125 0 0.25 0 0.25 0.125 
		0.125 0.125 0.375 0 0.375 0.125 0.25 0.125 0.25 0 0.375 0.25 0.25 0.25 0.25 0.125 
		0.375 0.125 0.125 0.25 0.125 0.125 0.25 0.125 0.25 0.25 0 0 0 0 0 0 0 0 0 0 0 0 0 
		0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.375 0.5 0.5 0.5 0.5 0.625 0.375 0.625 0.625 
		0.5 0.625 0.625 0.5 0.625 0.5 0.5 0.625 0.75 0.5 0.75 0.5 0.625 0.625 0.625 0.375 
		0.75 0.375 0.625 0.5 0.625 0.5 0.75 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
		0 0 0 0 0 0 0 0 0 0.375 0.25 0.5 0.25 0.5 0.375 0.375 0.375 0.625 0.25 0.625 0.375 
		0.5 0.375 0.5 0.25 0.625 0.5 0.5 0.5 0.5 0.375 0.625 0.375 0.375 0.5 0.375 0.375 
		0.5 0.375 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
		0.625 0 0.75 0 0.75 0.125 0.625 0.125 0.875 0 0.875 0.125 0.75 0.125 0.75 0 0.875 
		0.25 0.75 0.25 0.75 0.125 0.875 0.125 0.625 0.25 0.625 0.125 0.75 0.125 0.75 0.25 
		0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.375 0.75 0.5 0.75 
		0.5 0.875 0.375 0.875 0.625 0.75 0.625 0.875 0.5 0.875 0.5 0.75 0.625 1 0.5 1 0.5 
		0.875 0.625 0.875 0.375 1 0.375 0.875 0.5 0.875 0.5 1;
	setAttr ".dsr" 5;
	setAttr ".xsr" 4;
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".cc" -type "subd" 
		8
		0  -1.2000000476837158 -1.2000000476837158 1.2000000476837158
		1  1.2000000476837158 -1.2000000476837158 1.2000000476837158
		3  1.2000000476837158 1.2000000476837158 1.2000000476837158
		2  -1.2000000476837158 1.2000000476837158 1.2000000476837158
		5  1.2000000476837158 1.2000000476837158 -1.2000000476837158
		4  -1.2000000476837158 1.2000000476837158 -1.2000000476837158
		7  1.2000000476837158 -1.2000000476837158 -1.2000000476837158
		6  -1.2000000476837158 -1.2000000476837158 -1.2000000476837158
		
		6
		4  0 1 3 2 
		4  2 3 5 4 
		4  4 5 7 6 
		4  6 7 1 0 
		4  1 7 5 3 
		4  6 0 2 4 
		
		;
	setAttr ".dr" 3;
	setAttr ".ecr" -type "subdivEdgeCrease" 0 0
		
		;
	setAttr ".fuv[0]" -type "subdivFaceUVIds" 
		6
		0 
		4  0 1 2 3 
		4  42 38 4 5 
		4  5 4 6 7 
		4  7 6 8 9 
		4  1 10 11 38 
		4  12 0 42 13 
		
		
		0 0 1 0 4 30 31 32 33 
		0 1 1 0 4 34 35 32 31 
		0 2 1 0 4 38 39 32 35 
		0 3 1 0 4 42 33 32 39 
		0 0 1 1 4 42 39 128 129 
		0 1 1 1 4 38 131 128 39 
		0 2 1 1 4 134 95 128 131 
		0 3 1 1 4 138 139 128 95 
		0 0 1 2 4 94 95 96 97 
		0 1 1 2 4 98 99 96 95 
		0 2 1 2 4 102 103 96 99 
		0 3 1 2 4 106 107 96 103 
		0 0 1 3 4 190 103 192 193 
		0 1 1 3 4 194 195 192 103 
		0 2 1 3 4 198 199 192 201 
		0 3 1 3 4 202 203 192 205 
		0 0 1 4 4 158 159 160 35 
		0 1 1 4 4 162 163 160 159 
		0 2 1 4 4 166 167 160 169 
		0 3 1 4 4 38 35 160 173 
		0 0 1 5 4 62 63 64 65 
		0 1 1 5 4 66 33 64 63 
		0 2 1 5 4 42 71 64 33 
		0 3 1 5 4 74 65 64 71 
		;
createNode transform -n "n1trans";
	setAttr ".t" -type "double3" 16.176903223234365 0 -0.90552037845857924 ;
createNode nurbsSurface -n "n1" -p "n1trans";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".tw" yes;
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".dvu" 0;
	setAttr ".dvv" 0;
	setAttr ".cpr" 4;
	setAttr ".cps" 4;
	setAttr ".nufa" 4.5;
	setAttr ".nvfa" 4.5;
createNode lightLinker -n "lightLinker1";
	setAttr -s 5 ".lnk";
	setAttr -s 5 ".slnk";
createNode displayLayerManager -n "layerManager";
createNode displayLayer -n "defaultLayer";
createNode renderLayerManager -n "renderLayerManager";
createNode renderLayer -n "defaultRenderLayer";
	setAttr ".g" yes;
createNode script -n "sceneConfigurationScriptNode";
	setAttr ".b" -type "string" "playbackOptions -min 1.041667 -max 25 -ast 1.041667 -aet 50 ";
	setAttr ".st" 6;
createNode polyPlane -n "polyPlane1";
	setAttr ".sw" 1;
	setAttr ".sh" 1;
	setAttr ".cuv" 2;
createNode lambert -n "lambert2";
	setAttr ".c" -type "float3" 0.81568629 0.81568629 0.81568629 ;
createNode shadingEngine -n "sg1";
	setAttr ".ihi" 0;
	setAttr -s 4 ".dsm";
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo1";
createNode polyPlane -n "polyPlane2";
	setAttr ".sw" 2;
	setAttr ".sh" 2;
	setAttr ".cuv" 2;
createNode groupId -n "groupId1";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts1";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "f[0]";
createNode lambert -n "lambert3";
	setAttr ".c" -type "float3" 0.078431375 0.078431375 0.078431375 ;
createNode shadingEngine -n "sg2";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo2";
createNode groupId -n "groupId2";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts2";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "f[1]";
createNode lambert -n "lambert4";
	setAttr ".c" -type "float3" 0.010416746 0 0.5 ;
createNode shadingEngine -n "sg3";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo3";
createNode groupId -n "groupId3";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts3";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "f[2:3]";
createNode makeNurbSphere -n "makeNurbSphere1";
	setAttr ".ax" -type "double3" 0 1 0 ;
	setAttr ".r" 2.7077051033312447;
createNode objectSet -n "set1";
	setAttr ".ihi" 0;
	setAttr -s 4 ".dsm";
createNode objectSet -n "set2";
	setAttr ".ihi" 0;
	setAttr -s 4 ".dsm";
select -ne :time1;
	setAttr ".o" 1.0416666666666667;
select -ne :renderPartition;
	setAttr -s 5 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 5 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :lightList1;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :defaultHardwareRenderGlobals;
	setAttr ".fn" -type "string" "im";
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
select -ne :ikSystem;
	setAttr -s 4 ".sol";
connectAttr "polyPlane1.out" "p1.i";
connectAttr "groupId1.id" "p2.iog.og[0].gid";
connectAttr "sg1.mwc" "p2.iog.og[0].gco";
connectAttr "groupId2.id" "p2.iog.og[1].gid";
connectAttr "sg2.mwc" "p2.iog.og[1].gco";
connectAttr "groupId3.id" "p2.iog.og[2].gid";
connectAttr "sg3.mwc" "p2.iog.og[2].gco";
connectAttr "groupParts3.og" "p2.i";
connectAttr "makeNurbSphere1.os" "n1.cr";
connectAttr ":defaultLightSet.msg" "lightLinker1.lnk[0].llnk";
connectAttr ":initialShadingGroup.msg" "lightLinker1.lnk[0].olnk";
connectAttr ":defaultLightSet.msg" "lightLinker1.lnk[1].llnk";
connectAttr ":initialParticleSE.msg" "lightLinker1.lnk[1].olnk";
connectAttr ":defaultLightSet.msg" "lightLinker1.lnk[2].llnk";
connectAttr "sg1.msg" "lightLinker1.lnk[2].olnk";
connectAttr ":defaultLightSet.msg" "lightLinker1.lnk[3].llnk";
connectAttr "sg2.msg" "lightLinker1.lnk[3].olnk";
connectAttr ":defaultLightSet.msg" "lightLinker1.lnk[4].llnk";
connectAttr "sg3.msg" "lightLinker1.lnk[4].olnk";
connectAttr ":defaultLightSet.msg" "lightLinker1.slnk[0].sllk";
connectAttr ":initialShadingGroup.msg" "lightLinker1.slnk[0].solk";
connectAttr ":defaultLightSet.msg" "lightLinker1.slnk[1].sllk";
connectAttr ":initialParticleSE.msg" "lightLinker1.slnk[1].solk";
connectAttr ":defaultLightSet.msg" "lightLinker1.slnk[2].sllk";
connectAttr "sg1.msg" "lightLinker1.slnk[2].solk";
connectAttr ":defaultLightSet.msg" "lightLinker1.slnk[3].sllk";
connectAttr "sg2.msg" "lightLinker1.slnk[3].solk";
connectAttr ":defaultLightSet.msg" "lightLinker1.slnk[4].sllk";
connectAttr "sg3.msg" "lightLinker1.slnk[4].solk";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "lambert2.oc" "sg1.ss";
connectAttr "p1.iog" "sg1.dsm" -na;
connectAttr "p2.iog.og[0]" "sg1.dsm" -na;
connectAttr "s1.iog" "sg1.dsm" -na;
connectAttr "n1.iog" "sg1.dsm" -na;
connectAttr "groupId1.msg" "sg1.gn" -na;
connectAttr "sg1.msg" "materialInfo1.sg";
connectAttr "lambert2.msg" "materialInfo1.m";
connectAttr "polyPlane2.out" "groupParts1.ig";
connectAttr "groupId1.id" "groupParts1.gi";
connectAttr "lambert3.oc" "sg2.ss";
connectAttr "groupId2.msg" "sg2.gn" -na;
connectAttr "p2.iog.og[1]" "sg2.dsm" -na;
connectAttr "sg2.msg" "materialInfo2.sg";
connectAttr "lambert3.msg" "materialInfo2.m";
connectAttr "groupParts1.og" "groupParts2.ig";
connectAttr "groupId2.id" "groupParts2.gi";
connectAttr "lambert4.oc" "sg3.ss";
connectAttr "groupId3.msg" "sg3.gn" -na;
connectAttr "p2.iog.og[2]" "sg3.dsm" -na;
connectAttr "sg3.msg" "materialInfo3.sg";
connectAttr "lambert4.msg" "materialInfo3.m";
connectAttr "groupParts2.og" "groupParts3.ig";
connectAttr "groupId3.id" "groupParts3.gi";
connectAttr "p1.iog" "set1.dsm" -na;
connectAttr "p2.iog" "set1.dsm" -na;
connectAttr "s1.iog" "set1.dsm" -na;
connectAttr "n1.iog" "set1.dsm" -na;
connectAttr "p1.iog" "set2.dsm" -na;
connectAttr "p2.iog" "set2.dsm" -na;
connectAttr "s1.iog" "set2.dsm" -na;
connectAttr "n1.iog" "set2.dsm" -na;
connectAttr "sg1.pa" ":renderPartition.st" -na;
connectAttr "sg2.pa" ":renderPartition.st" -na;
connectAttr "sg3.pa" ":renderPartition.st" -na;
connectAttr "lambert2.msg" ":defaultShaderList1.s" -na;
connectAttr "lambert3.msg" ":defaultShaderList1.s" -na;
connectAttr "lambert4.msg" ":defaultShaderList1.s" -na;
connectAttr "lightLinker1.msg" ":lightList1.ln" -na;
// End of shadertest.ma
