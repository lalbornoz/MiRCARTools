#!/usr/bin/env python3
#
# Tool.py
# Copyright (c) 2018, 2019 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
#

class Tool(object):
    def onKeyboardEvent(self, atPoint, brushColours, brushPos, brushSize, canvas, keyChar, keyCode, keyModifiers, mapPoint):
        return False, None, None

    def onMouseEvent(self, atPoint, brushColours, brushPos, brushSize, canvas, keyModifiers, mapPoint, mouseDragging, mouseLeftDown, mouseRightDown):
        return False, None, None

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
