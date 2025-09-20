from aiogram.fsm.state import State, StatesGroup

class AnonymousMessage(StatesGroup):
    waiting_for_message = State()
    waiting_for_reply = State()