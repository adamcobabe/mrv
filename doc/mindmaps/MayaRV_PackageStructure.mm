<map version="0.9.0_Beta_8">
<!-- To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net -->
<node COLOR="#000000" CREATED="1208686967220" HGAP="117" ID="ID_526511468" LINK="MRVIndex.mm" MODIFIED="1208870099182" TEXT="Byronimo" VSHIFT="-51">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Root folder of all python scripts, maya and possibly more
    </p>
    <p>
      Follows Function
    </p>
    <p>
      <b>ALL PYTHON2.4 COMPATIBLE </b>! ( as it is used in Maya 8.5 )
    </p>
  </body>
</html>
</richcontent>
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="20"/>
<hook NAME="accessories/plugins/AutomaticLayout.properties"/>
<node COLOR="#0033ff" CREATED="1208870015264" ID="ID_1599971565" MODIFIED="1208873929005" POSITION="left" TEXT="Maya">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      contains all maya python code
    </p>
  </body>
</html></richcontent>
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1208695825422" ID="ID_728082396" MODIFIED="1208900165398" TEXT="Core">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208789494621" HGAP="15" ID="ID_1491827883" MODIFIED="1208900194489" TEXT="dgnode" VSHIFT="-5">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      DG node wrapped into python class
    </p>
    <p>
      Read all values using this object
    </p>
    <p>
      Basis for d[a]gmod package
    </p>
    <p>
      event handlers for changes to the node
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1208870553235" ID="ID_1697409774" MODIFIED="1208900190846" TEXT="dagnode">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      wraps a dag node, allows query access to parents, children and instance information
    </p>
  </body>
</html></richcontent>
<font BOLD="true" NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1208870694432" ID="ID_9030483" MODIFIED="1208900190847" TEXT="info">
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1208789656464" ID="ID_966022134" MODIFIED="1208870187008" TEXT="Wrap a maya object into a python class instance">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Allows to manipulate maya objects natively with python code
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1208790202692" ID="ID_418028408" MODIFIED="1208870187008" TEXT="Allow EventHandling  for use with D[A]G Manipulation">
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1208799022592" ID="ID_534101278" MODIFIED="1208870187009" TEXT="( Modify class definitions at runtime - dynamically on demand )">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Keep one-time on demand record of attributes in a class variable to allow instances to quickly set themselfes up dynamically without querying maya again.
    </p>
    <p>
      Implies special handling for custom attributes, that the instance has to gather on instance creation time anyway -&gt; performance tests should show whether this makes a difference - memory wise its just a few strings
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1208799887149" ID="ID_704308920" MODIFIED="1208870187009" TEXT="Override __getattr__ and __setattr__ accordingly">
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1208799930184" ID="ID_756229448" MODIFIED="1208870187009" TEXT="Mimic object inheritance employed by maya itself and delegate !">
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1208870526572" ID="ID_1300292838" MODIFIED="1208870526572" TEXT="PyClass-to-Maya Object"/>
</node>
</node>
<node COLOR="#990000" CREATED="1208789728899" ID="ID_328303614" MODIFIED="1208874120635" TEXT="dgmod">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Alter DG Objects with built-in undo - for database like atomic behaviour and rollback functionality
    </p>
    <ul>
      <li>
        Names
      </li>
      <li>
        Custom Attributes
      </li>
      <li>
        Connections
      </li>
    </ul>
    <p>
      Should probably use DGModifier to work as it already has such functionality.
    </p>
    <p>
      Assure <b>undo/redo work </b>properly with that system !
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1208789750069" HGAP="56" ID="ID_1207225140" MODIFIED="1208874120636" TEXT="dagmod" VSHIFT="12">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Inherits from DG Manipulation, but allows additionally to change DAG relations:
    </p>
    <ul>
      <li>
        Hierarchy Edits
      </li>
      <li>
        Instancing
      </li>
    </ul>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="12"/>
