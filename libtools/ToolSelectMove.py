#!/usr/bin/env python3
#
# ToolSelectMove.py -- XXX
# Copyright (c) 2018 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
#

from ToolSelect import ToolSelect

class ToolSelectMove(ToolSelect):
    """XXX"""
    name = "Move selection"

    #
    # onSelectEvent(self, disp, dispatchFn, eventDc, isCursor, newToolRect, selectRect): XXX
    def onSelectEvent(self, disp, dispatchFn, eventDc, isCursor, newToolRect, selectRect):
        for numRow in range(len(self.toolSelectMap)):
            for numCol in range(len(self.toolSelectMap[numRow])):
                dispatchFn(eventDc, isCursor, [self.srcRect[0] + numCol, self.srcRect[1] + numRow, 1, 1, 0, " "])
        for numRow in range(len(self.toolSelectMap)):
            for numCol in range(len(self.toolSelectMap[numRow])):
                cellOld = self.toolSelectMap[numRow][numCol]
                rectX, rectY = selectRect[0][0] + numCol, selectRect[0][1] + numRow
                dispatchFn(eventDc, isCursor, [rectX + disp[0], rectY + disp[1], *cellOld])

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120