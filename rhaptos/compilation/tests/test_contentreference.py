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

    def test_compilationsourcebinder(self):
        sourcebinder = CompilationSourceBinder(
            object_provides='Products.CMFCore.interfaces._content.IContentish'
        )
        self.portal.invokeFactory('Document', 'd1', title=u"Document 1")
        self.portal.invokeFactory('rhaptos.compilation.compilation',
            'c1', title=u"Compilation 1")

        # make sure both objects are catalogued
        self.assertTrue(len(self.portal.portal_catalog())==2)

        # compilation must be exclude from the source binder results
        results = sourcebinder(self.portal).search('')
        self.assertTrue(len(results)==1)
