from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import *
from data.bd import *
import asyncio


async def amdin_menu():
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = '📈 Statistics', callback_data='statistics'),
				InlineKeyboardButton(text = '📌 Control', callback_data='control'),
			],
			[
				InlineKeyboardButton(text = '🔎 Find user', callback_data='finduser'),
			],
			[
				InlineKeyboardButton(text = '🔙', callback_data='back'),
			],
		]
	)

	return markup

async def amdin_list_menu():
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = '📁 Category', callback_data='edit_category'),
				InlineKeyboardButton(text = '📄 Subcategories', callback_data='edit_subcategories'),

			],
			[
				InlineKeyboardButton(text = '🔙', callback_data='admin'),
			]
		]
	)

	return markup

async def find_user_adm(user_id):
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = '💵 Edit balance', callback_data=f'user_edit_balanse|{user_id}'),
			],
			[
				InlineKeyboardButton(text = '🔙', callback_data='admin'),
			]
		]
	)

	return markup

async def amdin_catalog_menu():
	categories = await get_categories()
	markup = InlineKeyboardMarkup(row_width=2)
	if categories != None:
		for category in categories:
			markup.insert(
				InlineKeyboardButton(text = category[1], callback_data=f'adm_category:{category[0]}'),
			)
		markup.add(
				InlineKeyboardButton(text = '➕ Add category', callback_data='add_category'),
			)
		markup.add(
				InlineKeyboardButton(text = '🔙', callback_data='admin'),
			)
	else:
		markup.add(
				InlineKeyboardButton(text = '➕ Add category', callback_data='add_category'),
			)
		markup.add(
				InlineKeyboardButton(text = '🔙', callback_data='admin'),
			)

	return markup


async def amdin_catalog_edit_menu(id, name):
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = '👁 Edit Name', callback_data=f'edit_name:{id}:{name}'),
				InlineKeyboardButton(text = '🗑 Delete', callback_data=f'delete:{id}'),
			],
			[
				InlineKeyboardButton(text = '🔙', callback_data='admin'),
			]
		]
	)

	return markup


async def back_menu_adm():
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = '🔙', callback_data='admin'),
			]
		]
	)

	return markup

async def amdin_catalog_sub_menu():
	categories = await get_categories()
	markup = InlineKeyboardMarkup(row_width=2)
	if categories != None:
		for category in categories:
			markup.insert(
				InlineKeyboardButton(text = category[1], callback_data=f'select_category:{category[0]}'),
			)
		markup.add(
				InlineKeyboardButton(text = '🔙', callback_data='admin'),
			)
	else:
		markup.add(
				InlineKeyboardButton(text = '🔙', callback_data='admin'),
			)

	return markup

async def amdin_subcategories_menu(category_id):
	subcategories = await get_subcategories(category_id)
	markup = InlineKeyboardMarkup(row_width=2)
	if subcategories != None:
		for subcategory in subcategories:
			markup.insert(
				InlineKeyboardButton(text = subcategory[1], callback_data=f'adm_subcategory:{subcategory[0]}'),
			)
		markup.add(
				InlineKeyboardButton(text = '➕ Add subcategory', callback_data=f'add_subcategory:{category_id}'),
			)
		markup.add(
				InlineKeyboardButton(text = '🔙', callback_data='admin'),
			)
	else:
		markup.add(
				InlineKeyboardButton(text = '➕ Add subcategory', callback_data=f'add_subcategory:{category_id}'),
			)
		markup.add(
				InlineKeyboardButton(text = '🔙', callback_data='admin'),
			)

	return markup

async def amdin_subcategories_edit_menu(id):
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = '👁 Edit Name', callback_data=f'edit_subcategories_name:{id}'),
				InlineKeyboardButton(text = '💬 Edit description', callback_data=f'edit_subcategories_description:{id}'),
			],
			[
				InlineKeyboardButton(text = '💸 Edit Price', callback_data=f'edit_subcategories_price:{id}'),
				InlineKeyboardButton(text = '🗑 Delete', callback_data=f'subcategories_delete:{id}'),
			],
			[
				InlineKeyboardButton(text = '➕ Add product', callback_data=f'subcategories_add_product:{id}'),
			],
			[
				InlineKeyboardButton(text = '🔙', callback_data='admin'),
			]
		]
	)

	return markup

