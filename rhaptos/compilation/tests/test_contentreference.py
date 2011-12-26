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

class TestCompilation(unittest.TestCase):
    """ Test marshal module """
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_compilationsourcebinder_nocontent(self):
        sourcebinder = CompilationSourceBinder(
            object_provides='Products.CMFCore.interfaces._content.IContentish'
        )
        self.assertTrue(len(self.portal.portal_catalog())==0)
        results = sourcebinder(self.portal).search('')
        self.assertTrue(len(results)==0)
    
    def test_compilationsourcebinder_nocompilationcontent(self):
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
    
    def _createContent(self):
        id = self.portal.invokeFactory(
            'rhaptos.compilation.compilation',
            'compilation001',
            title=u"Compilation 1")
        compilation = self.portal._getOb(id)
        structure = (('section001', 'rhaptos.compilation.section', 'Section 001'),
                     ('section002', 'rhaptos.compilation.section', 'Section 002'),
                     ('section003', 'rhaptos.compilation.section', 'Section 003'),
                    )
        for itemId, itemType, itemTitle in structure:
            compilation.invokeFactory(itemType, itemId, title=itemTitle)
        
    def test_compilationsourcebinder_withsections(self):
        self._createContent()
        # we should have 4 objects in the catalog
        self.assertTrue(len(self.portal.portal_catalog())==4)

        sourcebinder = CompilationSourceBinder(
            object_provides='Products.CMFCore.interfaces._content.IContentish'
        )
        results = sourcebinder(self.portal).search('')
        self.assertTrue(len(results)==0)

    def test_compilationsourcebinder_withcontentrefs(self):
        self._createContent()
        compilation = self.portal._getOb('compilation001')
        sections = compilation.getFolderContents(
            {'portal_type': 'rhaptos.compilation.section'},
            full_objects=True)
        for number, section in enumerate(sections):
            id = self.portal.invokeFactory(
                'File',
                'file%s' %number,
                title=u'File %s' %number)
            section.invokeFactory(
                'rhaptos.compilation.contentreference',
                'contentref%s' %number,
                title=u"Content reference %s" %number,
                relatedContent = self.portal._getOb(id))
        # we should have 10 objects in the catalog
        # 1 compilation, 3 sections, 3 contentrefs, 3 files
        self.assertTrue(len(self.portal.portal_catalog())==10)

        sourcebinder = CompilationSourceBinder(
            object_provides='Products.CMFCore.interfaces._content.IContentish'
        )
        results = sourcebinder(self.portal).search('')
        self.assertTrue(len(results)==3)
