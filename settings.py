# coding=utf-8
"""
Common Settings
"""

from lib.i18n import gettext as _


SOURCE_DATA_TYPES = {
    '*.txt': _('Channels Source Bundle'),
    '*.bin': _('Channel Data Source'),
}
SOURCE_DATA_TYPES_LINE = '|'.join('%s|%s' % (hint, ext) for ext, hint in SOURCE_DATA_TYPES.items())


__all__ = ['SOURCE_DATA_TYPES_LINE']