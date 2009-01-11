<map version="0.9.0">
<!-- To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net -->
<node COLOR="#000000" CREATED="1231665242915" ID="ID_503716400" MODIFIED="1231665826369" TEXT="Sets User Interface">
<font NAME="SansSerif" SIZE="20"/>
<hook NAME="accessories/plugins/AutomaticLayout.properties"/>
<node COLOR="#0033ff" CREATED="1231665826349" ID="ID_295592491" MODIFIED="1231666726225" POSITION="right" TEXT="Functionality">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1231665430068" ID="ID_1961282426" MODIFIED="1231666740106" TEXT="Handle">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1231665436207" ID="ID_875484206" MODIFIED="1231665826365" TEXT="Shading Engines">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1231665440806" ID="ID_838965270" MODIFIED="1231665826366" TEXT="Object Sets">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1231665443266" ID="ID_715138824" MODIFIED="1231665826366" TEXT="Deformer Sets">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1231665842446" ID="ID_1465770629" MODIFIED="1231666139075" TEXT="Operations">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1231665979176" ID="ID_1654771601" MODIFIED="1231668876735" TEXT="Set Operations">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1231666088221" ID="ID_1331634348" MODIFIED="1231666093632" TEXT="Boolean">
<node COLOR="#111111" CREATED="1231665984036" ID="ID_627654286" MODIFIED="1231666075325" TEXT="Union">
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1231665986635" ID="ID_47432408" MODIFIED="1231666075326" TEXT="Intersection">
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1231665995646" ID="ID_1906636995" MODIFIED="1231666075326" TEXT="Subtraction">
<font NAME="SansSerif" SIZE="12"/>
</node>
</node>
<node COLOR="#111111" CREATED="1231666099202" ID="ID_1847815142" MODIFIED="1231666107414" TEXT="Result goes to">
<node COLOR="#111111" CREATED="1231666108422" ID="ID_1522619412" MODIFIED="1231666115654" TEXT="New Set"/>
<node COLOR="#111111" CREATED="1231666116062" ID="ID_139550696" MODIFIED="1231666120275" TEXT="Given Set"/>
</node>
</node>
<node COLOR="#990000" CREATED="1231666312893" ID="ID_839012743" MODIFIED="1231668869510" TEXT="Member Operations">
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1231666290603" ID="ID_1878654232" MODIFIED="1231666318219" TEXT="Add/Remove/Select">
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1231665845188" ID="ID_386198082" MODIFIED="1231666301084" TEXT="Object">
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1231665848648" ID="ID_1652687466" MODIFIED="1231666301085" TEXT="Component ( ? )">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Components should be displayed as groups of components like &quot;vtx[1-100] - this can be hard or inconvenient with the sets editor - perhaps a separate UI element needs to be used to display them
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="12"/>
</node>
</node>
</node>
</node>
</node>
<node COLOR="#0033ff" CREATED="1231666182546" ID="ID_1179111458" MODIFIED="1231667306331" POSITION="left" TEXT="Modules">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Modules have a clear python interface - the interface should be located where one expects it - thus there should be a nice interface for SelectionConnections as well as the various fliters
    </p>
  </body>
</html>
</richcontent>
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1231666185546" ID="ID_902888288" MODIFIED="1231668876734" TEXT="Set Outliner">
<edge STYLE="bezier" WIDTH="thin"/>
<arrowlink DESTINATION="ID_1654771601" ENDARROW="Default" ENDINCLINATION="-99;-110;" ID="Arrow_ID_20080497" STARTARROW="None" STARTINCLINATION="-278;-199;"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1231666193700" ID="ID_1574689200" MODIFIED="1231666365004" TEXT="Shows">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      implemented as a filter
    </p>
  </body>
</html>
</richcontent>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1231666370800" ID="ID_554256223" MODIFIED="1231666905014" TEXT="By Type">
<node COLOR="#111111" CREATED="1231666204367" ID="ID_960411114" MODIFIED="1231666212318" TEXT="Deformer Sets"/>
<node COLOR="#111111" CREATED="1231666206766" ID="ID_1207090096" MODIFIED="1231666210398" TEXT="Shading Engines"/>
<node COLOR="#111111" CREATED="1231666213346" ID="ID_957312718" MODIFIED="1231666216379" TEXT="Object Sets"/>
<node COLOR="#111111" CREATED="1231666220428" ID="ID_338888063" MODIFIED="1231666381668" TEXT="[ Multiple ]">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Are combinations truly important - yes, if people want to shade things in a deformer set differently for example - it should be easy to select items in one set
    </p>
  </body>
