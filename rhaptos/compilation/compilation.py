from five import grok
from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable

from rhaptos.compilation.interfaces import INavigableCompilation
from rhaptos.compilation import MessageFactory as _


class ICompilation(form.Schema, IImageScaleTraversable):
    """
    A compilation of content and other compilation objects.
    """

class Compilation(dexterity.Container):
    grok.implements(ICompilation)


class View(grok.View):
    grok.context(ICompilation)
    grok.require('zope2.View')


class TableOfContentsHelpers(grok.View):
    """ Helper methods and a template that renders only the table of contents.
    """
    grok.context(ICompilation)
    grok.require('zope2.View')
    grok.name('rhaptos.compilation.table-of-contents-helpers')
    
    def getContentsAsDict(self):
        compilations = self.getCompilations()
        contentreferences = self.getContentReferences()
        content = {'children': compilations,
                   'contentreferences': contentreferences}
        return content

    def getCompilations(self, container=None):
        contentFilter = {'portal_type':
                         'rhaptos.compilation.compilation'}
        container = container or self.context
        brains = container.getFolderContents(contentFilter)
        return [b.getObject() for b in brains] or []

    def getContentReferences(self, container=None):
        contentFilter = {'portal_type':
                         'rhaptos.compilation.contentreference'}
        container = container or self.context
        brains = container.getFolderContents(contentFilter)
        return [b.getObject() for b in brains] or []
    
    def isroot(self, context=None):
        """ If the parent of 'context' does not provide ICompilation we can be
            sure 'context' is the topmost (root) Compilation object.
        """
        context = context or self.context
        parent = context.aq_parent
        return not ICompilation.providedBy(parent)

    def getContentItems(self, container=None):
        container = container or self.context
        return container.getFolderContents(full_objects=True)

    def isCompilation(self, item):
        return ICompilation.providedBy(item)


class TableOfContentsView(TableOfContentsHelpers):
    """ Renders only one level of compilations and contentreferences.
    """
    grok.context(ICompilation)
    grok.require('zope2.View')
    grok.name('rhaptos.compilation.table-of-contents')
    
