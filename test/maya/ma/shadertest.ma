//Maya ASCII 8.5 scene
//Name: shadertest.ma
//Last modified: Thu, Oct 09, 2008 12:54:19 PM
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
	setAttr ".t" -type "double3" 16.444479023847236 58.381145122915314 47.583691117147666 ;
	setAttr ".r" -type "double3" -64.538352729615852 19.799999999999994 3.3804014136654686e-15 ;
createNode camera -s -n "perspShape" -p "persp";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 77.746272130755955;
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
	setAttr -s 2 ".iog";
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
	setAttr -s 2 ".iog";
	setAttr -s 3 ".iog[0].og";
	setAttr ".iog[0].og[0].gcl" -type "componentList" 1 "f[0]";
	setAttr ".iog[0].og[1].gcl" -type "componentList" 1 "f[1]";
	setAttr ".iog[0].og[2].gcl" -type "componentList" 1 "f[2:3]";
	setAttr -s 3 ".iog[1].og";
	setAttr ".iog[1].og[0].gcl" -type "componentList" 1 "f[0]";
	setAttr ".iog[1].og[1].gcl" -type "componentList" 1 "f[1]";
	setAttr ".iog[1].og[2].gcl" -type "componentList" 1 "f[2:3]";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 9 ".uvst[0].uvsp[0:8]" -type "float2" 0 0 0.5 0 1 0 0 0.5 0.5 0.5 1 0.5 
		0 1 0.5 1 1 1;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 9 ".vt[0:8]"  -0.5 -1.110223e-16 0.5 0 -1.110223e-16 0.5 0.5 -1.110223e-16 
		0.5 -0.5 0 0 0 0 0 0.5 0 0 -0.5 1.110223e-16 -0.5 0 1.110223e-16 -0.5 0.5 1.110223e-16 
		-0.5;
	setAttr -s 12 ".ed[0:11]"  0 1 0 0 3 0 1 2 0 1 4 1 2 5 0 3 4 1 3 6 0 4 5 1 4 7 1 
		5 8 0 6 7 0 7 8 0;
	setAttr -s 4 ".fc[0:3]" -type "polyFaces" 
		f 4 0 3 -6 -2 
		mu 0 4 0 1 4 3 
		f 4 2 4 -8 -4 
		mu 0 4 1 2 5 4 
		f 4 5 8 -11 -7 
		mu 0 4 3 4 7 6 
		f 4 7 9 -12 -9 
		mu 0 4 4 5 8 7 ;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
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
createNode transform -n "pdtrans";
	setAttr ".t" -type "double3" -7.0570052989673711 2.6322399564439891 14.661721199792911 ;
	setAttr ".s" -type "double3" 8.2720194562654736 8.2720194562654736 8.2720194562654736 ;
createNode mesh -n "pd" -p "pdtrans";
	setAttr -k off ".v";
	setAttr -s 2 ".iog";
	setAttr -s 6 ".iog[0].og";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr -s 2 ".ciog";
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".dr" 3;
createNode mesh -n "pdtransShape1Orig" -p "pdtrans";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "sine1Handle";
	setAttr ".t" -type "double3" 6.9689388569625876 1.3258998430301627 14.947469653618779 ;
	setAttr ".r" -type "double3" 0 0 -89.79179981164755 ;
	setAttr ".s" -type "double3" 4.1360097281327377 29.312646556013952 4.1360097281327377 ;
	setAttr ".smd" 7;
createNode deformSine -n "sine1HandleShape" -p "sine1Handle";
	setAttr -k off ".v";
	setAttr ".dd" -type "doubleArray" 6 0 -1 1 0.80000000000000004 0.29999999999999982
		 0 ;
	setAttr ".hw" 4.5496107009460109;
createNode transform -n "p1transinst";
	setAttr ".t" -type "double3" -5.3569975829081891 0.62794501257321755 -7.2716100464206512 ;
	setAttr ".s" -type "double3" 6.9529314473320136 6.9529314473320136 6.9529314473320136 ;
