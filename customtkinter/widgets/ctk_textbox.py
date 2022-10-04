import tkinter
from typing import Union, Tuple

from .ctk_canvas import CTkCanvas
from ..theme_manager import ThemeManager
from ..draw_engine import DrawEngine
from .widget_base_class import CTkBaseClass

from .widget_helper_functions import pop_from_dict_by_set


class CTkTextbox(CTkBaseClass):
    """
    Textbox with rounded corners, and all text features of tkinter.Text widget.
    For detailed information check out the documentation.
    """

    # attributes that are passed to and managed by the tkinter textbox only:
    _valid_tk_text_attributes = {"autoseparators", "cursor", "exportselection",
                                 "insertborderwidth", "insertofftime", "insertontime", "insertwidth",
                                 "maxundo", "padx", "pady", "selectborderwidth", "spacing1",
                                 "spacing2", "spacing3", "state", "tabs", "takefocus", "undo", "wrap",
                                 "xscrollcommand", "yscrollcommand"}

    def __init__(self, *args,
                 width: int = 200,
                 height: int = 200,
                 corner_radius: Union[str, str] = "default_theme",
                 border_width: Union[str, str] = "default_theme",

                 bg_color: Union[str, Tuple[str, str], None] = None,
                 fg_color: Union[str, Tuple[str, str], None] = "default_theme",
                 border_color: Union[str, Tuple[str, str]] = "default_theme",
                 text_color: Union[str, str] = "default_theme",

                 font: any = "default_theme",
                 **kwargs):

        # transfer basic functionality (_bg_color, size, _appearance_mode, scaling) to CTkBaseClass
        if "master" in kwargs:
            super().__init__(*args, bg_color=bg_color, width=width, height=height, master=kwargs.pop("master"))
        else:
            super().__init__(*args, bg_color=bg_color, width=width, height=height)

        # color
        self._fg_color = ThemeManager.theme["color"]["entry"] if fg_color == "default_theme" else fg_color
        self._border_color = ThemeManager.theme["color"]["frame_border"] if border_color == "default_theme" else border_color
        self._text_color = ThemeManager.theme["color"]["text"] if text_color == "default_theme" else text_color

        # shape
        self._corner_radius = ThemeManager.theme["shape"]["frame_corner_radius"] if corner_radius == "default_theme" else corner_radius
        self._border_width = ThemeManager.theme["shape"]["frame_border_width"] if border_width == "default_theme" else border_width

        # text
        self._font = (ThemeManager.theme["text"]["font"], ThemeManager.theme["text"]["size"]) if font == "default_theme" else font

        # configure 1x1 grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._canvas = CTkCanvas(master=self,
                                 highlightthickness=0,
                                 width=self._apply_widget_scaling(self._current_width),
                                 height=self._apply_widget_scaling(self._current_height))
        self._canvas.grid(row=0, column=0, padx=0, pady=0, rowspan=1, columnspan=1, sticky="nsew")
        self._canvas.configure(bg=ThemeManager.single_color(self._bg_color, self._appearance_mode))
        self._draw_engine = DrawEngine(self._canvas)

        for arg in ["highlightthickness", "fg", "bg", "font", "width", "height"]:
            kwargs.pop(arg, None)
        self._textbox = tkinter.Text(self,
                                     fg=ThemeManager.single_color(self._text_color, self._appearance_mode),
                                     width=0,
                                     height=0,
                                     font=self._font,
                                     highlightthickness=0,
                                     relief="flat",
                                     insertbackground=ThemeManager.single_color(self._text_color, self._appearance_mode),
                                     bg=ThemeManager.single_color(self._fg_color, self._appearance_mode),
                                     **pop_from_dict_by_set(kwargs, self._valid_tk_text_attributes))
        self._textbox.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="nsew",
                           padx=self._apply_widget_scaling(self._corner_radius),
                           pady=self._apply_widget_scaling(self._corner_radius))

        self._check_kwargs_empty(kwargs, raise_error=True)

        super().bind('<Configure>', self._update_dimensions_event)
        self._draw()

    def _set_scaling(self, *args, **kwargs):
        super()._set_scaling(*args, **kwargs)

        self._textbox.configure(font=self._apply_font_scaling(self._font))
        self._textbox.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="nsew",
                           padx=self._apply_widget_scaling(self._corner_radius),
                           pady=self._apply_widget_scaling(self._corner_radius))

        self._canvas.configure(width=self._apply_widget_scaling(self._desired_width),
                               height=self._apply_widget_scaling(self._desired_height))
        self._draw()

    def _set_dimensions(self, width=None, height=None):
        super()._set_dimensions(width, height)

        self._canvas.configure(width=self._apply_widget_scaling(self._desired_width),
                               height=self._apply_widget_scaling(self._desired_height))
        self._draw()

    def _draw(self, no_color_updates=False):

        requires_recoloring = self._draw_engine.draw_rounded_rect_with_border(self._apply_widget_scaling(self._current_width),
                                                                              self._apply_widget_scaling(self._current_height),
                                                                              self._apply_widget_scaling(self._corner_radius),
                                                                              self._apply_widget_scaling(self._border_width))

        if no_color_updates is False or requires_recoloring:
            if self._fg_color is None:
                self._canvas.itemconfig("inner_parts",
                                        fill=ThemeManager.single_color(self._bg_color, self._appearance_mode),
                                        outline=ThemeManager.single_color(self._bg_color, self._appearance_mode))
            else:
                self._canvas.itemconfig("inner_parts",
                                        fill=ThemeManager.single_color(self._fg_color, self._appearance_mode),
                                        outline=ThemeManager.single_color(self._fg_color, self._appearance_mode))

            self._canvas.itemconfig("border_parts",
                                    fill=ThemeManager.single_color(self._border_color, self._appearance_mode),
                                    outline=ThemeManager.single_color(self._border_color, self._appearance_mode))
            self._canvas.configure(bg=ThemeManager.single_color(self._bg_color, self._appearance_mode))

            self._textbox.configure(fg=ThemeManager.single_color(self._text_color, self._appearance_mode),
                                    bg=ThemeManager.single_color(self._fg_color, self._appearance_mode),
                                    insertbackground=ThemeManager.single_color(self._text_color, self._appearance_mode))

        self._canvas.tag_lower("inner_parts")
        self._canvas.tag_lower("border_parts")

    def configure(self, require_redraw=False, **kwargs):
        if "fg_color" in kwargs:
            self._fg_color = kwargs.pop("fg_color")
            require_redraw = True

            # check if CTk widgets are children of the frame and change their _bg_color to new frame fg_color
            for child in self.winfo_children():
                if isinstance(child, CTkBaseClass) and hasattr(child, "_fg_color"):
                    child.configure(bg_color=self._fg_color)

        if "border_color" in kwargs:
            self._border_color = kwargs.pop("border_color")
            require_redraw = True

        if "text_color" in kwargs:
            self._text_color = kwargs.pop("text_color")
            require_redraw = True

        if "corner_radius" in kwargs:
            self._corner_radius = kwargs.pop("corner_radius")
            self._textbox.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="nsew",
                               padx=self._apply_widget_scaling(self._corner_radius),
                               pady=self._apply_widget_scaling(self._corner_radius))
            require_redraw = True

        if "border_width" in kwargs:
            self._border_width = kwargs.pop("border_width")
            require_redraw = True

        if "width" in kwargs:
            self._set_dimensions(width=kwargs.pop("width"))

        if "height" in kwargs:
            self._set_dimensions(height=kwargs.pop("height"))

        if "font" in kwargs:
            self._font = kwargs.pop("font")
            self._textbox.configure(font=self._apply_font_scaling(self._font))

        self._textbox.configure(**pop_from_dict_by_set(kwargs, self._valid_tk_text_attributes))
        super().configure(require_redraw=require_redraw, **kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "corner_radius":
            return self._corner_radius
        elif attribute_name == "border_width":
            return self._border_width

        elif attribute_name == "fg_color":
            return self._fg_color
        elif attribute_name == "border_color":
            return self._border_color
        elif attribute_name == "text_color":
            return self._text_color

        elif attribute_name == "font":
            return self._font

        else:
            return super().cget(attribute_name)

    def bind(self, sequence=None, command=None, add=None):
        """ called on the tkinter.Text """
        return self._textbox.bind(sequence, command, add)

    def unbind(self, sequence, funcid=None):
        """ called on the tkinter.Text """
        return self._textbox.unbind(sequence, funcid)

    def insert(self, index, text, tags=None):
        return self._textbox.insert(index, text, tags)

    def get(self, index1, index2=None):
        return self._textbox.get(index1, index2)