</node>
</node>
<node COLOR="#990000" CREATED="1208727811137" ID="ID_1644678651" MODIFIED="1208874120638" TEXT="exceptions">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1208870378751" ID="ID_908880237" MODIFIED="1208874120640" TEXT="utilities">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      maya specific utilities
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208726371715" FOLDED="true" ID="ID_687382456" MODIFIED="1208899968727" STYLE="bubble" TEXT="UI">
<edge STYLE="bezier" WIDTH="thin"/>
<font BOLD="true" NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208795686031" ID="ID_229971882" MODIFIED="1208899968735" TEXT="common">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1208795699738" ID="ID_469427823" MODIFIED="1208899968737" TEXT="exceptions">
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1208800007006" ID="ID_1598483566" MODIFIED="1208899968738" TEXT="Specialized UI exceptions"/>
</node>
<node COLOR="#111111" CREATED="1208795784456" ID="ID_341880042" MODIFIED="1208899968738" TEXT="logging">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Logging facilities specialized on usage with UIs
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1208795809540" ID="ID_487197493" MODIFIED="1208899968740">
<richcontent TYPE="NODE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Assure user <b>sees and understands</b> what is happening
    </p>
  </body>
</html></richcontent>
</node>
<node COLOR="#111111" CREATED="1208795931121" ID="ID_1946040871" MODIFIED="1208899968744" TEXT="Allow general setting on how errors should be presented"/>
<node COLOR="#111111" CREATED="1208795996129" ID="ID_259845822" MODIFIED="1208899968745" TEXT="Allow general setting on how progress should be presented"/>
<node COLOR="#111111" CREATED="1208796065701" ID="ID_959182241" MODIFIED="1208899968746" TEXT="UI Implementor should not be forced to implement such things manually"/>
<node COLOR="#111111" CREATED="1208796094398" ID="ID_1271884756" MODIFIED="1208899968746" TEXT="Allow implementor to tag messages and indicate certain behaviour"/>
</node>
</node>
<node COLOR="#990000" CREATED="1208792341718" ID="ID_1155069885" MODIFIED="1208899968747" TEXT="ELF Elements">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      ELF Elements wrapped in Python Objects to allow building UI structures and setting callbacks.
    </p>
    <p>
      As objects can be instantiated, unique names must be generated by the python wrappers for the underlying maya elf widget
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1208795322676" ID="ID_172242844" MODIFIED="1208899968748" TEXT="Python Class Instance Wraps ELF UI Element">
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1208795337194" ID="ID_860750478" MODIFIED="1208899968749">
<richcontent TYPE="NODE"><html>
  <head>
    
  </head>
  <body>
    <p>
      <b>UI Hierarchy</b> kept using inter-object links for easy traversal
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1208796344657" ID="ID_315793483" MODIFIED="1208899968753" TEXT="Thus Python Wrapper Classes will always be returned"/>
</node>
<node COLOR="#111111" CREATED="1208795447423" ID="ID_1560196137" MODIFIED="1208899968754" TEXT="No additional functionality added - just make UI elements object oriented">
<font BOLD="true" NAME="SansSerif" SIZE="12"/>
</node>
</node>
<node COLOR="#990000" CREATED="1208795495270" ID="ID_440565646" MODIFIED="1208899968754" TEXT="ELF Widgets">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      More powerful abstractions of ELF Elements, like Filebrowsers and easily usable outliners
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1208796798140" ID="ID_47697126" MODIFIED="1208899968755" TEXT="Logging">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Allow to review log results
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1208796819061" ID="ID_733862618" MODIFIED="1208899968756" TEXT="filebrowser">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      simple file browser, different appearances and optimizations dependant on the desired context
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1208797776257" ID="ID_417275632" MODIFIED="1208899968757" TEXT="get_child_by_index"/>
<node COLOR="#111111" CREATED="1208797783838" ID="ID_11261622" MODIFIED="1208899968758" TEXT="get_child_bz_index"/>
</node>
</node>
<node COLOR="#990000" CREATED="1208795631299" HGAP="39" ID="ID_1019150049" MODIFIED="1208899968758" TEXT="Editors" VSHIFT="39">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      MUST be divided into indivudal parts that can be used individually - internal folder and file structure follows this idiom !
    </p>
    <p>
      Editors must be reusable, and it should be easy to make them a panel ( perhaps they can do that automatically even or greatly aided by utilities )
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1208796878888" ID="ID_1759671682" MODIFIED="1208899968759" TEXT="Sets" VSHIFT="-6">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Manipulate all kinds of sets , properly and conveniently !
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1208800619373" ID="ID_1296655037" MODIFIED="1208899968760" TEXT="( Maya General Preferences )">
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1208800631016" ID="ID_1782625409" MODIFIED="1208899968761" TEXT="Together with Configuration Management useful for even switching between users in the same session"/>
</node>
<node COLOR="#111111" CREATED="1208797619823" ID="ID_1404441232" MODIFIED="1208899968761">
<richcontent TYPE="NODE"><html>
  <head>
    
  </head>
  <body>
    <p>
      ... at some point, all major UIs should be replaced with rewrites, finally the maya main UI itself ...&#160;
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="12"/>
</node>
</node>
<node COLOR="#990000" CREATED="1208793371159" HGAP="44" ID="ID_1208733062" MODIFIED="1208899968765" TEXT="util" VSHIFT="22">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
<node COLOR="#111111" CREATED="1208791929797" HGAP="58" ID="ID_1724488808" MODIFIED="1208899968769" TEXT="GUI Code Generator" VSHIFT="1">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1208791978064" ID="ID_901541965" MODIFIED="1208899968773" TEXT="Build ELF Widget Python Code using compatible .glade3 XML definitions">
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1208793400134" ID="ID_1955477832" MODIFIED="1208899968773" TEXT="Attach custom code in glade using some field that is otherwise unused in maya widgets"/>
<node COLOR="#111111" CREATED="1208792053029" ID="ID_324458944" MODIFIED="1208899968774" TEXT="Code can contain customizations in all other blocks but the autogenerated ones">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      See approach of wxglade to handle these sections
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="12"/>
</node>
<node COLOR="#111111" CREATED="1208794829769" ID="ID_1723202114" MODIFIED="1208899968775">
<richcontent TYPE="NODE"><html>
  <head>
    
  </head>
  <body>
    <p>
      wxGlade<b>VS</b>glade
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1208794677999" ID="ID_612456422" MODIFIED="1208899968781" TEXT="wxGlade">
<node COLOR="#111111" CREATED="1208794683941" ID="ID_1360481858" MODIFIED="1208899968783" TEXT="Simpler - less attributes that do not make sense to maya">
<edge COLOR="#00ff08"/>
</node>
<node COLOR="#111111" CREATED="1208795142528" ID="ID_122768766" MODIFIED="1208899968783" TEXT="Could be adjusted to match maya needs">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      As it is python code after all, using wx libraries
    </p>
  </body>
