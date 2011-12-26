from five import grok
from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable

from rhaptos.compilation.interfaces import INavigableCompilation
from rhaptos.compilation.section import ISection
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
    
    def getContentItems(self, container=None):
        container = container or self.context
        return container.getFolderContents(full_objects=True)

    def isCompilation(self, item):
        return ICompilation.providedBy(item)

    def isSection(self, item):
        return ISection.providedBy(item)

class TableOfContentsView(TableOfContentsHelpers):
    """ Renders only one level of compilations and contentreferences.
    """
    grok.context(ICompilation)
    grok.require('zope2.View')
    grok.name('rhaptos.compilation.table-of-contents')
    
