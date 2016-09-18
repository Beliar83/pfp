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
        Rectangle describing the selected cells
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
        self.dragging = False
        self.drag_start = (-1, -1)
        self.drag_rect = PyCEGUI.Rectf(-1, -1, -1, -1)
        self.select_color = PyCEGUI.Colour(1.0, 1.0, 1.0, 0)
        self.hover_color = PyCEGUI.Colour(1.0, 1.0, 1.0, 0)
        self.drag_color = PyCEGUI.Colour(1.0, 1.0, 1.0, 0)

    def update_grid(self):
        """Update the state of the grid cells"""
        height = self.grid_widget.getGridHeight()
        width = self.grid_widget.getGridWidth()
        rect = self.drag_rect if self.dragging else self.cell_rect
        for row in range(height):
            for col in range(width):
                cell = self.grid_widget.getChildAtPosition(col, row)
                cell_index = row * width + col
                #: :type cell_data: CellData
                cell_data = self.cells[cell_index]
                alpha = 0.0
                color = self.select_color
                if cell_data.selected:
                    alpha += 0.125
                if cell_data.hovered:
                    alpha += 0.125
                    color = self.hover_color
                if rect.isPointInRect(PyCEGUI.Vector2f(col, row)):
                    alpha += 0.125
                    if self.dragging:
                        color = self.drag_color
                p_helper = PyCEGUI.PropertyHelper
                color.setAlpha(alpha)
                new_img_colours_str = p_helper.colourToString(color)
                cell.setProperty("ImageColours",
                                 new_img_colours_str)

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
        for row in range(height):
            for col in range(width):
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
        if self.mouse_cell[0] >= 0:
            mouse_index = self.mouse_cell[1] * width + self.mouse_cell[0]
            self.cells[mouse_index].selected = False

        self.mouse_cell = (-1, -1)

        for row in range(sel_start_row, sel_start_row + sel_rows):
            for col in range(sel_start_col, sel_start_col + sel_cols):
                cell_index = row * width + col
                cell = self.cells[cell_index]
                #: :type cell: CellData
                cell.selected = False
        self.select_color = PyCEGUI.Colour(1.0, 1.0, 1.0, 0)

    def select_cell(self, row, col):
        """Selects the cell at the given row and column

        Parameters
        ----------
        row, col : int
            The row and column of the cell
        """
        width = self.grid_widget.getGridWidth()
        cell_index = row * width + col
        self.cells[cell_index].selected = True
        if self.mouse_cell[0] >= 0:
            mouse_index = self.mouse_cell[1] * width + self.mouse_cell[0]
            self.cells[mouse_index].selected = False
        self.mouse_cell = (col, row)

    def is_selection_valid(self, rect):
        """Check whether a selection is valid - at least one cell is near
        the mouse cell and no cell in the same row if reach behind is not
        active

        Parameters
        ----------
        rect : PyCEGUI.Rectf
            The selection rectangle to check
        Returns
        -------
        bool
            True if the selection is valid, otherwise False
        """
        in_rect = rect.isPointInRect
        mouse_col, mouse_row = self.mouse_cell
        Vec2f = PyCEGUI.Vector2f
        is_mouse_near_selection = False
        #: :type rect: PyCGUI.Rectf
        if not self.reach_behind and int(rect.bottom()) >= mouse_row:
            return False
        if mouse_col > 0 and in_rect(Vec2f(mouse_col - 1, mouse_row)):
            is_mouse_near_selection = True
        elif (mouse_col < self.cell_width.d_offset and
              in_rect(Vec2f(mouse_col + 1, mouse_row))):
            is_mouse_near_selection = True
        elif (mouse_row > 0 and
              in_rect(Vec2f(mouse_col, mouse_row - 1))):
            is_mouse_near_selection = True
        elif (mouse_row < self.cell_height.d_offset and
              in_rect(Vec2f(mouse_col, mouse_row + 1))):
            is_mouse_near_selection = True
        return is_mouse_near_selection

    def is_drag_selection_valid(self):
        """Check whether the current drag selection is valid (at least one cell
        near the mouse cell

        Returns
        -------
        bool
            True if the selection is valid, otherwise alse
        """
        return self.is_selection_valid(self.drag_rect)

    def is_cell_in_reach(self, row, col):
        """Check whether a cell is in reach of the mouse cell (a selection can
        reach a cell next to the mouse cell).

        Parameters
        ----------
        row, col : int
            The row and column of the cell

        Returns
        -------
        bool
            True if the cell is in reach, False otherwise
        """
        mouse_col, mouse_row = self.mouse_cell
        if (row <= mouse_row and row + self.y_reach >= mouse_row or
                self.reach_behind and
                (row >= mouse_row and row - self.y_reach <= mouse_row)):
            if (col <= mouse_col and col + self.x_reach >= mouse_col or
                    col >= mouse_col and col - self.y_reach <= mouse_col):
                return True
        return False

    def grid_widget_cell_mouse_enter(self, args, row, col):
        """Called when the mouse enters a cell of the grid

        Parameters
        ----------
        args : PyCEGUI.MouseEventArgs
            The event arguments
        row, col : int
            The row and column of the cell
        """
        #: :type args: PyCEGUI.MouseEventArgs
        if not self.dragging:
            if args.sysKeys & PyCEGUI.SystemKeys.Shift:
                if self.is_cell_in_reach(row, col):
                    self.hover_color = PyCEGUI.Colour(1, 1, 1, 0)
                else:
                    self.hover_color = PyCEGUI.Colour(1, 0, 0, 0)
            else:
                self.hover_color = PyCEGUI.Colour(1, 1, 1, 0)
            width = self.grid_widget.getGridWidth()
            cell_index = row * width + col
            cell = self.cells[cell_index]
            #: type cell: CellData
            cell.hovered = True
            self.last_hovered = cell_index
        else:
            left, right, top, bottom = calculate_sel_bounds(
                self.start_drag, (row, col))
            if right - left > self.x_reach:
                right -= left
            if bottom - top > self.y_reach:
                bottom -= top
            self.drag_rect.d_min.d_x = left
            self.drag_rect.d_min.d_y = top
            self.drag_rect.d_max.d_x = right + 0.9
            self.drag_rect.d_max.d_y = bottom + 0.9
            if (self.is_drag_selection_valid() and
                    self.is_cell_in_reach(row, col)):
                self.drag_color = PyCEGUI.Colour(1, 1, 1, 0)
            else:
                self.drag_color = PyCEGUI.Colour(1, 0, 0, 0)

    def grid_widget_cell_mouse_leave(self, args, row, col):
        """Called when the mouse leaves a cell of the grid

        Parameters
        ----------
        args : PyCEGUI.MouseEventArgs
            The event arguments
        row, col : int
            The row and column of the cell
        """
        #: :type args: PyCEGUI.MouseEventArgs
        if not self.dragging:
            width = self.grid_widget.getGridWidth()
            cell_index = row * width + col
            cell = self.cells[cell_index]
            #: type cell: CellData
            cell.hovered = False

    def start_selection(self, row, col):
        """Start a new Selection at the given row and column.

        Parameters
        ----------
        row, col : int
            The row and column of the cell
        """
        self.dragging = True
        self.start_drag = (row, col)
        self.drag_rect.d_min = PyCEGUI.Vector2f(col, row)
        self.drag_rect.d_max = PyCEGUI.Vector2f(col, row)
        width = self.grid_widget.getGridWidth()
        cell_index = row * width + col
        cell = self.cells[cell_index]
        #: type cell: CellData
        cell.hovered = False

    def check_and_end_selection(self, row, col):
        """End the current running selection at the given row and column if
        it is valid

        Parameters
        ----------
        row, col : int
            The row and column of the cell
        """
        if not (self.is_drag_selection_valid() and
                self.is_cell_in_reach(row, col)):
            return
        self.dragging = False
        left, right, top, bottom = calculate_sel_bounds(
            self.start_drag, (row, col))
        self.cell_rect.d_min.d_x = left
        self.cell_rect.d_min.d_y = top
        self.cell_rect.d_max.d_x = right + 0.9
        self.cell_rect.d_max.d_y = bottom + 0.9

    def cancel_selection(self):
        """Cancel the current running selection"""
        self.dragging = False

    def grid_widget_cell_clicked(self, args, row, col):
        """Called when a cell in the select grid was clicked

        Parameters
        ----------
        args : PyCEGUI.MouseEventArgs
            The event arguments
        row, col : int
            The row and column of the cell
        """
        #: :type args: PyCEGUI.MouseEventArgs
        if args.button == PyCEGUI.MouseButton.LeftButton:
            if args.sysKeys & PyCEGUI.SystemKeys.Shift:
                if not self.dragging:
                    self.start_selection(row, col)
                else:
                    self.check_and_end_selection(row, col)
            else:
                if not self.dragging:
                    self.reset_selection()
                    self.cell_rect.d_min = PyCEGUI.Vector2f(col, row)
                    self.cell_rect.d_max = PyCEGUI.Vector2f(
                        col + 0.9, row + 0.9)
                    self.select_cell(row, col)
                else:
                    self.check_and_end_selection(row, col)
        elif args.button == PyCEGUI.MouseButton.RightButton:
            if self.dragging:
                self.cancel_selection()

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
