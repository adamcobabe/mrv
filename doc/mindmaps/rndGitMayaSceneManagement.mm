<map version="0.9.0">
<!-- To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net -->
<node COLOR="#000000" CREATED="1255334389537" ID="ID_1895713059" MODIFIED="1255334456615" TEXT="MayaSceneManagement">
<font NAME="SansSerif" SIZE="20"/>
<hook NAME="accessories/plugins/AutomaticLayout.properties"/>
<node COLOR="#0033ff" CREATED="1255334458054" ID="ID_831971695" MODIFIED="1255335931743" POSITION="left" TEXT="Idioms">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1255334632776" HGAP="52" ID="ID_774583634" MODIFIED="1255334724015" TEXT="Keep own object store for Data Objects allowing all data to be centrally shared" VSHIFT="-9">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1255334700353" HGAP="50" ID="ID_763708773" MODIFIED="1255334720836" TEXT="Maya Scene Files only keep a pointer to the respective Tree in the Repository" VSHIFT="-23">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1255335884356" ID="ID_335633930" MODIFIED="1255335902912" TEXT="Merges can be done on scene level which is important for referencing">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node COLOR="#0033ff" CREATED="1255336976242" ID="ID_616386920" MODIFIED="1255336981873" POSITION="right" TEXT="Repacking">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1255336983003" ID="ID_379181543" MODIFIED="1255337041071" TEXT="Delta-Pack objects based based on object selection by walking commits-&gt;dags-&gt;objects to find similar ones">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node COLOR="#0033ff" CREATED="1255337046412" ID="ID_148417607" MODIFIED="1255337050576" POSITION="right" TEXT="Object Storage">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1255337051484" ID="ID_1366955176" MODIFIED="1255337075768" TEXT="Local storages for cloned repos, but Alternates must be supported to write objects locally, but send them to the server on push">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node COLOR="#0033ff" CREATED="1255335914132" FOLDED="true" ID="ID_1437325475" MODIFIED="1255336973346" POSITION="right" TEXT="Data Layout">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1255334479292" ID="ID_1300571964" MODIFIED="1255335924777" TEXT="Tree">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1255334483068" ID="ID_802463061" MODIFIED="1255335924777" TEXT="Tree is DAG">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1255334490812" ID="ID_1064034026" MODIFIED="1255335924778" TEXT="SubTree is DG">
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1255334511452" ID="ID_1197725089" MODIFIED="1255334524168" TEXT="Keeps references into DAG"/>
</node>
<node COLOR="#111111" CREATED="1255334500100" ID="ID_1839733943" MODIFIED="1255335924779" TEXT="Handles instances specifically">
<font NAME="SansSerif" SIZE="12"/>
</node>
</node>
</node>
<node COLOR="#00b439" CREATED="1255334463371" ID="ID_1522974953" MODIFIED="1255336341547" TEXT="Blob">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Keep Object Data
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1255334547830" ID="ID_1357196044" MODIFIED="1255335924793" TEXT="ObjectType">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1255334553797" ID="ID_671440156" MODIFIED="1255335924794" TEXT="All non-default attribute values">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1255334749683" ID="ID_236801204" MODIFIED="1255336139735" TEXT="Index Layout">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Prefixes for can generally be indexed
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1255334756385" ID="ID_100809299" MODIFIED="1255335924817" TEXT="DAG Paths">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1255335044760" ID="ID_1041300063" MODIFIED="1255335924818" TEXT="trans SHA">
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1255334961655" ID="ID_77044496" MODIFIED="1255335924818" TEXT="trans/shape SHA">
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1255334997975" ID="ID_1392878910" MODIFIED="1255335924819" TEXT="trans2/$1 0000">
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1255335013656" ID="ID_706857175" MODIFIED="1255335022196" TEXT="==reference to first entry in index"/>
</node>
<node COLOR="#111111" CREATED="1255336032215" ID="ID_368682030" MODIFIED="1255336714104">
<richcontent TYPE="NODE"><html>
  <head>
    
  </head>
  <body>
    <p>
      #r:SHA
    </p>
    <p>
      #r:scenes/20/40a/ani
    </p>
  </body>
</html></richcontent>
<node COLOR="#111111" CREATED="1255336284588" ID="ID_517791658" MODIFIED="1255336618950">
<richcontent TYPE="NODE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Reference Index to Refs or Tree SHAs. Refs pull the latest version, Tree SHAs keep version consistent ( like a submodule )
    </p>
  </body>
</html></richcontent>
</node>
</node>
<node COLOR="#111111" CREATED="1255336162882" ID="ID_758807338" MODIFIED="1255336174085" TEXT="#ns:">
<node COLOR="#111111" CREATED="1255336289716" ID="ID_1727395876" MODIFIED="1255336292240" TEXT="Namespace Index"/>
</node>
</node>
<node COLOR="#990000" CREATED="1255335091842" ID="ID_1083126322" MODIFIED="1255336118402" TEXT="DG">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Part of the index, but in own namespace
    </p>
    <p>
      Lists individual edges
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1255335169084" ID="ID_650521404" MODIFIED="1255336202849">
<richcontent TYPE="NODE"><html>
  <head>
    
  </head>
  <body>
    <p>
      #dga:/attr1
    </p>
    <p>
      #dga:/attr2
    </p>
  </body>
</html></richcontent>
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      &#160;Index of all attribute names ( long ) used in the dg - this is an insurance agains changes in the ordering of attributes between maya versions
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1255335315178" ID="ID_179711944" MODIFIED="1255336219495" TEXT="#dg:$1&amp;0/$2&amp;0">
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1255335598582" ID="ID_158534855" MODIFIED="1255335609937" TEXT="Edge from trans.attr1 to trans2.attr1"/>
</node>
</node>
</node>
<node COLOR="#00b439" CREATED="1255336411759" ID="ID_46342405" MODIFIED="1255336487348" TEXT="Commit/Scene">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1255336414639" ID="ID_1832786594" MODIFIED="1255336424563" TEXT="Tree to our scene State">
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1255336425015" ID="ID_1516021290" MODIFIED="1255336481116" TEXT="Each Scene has own deleveopment stream">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
</node>
<node COLOR="#0033ff" CREATED="1255335933884" ID="ID_1532811018" MODIFIED="1255335935792" POSITION="right" TEXT="Referencing">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1255336759166" ID="ID_503713908" MODIFIED="1255336772650" TEXT="SubTree merge scenes into own scene">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1255336776431" ID="ID_782680629" MODIFIED="1255336799162" TEXT="Changes are handled by diffing states - HOW TO KEEP THINGS SEPARATE ?">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node COLOR="#0033ff" CREATED="1255336830648" ID="ID_428949051" MODIFIED="1255336835355" POSITION="right" TEXT="Scene Layers">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1255336836559" ID="ID_1640649698" MODIFIED="1255336867116" TEXT="Would be Branches on top of our main scene that get rebased automatically whenever the main branch changes">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
</node>
</map>