</html></richcontent>
<edge COLOR="#00ff08"/>
</node>
<node COLOR="#111111" CREATED="1208794697305" ID="ID_1410865435" MODIFIED="1208899968784" TEXT="Would not support custom code since there is no field for it">
<edge COLOR="#ff0000"/>
</node>
<node COLOR="#111111" CREATED="1208794784510" ID="ID_1178146729" MODIFIED="1208899968785" TEXT="Version 0.5 indicates pre-mature status">
<edge COLOR="#ff0003"/>
</node>
</node>
<node COLOR="#111111" CREATED="1208794949319" ID="ID_121524152" MODIFIED="1208899968785" TEXT="glade3">
<node COLOR="#111111" CREATED="1208794954007" ID="ID_166369126" MODIFIED="1208899968787" TEXT="Feels very mature and looks excellent">
<edge COLOR="#0cff00"/>
</node>
<node COLOR="#111111" CREATED="1208794966617" ID="ID_1402605783" MODIFIED="1208899968787" TEXT="plug-in system for code-generators and such">
<edge COLOR="#0cff00"/>
</node>
<node COLOR="#111111" CREATED="1208797961711" ID="ID_1025791602" MODIFIED="1208899968788" TEXT="general glade standard allows UI to be used for UI driven maya-standalone apps">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Python could simply start maya as application internally, then use native GTK and glade directly .
    </p>
    <p>
      --&gt; Would mean application has to decide what do in advance though !
    </p>
  </body>