createNode transform -n "p2transinst";
	setAttr ".t" -type "double3" 2.9070527736880427 0.058072725182974239 -10.161994390775936 ;
	setAttr ".s" -type "double3" 8.2473569244518341 8.2473569244518341 8.2473569244518341 ;
createNode transform -n "pdtransinst";
	setAttr ".t" -type "double3" -7.0570052989673711 2.6322399564439891 26.53003780007284 ;
	setAttr ".s" -type "double3" 8.2720194562654736 8.2720194562654736 8.2720194562654736 ;
createNode transform -n "nurbsSphere1";
	setAttr ".t" -type "double3" 16.067662299962961 0.66510077228144127 23.741868262356363 ;
createNode nurbsSurface -n "nd" -p "nurbsSphere1";
	setAttr -k off ".v";
	setAttr -s 6 ".iog[0].og";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".tw" yes;
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".dvu" 3;
	setAttr ".dvv" 3;
	setAttr ".cpr" 15;
	setAttr ".cps" 4;
	setAttr ".nufa" 4.5;
	setAttr ".nvfa" 4.5;
createNode nurbsSurface -n "ndOrig" -p "nurbsSphere1";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".tw" yes;
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".dvu" 0;
	setAttr ".dvv" 0;
	setAttr ".cpr" 4;
	setAttr ".cps" 4;
	setAttr ".dcv" yes;
createNode transform -n "subdivSphere1";
	setAttr ".t" -type "double3" 29.2460422430118 0 22.89795295776355 ;
	setAttr ".s" -type "double3" 3.0350993064316598 3.0350993064316598 3.0350993064316598 ;
createNode subdiv -n "sd" -p "subdivSphere1";
	setAttr -k off ".v";
	setAttr -s 6 ".iog[0].og";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".tw" yes;
	setAttr ".dsr" 5;
	setAttr ".xsr" 4;
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".cc" -type "subd" 
		8
		0  -1.1973424206722694 -1.9313641365824934 1.2000000476837167
		1  2.0125064571090903 -0.7370969445982698 1.4194844244347875
		3  2.0033431142478353 1.4075161321184353 1.4169919576862404
		2  -0.64706881423896068 0.42199905305951824 1.421452550187758
		5  1.1987376602595896 1.5474020060129117 -1.2000000476837152
		4  -0.64706881423896068 0.42199905305951824 -1.2499238168888593
		7  2.0125064571090903 -0.7370969445982698 -1.2494801269113385
		6  -0.67179122071847885 -1.7265074197693164 -1.2476861807087822
		
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
createNode subdiv -n "subdivSphere1ShapeOrig" -p "subdivSphere1";
	setAttr -k off ".v";
	setAttr ".io" yes;
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
	setAttr ".dv" yes;
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
createNode transform -n "squash1Handle";
	setAttr ".t" -type "double3" 10.843278312034542 0.41224651968665871 20.595879499932877 ;
	setAttr ".s" -type "double3" 22.041051772224648 22.041051772224648 22.041051772224648 ;
	setAttr ".smd" 7;
createNode deformSquash -n "squash1HandleShape" -p "squash1Handle";
	setAttr -k off ".v";
	setAttr ".dd" -type "doubleArray" 7 -1 1 0 0 0.5 1 -0.11000000000000004 ;
	setAttr ".hw" 11.077184831099974;
parent -s -nc -r -add "|p1trans|p1" "p1transinst";
parent -s -nc -r -add "|p2trans|p2" "p2transinst";
parent -s -nc -r -add "|pdtrans|pd" "pdtransinst";
parent -s -nc -r -add "|pdtrans|pdtransShape1Orig" "pdtransinst";
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
	setAttr -s 10 ".dsm";
	setAttr ".ro" yes;
	setAttr -s 2 ".gn";
createNode materialInfo -n "materialInfo1";
createNode lambert -n "lambert3";
	setAttr ".c" -type "float3" 0.078431375 0.078431375 0.078431375 ;
