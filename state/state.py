from aiogram.dispatcher.filters.state import StatesGroup, State


class Edit(StatesGroup):
	name = State()

class Edit_subcat(StatesGroup):
	name = State()

class Edit_subcat1(StatesGroup):
	description = State()

class Edit_subcat2(StatesGroup):
	price = State()

class Add(StatesGroup):
	category = State()

class Add_subcat(StatesGroup):
	name = State()
	description = State()
	price = State()

class Get_ammot(StatesGroup):
	ammot = State()

class Add_sub(StatesGroup):
	product = State()

class Topup(StatesGroup):
	sum = State()
	currency = State()

class Find(StatesGroup):
	user = State()

class Balance(StatesGroup):
	edit = State()