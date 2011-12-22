from five import grok
from plone.directives import dexterity, form
from plone.indexer import indexer
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.relationfield.schema import RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.uuid.interfaces import IUUID

from rhaptos.xmlfile.xmlfile import IXMLFile
from rhaptos.compilation.interfaces import INavigableCompilation
from rhaptos.compilation.compilation import ICompilation
from rhaptos.compilation.section import ISection
from rhaptos.compilation import MessageFactory as _


class IContentReference(form.Schema, IImageScaleTraversable):
    """
    Reference to any content in the site.
    """
    relatedContent = RelationChoice(
        title=_(u'label_related_content', default=u'Related content'),
        source=ObjPathSourceBinder(object_provides=IXMLFile.__identifier__),
        required=True,
        )

@indexer(IContentReference)
def relatedContentUID(obj):
    uuid = IUUID(obj.relatedContent.to_object)
    return uuid
grok.global_adapter(relatedContentUID, name="relatedContentUID")

@indexer(IContentReference)
def compilationUID(obj):
    previousparent = parent = obj.aq_parent
    while ICompilation.providedBy(parent) or ISection.providedBy(parent):
        previousparent = parent
        parent = parent.aq_parent
    uuid = IUUID(previousparent)
    return uuid
grok.global_adapter(compilationUID, name="compilationUID")


class ContentReference(dexterity.Item):
    grok.implements(IContentReference)


class View(grok.View):
    grok.context(IContentReference)
    grok.require('zope2.View')