createNode shadingEngine -n "sg2";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
	setAttr -s 2 ".gn";
createNode materialInfo -n "materialInfo2";
createNode lambert -n "lambert4";
	setAttr ".c" -type "float3" 0.010416746 0 0.5 ;
createNode shadingEngine -n "sg3";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
	setAttr -s 2 ".gn";
createNode materialInfo -n "materialInfo3";
createNode makeNurbSphere -n "makeNurbSphere1";
	setAttr ".ax" -type "double3" 0 1 0 ;
	setAttr ".r" 2.7077051033312447;
createNode objectSet -n "set1";
	setAttr ".ihi" 0;
	setAttr -s 8 ".dsm";
createNode objectSet -n "set2";
	setAttr ".ihi" 0;
	setAttr -s 6 ".dsm";
createNode polyPlane -n "polyPlane3";
	setAttr ".sw" 2;
	setAttr ".sh" 2;
	setAttr ".cuv" 2;
createNode nonLinear -n "sine1";
	addAttr -is true -ci true -k true -sn "amp" -ln "amplitude" -bt "AMPL" -smn -5 
		-smx 5 -at "double";
	addAttr -is true -ci true -k true -sn "wav" -ln "wavelength" -bt "WLTH" -dv 2 -min 
		0.1 -smn 0.1 -smx 10 -at "double";
	addAttr -is true -ci true -k true -sn "off" -ln "offset" -bt "OFST" -smn -10 -smx 
		10 -at "double";
	addAttr -is true -ci true -k true -sn "dr" -ln "dropoff" -bt "DRPF" -min -1 -max 
		1 -at "double";
	addAttr -is true -ci true -k true -sn "lb" -ln "lowBound" -bt "STBD" -dv -1 -max 
		0 -smn -10 -smx 0 -at "double";
	addAttr -is true -ci true -k true -sn "hb" -ln "highBound" -bt "EDBD" -dv 1 -min 
		0 -smn 0 -smx 10 -at "double";
	setAttr -s 3 ".ip";
	setAttr -s 3 ".og";
	setAttr -k on ".amp" 0.8;
	setAttr -k on ".wav" 0.29999999999999982;
	setAttr -k on ".off";
	setAttr -k on ".dr";
	setAttr -k on ".lb";
	setAttr -k on ".hb";
createNode tweak -n "tweak1";
createNode objectSet -n "sine1Set";
	setAttr ".ihi" 0;
	setAttr -s 3 ".dsm";
	setAttr ".vo" yes;
	setAttr -s 3 ".gn";
createNode groupId -n "sine1GroupId";
	setAttr ".ihi" 0;
createNode groupParts -n "sine1GroupParts";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode objectSet -n "tweakSet1";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "groupId5";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts5";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode groupId -n "groupId6";
	setAttr ".ihi" 0;
createNode groupId -n "groupId7";
	setAttr ".ihi" 0;
createNode groupId -n "groupId8";
	setAttr ".ihi" 0;
createNode groupId -n "groupId9";
	setAttr ".ihi" 0;
createNode groupId -n "groupId10";
	setAttr ".ihi" 0;
createNode groupId -n "groupId11";
	setAttr ".ihi" 0;
createNode makeNurbSphere -n "makeNurbSphere2";
	setAttr ".ax" -type "double3" 0 1 0 ;
	setAttr ".r" 4.2390842865755269;
createNode tweak -n "tweak2";
createNode groupId -n "groupId12";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts6";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[0:6][0:7]";
createNode objectSet -n "tweakSet2";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "groupId13";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts7";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "cv[*][*]";
createNode hyperView -n "hyperView1";
	setAttr ".vl" -type "double2" -12.96 -120.0676571428572 ;
	setAttr ".vh" -type "double2" 530.96 196.96 ;
	setAttr ".dag" no;
