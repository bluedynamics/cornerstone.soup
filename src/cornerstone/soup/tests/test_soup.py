# Copyright 2009-2010, BlueDynamics Alliance - http://bluedynamics.com
import unittest
import zope.component
import zope.annotation
import zopyx.txng3.core
import cornerstone.soup.tests
from pprint import pprint
from interlude import interact
from zope.testing import doctest
from zope.app.testing.placelesssetup import setUp, tearDown
from zope.configuration.xmlconfig import XMLConfig

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    '../soup.txt',
    '../ting.txt',
]

def test_suite():
    setUp()
    XMLConfig('meta.zcml', zope.component)()
    XMLConfig('configure.zcml', zope.annotation)()
    XMLConfig('configure.zcml', zopyx.txng3.core)()
    XMLConfig('configure.zcml', cornerstone.soup.tests)()
    return unittest.TestSuite([
        doctest.DocFileSuite(
            file, 
            optionflags=optionflags,
            globs={'interact': interact,
                   'pprint': pprint},
        ) for file in TESTFILES
    ])

if __name__ == '__main__':                                   #pragma NO COVERAGE
    unittest.main(defaultTest='test_suite')                  #pragma NO COVERAGE