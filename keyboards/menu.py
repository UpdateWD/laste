from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from data.config import *
from data.bd import *
import asyncio


async def main_menu(user_id):
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = '🛒 Catalog', callback_data='catalog'),
				InlineKeyboardButton(text = '👤 Profile', callback_data='profile'),
			],
			[
				InlineKeyboardButton(text = '🏝 Information', callback_data='information'),
			],
		]
	)
	if user_id in admins:
		markup.add(
				InlineKeyboardButton(text = '☕️ Admin Panel', callback_data='admin')
			)

	return markup


async def profile_menu():
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = '🪐 Top Up', callback_data='topup'),
				InlineKeyboardButton(text = '👥 Referrals', callback_data='referal'),
			],
			[
				InlineKeyboardButton(text = '🔙', callback_data='back'),
			],
		]
	)

	return markup

async def back_profile_menu():
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = '🔙', callback_data='profile'),
			],
		]
	)

	return markup

async def information_menu():
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = 'Channel', url='https://t.me/+K_k00xexQ5E4MjU0'),
				#InlineKeyboardButton(text = 'Chat', url='https://'),
			],
			[
				
				InlineKeyboardButton(text = 'Admin', url='https://t.me/LeftHeelNiga'),
			],
			[
				InlineKeyboardButton(text = '🔙', callback_data='back'),
			],
		]
	)

	return markup

async def payment_currency_menu():
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = 'BTC', callback_data='crypto_bot_currency|BTC'),
				InlineKeyboardButton(text = 'ETH', callback_data='crypto_bot_currency}|ETH'),
				InlineKeyboardButton(text = 'USDT', callback_data='crypto_bot_currency|USDT'),
			],
			[
				InlineKeyboardButton(text = '🔙', callback_data='profile'),
			]
		]
	)

	return markup

async def check_crypto(url, invoice_id, amot):
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text='💳 Pay', url=url),
				InlineKeyboardButton(text='🔎 Check payment', callback_data=f'check_crypto_bot|{invoice_id}|{amot}'),
			],
			[
				InlineKeyboardButton(text = '🔙', callback_data='back'),
			]
		]
	)

	return markup


async def catalog_menu():
	categories = await get_categories()
	markup = InlineKeyboardMarkup(row_width=2)
	if categories != None:
		for category in categories:
			markup.insert(
				InlineKeyboardButton(text = category[1], callback_data=f'category:{category[0]}'),
			)
		markup.add(
				InlineKeyboardButton(text = '🔙', callback_data='back'),
			)
	else:
		markup.add(
				InlineKeyboardButton(text = '🔙', callback_data='back'),
			)

	return markup

async def subcategories_menu(category_id):
	subcategories = await get_subcategories(category_id)
	markup = InlineKeyboardMarkup(row_width=2)
	if subcategories != None:
		for subcategory in subcategories:
			markup.insert(
				InlineKeyboardButton(text = subcategory[1], callback_data=f'subcategory:{subcategory[0]}'),
			)
		markup.add(
				InlineKeyboardButton(text = '🔙', callback_data='catalog'),
			)
	else:
		markup.add(
				InlineKeyboardButton(text = '🔙', callback_data='catalog'),
			)

	return markup

async def buy_subcategory(id, price, name):
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = 'Buy', callback_data=f'buy:{id}:{price}:{name}'),
			],
			[
				InlineKeyboardButton(text = '🔙', callback_data='back'),
			]
		]
	)

	return markup


async def back_menu():
	markup = InlineKeyboardMarkup(
		inline_keyboard = [
			[
				InlineKeyboardButton(text = '🔙', callback_data='back'),
			]
		]
	)

	return markup

def cancel_menu():
	markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	markup.add(
		'Cancel',
	)

	return markup