from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid

from z3c.form import group, field

from plone.indexer import indexer
from plone.uuid.interfaces import IAttributeUUID 
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ContentTreeFieldWidget
from plone.formwidget.contenttree import ObjPathSourceBinder

from rhaptos.xmlfile.xmlfile import IXMLFile
from rhaptos.compilation.interfaces import INavigableCompilation
from rhaptos.compilation.section import ISection
from rhaptos.compilation import MessageFactory as _


# Interface class; used to define content-type schema.
class IContentReference(form.Schema, IImageScaleTraversable):
    """
    Reference to any content in the site.
    """
    relatedContent = RelationChoice(
        title=_(u'label_related_content', default=u'Related content'),
        source=ObjPathSourceBinder(object_provides=IXMLFile.__identifier__),
        required=True,
        )
    form.widget(relatedContent=ContentTreeFieldWidget)

@indexer(IContentReference)
def relatedContentUID(obj):
    return obj.relatedContent.to_object.UID()
grok.global_adapter(relatedContentUID, name="relatedContentUID")

@indexer(IContentReference)
def compilationUID(obj):
    # sequence of imports causes error if we put this at the top of the module.
    from rhaptos.compilation.compilation import ICompilation
    previousparent = parent = obj.aq_parent
    while ICompilation.providedBy(parent) or ISection.providedBy(parent):
        previousparent = parent
        parent = parent.aq_parent
    return previousparent and previousparent.UID()
grok.global_adapter(compilationUID, name="compilationUID")

class ContentReference(dexterity.Item):
    grok.implements(IContentReference, INavigableCompilation, IAttributeUUID)
    
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# contentreference_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class View(grok.View):
    grok.context(IContentReference)
    grok.require('zope2.View')
    
    # grok.name('view')
