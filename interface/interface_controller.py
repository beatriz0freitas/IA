from __future__ import annotations
import tkinter as tk
from typing import Callable, Optional


class InterfaceController:

    def __init__(self, root: tk.Misc):
        self.root = root
        self._after_id: Optional[str] = None

    def schedule(self, delay_ms: int, func: Callable[[], None]) -> None:
        self.cancel()
        self._after_id = self.root.after(delay_ms, func)

    def cancel(self) -> None:
        if self._after_id is None:
            return
        try:
            self.root.after_cancel(self._after_id)
        except tk.TclError:
            pass
        finally:
            self._after_id = None

    @property
    def active(self) -> bool:
        return self._after_id is not None