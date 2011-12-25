from five import grok
from Products.CMFCore.utils import getToolByName
from plone.directives import dexterity, form
from plone.indexer import indexer
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.relationfield.schema import RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.formwidget.contenttree.source import CustomFilter
from plone.uuid.interfaces import IUUID

from rhaptos.xmlfile.xmlfile import IXMLFile
from rhaptos.compilation.compilation import ICompilation
from rhaptos.compilation.section import ISection
from rhaptos.compilation import MessageFactory as _


class ConfigurableSourceBinder(ObjPathSourceBinder):
    def __call__(self, context):
        self.selectable_filter = self.getSelectableFilter(context)
        return super(ConfigurableSourceBinder, self).path_source(
            self._find_page_context(context),
            selectable_filter=self.selectable_filter,
            navigation_tree_query=self.navigation_tree_query)

    def getSelectableFilter(self, context):
        ptool = getToolByName(context, 'portal_properties')
        properties = ptool.get('configurablesourcebinder_properties')
        interfaces = properties.getProperty('interfaces', ['IContentish'])
        return CustomFilter(object_provides=interfaces)

class IContentReference(form.Schema, IImageScaleTraversable):
    """
    Reference to any content in the site.
    """
    relatedContent = RelationChoice(
        title=_(u'label_related_content', default=u'Related content'),
        source=ConfigurableSourceBinder(),
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