</html></richcontent>
<edge COLOR="#01ff00"/>
<node COLOR="#111111" CREATED="1208800034109" ID="ID_33542739" MODIFIED="1208899968789" TEXT="gtk is not yet fully available on OSX, maya is !">
<edge COLOR="#ff0000"/>
</node>
</node>
<node COLOR="#111111" CREATED="1208795010044" ID="ID_1663049802" MODIFIED="1208899968790" TEXT="Created files .glade files are larger and more complex xml">
<edge COLOR="#ff1100"/>
</node>
</node>
<node COLOR="#111111" CREATED="1208794848721" ID="ID_1145836807" MODIFIED="1208899968790" TEXT="General">
<node COLOR="#111111" CREATED="1208794851739" HGAP="39" ID="ID_416118227" MODIFIED="1208899968791" TEXT="If there is no direct representation of the Maya UI Element, some &apos;magic&apos; is required" VSHIFT="-1">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Sometimes some convention must be followed to get a certain UI element, making the tool possibly hard to use.
    </p>
  </body>
</html></richcontent>
<edge COLOR="#ff000e"/>
</node>
<node COLOR="#111111" CREATED="1208795061956" HGAP="44" ID="ID_1834284065" MODIFIED="1208899968792" TEXT="Rewriting wxGlade customized for maya would be best for maya-only applications" VSHIFT="4">
<edge COLOR="#00ff27"/>
<node COLOR="#111111" CREATED="1208795087997" ID="ID_245471883" MODIFIED="1208899968793" TEXT="BUT COSTS MUCH TIME !">
<edge COLOR="#ff0000"/>
</node>
</node>
</node>
<node COLOR="#111111" CREATED="1208798093130" ID="ID_569826287" MODIFIED="1208899968793" TEXT="NOTE:">
<font BOLD="true" NAME="SansSerif" SIZE="12"/>
<node COLOR="#111111" CREATED="1208798100459" ID="ID_1402693538" MODIFIED="1208899968794" TEXT="Finally, if all UI elements would be native GTK, there would be no need for maya UI wrapping anymore, and it would be a real complete rewrite">
<node COLOR="#111111" CREATED="1208798252614" ID="ID_241780292" MODIFIED="1208899968798" TEXT="probably not doable !"/>
</node>
</node>
</node>
</node>
</node>
</node>
<node COLOR="#00b439" CREATED="1208874134354" ID="ID_674005600" MODIFIED="1208874204796" TEXT="channels">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Deal with channels and their animation/connections in general
    </p>
  </body>
</html>
</richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208874206553" ID="ID_130289611" MODIFIED="1208874207970" TEXT="animation">
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1208874208269" ID="ID_92005270" MODIFIED="1208874210655" TEXT="constraints">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208900122862" ID="ID_1468159153" MODIFIED="1208900133643" TEXT="deformation">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1208900140491" FOLDED="true" ID="ID_1833594205" MODIFIED="1208900143603" TEXT="modeling">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208900144919" ID="ID_735258066" MODIFIED="1208900147354" TEXT="poly">
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1208900147719" ID="ID_1295321373" MODIFIED="1208900149009" TEXT="nurbs">
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1208900149365" ID="ID_1824373056" MODIFIED="1208900150874" TEXT="subdee">
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
</node>
<node COLOR="#0033ff" CREATED="1208732751451" FOLDED="true" ID="ID_774987381" MODIFIED="1208900228850" POSITION="right" TEXT="test">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Subfolders follow general project structure - and contain the respective tests.
    </p>
    <p>
      This way, for deployment, tests can simple be left out if required ( for end-user releases )
    </p>
  </body>
</html></richcontent>
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1208900228842" ID="ID_782855392" MODIFIED="1208900231294" TEXT="maya">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208800814232" ID="ID_1107786811" MODIFIED="1208900228849" TEXT="core">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1208800816031" ID="ID_496653173" MODIFIED="1208900232733" TEXT="UI">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208900249139" ID="ID_595658788" MODIFIED="1208900250672" TEXT="...">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node COLOR="#0033ff" CREATED="1208801212935" ID="ID_1419291762" MODIFIED="1208801294182" POSITION="left" TEXT="WEAK REFS !">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Assure that maya will be able to release resources on python GC collections - this is especially true if maya's UI elements are destroyed, but python wrappers cannot be deleted as some callbacks are still held by someone !
    </p>
    <p>
      <b>Assure that this works before starting anything major ! This is fundamental !</b>
    </p>
  </body>
