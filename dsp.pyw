#!/usr/bin/env python
# coding=utf-8
"""
DSP - Digital Signal Processing

=> entry point of application
"""

from lib.i18n import setup as setup_i18n
setup_i18n(force_lang='ru_RU')

from lib.log import setup as setup_logging
setup_logging()

from ui.app import DSPApp


if __name__ == '__main__':
    DSPApp().MainLoop()