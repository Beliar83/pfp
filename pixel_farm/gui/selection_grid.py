"""This module contains the classes to manage a selection grid.

.. module:: selection_grid
    :synopsis: Classes to manage a selection grid..

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

import PyCEGUI


class CellData(object):

    def __init__(self):
        self.selected = False
        self.hovered = False


class SelectionGrid(object):

    """A grid to choose the form and size of a selection

    Parameters
    ----------
    grid_widget: PyCEGUI.GridLayoutContainer
        A GridLayoutContainer that is the base for the grid

    Attributes
    ----------
    grid_widget : PyCCEGUI.GridLayoutContainer
        A GridLayoutContainer that is the base for the grid
    cell_width : PyCEGUI.UDim
        The width of each cell
    cell_height : PyCEGUI.UDim
        The height of each cell
    cells : list of CellData
        Cell data for each cell.
    cell_rect : PyCEGUI.Rectf
        Rectangle describing the selected clls
    last_hovered : int
        The index of the last hovered cell
    mouse_cell : list of int
        The grid coordinates of the mouse cell
    x_reach : int
        The vertical reach of the selection
    y_reach : int
        The horizontal reach of the selection
    reach_behind : bool
        Whether it is possible to select cells behind the mouse cell
    """

    def __init__(self, grid_widget):
        #: :type grid_widget: PyCEGUI.GridLayoutContainer
        self.grid_widget = grid_widget
        pcegui_glc = PyCEGUI.GridLayoutContainer
        self.grid_widget.subscribeEvent(pcegui_glc.EventMouseLeavesArea,
                                        self.grid_widget_mouse_leave)
        self.cell_width = PyCEGUI.UDim(0, 24)
        self.cell_height = PyCEGUI.UDim(0, 24)
        self.cells = []
        self.cell_rect = PyCEGUI.Rectf(-1, -1, -1, -1)
        self.last_hovered = -1
        self.mouse_cell = (-1, -1)
        self.x_reach = -1
        self.y_reach = -1
        self.reach_behind = False

    def update_grid(self):
        """Update the state of the grid cells"""
        height = self.grid_widget.getGridHeight()
        width = self.grid_widget.getGridWidth()
        for row in xrange(height):
            for col in xrange(width):
                cell = self.grid_widget.getChildAtPosition(col, row)
                cell_index = row * width + col
                #: :type cell_data: CellData
                cell_data = self.cells[cell_index]
                alpha = 0.0
                if cell_data.selected:
                    alpha += 0.125
                if cell_data.hovered:
                    alpha += 0.125
                if self.cell_rect.isPointInRect(PyCEGUI.Vector2f(col, row)):
                    alpha += 0.125
                p_helper = PyCEGUI.PropertyHelper
                img_colours_str = cell.getProperty("ImageColours")
                img_colours = p_helper.stringToColourRect(
                    img_colours_str)
                assert isinstance(img_colours, PyCEGUI.ColourRect)
                img_colours.setAlpha(alpha)
                new_bg_colours_str = p_helper.colourRectToString(
                    img_colours)
                cell.setProperty("ImageColours",
                                 new_bg_colours_str)

    def recreate_grid(self, x_reach, y_reach, reach_behind=False):
        """Recreates the grid using the given x_reach and y_reach.

        This also resets the selected cells.

        Parameters
        ----------

        x_reach : int
            The new x_reach of the grid
        y_reach : int
            The new y_reach of the grid
        reach_behind : int, optional
            Whether the selection can go below the mouse cell, vertically

        """
        self.x_reach = x_reach
        self.y_reach = y_reach
        self.reach_behind = reach_behind
        tmp_multi = 2 if reach_behind else 1
        width = x_reach * 2 + 1
        height = y_reach * tmp_multi + 1
        self.last_hovered = -1
        self.grid_widget.setGridDimensions(width, height)
        w_mgr = PyCEGUI.WindowManager.getSingleton()
        assert isinstance(w_mgr, PyCEGUI.WindowManager)
        new_size = PyCEGUI.USize()
        new_size.d_width = self.cell_width * width
        new_size.d_height = self.cell_height * height
        self.grid_widget.setSize(new_size)
        self.cells = []
        for row in xrange(height):
            for col in xrange(width):
                cell = self.grid_widget.getChildAtPosition(col, row)
                assert isinstance(cell, PyCEGUI.Window)
                if cell.getType() != "TaharezLook/StaticImage":
                    new_cell = w_mgr.createWindow("TaharezLook/StaticImage")
                    assert isinstance(new_cell, PyCEGUI.DefaultWindow)
                    new_cell.setWidth(self.cell_width)
                    new_cell.setHeight(self.cell_height)
                    new_cell.setProperty("Image", "images/1x1")
                    p_helper = PyCEGUI.PropertyHelper
                    img_colours_str = new_cell.getProperty("ImageColours")
                    img_colours = p_helper.stringToColourRect(
                        img_colours_str)
                    assert isinstance(img_colours, PyCEGUI.ColourRect)
                    img_colours.setAlpha(0.0)
                    new_bg_colours_str = p_helper.colourRectToString(
                        img_colours)
                    new_cell.setProperty("ImageColours",
                                         new_bg_colours_str)
                    tmp_emea = PyCEGUI.DefaultWindow.EventMouseEntersArea
                    tmp_emla = PyCEGUI.DefaultWindow.EventMouseLeavesArea
                    tmp_emc = PyCEGUI.DefaultWindow.EventMouseClick
                    new_cell.subscribeEvent(tmp_emea,
                                            lambda args, row=row, col=col:
                                            self.grid_widget_cell_mouse_enter(
                                                args, row, col))
                    new_cell.subscribeEvent(tmp_emla,
                                            lambda args, row=row, col=col:
                                            self.grid_widget_cell_mouse_leave(
                                                args, row, col))
                    new_cell.subscribeEvent(tmp_emc,
                                            lambda args, row=row, col=col:
                                            self.grid_widget_cell_clicked(
                                                args, row, col))

                    self.grid_widget.addChildToPosition(new_cell, col, row)
                    self.cells.append(CellData())
        self.cells[0].selected = True
        self.cell_rect.d_min = PyCEGUI.Vector2f(0, 0)
        self.cell_rect.d_max = PyCEGUI.Vector2f(0.9, 0.9)
        self.mouse_cell = (0, 0)

    def reset_selection(self):
        """Resets the selected cells"""
        width = self.grid_widget.getGridWidth()
        tmp_pos = self.cell_rect.getPosition()
        #: :type tmp_pos: PyCEGUI.Vector2f
        sel_start_col = int(tmp_pos.d_x)
        sel_start_row = int(tmp_pos.d_y)
        sel_cols = int(self.cell_rect.getWidth()) + 1
        sel_rows = int(self.cell_rect.getHeight()) + 1
        self.mouse_cell = (-1, -1)

        for row in xrange(sel_start_row, sel_start_row + sel_rows):
            for col in xrange(sel_start_col, sel_start_col + sel_cols):
                cell_index = row * width + col
                cell = self.cells[cell_index]
                #: :type cell: CellData
                cell.selected = False

    def select_cell(self, row, col):
        """Selects the cell at the given row and column

        Parameters
        ----------
        row : int
            The row of the cell
        col : int
            The Column of the cell
        """
        width = self.grid_widget.getGridWidth()
        cell_index = row * width + col
        self.cells[cell_index].selected = True
        if self.mouse_cell[1] >= 0:
            mouse_index = self.mouse_cell[1] * width + self.mouse_cell[0]
            self.cells[mouse_index].selected = False
        self.mouse_cell = (col, row)

    def grid_widget_cell_mouse_enter(self, args, row, col):
        """Called when the mouse enters a cell of the grid

        Parameters
        ----------
        args : PyCEGUI.MouseEventArgs
            The event arguments
        row : int
            The row of the cell
        col : int
            The Column of the cell
        """
        #: :type args: PyCEGUI.MouseEventArgs
        width = self.grid_widget.getGridWidth()
        cell_index = row * width + col
        cell = self.cells[cell_index]
        #: type cell: CellData
        cell.hovered = True
        self.last_hovered = cell_index

    def grid_widget_cell_mouse_leave(self, args, row, col):
        """Called when the mouse leaves a cell of the grid

        Parameters
        ----------
        args : PyCEGUI.MouseEventArgs
            The event arguments
        row : int
            The row of the cell
        col : int
            The Column of the cell
        """
        #: :type args: PyCEGUI.MouseEventArgs
        width = self.grid_widget.getGridWidth()
        cell_index = row * width + col
        cell = self.cells[cell_index]
        #: type cell: CellData
        cell.hovered = False

    def grid_widget_cell_clicked(self, args, row, col):
        """Called when a cell in the select grid was clicked

        Parameters
        ----------
        args : PyCEGUI.MouseEventArgs
            The event arguments
        row : int
            The row of the cell
        col : int
            The Column of the cell
        """
        #: :type args: PyCEGUI.MouseEventArgs
        if args.sysKeys & PyCEGUI.SystemKeys.Shift:
            mouse_col = self.mouse_cell[0]
            mouse_row = self.mouse_cell[1]
            x_reach = col - mouse_col
            y_reach = row - mouse_row
            if (x_reach > self.x_reach or
                    y_reach > self.y_reach or
                    x_reach < self.x_reach * -1 or
                    y_reach < self.y_reach * -1):
                return
            if x_reach > 0:
                self.cell_rect.d_max.d_x = col + 0.9
            elif x_reach < 0:
                self.cell_rect.d_min.d_x = col
            if y_reach > 0 and self.reach_behind:
                self.cell_rect.d_max.d_y = row + 0.9
            elif y_reach < 0:
                self.cell_rect.d_min.d_y = row
        else:
            self.reset_selection()
            self.cell_rect.d_min = PyCEGUI.Vector2f(col, row)
            self.cell_rect.d_max = PyCEGUI.Vector2f(col + 0.9, row + 0.9)
            self.select_cell(row, col)

    def grid_widget_mouse_leave(self, args):
        """Called when the mouse enters the grid area

        Parameters
        ----------
        args: PyCEGUI.MouseEventArgs
            The event data
        """
        if self.last_hovered >= 0:
            last_cell = self.cells[self.last_hovered]
            #: type last_cell: CellData
            last_cell.hovered = False
            self.last_hovered = -1


def calculate_sel_bounds(start, end):
    """Calculate the bounds of a selection using a start and end cell

    Parameters
    ----------
    start : list
        The cell where the selection starts
    end : list
        The cell where the selection ends

    Returns
    -------
    left : int
        The Leftmost column of the selection
    right : int
        The rightmost column of the selection
    top : int
        The topmost row of the selection
    bottom : int
        The bottommost row of the select
    """
    start_y = start[0]
    start_x = start[1]
    end_y = end[0]
    end_x = end[1]
    left = -1
    right = -1
    top = -1
    bottom = -1
    if start_x < end_x:
        left = start_x
        right = end_x
    else:
        left = end_x
        right = start_x
    if start_y < end_y:
        top = start_y
        bottom = end_y
    else:
        top = end_y
        bottom = start_y
    return left, right, top, bottom
