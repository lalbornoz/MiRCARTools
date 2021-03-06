#!/usr/bin/env python3
#
# RoarCanvasWindow.py
# Copyright (c) 2018, 2019 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
#

from GuiWindow import GuiWindow
from Rtl import natural_sort
from RtlPlatform import getLocalConfPathName
from ToolObject import ToolObject
from ToolText import ToolText
import copy, hashlib, json, os, pdb, re, time, wx, sys

class RoarCanvasWindowDropTarget(wx.TextDropTarget):
    def done(self):
        self.inProgress = False

    def OnDropText(self, x, y, data):
        rc = False
        if  ((self.parent.commands.currentTool.__class__ != ToolObject)                                 \
        or   (self.parent.commands.currentTool.toolState == self.parent.commands.currentTool.TS_NONE))  \
        and (not self.inProgress):
            try:
                dropMap, dropSize = json.loads(data)
                rectX, rectY = x - (x % self.parent.backend.cellSize[0]), y - (y % self.parent.backend.cellSize[1])
                mapX, mapY = int(rectX / self.parent.backend.cellSize[0] if rectX else 0), int(rectY / self.parent.backend.cellSize[1] if rectY else 0)
                viewRect = self.parent.GetViewStart(); mapPoint = [m + n for m, n in zip((mapX, mapY), viewRect)];
                self.parent.commands.lastTool, self.parent.commands.currentTool = self.parent.commands.currentTool, ToolObject()
                self.parent.commands.currentTool.setRegion(self.parent.canvas, mapPoint, dropMap, dropSize, external=True)
                self.parent.parent.menuItemsById[self.parent.commands.canvasOperator.attrList[4]["id"]].Enable(True)
                self.parent.commands.update(currentTool=self.parent.commands.currentTool, currentToolIdx=5)
                eventDc = self.parent.backend.getDeviceContext(self.parent.GetClientSize(), self.parent, viewRect)
                eventDcOrigin = eventDc.GetDeviceOrigin(); eventDc.SetDeviceOrigin(0, 0);
                self.parent.applyTool(eventDc, True, None, None, None, self.parent.brushPos, False, False, False, self.parent.commands.currentTool, viewRect)
                eventDc.SetDeviceOrigin(*eventDcOrigin)
                rc = True; self.inProgress = True;
            except:
                with wx.MessageDialog(self.parent, "Error: {}".format(sys.exc_info()[1]), "", wx.OK | wx.OK_DEFAULT) as dialog:
                    dialogChoice = dialog.ShowModal()
        return rc

    def __init__(self, parent):
        super().__init__(); self.inProgress, self.parent = False, parent;