</html></richcontent>
</node>
</node>
<node COLOR="#111111" CREATED="1231666394895" ID="ID_1068207096" MODIFIED="1231666908335" TEXT="By Function">
<node COLOR="#111111" CREATED="1231666413258" ID="ID_198887807" MODIFIED="1231667443220" TEXT="Sets from Selection">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Show all sets affecting the current selection of objects ( or sets )
    </p>
    <p>
      Includes &quot;Follow Selection&quot; mode where it will autoupdate whenever the selection changes
    </p>
  </body>
</html>
</richcontent>
</node>
<node COLOR="#111111" CREATED="1231666922704" ID="ID_1968843072" MODIFIED="1231667033785" TEXT="By Name">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Similar to the default outliner functionality, but possibly easier to use - perhaps it should not always take up space and should dynamically blend in if requested
    </p>
  </body>
</html>
</richcontent>
</node>
</node>
</node>
<node COLOR="#990000" CREATED="1231667624262" ID="ID_1720794262" MODIFIED="1231667680892" TEXT="Display Optional Display Port">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Visualizes shader attached to a shading engine
    </p>
  </body>
</html>
</richcontent>
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1231666697952" ID="ID_1376893876" MODIFIED="1231668869509" TEXT="Member Outliner">
<edge STYLE="bezier" WIDTH="thin"/>
<arrowlink DESTINATION="ID_839012743" ENDARROW="Default" ENDINCLINATION="-149;48;" ID="Arrow_ID_642131958" STARTARROW="None" STARTINCLINATION="-221;186;"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1231666783817" ID="ID_1237415301" MODIFIED="1231666785708" TEXT="Shows">
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1231667044549" ID="ID_1302180209" MODIFIED="1231667046722" TEXT="Types">
<node COLOR="#111111" CREATED="1231666786318" ID="ID_1994936662" MODIFIED="1231666800249" TEXT="Object Members"/>
<node COLOR="#111111" CREATED="1231666801419" ID="ID_1112300028" MODIFIED="1231666878194" TEXT="Components">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Components must be shown in a separate User Interface portion as the outliner will show each component ID as a separate entry by default which is unusable
    </p>
  </body>
</html></richcontent>
</node>
</node>
</node>
<node COLOR="#990000" CREATED="1231667050211" ID="ID_547966481" MODIFIED="1231667347052" TEXT="By Function">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Reminds me of the default outliner functionality
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1231667147728" ID="ID_637530474" MODIFIED="1231667224923" TEXT="By Object Type"/>
<node COLOR="#111111" CREATED="1231667153496" ID="ID_1753692197" MODIFIED="1231667156488" TEXT="By Name"/>
</node>
<node COLOR="#990000" CREATED="1231668930909" ID="ID_144939776" MODIFIED="1231669003981" TEXT="Input">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Input is sets, thus it is reacting to change events of the respective selection lists. All this is done by the main layout combining and setting up the modules
    </p>
  </body>
</html>
</richcontent>
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
</node>
<node COLOR="#0033ff" CREATED="1231666551638" ID="ID_676798257" MODIFIED="1231667350594" POSITION="left" TEXT="Interaction Via">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Most commonly used switches and functions should be either on a visible button, or in a marking menu
    </p>
  </body>
</html>
</richcontent>
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1231666559346" ID="ID_572205765" MODIFIED="1231666716381" TEXT="Marking Menus">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1231666564686" ID="ID_1138641907" MODIFIED="1231666716382" TEXT="RMB Popups">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1231667760309" ID="ID_593181797" MODIFIED="1231667895917" TEXT="Module RMB Menu API">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Provide Callbacks to hook own functions into the RMB Click menus, allowing to costumize the result according to the configuration of the user interface ( i.e. different types of sets might offer different special functions )
    </p>
  </body>
</html>
</richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node COLOR="#0033ff" CREATED="1231667310951" ID="ID_231441699" MODIFIED="1231668923888" POSITION="left" TEXT="Special Cases">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Handle:
    </p>
    <p>
      Scene Changes
    </p>
  </body>
</html>
</richcontent>
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
</node>
</node>
</map>
