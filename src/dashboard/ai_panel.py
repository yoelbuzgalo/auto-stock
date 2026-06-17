import threading
import json
import time
import requests
import customtkinter as ctk
from modules.ai import OllamaClient, get_sys_prompt
from src.constants import *
from .bases import BasePanel,BaseDashboard

SYS_PROMPT = get_sys_prompt("../../data/prompts/analyze_news.txt")

class AIPanel(BasePanel, ctk.CTkFrame):
    """
    Manages an asynchronous, smooth-streaming terminal view providing responses from local LLM engines.
    """

    def __init__(self, master, dashboard:BaseDashboard):
        """
        Sets initial configurations and invokes layout builds using responsive layout geometries.
        """
        super().__init__(master, fg_color="transparent")
        self.root = dashboard
        self.grid_rowconfigure(1, weight=2)
        self.grid_columnconfigure(0, weight=2)
        self._build_ui()
        self.ollama_client = OllamaClient(
            url=OLLAMA_URL,
            model=DEFAULT_MODEL,
            timeout=60
        )

    def _build_ui(self):
        """
        Creates basic interface infrastructure containing multi-line scrolling text nodes and action controls.
        """
        header = ctk.CTkLabel(self, text="AI Chat", font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"))
        header.grid(row=0, column=0, sticky="w", padx=PADDING_AI_HEADER_X, pady=(PADDING_AI_HEADER_Y_TOP, PADDING_AI_HEADER_Y_BOTTOM))
        self.chat_display = ctk.CTkTextbox(self, fg_color="transparent", font=(FONT_FAMILY, FONT_SIZE_BODY), wrap="word", state="disabled")
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=PADDING_AI_CHAT_X, pady=PADDING_AI_CHAT_Y)
        input_dock = ctk.CTkFrame(self, fg_color="transparent")
        input_dock.grid(row=2, column=0, sticky="ew", padx=PADDING_AI_DOCK_X, pady=(0, PADDING_AI_DOCK_Y_BOTTOM))
        input_dock.grid_columnconfigure(0, weight=1)
        self.chat_input = ctk.CTkEntry(input_dock, placeholder_text="Ask AI or type 'get news AAPL'...", font=(FONT_FAMILY, FONT_SIZE_BODY))
        self.chat_input.grid(row=0, column=0, sticky="ew", padx=(0, PADDING_AI_INPUT_X_RIGHT))
        self.chat_input.bind("<Return>", lambda e: self._submit_query())
        self.send_btn = ctk.CTkButton(input_dock, text="Send", width=AI_SEND_BTN_WIDTH, fg_color=DEEP_BLUE, font=(FONT_FAMILY, FONT_SIZE_BODY, "bold"), command=self._submit_query)
        self.send_btn.grid(row=0, column=1, sticky="e")
        self.grid(row=1, column=0, sticky="snew", padx=(PADDING_AI_GRID_X_RIGHT, PADDING_MAIN_X), pady=PADDING_MAIN_Y)
        self._append_message("Jordan Belfort", "Hello! Ask me market questions or tell me to retrieve news for a ticker.")

    def _append_message(self, sender, body):
        """
        Inserts static contextual strings safely formatted directly inside the text viewing target space.
        """
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}: {body}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _submit_query(self):
        """
        Extracts pending text buffers and boots an isolated worker execution context thread.
        """
        user_text = self.chat_input.get().strip()
        if not user_text:
            return
        self._append_message("You", user_text)
        self.chat_input.delete(0, "end")
        threading.Thread(target=self._process_ai_logic, args=(user_text,), daemon=True).start()

    def _process_ai_logic(self, query):
        """
        Routes dashboard commands or streams local AI output using a persistent Ollama connection.
        """
        query_lower = query.lower()

        if any(keyword in query_lower for keyword in ["news", "data", "chart"]):
            ticker = self._extract_ticker_from_query(query)

            self.root.queue.put(
                lambda t=ticker: self._append_message(
                    "System",
                    f"Dispatched background worker to pull fresh news for {t}..."
                )
            )

            self.root.queue.put(lambda s=self, t=ticker: set_input(s,t))
            return

        try:
            prompt = f"{SYS_PROMPT}\n\n{query}"

            self.root.queue.put(lambda: self._start_stream_block("AI: "))

            token_buffer = []
            last_flush = time.time()

            for token in self.ollama_client.stream_prompt(prompt):
                token_buffer.append(token)

                if time.time() - last_flush > 0.040:
                    text_to_print = "".join(token_buffer)
                    token_buffer.clear()

                    self.root.queue.put(
                        lambda t=text_to_print: self._stream_append_token(t)
                    )

                    last_flush = time.time()

            if token_buffer:
                text_to_print = "".join(token_buffer)

                self.root.queue.put(
                    lambda t=text_to_print: self._stream_append_token(t)
                )

            self.root.queue.put(lambda: self._finalize_stream_block())

        except requests.exceptions.ConnectionError:
            self.root.queue.put(
                lambda: self._append_message(
                    "System Error",
                    "Could not talk to local AI. Ensure Ollama service is running via port 11434."
                )
            )

        except requests.exceptions.Timeout:
            self.root.queue.put(
                lambda: self._append_message(
                    "System Error",
                    "Ollama request timed out. The model may still be loading or responding slowly."
                )
            )

        except Exception as e:
            self.root.queue.put(
                lambda err=str(e): self._append_message(
                    "System Error",
                    f"Inference failure: {err}"
                )
            )

    def _extract_ticker_from_query(self, query):
        """
        Extracts a likely ticker symbol from the user query.

        Args:
            query (str): User input text.

        Returns:
            str: Uppercase ticker symbol.
        """
        words = query.upper().replace(",", " ").replace(".", " ").split()

        ignored_words = {
            "NEWS",
            "DATA",
            "CHART",
            "FOR",
            "ABOUT",
            "SHOW",
            "GET",
            "ANALYZE",
            "ANALYSIS"
        }

        for word in words:
            if word.isalpha() and 1 <= len(word) <= 5 and word not in ignored_words:
                return word

        if hasattr(self.root, "chart") and hasattr(self.root.chart, "ticker"):
            ticker = self.root.chart.ticker
            if ticker:
                return ticker

        return DEFAULT_TICKER

    def _start_stream_block(self, sender_tag):
        """
        Prepares the textual landscape canvas to dynamically receive structured text fragment additions.
        """
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", sender_tag)
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _stream_append_token(self, token):
        """
        Appends batched text segments cleanly into the operational container element.
        """
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", token)
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _finalize_stream_block(self):
        """
        Injects uniform whitespace separation indicators marking conclusion sequences of text delivery operations.
        """
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", "\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")



"""

Getters


"""


"""

Setters


"""

def set_input(root:AIPanel,ticker:str):
    root.dashboard.chart.input = ticker