createNode hyperLayout -n "hyperLayout1";
	setAttr -s 7 ".hyp";
	setAttr ".hyp[0].x" 71;
	setAttr ".hyp[0].y" 92;
	setAttr ".hyp[0].isc" no;
	setAttr ".hyp[0].isf" no;
	setAttr ".hyp[1].x" 274;
	setAttr ".hyp[1].y" 67;
	setAttr ".hyp[1].isc" no;
	setAttr ".hyp[1].isf" no;
	setAttr ".hyp[2].x" 68;
	setAttr ".hyp[2].y" -17;
	setAttr ".hyp[2].isc" no;
	setAttr ".hyp[2].isf" no;
	setAttr ".hyp[3].x" 71;
	setAttr ".hyp[3].y" 168;
	setAttr ".hyp[3].isc" no;
	setAttr ".hyp[3].isf" no;
	setAttr ".hyp[4].x" 461;
	setAttr ".hyp[4].y" -70;
	setAttr ".hyp[4].isc" no;
	setAttr ".hyp[4].isf" no;
	setAttr ".hyp[5].x" 461;
	setAttr ".hyp[5].y" 146;
	setAttr ".hyp[5].isc" no;
	setAttr ".hyp[5].isf" no;
	setAttr ".anf" yes;
createNode hyperView -n "hyperView2";
	setAttr ".vl" -type "double2" -12.96 -120.0676571428572 ;
	setAttr ".vh" -type "double2" 530.96 196.96 ;
	setAttr ".dag" no;
createNode hyperLayout -n "hyperLayout2";
	setAttr -s 7 ".hyp";
	setAttr ".hyp[0].x" 71;
	setAttr ".hyp[0].y" 92;
	setAttr ".hyp[0].isc" no;
	setAttr ".hyp[0].isf" no;
	setAttr ".hyp[1].x" 274;
	setAttr ".hyp[1].y" 67;
	setAttr ".hyp[1].isc" no;
	setAttr ".hyp[1].isf" no;
	setAttr ".hyp[2].x" 68;
	setAttr ".hyp[2].y" -17;
	setAttr ".hyp[2].isc" no;
	setAttr ".hyp[2].isf" no;
	setAttr ".hyp[3].x" 71;
	setAttr ".hyp[3].y" 168;
	setAttr ".hyp[3].isc" no;
	setAttr ".hyp[3].isf" no;
	setAttr ".hyp[4].x" 461;
	setAttr ".hyp[4].y" -70;
	setAttr ".hyp[4].isc" no;
	setAttr ".hyp[4].isf" no;
	setAttr ".hyp[5].x" 461;
	setAttr ".hyp[5].y" 146;
	setAttr ".hyp[5].isc" no;
	setAttr ".hyp[5].isf" no;
	setAttr ".anf" yes;
createNode tweak -n "tweak3";
createNode groupId -n "groupId14";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts8";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 3 "smp[0][0:3]" "smp[256][2:3]" "smp[512][2:3]";
createNode objectSet -n "tweakSet3";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "groupId15";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts9";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 3 "smp[0][0:3]" "smp[256][2:3]" "smp[512][2:3]";
createNode nonLinear -n "squash1";
	addAttr -is true -ci true -k true -sn "fac" -ln "factor" -bt "FACT" -smn -10 -smx 
		10 -at "double";
	addAttr -is true -ci true -k true -sn "exp" -ln "expand" -bt "EXPA" -dv 1 -min 0 
		-smn 0 -smx 10 -at "double";
	addAttr -is true -ci true -k true -sn "mp" -ln "maxExpandPos" -bt "MAEP" -dv 0.5 
		-min 0.01 -max 0.99 -at "double";
	addAttr -is true -ci true -k true -sn "ss" -ln "startSmoothness" -bt "STSM" -min 
		0 -max 1 -at "double";
	addAttr -is true -ci true -k true -sn "es" -ln "endSmoothness" -bt "ENSM" -min 0 
		-max 1 -at "double";
	addAttr -is true -ci true -k true -sn "lb" -ln "lowBound" -bt "STBD" -dv -1 -max 
		0 -smn -10 -smx 0 -at "double";
	addAttr -is true -ci true -k true -sn "hb" -ln "highBound" -bt "EDBD" -dv 1 -min 
		0 -smn 0 -smx 10 -at "double";
	setAttr -s 3 ".ip";
	setAttr -s 3 ".og";
	setAttr -k on ".fac" -0.11000000000000004;
	setAttr -k on ".exp";
	setAttr -k on ".mp";
	setAttr -k on ".ss";
	setAttr -k on ".es";
	setAttr -k on ".lb";
	setAttr -k on ".hb";
