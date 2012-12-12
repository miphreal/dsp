# coding=utf-8
"""
just make
"""

import os
from fabric.api import local, env, cd


env.project_root = os.path.realpath(os.path.dirname(__file__))
PROJECT_ = lambda p: os.path.normpath(os.path.join(env.project_root, p))

env.pot_file = PROJECT_('locale/messages.pot')
env.languages = 'ru_RU'
env.default_language = 'ru_RU'


# Translation
def build_template():
    local('xgettext `find %(project_root)s -name "*.py"` -o %(pot_file)s' % env)

def build_po(lang):
    po_file = PROJECT_('locale/%(lang)s/LC_MESSAGES/messages.po' % dict(lang=lang))
    if not os.path.exists(po_file):
        local('msginit --no-translator -l %(locale)s -i %(pot_file)s -o %(po_file)s' % dict(env,
            locale=lang.partition('_')[0], po_file=po_file
        ))
        return True
    return False

def update_po(lang=env.default_language):
    po_file = PROJECT_('locale/%(lang)s/LC_MESSAGES/messages.po' % dict(lang=lang))
    local('msgmerge --update %(po_file)s %(pot_file)s' % dict(env, po_file=po_file))

def compile_mo(lang=env.default_language):
    local('msgfmt -cv {pattern}.po -o {pattern}.mo'.format(
        pattern=PROJECT_('locale/%(lang)s/LC_MESSAGES/messages' % dict(lang=lang))
    ))

def translate(languages=env.languages):
    build_template()
    for lang in languages.split(';'):
        local('mkdir -p locale/%s/LC_MESSAGES/' % lang)
        if not build_po(lang):
            update_po(lang)
        compile_mo(lang)




