#!/usr/bin/env python3
#
# RoarCanvasCommandsOperators.py
# Copyright (c) 2018, 2019 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
#

from OperatorFlipHorizontal import OperatorFlipHorizontal
from OperatorFlipVertical import OperatorFlipVertical
from OperatorInvert import OperatorInvert
from GuiFrame import GuiCommandListDecorator
from ToolObject import ToolObject
import copy, wx

class RoarCanvasCommandsOperators():
    # {{{ canvasOperator(self, f, idx)
    @GuiCommandListDecorator(0, "Flip", "&Flip", None, None, None)
    @GuiCommandListDecorator(1, "Flip horizontally", "Flip &horizontally", None, None, None)
    @GuiCommandListDecorator(2, "Invert", "&Invert", None, None, None)
    def canvasOperator(self, f, idx):
        def canvasOperator_(event):
            applyOperator = [OperatorFlipVertical, OperatorFlipHorizontal, OperatorInvert][idx]()
            if  (self.currentTool.__class__ == ToolObject)  \
            and (self.currentTool.toolState >= self.currentTool.TS_SELECT):
                region = self.currentTool.getRegion(self.parentCanvas.canvas)
            else:
                region = self.parentCanvas.canvas.map
            region = applyOperator.apply(copy.deepcopy(region))
            if  (self.currentTool.__class__ == ToolObject)  \
            and (self.currentTool.toolState >= self.currentTool.TS_SELECT):
                if self.parentCanvas.popupEventDc == None:
                    eventDc = self.parentCanvas.backend.getDeviceContext(self.parentCanvas.GetClientSize(), self.parentCanvas)
                else:
                    eventDc = self.parentCanvas.popupEventDc
                eventDcOrigin = eventDc.GetDeviceOrigin(); eventDc.SetDeviceOrigin(0, 0);
                self.currentTool.setRegion(self.parentCanvas.canvas, None, region, [len(region[0]), len(region)], self.currentTool.external)
                self.currentTool.onSelectEvent(self.parentCanvas.canvas, (0, 0), self.parentCanvas.dispatchPatchSingle, eventDc, True, wx.MOD_NONE, None, self.currentTool.targetRect)
                eventDc.SetDeviceOrigin(*eventDcOrigin)
            else:
                if self.parentCanvas.popupEventDc == None:
                    eventDc = self.parentCanvas.backend.getDeviceContext(self.parentCanvas.GetClientSize(), self.parentCanvas)
                else:
                    eventDc = self.parentCanvas.popupEventDc
                eventDcOrigin = eventDc.GetDeviceOrigin(); eventDc.SetDeviceOrigin(0, 0);
                self.parentCanvas.canvas.journal.begin()
                dirty = False
                for numRow in range(len(region)):
                    for numCol in range(len(region[numRow])):
                        if not dirty:
                            self.parentCanvas.dirty = True
                        self.parentCanvas.dispatchPatchSingle(eventDc, False, [numCol, numRow, *region[numRow][numCol]])
                self.parentCanvas.canvas.journal.end()
                self.parentCanvas.commands.update(dirty=self.parentCanvas.dirty, undoLevel=self.parentCanvas.canvas.journal.patchesUndoLevel)
                eventDc.SetDeviceOrigin(*eventDcOrigin)
        setattr(canvasOperator_, "attrDict", f.attrList[idx])
        return canvasOperator_
    # }}}

    #
    # __init__(self)
    def __init__(self):
        self.menus = (
            ("&Operators",
                self.canvasOperator(self.canvasOperator, 0), self.canvasOperator(self.canvasOperator, 1), self.canvasOperator(self.canvasOperator, 2),
            ),
        )
        self.toolBars = ()

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