</html></richcontent>
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
</node>
<node COLOR="#0033ff" CREATED="1208726380050" HGAP="34" ID="ID_1742046453" MODIFIED="1208870243954" POSITION="right" TEXT="Logging" VSHIFT="-12">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Logging Module
    </p>
  </body>
</html></richcontent>
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1208795734503" ID="ID_1137829478" MODIFIED="1208870237210" TEXT="based on &quot;logging&quot; package">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1208795741473" ID="ID_1253244381" MODIFIED="1208870237211" TEXT="keep and archive messages for user presentation">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1208796200570" ID="ID_1033633717" MODIFIED="1208870237213" TEXT="tag messages to allow better message processing">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node COLOR="#00b439" CREATED="1208870249418" ID="ID_1236011934" MODIFIED="1208870256289" TEXT="can be configured using configuration management">
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node COLOR="#0033ff" CREATED="1208727851606" ID="ID_850401127" MODIFIED="1208870228219" POSITION="right" TEXT="ConfigurationManagement">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Belongs to core, as batch scripts could be configured using this interface too
    </p>
  </body>
</html></richcontent>
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1208799248857" ID="ID_1443710833" MODIFIED="1208870228220" TEXT="Behaves as database">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      For methods that require it, it will be a simple database
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208800334551" ID="ID_1752427901" MODIFIED="1208870228221" TEXT="Simple DB could be INI based for readability">
<font NAME="SansSerif" SIZE="14"/>
</node>
<node COLOR="#990000" CREATED="1208728997949" ID="ID_652012926" MODIFIED="1208870228222" TEXT="ConfigParser could perhaps be used">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Simple INI Style Configuration files - perhaps using the same ID based super-flexible file structure to generate arbitarily complex configuration representations
    </p>
  </body>
</html></richcontent>
<font NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208799256755" ID="ID_221895962" MODIFIED="1208870228224" TEXT="UseCasese: Would an interface for communication be an improvement ? ( as on-demand addon )">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Classes, like UI widgets, could configure this interface to store configuration directly on user level, inheriting appropriate global level configuration accordingly.
    </p>
    <p>
      Same could be done even for wrapped maya objects that comeup with different settings by default then. This would work automatically if these values would correspond to actual attributes that could simply be set to the subclass of the interface.
    </p>
    <p>
      
    </p>
    <p>
      ( Interface that allow simple configuration and serialization of class data into some defined output )
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font BOLD="true" NAME="SansSerif" SIZE="16"/>
<node COLOR="#990000" CREATED="1208800247972" ID="ID_201242948" MODIFIED="1208870228225" TEXT="XML Files should be preferred">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      They are more feature-proof and would allow anything one ever needed
    </p>
    <p>
      CON: They are harder to read by the User - perhaps there are good visual editors for that eliminating the problem
    </p>
  </body>
</html></richcontent>
<font BOLD="true" NAME="SansSerif" SIZE="14"/>
</node>
</node>
<node COLOR="#00b439" CREATED="1208728524804" ID="ID_1328617563" MODIFIED="1208870228228" TEXT="Hierarchical Configuration">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Sources can overwrite each other and thus add up to the final configuration
    </p>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node COLOR="#0033ff" CREATED="1208796453946" ID="ID_1678134870" MODIFIED="1208873925938" POSITION="right" TEXT="Utilities">
<edge STYLE="sharp_bezier" WIDTH="8"/>
<font NAME="SansSerif" SIZE="18"/>
<node COLOR="#00b439" CREATED="1208796459697" ID="ID_1142567033" MODIFIED="1208870374229" TEXT="with_methods">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Simple implementation of *args and **kwargs methods that aid in writing safe code, like
    </p>
    <ul>
      <li>
        with_objectsExist( *args )
      </li>
    </ul>
  </body>
</html></richcontent>
<edge STYLE="bezier" WIDTH="thin"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
</node>
</map>
