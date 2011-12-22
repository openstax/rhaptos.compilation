from five import grok
from zope.component import queryAdapter
from plone.app.layout.viewlets.interfaces import IAboveContent
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
    grok.viewletmanager(IAboveContent)
    
    def update(self):
        self.referencedcontent = [b.getObject() for b in self.getContent()]
        self.ptool = getToolByName(self.context, 'portal_url')
        self.physicalRoot = self.ptool.getPhysicalRoot()
        props = getToolByName(self.context, 'portal_properties').site_properties
        self.vat = props.getProperty('typesUseViewActionInListings', ())

    def getOrdering(self, context):
        order = context.getOrdering()
        if not isinstance(order, list):
            order = order.idsInOrder()
        if not isinstance(order, list):
            order = None
        return order
    
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
        
        context = currentItem.aq_parent
        nextItem = self.getNextItem(context, currentItem)
        if nextItem:
            relatedcontent = self.getRelatedContent(nextItem)
            if relatedcontent:
                url = relatedcontent.to_path
                return '%s?compilationuid=%s' %(url, self.getUUID(root))

    def getNextItem(self, context, obj=None):
        order = self.getOrdering(context)
        if not order: return None
        pos = 0
        if obj:
            pos = context.getObjectPosition(obj.getId())
        # find the first object the provides IContentReference
        offset = 1
        data = None
        for oid in order[pos+offset:]:
            nextObj = context[oid]
            if IContentReference.providedBy(nextObj):
                data = self.getData(nextObj)
            elif ISection.providedBy(nextObj):
                data = self.getNextItem(nextObj)
            elif ICompilation.providedBy(nextObj):
                return None
            if data:
                return data
        return None

    def getPreviousItem(self, context, obj=None):
        """  """
        order = self.getOrdering(context)
        if not order: return None
        pos = len(context.objectIds()) or 0
        order_reversed = list(reversed(order))
        if obj:
            pos = order_reversed.index(obj.getId())
        data = None
        for oid in order_reversed[pos+1:]:
            nextObj = context[oid]
            if IContentReference.providedBy(nextObj):
                data = self.getData(nextObj)
            elif ISection.providedBy(nextObj):
                data = self.getNextItem(nextObj)
            elif ICompilation.providedBy(nextObj):
                return None
            if data:
                return data
        return None
        
    def getData(self, obj):
        """ return the expected mapping, see `INextPreviousProvider` """
        if not self.security.checkPermission('View', obj):
            return None
        elif not IContentish.providedBy(obj):
            # do not return a not contentish object
            # such as a local workflow policy for example (#11234)
            return None

        ptype = obj.portal_type
        url = obj.absolute_url()
        if ptype in self.vat:       # "use view action in listings"
            url += '/view'
        return dict(id=obj.getId(), url=url, title=obj.Title(),
            description=obj.Description(), portal_type=ptype)

    def getPreviousURL(self):
        currentItem = self.getCurrentItem()
        if not currentItem: return None
        
        context = currentItem.aq_parent
        previousItem = self.getPreviousItem(context, currentItem)
        if previousItem:
            relatedcontent = self.getRelatedContent(previousItem)
            if relatedcontent:
                url = relatedcontent.to_path
                return '%s?compilationuid=%s' %(url, self.getUUID(root))
    
    def getRelatedContent(self, item):
        rooturl = self.physicalRoot.absolute_url()
        url = item['url'].split(rooturl)[1]
        contentref = self.physicalRoot.restrictedTraverse(url)
        if hasattr(contentref, 'relatedContent'):
            return contentref.relatedContent
        return None

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
