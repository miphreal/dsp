#!/usr/bin/env python
# coding=utf-8
"""
DSP - Digital Signal Processing
"""

from lib.i18n import setup
setup(force_lang='ru_RU')

from ui.app import DSPApp


if __name__ == '__main__':
    DSPApp().MainLoop()