<map version="0.9.0">
<!-- To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net -->
<node COLOR="#000000" CREATED="1231853290116" ID="ID_1847882576" MODIFIED="1231855894290" TEXT="FileStack">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Simple to configure main buttons and elements upon initialization
    </p>
  </body>
</html>
</richcontent>
<font NAME="SansSerif" SIZE="20"/>
<hook NAME="accessories/plugins/AutomaticLayout.properties"/>
<node COLOR="#0033ff" CREATED="1231855514342" ID="ID_1037771733" MODIFIED="1231855516535" POSITION="left" TEXT="BaseModules">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1231855269305" ID="ID_797594974" MODIFIED="1231855519803" TEXT="ItemArray">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Linked list of items allowing to add/remove items and to listen to events of children in general ( perhaps it would be easier not to overgeneralize it, but I could imagine an item array of item array forming a new way of viewing the dependency graph for instance
    </p>
  </body>
</html>
</richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1231855494091" ID="ID_865016219" MODIFIED="1231855519794" TEXT="iItem">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Simple interface allowing itemArray to communicate to children
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1231855654076" ID="ID_768116134" MODIFIED="1231855707718" TEXT="VirtualGrid">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Horizontal and/or vertical form layout allowing to dynamically add and remove children. If appropriate, it shows intScrollBars that allow to scrub through the items
    </p>
  </body>
</html>
</richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node COLOR="#0033ff" CREATED="1231855245206" ID="ID_440261336" MODIFIED="1231855246640" POSITION="left" TEXT="Modules">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1231855527584" ID="ID_951373937" MODIFIED="1231855532216" TEXT="ItemScrollList">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1231855533885" ID="ID_1652047197" MODIFIED="1231855552604" TEXT="Filtering Support">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Custom Filters with custom user interfaces
    </p>
  </body>
</html>
</richcontent>
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1231855721409" ID="ID_1658196292" MODIFIED="1231855816140" TEXT="FileList">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Same as ItemScrollList, but shows files given by folder selection in ItemScrollLists, filter support
    </p>
  </body>
</html>
</richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1231855827020" ID="ID_252683111" MODIFIED="1231855840479" TEXT="FileStack">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      show all selected files
    </p>
  </body>
</html>
</richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1231855928477" ID="ID_330369415" MODIFIED="1231856006960" TEXT="TabLayout">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Showing the base folders as defined by itemarrays in virtual grids.
    </p>
  </body>
</html>
</richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1231855842276" ID="ID_426119747" MODIFIED="1231855927280" TEXT="MainForm">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Show all elements together to form a file browser
    </p>
  </body>
</html>
</richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node COLOR="#0033ff" CREATED="1231856014241" ID="ID_566502224" MODIFIED="1231856020001" POSITION="right" TEXT="Easily browse files">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
</node>
<node COLOR="#0033ff" CREATED="1231856020330" ID="ID_690596669" MODIFIED="1231856034842" POSITION="right" TEXT="remember (sub)path portions and reapply them">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
</node>
<node COLOR="#0033ff" CREATED="1231856038151" ID="ID_1625213168" MODIFIED="1231856069281" POSITION="right" TEXT="allow to selected several files and/or folders at once">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
</node>
<node COLOR="#0033ff" CREATED="1231856116312" ID="ID_494001347" MODIFIED="1231856123524" POSITION="right" TEXT="Customizable filtering">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
</node>
<node COLOR="#0033ff" CREATED="1231856126332" ID="ID_898800468" MODIFIED="1231856146364" POSITION="right" TEXT="Flexible main layouts allow to add your own pieces or build your completely own version of it">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
</node>
</node>
</map>
