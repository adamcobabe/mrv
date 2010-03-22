==============
What is MRV
==============
Maya ReVised is a multi-platform python development environment consisting of many packages and modules to ease rapid development of high-performance code to be used in and around Autodesk Maya.

Maya ReVised adds a lightweight convenience layer on top of the Maya API exposed to python, correcting inconveniences and sources for common programming errors on the way. It essentially enables a more convenient way of using the Maya API by allowing more intuitive access to maya's nodes, the DAG and the dependency graph. In effect, this greatly improves the programmers efficiency. 

As programming convenience within python is achieved at runtime, it clearly comes at the cost of performance, which is way MRV will always allow you to operate directly on MayaAPI objects, bypassing the convenience wrapper to optimize tight loops or performance critical parts of your program if needed. 

As an additional benefit, it provides an extensible undo system to enable undo for the most common wrapped API operations, hence programs requireing user interaction will work natively within maya at no additional development costs, undo usually does not need to be implemented explicitly. If no undo is required, MRV can automatically use alternative implementations which incour no-undo overhead at all to additionally boost performance in non-gui modes of operation.

MRV is versatile, as it runs on all platforms supported by Maya, starting at Maya 8.5 up to the latest version. Using MRV it is easy to write standalone applications, using a python interpreter alone as long as access to the maya python libraries is available.

Reliablity is a major concern, hence everything within MRV is backed by unittests. New features are implemented using test-driven development practices, new releases are only done if no unittest fails on any supported platform.

In future, MRV will add more convenience to Maya's builtin facilities to interact with the scene, possibly replacing parts of the outdated MEL interface with extensible python scripts which eases integration into production pipelines.

====================
What MRV is *not*
====================
MRV does not try to improve anything related to using MEL commands from within python as its focus rests on performance and the MayaAPI.

It is not simple to develop using MRV as you need to be familiar to some extend with the MayaAPI, and with Python of course. The learning curve is relatively steep instead of simple, but ... there is a reward at the other end for sure !

