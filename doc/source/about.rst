#########
About MRV
#########

***********
What is MRV
***********
MRV is a multi-platform python development environment to ease rapid development of maintainable, reliable and high-performance code to be used in and around Autodesk Maya.

MRV adds a lightweight convenience layer on top of the Maya API exposed to python, correcting inconveniences and sources for common programming errors on the way. It essentially enables a more convenient way of using the Maya API by allowing more intuitive access to maya's nodes, the DAG and the dependency graph. In effect, this greatly improves the programmers productivity. 

As programming convenience within python is achieved at runtime, it clearly comes at the cost of performance, which is why MRV will always allow you to operate directly on MayaAPI objects, bypassing the convenience wrapper to optimize tight loops or performance critical parts of your program if needed. 

As an additional benefit, it provides an extensible undo system to enable undo for the most common wrapped API operations, hence programs requiring user interaction will work natively within maya at no additional development costs, undo usually does not need to be implemented explicitly. If no undo is required, MRV can automatically use alternative implementations which incur no undo overhead at all to additionally boost performance in non-gui modes of operation.

MRV is versatile, as it runs on all platforms supported by Maya, starting at Maya 8.5 up to the latest version. Using MRV it is easy to write standalone applications, using a python interpreter alone as long as access to the maya python libraries is available.

Reliability is a major concern, hence everything within MRV is backed by unittests. New features are implemented using :doc:`test-driven development practices <develop>`, new releases are only done if no unittest fails on any supported platform.

In future, MRV will add more convenience to Maya's built-in facilities to interact with the scene, possibly replacing parts of the outdated MEL interface with extensible python scripts which eases integration into production pipelines.

******************
What MRV is *not*
******************
MRV does not try to improve anything related to using MEL commands from within python as its focus rests on performance and the MayaAPI.

MRV might require heightened initial effort by people who are only familiar with MEL, and an understanding of the Maya API is beneficial. The learning curve is relatively steep, but ... there is a reward at the other end for sure !

