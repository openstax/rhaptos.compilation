from five import grok
from plone.directives import dexterity, form

from plone.namedfile.interfaces import IImageScaleTraversable

from rhaptos.compilation import MessageFactory as _


class ISection(form.Schema, IImageScaleTraversable):
    """
    Compilation section.
    """


class Section(dexterity.Container):
    grok.implements(ISection)
