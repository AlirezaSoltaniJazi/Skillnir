"""Styled form card wrapper component."""

from contextlib import contextmanager

from nicegui import ui


@contextmanager
def form_card():
    """Context manager that yields a styled card for form inputs.

    Usage::

        with form_card():
            ui.input('Target project').props('outlined dense rounded')
    """
    with ui.card().classes('w-full p-6 rounded-xl').props('flat bordered'):
        yield
