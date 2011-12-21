from five import grok
from plone.app.layout.viewlets.interfaces import IAboveContent
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from rhaptos.compilation.interfaces import INavigableCompilation
from rhaptos.compilation.contentreference import IContentReference
from rhaptos.compilation.compilation import ICompilation

class NavigationViewlet(grok.Viewlet):
    """Display the navigation controls to move between ContentReferences.
    """

    grok.name('rhaptos.compilation.navigation-viewlet')
    grok.context(INavigableCompilation)
    grok.require('zope2.View')
    grok.viewletmanager(IAboveContent)
    
    def update(self):
        self.referencedcontent = [b.getObject() for b in self.getContent()]
        
    def getStartURL(self):
        root = self.getRootCompilation(self.context)
        if self.referencedcontent:
            obj = self.referencedcontent[0]
            url = obj.absolute_url()
        else:
            url = self.context.absolute_url() 
        return '%s?compilation=%s' %(url, root.getId())
    
    def getRootCompilation(self, context):
        while context:
            if self.isroot(context): return context
            if ISiteRoot.providedBy(context): return None
            context = context.aq_parent

    def getNextURL(self, currentItem):
        idx = self.referencedcontent.index(currentItem)
        if idx > -1 and idx < len(self.referencedcontent) -1:
            nextItem = self.referencedcontent[idx +1]
            url = nextItem.absolute_url()
            root = self.getRootCompilation(self.context)
            return '%s?compilation=%s' %(url, root.getId())

    def getPreviousURL(self, currentItem):
        idx = self.referencedcontent.index(currentItem)
        if idx > 0:
            previous = self.referencedcontent[idx -1]
            url = previous.absolute_url()
            root = self.getRootCompilation(self.context)
            return '%s?compilation=%s' %(url, root.getId())
    
    def getContent(self):
        pc = getToolByName(self.context, 'portal_catalog')
        #'path': '/'.join(self.context.getPhysicalPath())
        query = {'portal_type': 'rhaptos.compilation.contentreference', }
        brains = pc(query)
        return brains and brains or []

    def isroot(self, context=None):
        context = context or self.context
        parent = context.aq_parent
        return not ICompilation.providedBy(parent)

    def isCompilation(self, context=None):
        context = context or self.context
        return ICompilation.providedBy(context)

    def isContentReference(self, context=None):
        context = context or self.context
        return IContentReference.providedBy(context)
