<map version="0.9.0_Beta_8">
<!-- To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net -->
<attribute_registry SHOW_ATTRIBUTES="hide"/>
<node COLOR="#000000" CREATED="1208681350261" ID="ID_823383288" MODIFIED="1208686877317" TEXT="MayaRVIndex">
<font NAME="SansSerif" SIZE="20"/>
<hook NAME="accessories/plugins/AutomaticLayout.properties"/>
<node COLOR="#0033ff" CREATED="1208686847712" HGAP="84" ID="ID_1582204477" MODIFIED="1208702319183" POSITION="right" TEXT="Packaging" VSHIFT="-90">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1208686978207" ID="ID_986166965" MODIFIED="1208701189331" TEXT="Structure ( internal )">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208695747290" ID="ID_1647776166" MODIFIED="1208701234857" TEXT="Byronimo(folder)">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Contains python scripts, thus this is the python root folder
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1208696822484" HGAP="26" ID="ID_358119350" MODIFIED="1208701237311" TEXT="docs(folder)" VSHIFT="1">
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1208696839488" ID="ID_1880796830" MODIFIED="1208696880119" TEXT="API">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Contains from-source API documentation to allow easy reusage of all the code and libraries
    </p>
  </body>
</html></richcontent>
</node>
<node COLOR="#111111" CREATED="1208696843361" ID="ID_1084301193" MODIFIED="1208696986782" TEXT="User">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Offline Version of online WIKI - at some point users should be able to adjust the documentation according to their needs and add missing information - after all its an open source project
    </p>
  </body>
</html></richcontent>
</node>
</node>
<node COLOR="#990000" CREATED="1208701224157" ID="ID_285719389" MODIFIED="1208701261321" TEXT="Readme.txt">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      General Information about authors and the project.
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208695768761" ID="ID_1383010455" MODIFIED="1208696346577" TEXT="Types">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      At the beginning of the development, only tools packages will be released as frequent as possible, being as versatile as possible.
    </p>
    <p>
      Once all that integrates into a bigger system, the indivudual tools should only be packaged together.
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208695778226" ID="ID_1900683521" MODIFIED="1208696101137" TEXT="1. Tool Package">
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1208695916219" ID="ID_293056637" MODIFIED="1208696050479" TEXT="Only one tool including of prerequesites"/>
<node COLOR="#111111" CREATED="1208696052141" ID="ID_1116124689" MODIFIED="1208696088295" TEXT="All tools are part of the main system"/>
</node>
<node COLOR="#990000" CREATED="1208695784025" ID="ID_524381597" MODIFIED="1208797563165" TEXT="2. Complete Package. ">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Once complete packages are being released, Tools should not be available individually anymore.
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1208695906106" HGAP="36" ID="ID_38366676" MODIFIED="1208696625757" TEXT="Contains all tools and thus all code" VSHIFT="2"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208696631733" HGAP="30" ID="ID_1361501986" MODIFIED="1208931933650" TEXT="Utilities" VSHIFT="11">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208696636806" ID="ID_649327739" MODIFIED="1208696677223" TEXT="SCons">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Use SCons to define packages, manage dependencies and to get it all together.
    </p>
    <p>
      Works on all target platforms and appears to be mature
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1208696887739" ID="ID_909606764" MODIFIED="1208696948465" TEXT="wget">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Generate offline version of online wiki containing all the data. This will only be possible if a proper index is given which in turn (indirectly) links to all desired documents and images.
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1208931933628" ID="ID_1640886407" MODIFIED="1208931959678" TEXT="Not Required">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      See distutils
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1208701194338" ID="ID_426472722" MODIFIED="1208931933644" TEXT="Installer">
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1208701265956" ID="ID_1319676793" MODIFIED="1208701292397" TEXT="NSIS">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Nullsoft Installer - Linux and Windows Only - no macosx
    </p>
  </body>
</html></richcontent>
</node>
<node COLOR="#111111" CREATED="1208701293730" ID="ID_827317582" MODIFIED="1208701320018" TEXT="Bitrock">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Comercial Installer for most of the systems, but appears to be free for opensource projects
    </p>
  </body>
