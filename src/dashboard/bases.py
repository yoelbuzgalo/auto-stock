from abc import ABC, abstractmethod
import queue as q
import customtkinter as ctk

class BasePanel(ABC):
    """
    Abstract Base Class for all auxiliary dashboard panels.
    Enforces a standardized UI initialization lifecycle and provides
    consistent geometric constraints across the application.
    """
    
    def __init__(self, master, width: int = 320, height: int = 500, **kwargs):
        """
        Initializes base configuration parameters for CustomTkinter frames.

        Args:
            master (tk.Tk / ctk.CTk / ctk.CTkFrame): The parent container.
            width (int): Fixed runtime layout width configuration. Defaults to 320.
            height (int): Fixed runtime layout height configuration. Defaults to 500.
            **kwargs: Arbitrary keyword arguments passed to the ctk.CTkFrame superclass.
        """
        super().__init__(master, width=width, height=height, **kwargs)

    @abstractmethod
    def _build_ui(self):
        """
        Abstract lifecycle hook. Child classes must override this method 
        to assemble, bind, and pack internal frame widget configurations.
        """
        pass

class BaseDashboard(ctk.CTkFrame, ABC):
    __slots__ = ()

    def __init__(self, master, fg_color):
        super().__init__(master=master, fg_color=fg_color)
        self.gui_queue = q.Queue()

    def _safe_get_queue(self):
        return getattr(self, "gui_queue", None)

    def _safe_get_chart(self):
        if hasattr(self, "layout"):
            return getattr(self.layout, "chart", None)
        return None

    @property
    @abstractmethod
    def chart(self):
        pass

    @chart.setter
    @abstractmethod
    def chart(self, chart):
        pass

    @property
    @abstractmethod
    def queue(self):
        pass


class BaseLayout(ABC):

    def __init__(self, root: BaseDashboard, worker: BaseWorker):
        self.root = root
        self.worker = worker

    def _configure_grid_layout(self):
        pass

    def _init_dashboard_panels(self, worker):
        pass

    def get_chart(self):
        return None

    def update_status_msg(self, text, color=""):
        pass

    def clear_all_news(self):
        pass

class BaseThread(ABC):
    pass

class BaseWorker(ABC):
    
    def get_price_input(self):
        pass

    def retrieve_yfinance(self,ticker):
        pass