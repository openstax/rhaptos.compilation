from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid

from z3c.form import group, field

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from rhaptos.compilation.interfaces import INavigableCompilation
from rhaptos.compilation.contentreference import IContentReference
from rhaptos.compilation import MessageFactory as _


# Interface class; used to define content-type schema.

class ICompilation(form.Schema, IImageScaleTraversable):
    """
    A compilation of content and other compilation objects.
    """


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class Compilation(dexterity.Container):
    grok.implements(ICompilation, INavigableCompilation)
    
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# compilation_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class View(grok.View):
    grok.context(ICompilation)
    grok.require('zope2.View')
    
    # grok.name('view')

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
        contentFilter = {'object_provides':
                         'rhaptos.compilation.compilation.ICompilation'}
        container = container or self.context
        brains = container.getFolderContents(contentFilter)
        return [b.getObject() for b in brains] or []

    def getContentReferences(self, container=None):
        contentFilter = {'object_provides':
                         'rhaptos.compilation.contentreference.IContentReference'}
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

    def isContentReference(self, item):
        return IContentReference.providedBy(item)


class TableOfContentsView(TableOfContentsHelpers):
    """ Renders only one level of compilations and contentreferences.
    """
    grok.context(ICompilation)
    grok.require('zope2.View')
    grok.name('rhaptos.compilation.table-of-contents')
    
