import os
import unittest2 as unittest

from plone.uuid.interfaces import IUUID
from zope.component import createObject
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from z3c.relationfield.relation import create_relation
from Products.CMFCore.utils import getToolByName

from rhaptos.compilation.contentreference import CompilationSourceBinder
from rhaptos.compilation.compilation import TableOfContentsHelpers, ICompilation
from rhaptos.compilation.section import ISection 
from rhaptos.compilation.viewlets import NavigationViewlet

from base import PROJECTNAME
from base import INTEGRATION_TESTING

dirname = os.path.dirname(__file__)

class CompilationBaseTestCase(unittest.TestCase):
    """ Basic methods for all other compilation tests """

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
            file = self.portal._getOb(id)
            id = section.invokeFactory(
                'rhaptos.compilation.contentreference',
                'contentref%s' %number,
                title=u"Content reference %s" %number)
            contentref = section._getOb(id)
            relation = create_relation(file.getPhysicalPath())
            contentref.relatedContent = relation
            contentref.reindexObject(idxs=['compilationUID', 'relatedContentUID'])

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        sections = self._createSections()
        self._createContentRefs(sections)
        self.portal.invokeFactory('Document', 'd1', title=u"Document 1")


class TestCompilationSourceBinder(CompilationBaseTestCase):
    """ Test compilation source binder """

    def test_compilationsourcebinder(self):
        sourcebinder = CompilationSourceBinder(
            object_provides='Products.CMFCore.interfaces._content.IContentish'
        )

        # make sure all our objects are catalogued
        self.assertTrue(len(self.portal.portal_catalog())==11)

        # we should only get the one document and 3 files we create in setup
        results = sourcebinder(self.portal).search('')
        self.assertTrue(len(results)==4)


class TestTOCHelpers(CompilationBaseTestCase):
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


class TestReferenceContent(CompilationBaseTestCase):
    
    def test_relatedContentUID(self):
        pass

    def test_compilationUID(self):
        pass


class TestNavigationViewlet(CompilationBaseTestCase):
    
    def setUp(self):
        super(TestNavigationViewlet, self).setUp()
        self.compilation = self.portal._getOb('compilation001')
        self.navviewlet = NavigationViewlet(self.compilation, {}, {}, None) 
        self.navviewlet.update()

    def test_update(self):
        """ Probably don't need testing as each of the methods called here
            get tested on their own.
        """
        pass

    def test_getUUID(self):
        """ Simple utility method; no need to test.
        """
        pass

    def test_getStartURL(self):
        starturl = self.navviewlet.getStartURL()
        refUrl = '%s/file0?compilationuid=%s' % \
            ('/'.join(self.portal.getPhysicalPath()), IUUID(self.compilation))
        self.assertEqual(starturl, refUrl)

    def test_getCompilation(self):
        self.assertEqual(self.navviewlet.getCompilation(), self.compilation)

    def test_getCurrentItem(self):
        pass

    def test_getNextURL_emptyrequest(self):
        nexturl = self.navviewlet.getNextURL()
        self.assertEqual(nexturl, None)

    def test_getNextURL(self):
        currentfile = self.portal.file0
        navviewlet = NavigationViewlet(
            currentfile,
            {'compilationuid': IUUID(self.compilation)},
            {},
            None) 
        navviewlet.update()
        nexturl = navviewlet.getNextURL()
        #/plone/file1?compilationuid=3b5cf1f3-10c1-4c29-a94c-53a915215262
        nextfile = self.portal.file1
        refurl = '%s?compilationuid=%s' % \
            ('/'.join(nextfile.getPhysicalPath()), IUUID(self.compilation))
        self.assertEqual(nexturl, refurl)

    def test_NextItem(self):
        pass

    def test_getContentRefsFromTree(self):
        pass

    def test_getPreviousItem(self):
        pass

    def test_getPreviousURL(self):
        pass

    def test_getContent(self):
        pass

    def test_isContentReference(self):
        """ Simple utility method; no need to test.
        """
        pass

    def test_isContentish(self):
        """ Simple utility method; no need to test.
        """
        pass

    def test_isXMLFile(self):
        """ Simple utility method; no need to test.
        """
        pass
