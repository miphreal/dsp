# coding=utf-8
"""
i18n helper
"""


import gettext as _gettext
import os


t = _gettext.NullTranslations()


def setup(force_lang=None):
    global t
    if force_lang:
        os.environ['LANGUAGE'] = force_lang
    t = _gettext.translation('messages', 'locale', fallback=True)

def gettext(message):
    return t.gettext(message)