class RoarCanvasWindow(GuiWindow):
    def _applyPatches(self, eventDc, patches, patchesCursor, rc, commitUndo=True, dirty=True, eventDcResetOrigin=True, hideCursor=True):
        if rc:
            if eventDc == None:
                eventDc = self.backend.getDeviceContext(self.GetClientSize(), self, self.GetViewStart())
            if eventDcResetOrigin:
                eventDcOrigin = eventDc.GetDeviceOrigin(); eventDc.SetDeviceOrigin(0, 0);
            if hideCursor and (((patches != None) and (len(patches) > 0)) or ((patchesCursor != None) and (len(patchesCursor) > 0))):
                self.cursorHide(eventDc, False, True)
            if (patches != None) and (len(patches) > 0):
                self.backend.drawPatches(self.canvas, eventDc, patches, isCursor=False)
                if dirty and not self.dirty:
                    self.dirty = True
                if commitUndo:
                    self.canvas.begin()
                for patch in patches if patches != None else []:
                    self.canvas.applyPatch(patch, commitUndo=commitUndo)
                if commitUndo:
                    self.canvas.end()
            if hideCursor and (patchesCursor != None):
                self.cursorShow(eventDc, False, patchesCursor=patchesCursor)
            if eventDcResetOrigin:
                eventDc.SetDeviceOrigin(*eventDcOrigin)
            self.commands.update(cellPos=self.brushPos, dirty=self.dirty, undoLevel=self.canvas.patchesUndoLevel)
        return eventDc

    def _snapshotsReset(self):
        self._snapshotFiles, self._snapshotsUpdateLast = [], time.time()
        self.commands._snapshotsReset()
        if self.commands.canvasPathName != None:
            canvasPathName = os.path.abspath(self.commands.canvasPathName)
            canvasFileName = os.path.basename(canvasPathName)
            canvasPathNameHash = hashlib.sha1(canvasPathName.encode()).hexdigest()
            self._snapshotsDirName = os.path.join(getLocalConfPathName(), "{}_{}".format(canvasFileName, canvasPathNameHash))
            if os.path.exists(self._snapshotsDirName):
                for snapshotFile in natural_sort([f for f in os.listdir(self._snapshotsDirName) \
                        if (re.match(r'snapshot\d+\.txt$', f)) and os.path.isfile(os.path.join(self._snapshotsDirName, f))]):
                    self.commands._snapshotsPush(os.path.join(self._snapshotsDirName, snapshotFile))
        else:
            self._snapshotsDirName = None

    def _snapshotsUpdate(self):
        if self._snapshotsDirName != None:
            t = time.time()
            if (t > self._snapshotsUpdateLast) and ((t - self._snapshotsUpdateLast) >= (5 * 60)):
                try:
                    if not os.path.exists(self._snapshotsDirName):
                        os.makedirs(self._snapshotsDirName)
                    self._snapshotFiles = natural_sort([f for f in os.listdir(self._snapshotsDirName)
                        if (re.match(r'snapshot\d+\.txt$', f)) and os.path.isfile(os.path.join(self._snapshotsDirName, f))])
                    if self._snapshotFiles != []:
                        snapshotsCount, snapshotIndex = len(self._snapshotFiles), abs(int(re.match(r'snapshot(\d+)\.txt$', self._snapshotFiles[-1])[1])) + 1
                    else:
                        snapshotsCount, snapshotIndex = 0, 1
                    snapshotPathName = os.path.join(self._snapshotsDirName, "snapshot{}.txt".format(snapshotIndex));
                    self.commands.update(snapshotStatus=True)
                    with open(snapshotPathName, "w", encoding="utf-8") as outFile:
                        self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
                        self.canvas.exportStore.exportTextFile(self.canvas.map, self.canvas.size, outFile)
                        self.SetCursor(wx.Cursor(wx.NullCursor))
                    self.commands.update(snapshotStatus=False); self._snapshotsUpdateLast = time.time();
                    self._snapshotFiles += [os.path.basename(snapshotPathName)];
                    self.commands._snapshotsPush(snapshotPathName)
                    if len(self._snapshotFiles) > 72:
                        for snapshotFile in self._snapshotFiles[:len(self._snapshotFiles) - 8]:
                            self.commands._snapshotsPop(os.path.join(self._snapshotsDirName, snapshotFile))
                            os.remove(os.path.join(self._snapshotsDirName, snapshotFile)); snapshotsCount -= 1;
                except:
                    print("Exception during _snapshotsUpdate(): {}".format(sys.exc_info()[1]))

    def _windowEraseBackground(self, eventDc):
        viewRect = self.GetViewStart()
        canvasSize, panelSize = [a * b for a, b in zip(self.backend.canvasSize, self.backend.cellSize)], self.GetSize()
        if viewRect != (0, 0):
            viewRect = [a * b for a, b in zip(self.backend.cellSize, viewRect)]
            canvasSize = [a - b for a, b in zip(canvasSize, viewRect)]
        rectangles, pens, brushes = [], [], []
        if panelSize[0] > canvasSize[0]:
            brushes += [self.bgBrush]; pens += [self.bgPen];
            rectangles += [[canvasSize[0], 0, panelSize[0] - canvasSize[0], panelSize[1]]]
        if panelSize[1] > canvasSize[1]:
            brushes += [self.bgBrush]; pens += [self.bgPen];
            rectangles += [[0, canvasSize[1], panelSize[0], panelSize[1] - canvasSize[1]]]
        if len(rectangles) > 0:
            eventDc.DrawRectangleList(rectangles, pens, brushes)

    def applyOperator(self, currentTool, mapPoint, mouseLeftDown, mousePoint, operator, viewRect):
        eventDc, patches, patchesCursor, rc = self.backend.getDeviceContext(self.GetClientSize(), self), None, None, True
        if (currentTool.__class__ == ToolObject) and (currentTool.toolState >= currentTool.TS_SELECT):
            region = currentTool.getRegion(self.canvas)
        else:
            region = self.canvas.map
        if hasattr(operator, "apply2"):
            self.commands.update(operator=self.commands.currentOperator.name)
            if mouseLeftDown:
                self.commands.operatorState = True if self.commands.operatorState == None else self.commands.operatorState
                region = operator.apply2(mapPoint, mousePoint, region, copy.deepcopy(region))
            elif self.commands.operatorState != None:
                self.commands.currentOperator = None; self.commands.update(operator=None); rc = False;
        else:
            region = operator.apply(copy.deepcopy(region)); self.commands.currentOperator = None;
        if rc:
            if (currentTool.__class__ == ToolObject) and (currentTool.toolState >= currentTool.TS_SELECT):
                currentTool.setRegion(self.canvas, None, region, [len(region[0]), len(region)], currentTool.external)
                rc, patches, patchesCursor = currentTool.onSelectEvent(self.canvas, (0, 0), True, wx.MOD_NONE, None, currentTool.targetRect)
                patchesCursor = [] if patchesCursor == None else patchesCursor
                patchesCursor += currentTool._drawSelectRect(currentTool.targetRect)
                self._applyPatches(eventDc, patches, patchesCursor, rc)
            else:
                patches = []
                for numRow in range(len(region)):
                    for numCol in range(len(region[numRow])):
                        patches += [[numCol, numRow, *region[numRow][numCol]]]
                self._applyPatches(eventDc, patches, patchesCursor, rc)
                if (patches != None) and (len(patches) > 0):
                    self._snapshotsUpdate()
        return rc

    def applyTool(self, eventDc, eventMouse, keyChar, keyCode, keyModifiers, mapPoint, mouseDragging, mouseLeftDown, mouseRightDown, tool, viewRect, force=False):
        patches, patchesCursor, rc = None, None, False
        if viewRect == None:
            viewRect = self.GetViewStart()
        if eventDc == None:
            eventDc = self.backend.getDeviceContext(self.GetClientSize(), self, viewRect)
        if eventMouse:
            self.lastCellState = None if force else self.lastCellState
            if  ((mapPoint[0] < self.canvas.size[0]) and (mapPoint[1] < self.canvas.size[1]))   \
            and ((self.lastCellState == None) or (self.lastCellState != [list(mapPoint), mouseDragging, mouseLeftDown, mouseRightDown, list(viewRect)])):
                self.brushPos = list(mapPoint) if tool.__class__ != ToolText else self.brushPos
                if tool != None:
                    rc, patches, patchesCursor = tool.onMouseEvent(mapPoint, self.brushColours, self.brushPos, self.brushSize, self.canvas, keyModifiers, self.brushPos, mouseDragging, mouseLeftDown, mouseRightDown)
                else:
                    rc, patches, patchesCursor = True, None, [[*mapPoint, self.brushColours[0], self.brushColours[0], 0, " "]]
                self.lastCellState = [list(mapPoint), mouseDragging, mouseLeftDown, mouseRightDown, list(viewRect)]
        else:
            if tool != None:
                rc, patches, patchesCursor = tool.onKeyboardEvent(mapPoint, self.brushColours, self.brushPos, self.brushSize, self.canvas, keyChar, keyCode, keyModifiers, self.brushPos)
            elif mapPoint != None:
                rc, patches, patchesCursor = True, None, [[*mapPoint, self.brushColours[0], self.brushColours[0], 0, " "]]
        if rc:
            for patch in patches if patches != None else []:
                if  ((patch[2] == -1) and (patch[3] == -1)) \
                and (patch[0] < self.canvas.size[0])        \
                and (patch[1] < self.canvas.size[1]):
                    patch[2:] = self.canvas.map[patch[1]][patch[0]]
            self._applyPatches(eventDc, patches, patchesCursor, rc)
            if (tool.__class__ == ToolObject) and (tool.external, tool.toolState) == (True, tool.TS_NONE):
                self.dropTarget.done(); self.commands.currentTool, self.commands.lastTool = self.commands.lastTool, self.commands.currentTool;
                self.commands.update(currentTool=self.commands.currentTool)
            if (patches != None) and (len(patches) > 0):
                self._snapshotsUpdate()
        return rc

    def cursorHide(self, eventDc=None, eventDcResetOrigin=True, reset=False):
        if eventDc == None:
            eventDc = self.backend.getDeviceContext(self.GetClientSize(), self)
        if eventDcResetOrigin:
            eventDcOrigin = eventDc.GetDeviceOrigin(); eventDc.SetDeviceOrigin(0, 0);
        patchesCursor = self.canvas.popCursor(reset=reset); patchesCursor_ = [];
        for cursorCell in [p[:2] for p in patchesCursor]:
            if (cursorCell[0] < self.canvas.size[0]) and (cursorCell[1] < self.canvas.size[1]):
                patchesCursor_ += [[*cursorCell, *self.canvas.map[cursorCell[1]][cursorCell[0]]]]
        if len(patchesCursor_) > 0:
            self.backend.drawPatches(self.canvas, eventDc, patchesCursor_, False)
        if eventDcResetOrigin:
            eventDc.SetDeviceOrigin(*eventDcOrigin)
        return eventDc

    def cursorShow(self, eventDc=None, eventDcResetOrigin=True, patchesCursor=None):
        if eventDc == None:
            eventDc = self.backend.getDeviceContext(self.GetClientSize(), self)
        if eventDcResetOrigin:
            eventDcOrigin = eventDc.GetDeviceOrigin(); eventDc.SetDeviceOrigin(0, 0);
        if patchesCursor == None:
            patchesCursor = self.canvas.popCursor(reset=False)
        elif len(patchesCursor) > 0:
            self.canvas.pushCursor(patchesCursor)
        if (patchesCursor != None) and (len(patchesCursor) > 0):
            self.backend.drawPatches(self.canvas, eventDc, patchesCursor, isCursor=True)
        if eventDcResetOrigin:
            eventDc.SetDeviceOrigin(*eventDcOrigin)

    def onEnterWindow(self, event):
        self.lastCellState = None

    def onKeyboardInput(self, event):
        keyCode, keyModifiers = event.GetKeyCode(), event.GetModifiers()
        viewRect = self.GetViewStart(); eventDc = self.backend.getDeviceContext(self.GetClientSize(), self, viewRect);
        if (keyCode, keyModifiers,) == (wx.WXK_PAUSE, wx.MOD_SHIFT,):
            pdb.set_trace()
        elif keyCode in (wx.WXK_DOWN, wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP):
            if keyCode == wx.WXK_DOWN:
                self.brushPos[1] = (self.brushPos[1] + 1) % self.canvas.size[1]
            elif keyCode == wx.WXK_LEFT:
                self.brushPos[0] = (self.brushPos[0] - 1) if (self.brushPos[0] > 0) else (self.canvas.size[0] - 1)
            elif keyCode == wx.WXK_RIGHT:
                self.brushPos[0] = (self.brushPos[0] + 1) % self.canvas.size[0]
            elif keyCode == wx.WXK_UP:
                self.brushPos[1] = (self.brushPos[1] - 1) if (self.brushPos[1] > 0) else (self.canvas.size[1] - 1)
            self.commands.update(cellPos=self.brushPos)
            self.applyTool(eventDc, True, None, None, None, self.brushPos, False, False, False, self.commands.currentTool, viewRect)
        elif (chr(event.GetUnicodeKey()) == " ") and (self.commands.currentTool.__class__ != ToolText):
            if not self.applyTool(eventDc, True, None, None, event.GetModifiers(), self.brushPos, False, True, False, self.commands.currentTool, viewRect):
                event.Skip()
            else:
                self.brushPos[0] = (self.brushPos[0] + 1) if (self.brushPos[0] < (self.canvas.size[0] - 1)) else 0
                self.commands.update(cellPos=self.brushPos)
                self.applyTool(eventDc, True, None, None, None, self.brushPos, False, False, False, self.commands.currentTool, viewRect)
        elif not self.applyTool(eventDc, False, chr(event.GetUnicodeKey()), keyCode, keyModifiers, None, None, None, None, self.commands.currentTool, viewRect):
            event.Skip()

    def onLeaveWindow(self, event):
        if False:
            self.cursorHide()
        self.lastCellState = None

    def onMouseInput(self, event):
        viewRect = self.GetViewStart(); eventDc = self.backend.getDeviceContext(self.GetClientSize(), self, viewRect);
        mouseDragging, mouseLeftDown, mouseRightDown = event.Dragging(), event.LeftIsDown(), event.RightIsDown()
        self.lastMouseState = [mouseDragging, mouseLeftDown, mouseRightDown]
        mapPoint = self.backend.xlateEventPoint(event, eventDc, viewRect)
        if viewRect != (0, 0):
            mapPoint = [a + b for a, b in zip(mapPoint, viewRect)]
        if self.commands.currentOperator != None:
            self.applyOperator(self.commands.currentTool, mapPoint, mouseLeftDown, event.GetLogicalPosition(eventDc), self.commands.currentOperator, viewRect)
        elif  mouseRightDown                                    \
        and (self.commands.currentTool.__class__ == ToolObject) \
        and (self.commands.currentTool.toolState >= self.commands.currentTool.TS_SELECT):
            self.popupEventDc = eventDc; self.PopupMenu(self.operatorsMenu); self.popupEventDc = None;
        elif not self.applyTool(eventDc, True, None, None, event.GetModifiers(), mapPoint, mouseDragging, mouseLeftDown, mouseRightDown, self.commands.currentTool, viewRect):
            event.Skip()

    def onMouseWheel(self, event):
        delta, modifiers = +1 if event.GetWheelRotation() >= event.GetWheelDelta() else -1, event.GetModifiers()
        if modifiers == (wx.MOD_CONTROL | wx.MOD_ALT):
            newFontSize = self.backend.fontSize + delta
            if newFontSize > 0:
                self.Freeze()
                self.backend.fontSize = newFontSize; self.backend.resize(self.canvas.size); self.scrollStep = self.backend.cellSize;
                super().resize([a * b for a, b in zip(self.canvas.size, self.backend.cellSize)])
                patches = []
                for numRow in range(self.canvas.size[1]):
                    for numCol in range(len(self.canvas.map[numRow])):
                        patches += [[numCol, numRow, *self.canvas.map[numRow][numCol]]]
                eventDc = self.backend.getDeviceContext(self.GetClientSize(), self, self.GetViewStart())
                eventDcOrigin = eventDc.GetDeviceOrigin(); eventDc.SetDeviceOrigin(0, 0);
                self.cursorHide(eventDc, False, False)
                self.backend.drawPatches(self.canvas, eventDc, patches, isCursor=False)
                self.cursorShow(eventDc, False)
                eventDc.SetDeviceOrigin(*eventDcOrigin)
                self.Thaw(); self._windowEraseBackground(wx.ClientDC(self));
        elif modifiers == (wx.MOD_CONTROL | wx.MOD_SHIFT):
            self.commands.canvasCanvasSize(self.commands.canvasCanvasSize, 2, 1 if delta > 0 else 0)(None)
        elif modifiers == wx.MOD_CONTROL:
            self.commands.canvasBrushSize(self.commands.canvasBrushSize, 2, 1 if delta > 0 else 0)(None)
        else:
            event.Skip()

    def onPaint(self, event):
        viewRect = self.GetViewStart()
        eventDc = self.backend.getDeviceContext(self.GetClientSize(), self)
        self.backend.onPaint(self.GetClientSize(), self, viewRect)
        del eventDc; self._windowEraseBackground(wx.PaintDC(self));

    def resize(self, newSize, commitUndo=True, dirty=True, freeze=True):
        if freeze:
            self.Freeze()
        viewRect = self.GetViewStart()
        oldSize = [0, 0] if self.canvas.map == None else self.canvas.size
        deltaSize = [b - a for a, b in zip(oldSize, newSize)]
        rc, newCells = self.canvas.resize(self.brushColours, newSize, commitUndo)
        if rc:
            self.backend.resize(newSize); self.scrollStep = self.backend.cellSize;
            super().resize([a * b for a, b in zip(newSize, self.backend.cellSize)])
            self._applyPatches(None, newCells, None, True, commitUndo=False, dirty=True, hideCursor=False)
            self.Scroll(*viewRect); self.dirty = dirty;
            self.commands.update(dirty=self.dirty, size=newSize, undoLevel=self.canvas.patchesUndoLevel)
            if commitUndo:
                self._snapshotsUpdate()
        if freeze:
            self.cursorShow(); self.Thaw(); self._windowEraseBackground(wx.ClientDC(self));

    def undo(self, redo=False):
        freezeFlag, patches, patchesDelta = False, [], self.canvas.popUndo(redo)
        for patch in [p for p in patchesDelta if p != None]:
            if patch[0] == "resize":
                if not freezeFlag:
                    self.Freeze(); freezeFlag = True;
                self.resize(patch[1:], False, freeze=False)
            else:
                patches += [patch]
        eventDc = self._applyPatches(None, patches, None, True, commitUndo=False, hideCursor=False)
        self.cursorShow(eventDc, True, None)
        if freezeFlag:
            self.Thaw(); self._windowEraseBackground(wx.ClientDC(self));

    def update(self, newSize, commitUndo=True, newCanvas=None, dirty=True):
        self.resize(newSize, commitUndo, dirty); self.canvas.update(newSize, newCanvas);
        patches = []
        for numRow in range(newSize[1]):
            for numCol in range(newSize[0]):
                patches += [[numCol, numRow, *self.canvas.map[numRow][numCol]]]
        self._applyPatches(None, patches, None, True, dirty=False)

    def __init__(self, backend, canvas, commands, parent, pos, size):
        super().__init__(parent, pos); self.parent, self.size = parent, size;
        self.backend, self.canvas, self.commands = backend(self.size), canvas, commands(self, parent)
        self.bgBrush, self.bgPen = wx.Brush(self.GetBackgroundColour(), wx.BRUSHSTYLE_SOLID), wx.Pen(self.GetBackgroundColour(), 1)
        self.brushColours, self.brushPos, self.brushSize, = [3, -1], [0, 0], [1, 1]
        self.dirty, self.lastCellState, self.lastMouseState = False, None, [False, False, False]
        self.dropTarget, self.popupEventDc = RoarCanvasWindowDropTarget(self), None
        for event, handler in ((wx.EVT_ERASE_BACKGROUND, lambda event: None,), (wx.EVT_MOUSEWHEEL, self.onMouseWheel,),):
            self.Bind(event, handler)
        self.SetDropTarget(self.dropTarget)
        self._snapshotsReset()

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
