#!/usr/bin/env python3
#
# MiRCARTFrame.py -- XXX
# Copyright (c) 2018 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from MiRCARTCanvas import MiRCARTCanvas, haveUrllib
from MiRCARTColours import MiRCARTColours
from MiRCARTGeneralFrame import MiRCARTGeneralFrame,    \
    TID_ACCELS, TID_COMMAND, TID_LIST, TID_MENU, TID_NOTHING, TID_SELECT, TID_TOOLBAR
from MiRCARTToolCircle import MiRCARTToolCircle
from MiRCARTToolLine import MiRCARTToolLine
from MiRCARTToolRect import MiRCARTToolRect
from MiRCARTToolText import MiRCARTToolText
                
import os, wx

class MiRCARTFrame(MiRCARTGeneralFrame):
    """XXX"""
    panelCanvas = canvasPathName = None
    canvasPos = canvasSize = cellSize = None

    # {{{ Commands
    #                      Id     Type Id      Labels                           Icon bitmap                 Accelerator                 [Initial state]
    CID_NEW             = [0x100, TID_COMMAND, "New", "&New",                   ["", wx.ART_NEW],           [wx.ACCEL_CTRL, ord("N")]]
    CID_OPEN            = [0x101, TID_COMMAND, "Open", "&Open",                 ["", wx.ART_FILE_OPEN],     [wx.ACCEL_CTRL, ord("O")]]
    CID_SAVE            = [0x102, TID_COMMAND, "Save", "&Save",                 ["", wx.ART_FILE_SAVE],     [wx.ACCEL_CTRL, ord("S")]]
    CID_SAVEAS          = [0x103, TID_COMMAND, "Save As...", "Save &As...",     ["", wx.ART_FILE_SAVE_AS],  None]
    CID_EXPORT_AS_PNG   = [0x104, TID_COMMAND, "Export as PNG...",              \
                                               "Export as PN&G...",             None,                       None]
    CID_EXPORT_IMGUR    = [0x105, TID_COMMAND, "Export to Imgur...",            \
                                               "Export to I&mgur...",           None,                       None,                       haveUrllib]
    CID_EXPORT_PASTEBIN = [0x106, TID_COMMAND, "Export to Pastebin...",         \
                                               "Export to Pasteb&in...",        None,                       None,                       haveUrllib]
    CID_EXIT            = [0x107, TID_COMMAND, "Exit", "E&xit",                 None,                       None]
    CID_UNDO            = [0x108, TID_COMMAND, "Undo", "&Undo",                 ["", wx.ART_UNDO],          [wx.ACCEL_CTRL, ord("Z")],  False]
    CID_REDO            = [0x109, TID_COMMAND, "Redo", "&Redo",                 ["", wx.ART_REDO],          [wx.ACCEL_CTRL, ord("Y")],  False]
    CID_CUT             = [0x10a, TID_COMMAND, "Cut", "Cu&t",                   ["", wx.ART_CUT],           None,                       False]
    CID_COPY            = [0x10b, TID_COMMAND, "Copy", "&Copy",                 ["", wx.ART_COPY],          None,                       False]
    CID_PASTE           = [0x10c, TID_COMMAND, "Paste", "&Paste",               ["", wx.ART_PASTE],         None,                       False]
    CID_DELETE          = [0x10d, TID_COMMAND, "Delete", "De&lete",             ["", wx.ART_DELETE],        None,                       False]
    CID_INCRBRUSH       = [0x10e, TID_COMMAND, "Increase brush size",           \
                                               "&Increase brush size",          ["", wx.ART_PLUS],          [wx.ACCEL_CTRL, ord("+")]]
    CID_DECRBRUSH       = [0x10f, TID_COMMAND, "Decrease brush size",           \
                                               "&Decrease brush size",          ["", wx.ART_MINUS],         [wx.ACCEL_CTRL, ord("-")]]
    CID_SOLID_BRUSH     = [0x110, TID_SELECT,  "Solid brush", "&Solid brush",   None,                       None,                       True]

    CID_RECT            = [0x150, TID_SELECT,  "Rectangle", "&Rectangle",       ["toolRect.png"],           [wx.ACCEL_CTRL, ord("R")],  True]
    CID_CIRCLE          = [0x151, TID_SELECT,  "Circle", "&Circle",             ["toolCircle.png"],         [wx.ACCEL_CTRL, ord("C")],  False]
    CID_LINE            = [0x152, TID_SELECT,  "Line", "&Line",                 ["toolLine.png"],           [wx.ACCEL_CTRL, ord("L")],  False]
    CID_TEXT            = [0x153, TID_SELECT,  "Text", "&Text",                 ["toolText.png"],           [wx.ACCEL_CTRL, ord("T")],  False]

    CID_COLOUR00        = [0x1a0, TID_COMMAND, "Colour #00", "Colour #00",      None,                       None]
    CID_COLOUR01        = [0x1a1, TID_COMMAND, "Colour #01", "Colour #01",      None,                       None]
    CID_COLOUR02        = [0x1a2, TID_COMMAND, "Colour #02", "Colour #02",      None,                       None]
    CID_COLOUR03        = [0x1a3, TID_COMMAND, "Colour #03", "Colour #03",      None,                       None]
    CID_COLOUR04        = [0x1a4, TID_COMMAND, "Colour #04", "Colour #04",      None,                       None]
    CID_COLOUR05        = [0x1a5, TID_COMMAND, "Colour #05", "Colour #05",      None,                       None]
    CID_COLOUR06        = [0x1a6, TID_COMMAND, "Colour #06", "Colour #06",      None,                       None]
    CID_COLOUR07        = [0x1a7, TID_COMMAND, "Colour #07", "Colour #07",      None,                       None]
    CID_COLOUR08        = [0x1a8, TID_COMMAND, "Colour #08", "Colour #08",      None,                       None]
    CID_COLOUR09        = [0x1a9, TID_COMMAND, "Colour #09", "Colour #09",      None,                       None]
    CID_COLOUR10        = [0x1aa, TID_COMMAND, "Colour #10", "Colour #10",      None,                       None]
    CID_COLOUR11        = [0x1ab, TID_COMMAND, "Colour #11", "Colour #11",      None,                       None]
    CID_COLOUR12        = [0x1ac, TID_COMMAND, "Colour #12", "Colour #12",      None,                       None]
    CID_COLOUR13        = [0x1ad, TID_COMMAND, "Colour #13", "Colour #13",      None,                       None]
    CID_COLOUR14        = [0x1ae, TID_COMMAND, "Colour #14", "Colour #14",      None,                       None]
    CID_COLOUR15        = [0x1af, TID_COMMAND, "Colour #15", "Colour #15",      None,                       None]
    # }}}
    # {{{ Non-items
    NID_MENU_SEP        = (0x200, TID_NOTHING)
    NID_TOOLBAR_SEP     = (0x201, TID_NOTHING)
    # }}}
    # {{{ Menus
    MID_FILE            = (0x300, TID_MENU, "File", "&File", (                  \
        CID_NEW, CID_OPEN, CID_SAVE, CID_SAVEAS, NID_MENU_SEP,                  \
        CID_EXPORT_AS_PNG, CID_EXPORT_IMGUR, CID_EXPORT_PASTEBIN, NID_MENU_SEP, \
        CID_EXIT))
    MID_EDIT            = (0x301, TID_MENU, "Edit", "&Edit", (                  \
        CID_UNDO, CID_REDO, NID_MENU_SEP,                                       \
        CID_CUT, CID_COPY, CID_PASTE, CID_DELETE, NID_MENU_SEP,                 \
        CID_INCRBRUSH, CID_DECRBRUSH, CID_SOLID_BRUSH))
    MID_TOOLS           = (0x302, TID_MENU, "Tools", "&Tools", (                \
        CID_RECT, CID_CIRCLE, CID_LINE, CID_TEXT))
    # }}}
    # {{{ Toolbars
    BID_TOOLBAR         = (0x400, TID_TOOLBAR, (                                \
        CID_NEW, CID_OPEN, CID_SAVE, CID_SAVEAS, NID_TOOLBAR_SEP,               \
        CID_UNDO, CID_REDO, NID_TOOLBAR_SEP,                                    \
        CID_CUT, CID_COPY, CID_PASTE, CID_DELETE, NID_TOOLBAR_SEP,              \
        CID_INCRBRUSH, CID_DECRBRUSH, CID_SOLID_BRUSH, NID_TOOLBAR_SEP,         \
        CID_RECT, CID_CIRCLE, CID_LINE, CID_TEXT, NID_TOOLBAR_SEP,              \
        CID_COLOUR00, CID_COLOUR01, CID_COLOUR02, CID_COLOUR03, CID_COLOUR04,   \
        CID_COLOUR05, CID_COLOUR06, CID_COLOUR07, CID_COLOUR08, CID_COLOUR09,   \
        CID_COLOUR10, CID_COLOUR11, CID_COLOUR12, CID_COLOUR13, CID_COLOUR14,   \
        CID_COLOUR15))
    # }}}
    # {{{ Accelerators (hotkeys)
    AID_EDIT            = (0x500, TID_ACCELS, (                                 \
        CID_NEW, CID_OPEN, CID_SAVE, CID_UNDO, CID_REDO, CID_INCRBRUSH, CID_DECRBRUSH))
    # }}}
    # {{{ Lists
    LID_ACCELS          = (0x600, TID_LIST, (AID_EDIT))
    LID_MENUS           = (0x601, TID_LIST, (MID_FILE, MID_EDIT, MID_TOOLS))
    LID_TOOLBARS        = (0x602, TID_LIST, (BID_TOOLBAR))
    # }}}

    # {{{ _initPaletteToolBitmaps(self): XXX
    def _initPaletteToolBitmaps(self):
        paletteDescr = (                                                                                        \
                self.CID_COLOUR00, self.CID_COLOUR01, self.CID_COLOUR02, self.CID_COLOUR03, self.CID_COLOUR04,  \
                self.CID_COLOUR05, self.CID_COLOUR06, self.CID_COLOUR07, self.CID_COLOUR08, self.CID_COLOUR09,  \
                self.CID_COLOUR10, self.CID_COLOUR11, self.CID_COLOUR12, self.CID_COLOUR13, self.CID_COLOUR14,  \
                self.CID_COLOUR15)
        for numColour in range(len(paletteDescr)):
            toolBitmapColour = MiRCARTColours[numColour][0:4]
            toolBitmap = wx.Bitmap((16,16))
            toolBitmapDc = wx.MemoryDC(); toolBitmapDc.SelectObject(toolBitmap);
            toolBitmapBrush = wx.Brush(         \
                wx.Colour(toolBitmapColour), wx.BRUSHSTYLE_SOLID)
            toolBitmapDc.SetBrush(toolBitmapBrush)
            toolBitmapDc.SetBackground(toolBitmapBrush)
            toolBitmapDc.SetPen(wx.Pen(wx.Colour(toolBitmapColour), 1))
            toolBitmapDc.DrawRectangle(0, 0, 16, 16)
            paletteDescr[numColour][4] = ["", None, toolBitmap]
    # }}}
    # {{{ _dialogSaveChanges(self)
    def _dialogSaveChanges(self):
        with wx.MessageDialog(self,                             \
                "Do you want to save changes to {}?".format(    \
                    self.canvasPathName), "MiRCART",            \
                wx.CANCEL|wx.CANCEL_DEFAULT|wx.ICON_QUESTION|wx.YES_NO) as dialog:
            dialogChoice = dialog.ShowModal()
            return dialogChoice
    # }}}
    # {{{ _updateStatusBar(self, showColours=None, showFileName=True, showPos=None): XXX
    def _updateStatusBar(self, showColours=True, showFileName=True, showPos=True):
        if showColours == True:
            showColours = self.panelCanvas.brushColours
        if showPos == True:
            showPos = self.panelCanvas.brushPos
        if showFileName == True:
            showFileName = self.canvasPathName
        textItems = []
        if showPos != None:
            textItems.append("X: {:03d} Y: {:03d}".format(      \
                showPos[0], showPos[1]))
        if showColours != None:
            textItems.append("FG: {:02d}, BG: {:02d}".format(   \
                showColours[0],showColours[1]))
            textItems.append("{} on {}".format(                 \
                MiRCARTColours[showColours[0]][4],              \
                MiRCARTColours[showColours[1]][4]))
        if showFileName != None:
            textItems.append("Current file: {}".format(         \
                os.path.basename(showFileName)))
        self.statusBar.SetStatusText(" | ".join(textItems))
    # }}}

    # {{{ canvasExportAsPng(self): XXX
    def canvasExportAsPng(self):
        with wx.FileDialog(self, self.CID_SAVEAS[2], os.getcwd(), "",       \
                "*.png", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return False
            else:
                outPathName = dialog.GetPath()
                self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
                self.panelCanvas.canvasStore.exportBitmapToPngFile(         \
                    self.panelCanvas.canvasBitmap, outPathName,             \
                        wx.BITMAP_TYPE_PNG)
                self.SetCursor(wx.Cursor(wx.NullCursor))
                return True
    # }}}
    # {{{ canvasExportImgur(self): XXX
    def canvasExportImgur(self):
        self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
        imgurResult = self.panelCanvas.canvasStore.exportBitmapToImgur(     \
            "c9a6efb3d7932fd", self.panelCanvas.canvasBitmap, "", "", wx.BITMAP_TYPE_PNG)
        self.SetCursor(wx.Cursor(wx.NullCursor))
        if imgurResult[0] == 200:
            if not wx.TheClipboard.IsOpened():
                wx.TheClipboard.Open()
                wx.TheClipboard.SetData(wx.TextDataObject(imgurResult[1]))
                wx.TheClipboard.Close()
            wx.MessageBox("Exported to Imgur: " + imgurResult[1],           \
                "Export to Imgur", wx.OK|wx.ICON_INFORMATION)
        else:
            wx.MessageBox("Failed to export to Imgur: " + imgurResult[1],   \
                "Export to Imgur", wx.OK|wx.ICON_EXCLAMATION)
    # }}}
    # {{{ canvasExportPastebin(self): XXX
    def canvasExportPastebin(self):
        self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
        pasteStatus, pasteResult =                                          \
            self.panelCanvas.canvasStore.exportPastebin(                    \
                "",                          \
                self.panelCanvas.canvasMap,                                 \
                self.panelCanvas.canvasSize)
        self.SetCursor(wx.Cursor(wx.NullCursor))
        if pasteStatus:
            if not wx.TheClipboard.IsOpened():
                wx.TheClipboard.Open()
                wx.TheClipboard.SetData(wx.TextDataObject(pasteResult))
                wx.TheClipboard.Close()
            wx.MessageBox("Exported to Pastebin: " + pasteResult,           \
                "Export to Pastebin", wx.OK|wx.ICON_INFORMATION)
        else:
            wx.MessageBox("Failed to export to Pastebin: " + pasteResult,   \
                "Export to Pastebin", wx.OK|wx.ICON_EXCLAMATION)
    # }}}
    # {{{ canvasNew(self, newCanvasSize=None): XXX
    def canvasNew(self, newCanvasSize=None):
        if self.canvasPathName != None:
            saveChanges = self._dialogSaveChanges()
            if saveChanges == wx.ID_CANCEL:
                return
            elif saveChanges == wx.ID_NO:
                pass
            elif saveChanges == wx.ID_YES:
                self.canvasSave()
        self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
        if newCanvasSize == None:
            newCanvasSize = (100, 30)
        self.panelCanvas.canvasStore.importNew(newCanvasSize)
        self.canvasPathName = None
        self.SetCursor(wx.Cursor(wx.NullCursor))
        self._updateStatusBar(); self.onCanvasUpdate();
    # }}}
    # {{{ canvasOpen(self): XXX
    def canvasOpen(self):
        if self.canvasPathName != None:
            saveChanges = self._dialogSaveChanges()
            if saveChanges == wx.ID_CANCEL:
                return
            elif saveChanges == wx.ID_NO:
                pass
            elif saveChanges == wx.ID_YES:
                self.canvasSave()
        with wx.FileDialog(self, self.CID_OPEN[2], os.getcwd(), "", \
                "*.txt", wx.FD_OPEN) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return False
            else:
                self.canvasPathName = dialog.GetPath()
                self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
                self.panelCanvas.canvasStore.importTextFile(self.canvasPathName)
                self.panelCanvas.canvasStore.importIntoPanel()
                self.SetCursor(wx.Cursor(wx.NullCursor))
                self._updateStatusBar(); self.onCanvasUpdate();
                return True
    # }}}
    # {{{ canvasSave(self): XXX
    def canvasSave(self):
        if self.canvasPathName == None:
            if self.canvasSaveAs() == False:
                return
        try:
            with open(self.canvasPathName, "w") as outFile:
                self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
                self.panelCanvas.canvasStore.exportTextFile(            \
                    self.panelCanvas.canvasMap,                         \
                    self.panelCanvas.canvasSize, outFile)
                self.SetCursor(wx.Cursor(wx.NullCursor))
                return True
        except IOError as error:
            return False
    # }}}
    # {{{ canvasSaveAs(self): XXX
    def canvasSaveAs(self):
        with wx.FileDialog(self, self.CID_SAVEAS[2], os.getcwd(), "",   \
                "*.txt", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return False
            else:
                self.canvasPathName = dialog.GetPath()
                return self.canvasSave()
    # }}}
    # {{{ onCanvasMotion(self, event): XXX
    def onCanvasMotion(self, event, mapPoint=None):
        eventType = event.GetEventType()
        if eventType == wx.wxEVT_ENTER_WINDOW:
            pass
        elif eventType == wx.wxEVT_MOTION:
            self._updateStatusBar(showPos=mapPoint)
        elif eventType == wx.wxEVT_LEAVE_WINDOW:
            pass
    # }}}
    # {{{ onCanvasUpdate(self): XXX
    def onCanvasUpdate(self):
        if self.panelCanvas.canvasJournal.patchesUndo[self.panelCanvas.canvasJournal.patchesUndoLevel] != None:
            self.menuItemsById[self.CID_UNDO[0]].Enable(True)
            self.toolBar.EnableTool(self.CID_UNDO[0], True)
        else:
            self.menuItemsById[self.CID_UNDO[0]].Enable(False)
            self.toolBar.EnableTool(self.CID_UNDO[0], False)
        if self.panelCanvas.canvasJournal.patchesUndoLevel > 0:
            self.menuItemsById[self.CID_REDO[0]].Enable(True)
            self.toolBar.EnableTool(self.CID_REDO[0], True)
        else:
            self.menuItemsById[self.CID_REDO[0]].Enable(False)
            self.toolBar.EnableTool(self.CID_REDO[0], False)
    # }}}
    # {{{ onFrameCommand(self, event): XXX
    def onFrameCommand(self, event):
        cid = event.GetId()
        if cid == self.CID_NEW[0]:
            self.canvasNew()
        elif cid == self.CID_OPEN[0]:
            self.canvasOpen()
        elif cid == self.CID_SAVE[0]:
            self.canvasSave()
        elif cid == self.CID_SAVEAS[0]:
            self.canvasSaveAs()
        elif cid == self.CID_EXPORT_AS_PNG[0]:
            self.canvasExportAsPng()
        elif cid == self.CID_EXPORT_IMGUR[0]:
            self.canvasExportImgur()
        elif cid == self.CID_EXPORT_PASTEBIN[0]:
            self.canvasExportPastebin()
        elif cid == self.CID_EXIT[0]:
            self.Close(True)
        elif cid == self.CID_UNDO[0]:
            self.panelCanvas.undo()
        elif cid == self.CID_REDO[0]:
            self.panelCanvas.redo()
        elif cid == self.CID_CUT[0]:
            pass
        elif cid == self.CID_COPY[0]:
            pass
        elif cid == self.CID_PASTE[0]:
            pass
        elif cid == self.CID_DELETE[0]:
            pass
        elif cid == self.CID_INCRBRUSH[0]:
            self.panelCanvas.brushSize =        \
                [a+1 for a in self.panelCanvas.brushSize]
        elif cid == self.CID_DECRBRUSH[0]       \
        and  self.panelCanvas.brushSize[0] > 1  \
        and  self.panelCanvas.brushSize[1] > 1:
            self.panelCanvas.brushSize =        \
                [a-1 for a in self.panelCanvas.brushSize]
        elif cid == self.CID_SOLID_BRUSH[0]:
            pass
        elif cid == self.CID_RECT[0]:
            self.menuItemsById[cid].Check(True)
            self.panelCanvas.canvasCurTool =    \
                MiRCARTToolRect(self.panelCanvas)
        elif cid == self.CID_CIRCLE[0]:
            self.menuItemsById[cid].Check(True)
            self.panelCanvas.canvasCurTool =    \
                MiRCARTToolCircle(self.panelCanvas)
        elif cid == self.CID_LINE[0]:
            self.menuItemsById[cid].Check(True)
            self.panelCanvas.canvasCurTool =    \
                MiRCARTToolLine(self.panelCanvas)
        elif cid == self.CID_TEXT[0]:
            self.menuItemsById[cid].Check(True)
            self.panelCanvas.canvasCurTool =    \
                MiRCARTToolText(self.panelCanvas)
        elif cid >= self.CID_COLOUR00[0]        \
        and  cid <= self.CID_COLOUR15[0]:
            numColour = cid - self.CID_COLOUR00[0]
            if event.GetEventType() == wx.wxEVT_TOOL:
                self.panelCanvas.brushColours[0] = numColour
            elif event.GetEventType() == wx.wxEVT_TOOL_RCLICKED:
                self.panelCanvas.brushColours[1] = numColour
            self._updateStatusBar()
    # }}}
    # {{{ __del__(self): destructor method
    def __del__(self):
        if self.panelCanvas != None:
            self.panelCanvas.Close(); self.panelCanvas = None;
    # }}}

    #
    # __init__(self, parent, appSize=(800, 600), canvasPos=(25, 50), canvasSize=(100, 30), cellSize=(7, 14)): initialisation method
    def __init__(self, parent, appSize=(800, 600), canvasPos=(25, 50), canvasSize=(100, 30), cellSize=(7, 14)):
        self._initPaletteToolBitmaps()
        panelSkin = super().__init__(parent, wx.ID_ANY, "MiRCART", size=appSize)
        self.canvasPos = canvasPos; self.cellSize = cellSize; self.canvasSize = canvasSize;
        self.canvasPathName = None
        self.panelCanvas = MiRCARTCanvas(panelSkin, parentFrame=self,   \
            canvasPos=self.canvasPos, canvasSize=self.canvasSize,       \
            cellSize=self.cellSize)
        self.panelCanvas.canvasCurTool = MiRCARTToolRect(self.panelCanvas)
        self.canvasNew()

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
