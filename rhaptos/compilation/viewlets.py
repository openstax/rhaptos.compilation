from five import grok
from collections import deque
from zope.component import queryAdapter
from plone.app.layout.viewlets.interfaces import IBelowContent
from Products.CMFCore.interfaces import ISiteRoot, IContentish
from Products.CMFCore.utils import getToolByName
from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from plone.uuid.interfaces import IUUID

from rhaptos.xmlfile.xmlfile import IXMLFile
from rhaptos.compilation.interfaces import INavigableCompilation
from rhaptos.compilation.contentreference import IContentReference
from rhaptos.compilation.section import ISection
from rhaptos.compilation.compilation import ICompilation

class NavigationViewlet(grok.Viewlet):
    """Display the navigation controls to move between ContentReferences.
    """

    grok.name('rhaptos.compilation.navigation-viewlet')
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.viewletmanager(IBelowContent)
    
    def update(self):
        self.root = self.getCompilation()
        self.contentrefs = self.getContentRefsFromTree(self.root)
        self.currentItem = self.getCurrentItem()

    def getUUID(self, obj):
        return IUUID(obj)

    def getStartURL(self):
        if self.contentrefs:
            obj = self.contentrefs[0].getObject()
            url = obj.relatedContent.to_path
            return '%s?compilationuid=%s' %(url, self.getUUID(self.root))

    def getCompilation(self, request=None):
        if ICompilation.providedBy(self.context): return self.context

        request = request or self.request
        compilationuid = request.get('compilationuid', None)
        if compilationuid is None:
            return
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(UID=compilationuid)
        return brains and brains[0].getObject() or None
    
    def getCurrentItem(self):
        if IContentReference.providedBy(self.context):
            return self.context
        compilationuid = self.request.get('compilationuid', None)
        if not compilationuid: return None
        relatedcontentuid = self.getUUID(self.context)
        if not relatedcontentuid: return None

        pc = getToolByName(self.context, 'portal_catalog')
        query = {'portal_type': 'rhaptos.compilation.contentreference',
                 'compilationUID': compilationuid,
                 'relatedContentUID': relatedcontentuid,
                }
        brains = pc(query)
        return brains and brains[0].getObject() or None

    def getNextURL(self):
        if not self.currentItem: return None
        
        nextItem = self.getNextItem(self.currentItem)
        if nextItem:
            relatedcontent = nextItem.relatedContent
            if relatedcontent:
                url = relatedcontent.to_path
                return '%s?compilationuid=%s' %(url, self.getUUID(self.root))

    def getNextItem(self, currentItem):
        for idx, brain in enumerate(self.contentrefs):
            if brain.UID == IUUID(currentItem):
                if len(self.contentrefs) > idx+1:
                    return self.contentrefs[idx+1].getObject()

    def getContentRefsFromTree(self, root):
        contentrefFilter = {'portal_type':'rhaptos.compilation.contentreference'}
        sectionFilter = {'portal_type':'rhaptos.compilation.section'}
        contentrefs = []
        if root is None: return contentrefs
        sections = deque([root,])
        while len(sections) > 0:
            item = sections.popleft()
            contentrefs.extend(item.getFolderContents(contentFilter=contentrefFilter))
            sections.extend(item.getFolderContents(
                full_objects=True, contentFilter=sectionFilter))
        return contentrefs 

    def getPreviousItem(self, currentItem):
        """  """
        for idx, brain in enumerate(self.contentrefs):
            if brain.UID == IUUID(currentItem):
                if len(self.contentrefs) > idx-1 > -1:
                    return self.contentrefs[idx-1].getObject()

    def getPreviousURL(self):
        if not self.currentItem: return None
        
        previousItem = self.getPreviousItem(self.currentItem)
        if previousItem:
            relatedcontent = previousItem.relatedContent
            if relatedcontent:
                url = relatedcontent.to_path
                return '%s?compilationuid=%s' %(url, self.getUUID(self.root))
    
    def getContent(self):
        pc = getToolByName(self.context, 'portal_catalog')
        #'path': '/'.join(self.context.getPhysicalPath())
        query = {'portal_type': 'rhaptos.compilation.contentreference',
                 'sort_on': 'getObjPositionInParent'}
        brains = pc(query)
        return brains and brains or []

    def isCompilation(self, context=None):
        context = context or self.context
        return ICompilation.providedBy(context)

    def isContentReference(self, context=None):
        context = context or self.context
        return IContentReference.providedBy(context)

    def isContentish(self, context=None):
        context = context or self.context
        return IContentish.providedBy(context)

    def isXMLFile(self, context=None):
        context = context or self.context
        return IXMLFile.providedBy(context)
