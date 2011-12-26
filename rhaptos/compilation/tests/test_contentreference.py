import os
import unittest2 as unittest

from zope.component import createObject
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from Products.CMFCore.utils import getToolByName

from rhaptos.compilation.contentreference import CompilationSourceBinder
from rhaptos.compilation.compilation import TableOfContentsHelpers, ICompilation
from rhaptos.compilation.section import ISection 

from base import PROJECTNAME
from base import INTEGRATION_TESTING

dirname = os.path.dirname(__file__)

class TestCompilationSourceBinder(unittest.TestCase):
    """ Test compilation source binder """
    layer = INTEGRATION_TESTING

    def _createSections(self):
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
        sections = compilation.getFolderContents(
            {'portal_type': 'rhaptos.compilation.section'},
            full_objects=True)
        return sections
        
    def _createContentRefs(self, sections):
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

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        sections = self._createSections()
        self._createContentRefs(sections)
        self.portal.invokeFactory('Document', 'd1', title=u"Document 1")

    def test_compilationsourcebinder(self):
        sourcebinder = CompilationSourceBinder(
            object_provides='Products.CMFCore.interfaces._content.IContentish'
        )

        # make sure all our objects are catalogued
        self.assertTrue(len(self.portal.portal_catalog())==11)

        # we should only get the one document and 3 files we create in setup
        results = sourcebinder(self.portal).search('')
        self.assertTrue(len(results)==4)


class TestTOCHelpers(TestCompilationSourceBinder):
    """ Test compilation TOC helpers """
    layer = INTEGRATION_TESTING

    def test_getContentItems(self):
        compilation = self.portal._getOb('compilation001')
        tochelper = TableOfContentsHelpers(compilation, {}) 
        items = tochelper.getContentItems()
        self.assertTrue(len(items)==3)

    def test_isCompilation(self):
        compilation = self.portal._getOb('compilation001')
        self.assertTrue(ICompilation.providedBy(compilation))

    def test_isSection(self):
        compilation = self.portal._getOb('compilation001')
        tochelper = TableOfContentsHelpers(compilation, {}) 
        items = tochelper.getContentItems()
        for item in items:
            self.assertTrue(ISection.providedBy(item))