</html></richcontent>
</node>
<node COLOR="#111111" CREATED="1208701825274" ID="ID_1325438934" MODIFIED="1208701875470" TEXT="Distutils">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Python-Included utils could possibly do the job too, assumed there is an easy to use gui installer for it.
    </p>
    <p>
      <b>TODO: Evaluate</b>
    </p>
  </body>
</html></richcontent>
</node>
</node>
</node>
</node>
<node COLOR="#00b439" CREATED="1208931768257" ID="ID_853271748" LINK="file:///usr/share/doc/python2.4/html/dist/built-dist.html" MODIFIED="1208931922428" TEXT="Python Built Distribution">
<edge STYLE="bezier" WIDTH="thin"/>
<font BOLD="true" NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node COLOR="#0033ff" CREATED="1208686877280" HGAP="97" ID="ID_335446280" MODIFIED="1208686905096" POSITION="right" TEXT="Deployment" VSHIFT="8">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1208701506163" ID="ID_294532007" MODIFIED="1208701615009" TEXT="1. Packages">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      For all those that do not want to execute an exe file
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1208701492343" ID="ID_631744321" MODIFIED="1208701697693" TEXT="2. Self-Install Packages">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Using packaging tools, allows quick-and-easy installation of all required files.
    </p>
    <p>
      Should just be seen as second step, as it might not be available for the first releases. Package creator utilities should be able to create both outputs at the same time though
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208686857455" ID="ID_882930763" MODIFIED="1208701809118" TEXT="Versioning">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      You can only run one version of the tools at the time - packages to be installed must deal with possibly of already installed versions.
    </p>
    <p>
      Having an installation routine greatly helps the idea that you are dealing with professional software.
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
</node>
<node COLOR="#0033ff" CREATED="1208870853042" ID="ID_1565932175" LINK="MayaRV_Development.mm" MODIFIED="1208870853043" POSITION="left" TEXT="Development">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
</node>
<node COLOR="#0033ff" CREATED="1208789464984" HGAP="110" ID="ID_1157250519" LINK="MayaRV_PackageStructure.mm" MODIFIED="1208789473175" POSITION="left" TEXT="Package Structure" VSHIFT="-4">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
</node>
<node COLOR="#0033ff" CREATED="1208797486585" HGAP="112" ID="ID_645288055" MODIFIED="1208871730909" POSITION="left" TEXT="Project Management" VSHIFT="3">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1208797495915" ID="ID_1723405654" MODIFIED="1208797497868" TEXT="Trac">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node COLOR="#0033ff" CREATED="1208729970934" HGAP="106" ID="ID_548235644" MODIFIED="1208731532687" POSITION="left" TEXT="Useful Python Packages" VSHIFT="42">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1208729981038" ID="ID_775477198" MODIFIED="1208729984852" TEXT="ConfigParser">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208729986307" ID="ID_1641434172" MODIFIED="1208730000512" TEXT="INI File Handling">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208730020589" ID="ID_721429745" MODIFIED="1208730023195" TEXT="Chunk">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208730023945" ID="ID_736162117" MODIFIED="1208730027088" TEXT="Chunk File Handling">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208730046854" ID="ID_1548247275" MODIFIED="1208730049713" TEXT="Base64">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208730050375" ID="ID_147461463" MODIFIED="1208730058683" TEXT="binary ascii representation">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208730226851" ID="ID_144077163" MODIFIED="1208730236200" TEXT="Codecs">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208730237662" ID="ID_220945861" MODIFIED="1208730242481" TEXT="Ascii Data Encoding">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208730292078" ID="ID_475247434" MODIFIED="1208730294057" TEXT="Colorsys">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208730295416" ID="ID_185223628" MODIFIED="1208730301402" TEXT="Color Space Conversion Functions">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208730321976" ID="ID_1535759623" MODIFIED="1208730323603" TEXT="commands">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208730324167" ID="ID_394568428" MODIFIED="1208730329760" TEXT="Simple Shell Command Execution">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208991139528" ID="ID_1183242489" MODIFIED="1208991140991" TEXT="cmd">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208991141847" ID="ID_1111208181" MODIFIED="1208991155398" TEXT="for simple commandline interface for interactive sessions">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208730662852" ID="ID_1602107256" MODIFIED="1208730688308" TEXT="difflib">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Could possibly be used for more advanced stuff too ...
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208730665793" ID="ID_779880822" MODIFIED="1208730671750" TEXT="Compare Sequences Of Any Type">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208730866818" ID="ID_346651602" MODIFIED="1208731127381" TEXT="fnmatcher">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208730870028" ID="ID_414064546" MODIFIED="1208730877718" TEXT="Shell-like file globbing">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208731130783" ID="ID_1002114975" MODIFIED="1208731134614" TEXT="gettext">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208731135884" ID="ID_1164914811" MODIFIED="1208731155810" TEXT="Internationalization and Localization">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208731240472" ID="ID_1429028921" MODIFIED="1208731245173" TEXT="hashlib">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208731246191" ID="ID_1659332640" MODIFIED="1208731262360" TEXT="generate hash digests and encriptions">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208731386962" ID="ID_889112511" MODIFIED="1208731390470" TEXT="heapq">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208731391560" ID="ID_789020398" MODIFIED="1208731398702" TEXT="fast priority queue">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208731501499" ID="ID_1328227985" MODIFIED="1208731504559" TEXT="Hotshots">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208731504562" ID="ID_408786427" MODIFIED="1208731509520" TEXT="profiling python code">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208731818542" ID="ID_1726404059" MODIFIED="1208731819835" TEXT="Logging">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1208732164197" ID="ID_1916695079" MODIFIED="1208732166973" TEXT="rexec">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208732167913" ID="ID_65746458" MODIFIED="1208732172105" TEXT="Restricted Code Execution">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208732419342" ID="ID_1668698278" MODIFIED="1208732425980" TEXT="shelve">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208732426909" ID="ID_3942446" MODIFIED="1208732436386" TEXT="persistent dictionary of pickled objects">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208732633615" ID="ID_143171812" MODIFIED="1208732636090" TEXT="subprocess">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208732636732" ID="ID_1242352395" MODIFIED="1208732648323" TEXT="handle multiple processes and connect them by pipes">
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1208871772646" ID="ID_456628903" MODIFIED="1208871787333" TEXT="simple to use, much better to starting a subshell in that sense">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208732716874" ID="ID_785800423" MODIFIED="1208732718781" TEXT="tempfile">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208732719428" ID="ID_203886283" MODIFIED="1208732726626" TEXT="get temp files and directories">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208732740226" ID="ID_1729433696" MODIFIED="1208732944647" TEXT="unittest">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208732742282" ID="ID_421494221" MODIFIED="1208732744368" TEXT="unit testing">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208732796547" ID="ID_1554521625" MODIFIED="1208732802123" TEXT="threading">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208732802833" ID="ID_119016916" MODIFIED="1208732810764" TEXT="implement multiple threads">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208733150591" ID="ID_1664558224" MODIFIED="1208733152651" TEXT="uu">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208733153236" ID="ID_913673228" MODIFIED="1208733160854" TEXT="typical uu codec">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208733030786" ID="ID_997954001" MODIFIED="1208733032701" TEXT="uuid">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208733033296" ID="ID_1963923287" MODIFIED="1208733041756" TEXT="get unique id  for current host">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208733189269" ID="ID_196744911" MODIFIED="1208733195741" TEXT="weakref">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208733196386" ID="ID_1960035635" MODIFIED="1208733209380" TEXT="weakreferences to allow proper garbagecollection">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208733296571" ID="ID_882797852" MODIFIED="1208733299636" TEXT="webbrowser">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208733300555" ID="ID_458863765" MODIFIED="1208733310660" TEXT="control webbrowsers for this environment">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208977953326" ID="ID_1408922364" MODIFIED="1208977956200" TEXT="Itertools">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208977956914" ID="ID_1590978091" MODIFIED="1208977966897" TEXT="very useful tools for iterating over sequences !!">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
</node>
<node COLOR="#0033ff" CREATED="1208697693750" ID="ID_1261545421" MODIFIED="1208871761957" POSITION="left" TEXT="License">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1208697697306" ID="ID_1685180373" MODIFIED="1208871761957" TEXT="MIT">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1208697699108" ID="ID_340648720" MODIFIED="1208871761958" TEXT="GNU">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
</node>
</map>
