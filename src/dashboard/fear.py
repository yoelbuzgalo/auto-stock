import customtkinter as ctk
from src.constants import *

class FearMeter(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        kwargs.setdefault("width", int(FEAR_PANEL_WIDTH))
        kwargs.setdefault("height", int(FEAR_PANEL_HEIGHT))
        super().__init__(master, **kwargs)
        
        fear_title = ctk.CTkLabel(self, text="Fear & Greed Index", font=(FONT_FAMILY, int(FONT_SIZE_MEDIUM), "bold"))
        fear_title.pack(pady=(PADDING_FEAR_INNER_X, PADDING_FEAR_INNER_X // 3))

        self.meter_bar = ctk.CTkProgressBar(
            self, 
            orientation="horizontal", 
            height=25, 
            fg_color="#444444", 
            progress_color=GREEN
        )
        self.meter_bar.set(0.32)
        self.meter_bar.pack(fill="x", padx=PADDING_FEAR_INNER_X + 10, pady=PADDING_FEAR_INNER_Y)

        self.meter_label = ctk.CTkLabel(self, text="Fear", font=(FONT_FAMILY, int(FONT_SIZE_LARGE), "bold"), text_color=GREEN)
        self.meter_label.pack(pady=(0, PADDING_FEAR_INNER_X))
        self.grid(row=0, column=1, padx=PADDING_FEAR_PANEL_X, pady=PADDING_FEAR_PANEL_Y, sticky="nsew")

    def update(self, value):
        self._update_fear_meter(value)
        
    def _update_fear_meter(self, value):
        self.meter_bar.set(round(value, 2) / 100)
        text = "Greed"
        color = RED
        if value <= 50:
            text = "Fear"
            color = GREEN
        self.meter_label.configure(text=text, text_color=color)
        self.meter_bar.configure(progress_color=color)
        self.meter_label.update()
        self.meter_bar.update()