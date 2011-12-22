from five import grok
from zope.component import queryAdapter
from plone.app.layout.viewlets.interfaces import IAboveContent
from Products.CMFCore.interfaces import ISiteRoot, IContentish
from Products.CMFCore.utils import getToolByName
from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from plone.uuid.interfaces import IUUID

from rhaptos.compilation.interfaces import INavigableCompilation
from rhaptos.compilation.contentreference import IContentReference
from rhaptos.compilation.compilation import ICompilation

class NavigationViewlet(grok.Viewlet):
    """Display the navigation controls to move between ContentReferences.
    """

    grok.name('rhaptos.compilation.navigation-viewlet')
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.viewletmanager(IAboveContent)
    
    def update(self):
        self.referencedcontent = [b.getObject() for b in self.getContent()]
        self.ptool = getToolByName(self.context, 'portal_url')
        self.physicalRoot = self.ptool.getPhysicalRoot()
    
    def getUUID(self, obj):
        return IUUID(obj)

    def getStartURL(self):
        root = self.getRootCompilation(self.context)
        if self.referencedcontent:
            obj = self.referencedcontent[0]
            url = obj.relatedContent.to_path
            return '%s?compilationuid=%s' %(url, self.getUUID(root))
    
    def getRootCompilation(self, context):
        while context:
            if ICompilation.providedBy(context): return context
            context = context.aq_parent
    
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
        currentItem = self.getCurrentItem()
        if not currentItem: return None
        
        root = self.getRootCompilation(currentItem)
        adapter = queryAdapter(root, INextPreviousProvider)
        if adapter:
            nextItem = adapter.getNextItem(currentItem)
            if nextItem:
                relatedcontent = self.getRelatedContent(nextItem)
                url = relatedcontent.to_path
                return '%s?compilationuid=%s' %(url, self.getUUID(root))

    def getPreviousURL(self):
        currentItem = self.getCurrentItem()
        if not currentItem: return None

        root = self.getRootCompilation(currentItem)
        adapter = queryAdapter(root, INextPreviousProvider)
        if adapter:
            previousItem = adapter.getPreviousItem(currentItem)
            if previousItem:
                relatedcontent = self.getRelatedContent(previousItem)
                url = relatedcontent.to_path
                return '%s?compilationuid=%s' %(url, self.getUUID(root))
    
    def getRelatedContent(self, item):
        rooturl = self.physicalRoot.absolute_url()
        url = item['url'].split(rooturl)[1]
        contentref = self.physicalRoot.restrictedTraverse(url)
        return contentref.relatedContent

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
