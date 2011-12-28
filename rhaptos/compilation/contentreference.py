from five import grok
from Products.CMFCore.utils import getToolByName
from plone.directives import dexterity, form
from plone.indexer import indexer
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.relationfield.schema import RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.formwidget.contenttree.source import CustomFilter, ObjPathSource
from plone.app.vocabularies.catalog import parse_query
from plone.uuid.interfaces import IUUID

from rhaptos.xmlfile.xmlfile import IXMLFile
from rhaptos.compilation.compilation import ICompilation
from rhaptos.compilation.section import ISection
from rhaptos.compilation import MessageFactory as _
from rhaptos.compilation import COMPILATION_TYPES

class CompilationPathSource(ObjPathSource):

    def search(self, query, limit=20):
        catalog_query = self.selectable_filter.criteria.copy()
        catalog_query.update(parse_query(query, self.portal_path))

        if limit and 'sort_limit' not in catalog_query:
            catalog_query['sort_limit'] = limit

        try:
            results = []
            for brain in self.catalog(**catalog_query):
                if brain.portal_type not in COMPILATION_TYPES:
                    results.append(self.getTermByBrain(brain, real_value=False))
        except ParseError:
            return []

        return results


class CompilationSourceBinder(ObjPathSourceBinder):
    path_source = CompilationPathSource

class IContentReference(form.Schema, IImageScaleTraversable):
    """
    Reference to any content in the site.
    """
    relatedContent = RelationChoice(
        title=_(u'label_related_content', default=u'Related content'),
        source=CompilationSourceBinder(
            object_provides='Products.CMFCore.interfaces._content.IContentish'),
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