createNode objectSet -n "squash1Set";
	setAttr ".ihi" 0;
	setAttr -s 3 ".dsm";
	setAttr ".vo" yes;
	setAttr -s 3 ".gn";
createNode groupId -n "squash1GroupId";
	setAttr ".ihi" 0;
createNode groupParts -n "squash1GroupParts";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[1:7]";
	setAttr ".irc" -type "componentList" 2 "vtx[0]" "vtx[8]";
createNode groupId -n "squash1GroupId1";
	setAttr ".ihi" 0;
createNode groupParts -n "squash1GroupParts1";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 7 "cv[0:2][0:7]" "cv[3][0:1]" "cv[3][3]" "cv[3][5:7]" "cv[4][0:5]" "cv[4][7]" "cv[5:6][0:7]";
	setAttr ".irc" -type "componentList" 3 "cv[4][6]" "cv[3][2]" "cv[3][4]";
createNode groupId -n "squash1GroupId2";
	setAttr ".ihi" 0;
createNode groupParts -n "squash1GroupParts2";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 3 "smp[0][1:3]" "smp[256][3]" "smp[512][2:3]";
	setAttr ".irc" -type "componentList" 2 "smp[0][0]" "smp[256][2]";
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
select -ne :hyperGraphInfo;
	setAttr -s 2 ".b";
