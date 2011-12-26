from zope.i18nmessageid import MessageFactory

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('rhaptos.compilation')

COMPILATION_TYPES = [
    'rhaptos.compilation.compilation',
    'rhaptos.compilation.contentreference',
    'rhaptos.compilation.section',
]
