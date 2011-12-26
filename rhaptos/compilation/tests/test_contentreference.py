import os
import unittest2 as unittest

from zope.component import createObject
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from Products.CMFCore.utils import getToolByName

from rhaptos.compilation.contentreference import CompilationSourceBinder

from base import PROJECTNAME
from base import INTEGRATION_TESTING

dirname = os.path.dirname(__file__)

class TestMarshal(unittest.TestCase):
    """ Test marshal module """
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_compiliationsourcebinder(self):
        sourcebinder = CompilationSourceBinder(
            object_provides='Products.CMFCore.interfaces.IContentish'
        )
        self.portal.invokeFactory('Document', 'd1', title=u"Document 1")
        results = sourcebinder(self.portal).search('path:/portal')
        self.assertTrue(len(results)==1)
