import customtkinter as ctk
from src.constants import *

class FearMeter(ctk.CTkFrame):


    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        fear_title = ctk.CTkLabel(self, text="Fear & Greed Index", font=("Helvetica", 16, "bold"))
        fear_title.pack(pady=(15, 5))

        self.meter_bar = ctk.CTkProgressBar(
            self, 
            orientation="horizontal", 
            height=25, 
            fg_color="#444444", 
            progress_color=GREEN
        )
        self.meter_bar.set(0.32)
        self.meter_bar.pack(fill="x", padx=30, pady=20)

        self.meter_label = ctk.CTkLabel(self, text="Fear", font=("Helvetica", 24, "bold"), text_color=GREEN)
        self.meter_label.pack(pady=(0, 15))
        self.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")


    def update(self,value):
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
        