connectAttr "polyPlane1.out" "|p1trans|p1.i";
connectAttr "groupId6.id" "|p2trans|p2.iog.og[0].gid";
connectAttr "sg1.mwc" "|p2trans|p2.iog.og[0].gco";
connectAttr "groupId7.id" "|p2trans|p2.iog.og[1].gid";
connectAttr "sg2.mwc" "|p2trans|p2.iog.og[1].gco";
connectAttr "groupId8.id" "|p2trans|p2.iog.og[2].gid";
connectAttr "sg3.mwc" "|p2trans|p2.iog.og[2].gco";
connectAttr "groupId9.id" "|p2transinst|p2.iog.og[0].gid";
connectAttr "sg1.mwc" "|p2transinst|p2.iog.og[0].gco";
connectAttr "groupId10.id" "|p2transinst|p2.iog.og[1].gid";
connectAttr "sg2.mwc" "|p2transinst|p2.iog.og[1].gco";
connectAttr "groupId11.id" "|p2transinst|p2.iog.og[2].gid";
connectAttr "sg3.mwc" "|p2transinst|p2.iog.og[2].gco";
connectAttr "makeNurbSphere1.os" "n1.cr";
connectAttr "sine1GroupId.id" "|pdtrans|pd.iog.og[0].gid";
connectAttr "sine1Set.mwc" "|pdtrans|pd.iog.og[0].gco";
connectAttr "groupId5.id" "|pdtrans|pd.iog.og[1].gid";
connectAttr "tweakSet1.mwc" "|pdtrans|pd.iog.og[1].gco";
connectAttr "squash1GroupId.id" "|pdtrans|pd.iog.og[2].gid";
connectAttr "squash1Set.mwc" "|pdtrans|pd.iog.og[2].gco";
connectAttr "squash1.og[0]" "|pdtrans|pd.i";
connectAttr "tweak1.vl[0].vt[0]" "|pdtrans|pd.twl";
connectAttr "polyPlane3.out" "|pdtrans|pdtransShape1Orig.i";
connectAttr "sine1.msg" "sine1Handle.sml";
connectAttr "sine1.amp" "sine1HandleShape.amp";
connectAttr "sine1.wav" "sine1HandleShape.wav";
connectAttr "sine1.off" "sine1HandleShape.off";
connectAttr "sine1.dr" "sine1HandleShape.dr";
connectAttr "sine1.lb" "sine1HandleShape.lb";
connectAttr "sine1.hb" "sine1HandleShape.hb";
connectAttr "groupId12.id" "nd.iog.og[0].gid";
connectAttr "sine1Set.mwc" "nd.iog.og[0].gco";
connectAttr "groupId13.id" "nd.iog.og[1].gid";
connectAttr "tweakSet2.mwc" "nd.iog.og[1].gco";
connectAttr "squash1GroupId1.id" "nd.iog.og[2].gid";
connectAttr "squash1Set.mwc" "nd.iog.og[2].gco";
connectAttr "squash1.og[1]" "nd.cr";
connectAttr "tweak2.pl[0].cp[0]" "nd.twl";
connectAttr "makeNurbSphere2.os" "ndOrig.cr";
connectAttr "groupId14.id" "sd.iog.og[0].gid";
connectAttr "sine1Set.mwc" "sd.iog.og[0].gco";
connectAttr "groupId15.id" "sd.iog.og[1].gid";
connectAttr "tweakSet3.mwc" "sd.iog.og[1].gco";
connectAttr "squash1GroupId2.id" "sd.iog.og[2].gid";
connectAttr "squash1Set.mwc" "sd.iog.og[2].gco";
connectAttr "squash1.og[2]" "sd.cr";
connectAttr "tweak3.pl[0].cp[0]" "sd.twl";
connectAttr "squash1.msg" "squash1Handle.sml";
connectAttr "squash1.fac" "squash1HandleShape.fac";
connectAttr "squash1.exp" "squash1HandleShape.exp";
connectAttr "squash1.mp" "squash1HandleShape.mp";
connectAttr "squash1.ss" "squash1HandleShape.ss";
connectAttr "squash1.es" "squash1HandleShape.es";
connectAttr "squash1.lb" "squash1HandleShape.lb";
connectAttr "squash1.hb" "squash1HandleShape.hb";
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
connectAttr "|p1trans|p1.iog" "sg1.dsm" -na;
connectAttr "s1.iog" "sg1.dsm" -na;
connectAttr "n1.iog" "sg1.dsm" -na;
connectAttr "|p1transinst|p1.iog" "sg1.dsm" -na;
connectAttr "|p2trans|p2.iog.og[0]" "sg1.dsm" -na;
connectAttr "|p2transinst|p2.iog.og[0]" "sg1.dsm" -na;
connectAttr "|pdtrans|pd.iog" "sg1.dsm" -na;
connectAttr "|pdtransinst|pd.iog" "sg1.dsm" -na;
connectAttr "sd.iog" "sg1.dsm" -na;
connectAttr "nd.iog" "sg1.dsm" -na;
connectAttr "groupId6.msg" "sg1.gn" -na;
connectAttr "groupId9.msg" "sg1.gn" -na;
connectAttr "sg1.msg" "materialInfo1.sg";
connectAttr "lambert2.msg" "materialInfo1.m";
connectAttr "lambert3.oc" "sg2.ss";
connectAttr "groupId7.msg" "sg2.gn" -na;
connectAttr "groupId10.msg" "sg2.gn" -na;
connectAttr "|p2trans|p2.iog.og[1]" "sg2.dsm" -na;
connectAttr "|p2transinst|p2.iog.og[1]" "sg2.dsm" -na;
connectAttr "sg2.msg" "materialInfo2.sg";
connectAttr "lambert3.msg" "materialInfo2.m";
connectAttr "lambert4.oc" "sg3.ss";
connectAttr "groupId8.msg" "sg3.gn" -na;
connectAttr "groupId11.msg" "sg3.gn" -na;
connectAttr "|p2trans|p2.iog.og[2]" "sg3.dsm" -na;
connectAttr "|p2transinst|p2.iog.og[2]" "sg3.dsm" -na;
connectAttr "sg3.msg" "materialInfo3.sg";
connectAttr "lambert4.msg" "materialInfo3.m";
connectAttr "|p1trans|p1.iog" "set1.dsm" -na;
connectAttr "|p2trans|p2.iog" "set1.dsm" -na;
connectAttr "s1.iog" "set1.dsm" -na;
connectAttr "n1.iog" "set1.dsm" -na;
connectAttr "|p1transinst|p1.iog" "set1.dsm" -na;
connectAttr "|p2transinst|p2.iog" "set1.dsm" -na;
connectAttr "|pdtransinst|pd.iog" "set1.dsm" -na;
connectAttr "|pdtrans|pd.iog" "set1.dsm" -na;
connectAttr "|p1trans|p1.iog" "set2.dsm" -na;
connectAttr "|p2trans|p2.iog" "set2.dsm" -na;
connectAttr "s1.iog" "set2.dsm" -na;
connectAttr "n1.iog" "set2.dsm" -na;
connectAttr "|p1transinst|p1.iog" "set2.dsm" -na;
connectAttr "|p2transinst|p2.iog" "set2.dsm" -na;
connectAttr "sine1GroupParts.og" "sine1.ip[0].ig";
connectAttr "sine1GroupId.id" "sine1.ip[0].gi";
connectAttr "groupParts6.og" "sine1.ip[1].ig";
connectAttr "groupId12.id" "sine1.ip[1].gi";
connectAttr "groupParts8.og" "sine1.ip[2].ig";
connectAttr "groupId14.id" "sine1.ip[2].gi";
connectAttr "sine1HandleShape.dd" "sine1.dd";
connectAttr "sine1Handle.wm" "sine1.ma";
connectAttr "groupParts5.og" "tweak1.ip[0].ig";
connectAttr "groupId5.id" "tweak1.ip[0].gi";
connectAttr "sine1GroupId.msg" "sine1Set.gn" -na;
connectAttr "groupId12.msg" "sine1Set.gn" -na;
connectAttr "groupId14.msg" "sine1Set.gn" -na;
connectAttr "|pdtrans|pd.iog.og[0]" "sine1Set.dsm" -na;
connectAttr "nd.iog.og[0]" "sine1Set.dsm" -na;
connectAttr "sd.iog.og[0]" "sine1Set.dsm" -na;
connectAttr "sine1.msg" "sine1Set.ub[0]";
connectAttr "tweak1.og[0]" "sine1GroupParts.ig";
connectAttr "sine1GroupId.id" "sine1GroupParts.gi";
connectAttr "groupId5.msg" "tweakSet1.gn" -na;
connectAttr "|pdtrans|pd.iog.og[1]" "tweakSet1.dsm" -na;
connectAttr "tweak1.msg" "tweakSet1.ub[0]";
connectAttr "|pdtrans|pdtransShape1Orig.w" "groupParts5.ig";
connectAttr "groupId5.id" "groupParts5.gi";
connectAttr "groupParts7.og" "tweak2.ip[0].ig";
connectAttr "groupId13.id" "tweak2.ip[0].gi";
connectAttr "tweak2.og[0]" "groupParts6.ig";
connectAttr "groupId12.id" "groupParts6.gi";
connectAttr "groupId13.msg" "tweakSet2.gn" -na;
connectAttr "nd.iog.og[1]" "tweakSet2.dsm" -na;
connectAttr "tweak2.msg" "tweakSet2.ub[0]";
connectAttr "ndOrig.ws" "groupParts7.ig";
connectAttr "groupId13.id" "groupParts7.gi";
connectAttr "sine1Set.msg" "hyperView1.rnd[0]";
connectAttr "hyperLayout1.msg" "hyperView1.hl";
connectAttr "sine1.msg" "hyperLayout1.hyp[0].dn";
connectAttr "sine1Set.msg" "hyperLayout1.hyp[1].dn";
connectAttr "sine1GroupId.msg" "hyperLayout1.hyp[2].dn";
connectAttr "groupId12.msg" "hyperLayout1.hyp[3].dn";
connectAttr "|pdtrans|pd.msg" "hyperLayout1.hyp[4].dn";
connectAttr "nd.msg" "hyperLayout1.hyp[5].dn";
connectAttr "sine1Set.msg" "hyperView2.rnd[0]";
connectAttr "hyperLayout2.msg" "hyperView2.hl";
connectAttr "sine1.msg" "hyperLayout2.hyp[0].dn";
connectAttr "sine1Set.msg" "hyperLayout2.hyp[1].dn";
connectAttr "sine1GroupId.msg" "hyperLayout2.hyp[2].dn";
connectAttr "groupId12.msg" "hyperLayout2.hyp[3].dn";
connectAttr "|pdtrans|pd.msg" "hyperLayout2.hyp[4].dn";
connectAttr "nd.msg" "hyperLayout2.hyp[5].dn";
connectAttr "groupParts9.og" "tweak3.ip[0].ig";
connectAttr "groupId15.id" "tweak3.ip[0].gi";
connectAttr "tweak3.og[0]" "groupParts8.ig";
connectAttr "groupId14.id" "groupParts8.gi";
connectAttr "groupId15.msg" "tweakSet3.gn" -na;
connectAttr "sd.iog.og[1]" "tweakSet3.dsm" -na;
connectAttr "tweak3.msg" "tweakSet3.ub[0]";
connectAttr "subdivSphere1ShapeOrig.ws" "groupParts9.ig";
connectAttr "groupId15.id" "groupParts9.gi";
connectAttr "squash1GroupParts.og" "squash1.ip[0].ig";
connectAttr "squash1GroupId.id" "squash1.ip[0].gi";
connectAttr "squash1GroupParts1.og" "squash1.ip[1].ig";
connectAttr "squash1GroupId1.id" "squash1.ip[1].gi";
connectAttr "squash1GroupParts2.og" "squash1.ip[2].ig";
connectAttr "squash1GroupId2.id" "squash1.ip[2].gi";
connectAttr "squash1HandleShape.dd" "squash1.dd";
connectAttr "squash1Handle.wm" "squash1.ma";
connectAttr "squash1GroupId.msg" "squash1Set.gn" -na;
connectAttr "squash1GroupId1.msg" "squash1Set.gn" -na;
connectAttr "squash1GroupId2.msg" "squash1Set.gn" -na;
connectAttr "|pdtrans|pd.iog.og[2]" "squash1Set.dsm" -na;
connectAttr "nd.iog.og[2]" "squash1Set.dsm" -na;
connectAttr "sd.iog.og[2]" "squash1Set.dsm" -na;
connectAttr "squash1.msg" "squash1Set.ub[0]";
connectAttr "sine1.og[0]" "squash1GroupParts.ig";
connectAttr "squash1GroupId.id" "squash1GroupParts.gi";
connectAttr "sine1.og[1]" "squash1GroupParts1.ig";
connectAttr "squash1GroupId1.id" "squash1GroupParts1.gi";
connectAttr "sine1.og[2]" "squash1GroupParts2.ig";
connectAttr "squash1GroupId2.id" "squash1GroupParts2.gi";
connectAttr "sg1.pa" ":renderPartition.st" -na;
connectAttr "sg2.pa" ":renderPartition.st" -na;
connectAttr "sg3.pa" ":renderPartition.st" -na;
connectAttr "lambert2.msg" ":defaultShaderList1.s" -na;
connectAttr "lambert3.msg" ":defaultShaderList1.s" -na;
connectAttr "lambert4.msg" ":defaultShaderList1.s" -na;
connectAttr "lightLinker1.msg" ":lightList1.ln" -na;
connectAttr "hyperView1.msg" ":hyperGraphInfo.b[0]";
connectAttr "hyperView2.msg" ":hyperGraphInfo.b[1]";
// End of shadertest.ma
