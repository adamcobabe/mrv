#######
History
#######

The story of MRV begins more than two years ago when I was starting a new job in Sweden. The task wasn't easy, as it involved the creation of a Maya 8.5 based production pipeline in exactly 240 days, and alone.

Based on the experiences with my previous pipeline, which was based on MEL and partly C++, I knew that I'd never touch MEL again ( for the purpose of writing a complex framework at least ). Fortunately, Maya 8.5 supported python for the first time, and opened up a whole new world of possibilities.

Shortly after my initial excitement came the crash into the bitter truth: its not going to be a cake walk at all. Even though python is the language you want to write a pipeline in ( give the choices of MEL and c++ as well as the time frame ), it would end up being either ugly MEL using ``maya.cmds``, or ``maya.OpenMaya`` which would force me to write 5 lines instead of one !

But let me illustrate the situation I was facing::
	
	# MEL - adding a string array attribute and retrieving its value
	addAttr -ln "stringarray" -sn "sa" -dt "stringArray" "persp"
	getAttr "persp.sa"
	
Sure, MEL is short, but that language is simply to primitive to built a proper pipeline upon it. Previously, I simulated virtual function calls, and emulated associative array using MEL string arrays, but of course it stays a workaround for something that should be provided by the language natively.

The same code in python using ``maya.cmds`` looks even worse - although you have the chance to work in an object oriented fashion, lots of work would be needed to meld MEL into python, or you end up writing code like this::
	
	import maya.cmds as cmds
	cmds.addAttr("persp", ln="stringArray", sn="sa", dt="stringArray")
	cmds.getAttr("persp.sa")		# ups, its an empty array, so we get None in 8.5 at least !!

Sure thing, I would use the API instead, but lets see what we get then::
	
	import maya.OpenMaya as api  
	sellist = api.MSelectionList()
	sellist.add("persp")
	p = api.MDagPath()
	sellist.getDagPath(0, p)
		
	mfndag = api.MFnDagNode(p)
	mfnattr = api.MFnTypedAttribute()
	mfndata = api.MFnStringArrayData()
	attr = mfnattr.create("stringArray", "sa", api.MFnData.kStringArray, mfndata.create())
	mfndag.addAttribute(attr)
		
	# all this to add an attribute, now retrieve the value
	# this is rather short as we reuse the function set.
	mfndata.setObject(mfndag.findPlug("sa").asMObject())
	mfndata.array()
	
MEL needs me to write two lines of code, python MEL 3 lines, and python API 13 (!!) lines ! Considering that less code is more, I would have to choose maya.cmds as a basis for a new pipeline, but would have to be aware of the fact that it needs quite some fixing before being usable.

Fortunately, back in that time, an early version of PyMel would already be available, and they even had Node wraps which would provide native access to suitable MEL procedures, and effectively hide MEL from you as much as possible. Once again I was exited, but crash landed soon after. In short words, it was still far too early to be usable, and, as a most important point, it wouldn't work reliably on Maya 8.5 as it was actively developed on Maya 2008 and newer. Back in that time, there was no unittesting, and things could ( and would ) break at will.

As giving up is not exactly my way, I realized something new would have to be created, and if PyMel made MEL nice in python, why shouldn't there be something that makes the MayaAPI at least as nice, to allow writing something like this::
	
	import mrv.maya.nt as nt
	p = nt.Node("persp")
	p.addAttribute(nt.TypedAttribute.create('stringarray', 'sa', Data.Type.kStringArray, nt.StringArrayData.create()))
	p.sa.masData().array()
	
The previous code should of course internally use the API exclusively, and it should support undo - what you see here is how you could write it in MRV 1.0 Effectively, I needed to reduce the amount of typing required to use the API by factor 3 ( or more ), while improving the reliability of the code as well as the readability, without hurting performance much or make the rest of the API unusable.

The solution, back in the days, was a new open source project called *Maya ReVised*, and its goal was nothing less than providing a foundation to rebuild everything about Maya if you like, or to alter it according to your needs, using the Maya API whenever possible.

The following 3 months I spent working around the clock ( literally ) to build the framework, so I had to get used to Test-Driven-Development, Python and the use of Metaclasses, Descriptors, Decorators, and everything that allowed me to dynamically and on demand wrap the function sets onto the respective API objects. I probably crashed maya more often than with all previous MEL and C++ code together, but also learned a lot about it while digging into areas that I previously only touched superficially.

With the (internal) release of version 0.1, I had something to built a pipeline upon, with quite a good unit-test coverage, although my workflow was still worth many improvements.

The pipeline code was closed source of course, but MayaRV stayed open, and was publicly available throughout that time. During the following 9 months, it got faster and more reliable, the main development time was spent on closed source though so it only got as much attention as it needed to just keep up.

Once the job was done, after only 11 months, I left Stockholm and arrived back in Berlin, ready to ... just do nothing for a while but having fun and enjoying myself, which is why MayaRV didn't evolve much for a while.

When the time passed, I got a little fed up with that new lifestyle of mine, and wanted to get back into the old one to be productive once again. This time, it should be the version 3 of a maya based production pipeline, which of course is owned by no one but myself.

During the evolution of the next-gen pipeline project, MayaRV didn't evolve at all as I was busy developing the very foundation of any production, the data storage solution. My one would be distributed by nature, based on git, using `git-python <http://gitorious.org/git-python>`_. From time to time, when the storage solution would upset me, I switched to MayaRV to improve existing things, which is how MayaRV would get nose support, as well as sphinx ( in the beginnings, it would only use epydoc ).

When the first rumors of Maya 2011 would reach my ears, saying it would use QT as GUI framework, I started getting very interested as it would clearly help me developing platform- and software-independent interfaces, one of these would be the GUI for the git-based storage management system.

With these news, I also got the impression that PyMel was going to be integrated into Maya, which was reason enough to put all my attention back to MayaRV, which became MRV in the course of that, and better and faster than ever. 

The goal was to provide an alternative for all the Sebastian's out there, who cannot use PyMel for whichever reason. In the end, all the time spent on it is time well spent, as my pipeline V3 will clearly benefit from it. Hopefully there will be others who see MRV's :doc:`potential <roadmap>`, and start using it to further :doc:`boost its development <develop/index>`, for the benefit of the whole community this time.
