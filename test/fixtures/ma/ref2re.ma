//Maya ASCII 8.5 scene
//Name: ref2re.ma
//Last modified: Thu, Mar 11, 2010 06:10:42 PM
//Codeset: UTF-8
file -rdi 1 -ns "ref4m2r" -rfn "ref4m2rRN" "$MAYAFILEBASE/ma/ref4m2r.ma";
file -rdi 2 -ns "ref10m" -rfn "ref4m2r:ref10mRN" "$MAYAFILEBASE/ma/ref10m.ma";
file -rdi 2 -ns "ref8m" -rfn "ref4m2r:ref8mRN" "$MAYAFILEBASE/ma/ref8m.ma";
file -rdi 1 -ns "ref4m2r1" -rfn "ref4m2rRN1" "$MAYAFILEBASE/ma/ref4m2r.ma";
file -rdi 2 -ns "ref10m" -rfn "ref4m2r1:ref10mRN" "$MAYAFILEBASE/ma/ref10m.ma";
file -rdi 2 -ns "ref8m" -rfn "ref4m2r1:ref8mRN" "$MAYAFILEBASE/ma/ref8m.ma";
file -r -ns "ref4m2r" -dr 1 -rfn "ref4m2rRN" "$MAYAFILEBASE/ma/ref4m2r.ma";
file -r -ns "ref4m2r1" -dr 1 -rfn "ref4m2rRN1" "$MAYAFILEBASE/ma/ref4m2r.ma";
requires maya "8.5";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya Unlimited 8.5";
fileInfo "version" "8.5 Service Pack 1 x64";
fileInfo "cutIdentifier" "200706070006-700509";
fileInfo "osv" "Linux 2.6.27-17-generic #1 SMP Wed Jan 27 23:22:32 UTC 2010 x86_64";
createNode transform -s -n "persp";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -26.91720821899807 21.132330606937973 -35.562303280255705 ;
	setAttr ".r" -type "double3" -17.138352729599653 -141.40000000000038 0 ;
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
createNode lightLinker -n "lightLinker1";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
createNode displayLayer -n "defaultLayer";
createNode renderLayerManager -n "renderLayerManager";
createNode renderLayer -n "defaultRenderLayer";
	setAttr ".g" yes;
createNode script -n "sceneConfigurationScriptNode";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 24 -ast 1 -aet 48 ";
	setAttr ".st" 6;
createNode reference -n "ref4m2rRN";
	setAttr ".ed" -type "dataReferenceEdits" 
		"ref4m2rRN"
		"ref4m2r:ref10RN" 0
		"ref4m2r:ref8RN" 0
		"ref4m2rRN" 0
		"ref4m2r:ref10mRN" 0
		"ref4m2r:ref8mRN" 0
		"ref4m2rRN" 4
		2 "|ref4m2r:pCylinder1" "translate" " -type \"double3\" 0 0 0"
		2 "|ref4m2r:pCylinder2" "translate" " -type \"double3\" 0 0 0"
		2 "|ref4m2r:pCylinder3" "translate" " -type \"double3\" 0 0 0"
		2 "|ref4m2r:pCylinder4" "translate" " -type \"double3\" 0 0 0";
	setAttr ".ptag" -type "string" "";
lockNode;
createNode reference -n "ref4m2rRN1";
	setAttr ".ed" -type "dataReferenceEdits" 
		"ref4m2rRN1"
		"ref4m2r1:ref8mRN" 0
		"ref4m2r1:ref10mRN" 0
		"ref4m2rRN1" 0
		"ref4m2r1:ref8RN" 0
		"ref4m2r1:ref10RN" 0
		"ref4m2rRN1" 4
		2 "|ref4m2r1:pCylinder1" "translate" " -type \"double3\" 4.149239 -0.651723 -13.937374"
		
		2 "|ref4m2r1:pCylinder2" "translate" " -type \"double3\" 4.149239 -0.651723 -13.937374"
		
		2 "|ref4m2r1:pCylinder3" "translate" " -type \"double3\" 4.149239 -0.651723 -13.937374"
		
		2 "|ref4m2r1:pCylinder4" "translate" " -type \"double3\" 4.149239 -0.651723 -13.937374"
		
		"ref4m2r1:ref8mRN" 8
		2 "|ref4m2r1:ref8m:pSphere1" "translate" " -type \"double3\" 9.239202 -0.651723 -13.937374"
		
		2 "|ref4m2r1:ref8m:pSphere2" "translate" " -type \"double3\" 9.239202 -0.651723 -13.937374"
		
		2 "|ref4m2r1:ref8m:pSphere3" "translate" " -type \"double3\" 4.149239 -0.651723 -19.027336"
		
		2 "|ref4m2r1:ref8m:pSphere4" "translate" " -type \"double3\" 0.550092 -0.651723 -17.536521"
		
		2 "|ref4m2r1:ref8m:pSphere5" "translate" " -type \"double3\" -0.940724 -0.651723 -13.937374"
		
		2 "|ref4m2r1:ref8m:pSphere6" "translate" " -type \"double3\" 0.550092 -0.651723 -10.338226"
		
		2 "|ref4m2r1:ref8m:pSphere7" "translate" " -type \"double3\" 4.149239 -0.651723 -8.847411"
		
		2 "|ref4m2r1:ref8m:pSphere8" "translate" " -type \"double3\" 7.748386 -0.651723 -10.338226"
		
		"ref4m2r1:ref10mRN" 10
		2 "|ref4m2r1:ref10m:pCube1" "translate" " -type \"double3\" 4.149239 -0.651723 -13.937374"
		
		2 "|ref4m2r1:ref10m:pCube2" "translate" " -type \"double3\" 5.149239 0.348277 -13.937374"
		
		2 "|ref4m2r1:ref10m:pCube3" "translate" " -type \"double3\" 6.149239 1.348277 -13.937374"
		
		2 "|ref4m2r1:ref10m:pCube4" "translate" " -type \"double3\" 7.149239 2.348277 -13.937374"
		
		2 "|ref4m2r1:ref10m:pCube5" "translate" " -type \"double3\" 8.149239 3.348277 -13.937374"
		
		2 "|ref4m2r1:ref10m:pCube6" "translate" " -type \"double3\" 9.149239 4.348277 -13.937374"
		
		2 "|ref4m2r1:ref10m:pCube7" "translate" " -type \"double3\" 10.149239 5.348277 -13.937374"
		
		2 "|ref4m2r1:ref10m:pCube8" "translate" " -type \"double3\" 11.149239 6.348277 -13.937374"
		
		2 "|ref4m2r1:ref10m:pCube9" "translate" " -type \"double3\" 12.149239 7.348277 -13.937374"
		
		2 "|ref4m2r1:ref10m:pCube10" "translate" " -type \"double3\" 13.149239 8.348277 -13.937374";
	setAttr ".ptag" -type "string" "";
lockNode;
createNode reference -n "sharedReferenceNode";
	setAttr ".ed" -type "dataReferenceEdits" 
		"sharedReferenceNode";
lockNode;
select -ne :time1;
	setAttr ".o" 1;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 2 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :lightList1;
	setAttr -s 7 ".ln";
select -ne :initialShadingGroup;
	setAttr -s 44 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :defaultHardwareRenderGlobals;
	setAttr ".fn" -type "string" "im";
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
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
connectAttr "sharedReferenceNode.sr" "ref4m2rRN.sr";
connectAttr "lightLinker1.msg" ":lightList1.ln" -na;
// End of ref2re.ma
