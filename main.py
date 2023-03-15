import re
import aiogram
import hashlib
import datetime
from loguru import logger
from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.exceptions import CryptoPayAPIError
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle


from data.bd import *
from data.config import *
from state.state import *
from keyboards.menu import *
from keyboards.admin import *
from functions.cryptopay import *

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
vip = Dispatcher(bot=bot, storage=MemoryStorage())

@vip.message_handler(commands='start')
async def start_msg(message: types.Message):
	if message.chat.type == 'private':
		user_id = message.from_user.id
		user = await get_user(user_id)

		if user is None:
			start_command = message.text
			referal_id = str(start_command)[7:]
			if str(referal_id) != '':
				if str(referal_id) != str(user_id):
					await register_user(user_id, str(referal_id))
					try:
						amount = float(f'{random.uniform(0.100, 0.500):.3f}')
						user = await get_user(referal_id)
						ammot = float(user[1]) + amount
						await edit_user_balanse(int(referal_id), ammot)
						await bot.send_message(referal_id, f"<b>You received +{amount}$ per referral | {message.from_user.get_mention()} </b>")
					except Exception as e:
						print(e)
						pass
				else:
					await register_user(user_id, None)
					await bot.send_message(message.chat.id, f"<b>Вы не можете зарегистрироваться по своей ссылке</b>")
			else:
				await register_user(user_id, None)
			await bot.send_message(logs, f'<b>New user {message.from_user.get_mention()} / <code>{user_id}</code></b>')

		await message.answer_photo(photo=photo, caption=f'<b>Welcome {message.from_user.get_mention()}. Left Shop - Лучшее качество.</b>', reply_markup=await main_menu(user_id))

@vip.callback_query_handler(text='back', state='*')
async def back_msg(call: types.CallbackQuery):
	await call.message.edit_caption(caption=f'<b>Welcome {call.from_user.get_mention()}. Left Shop - Лучшее качество.</b>', reply_markup=await main_menu(call.from_user.id))

@vip.callback_query_handler(text='profile', state='*')
async def profile_msg(call: types.CallbackQuery):
	user_id = call.from_user.id
	user = await get_user(user_id)
	await call.message.edit_caption(caption=f'<b>👤 Profile {call.from_user.get_mention()}\n\n💸 Balanse: {float(user[1]):.3f}$\n📦 Number of purchases: {user[2]}</b>', reply_markup=await profile_menu())

@vip.callback_query_handler(text='topup', state='*')
async def topup_msg(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(cl=call)
	await call.message.edit_caption(caption=f'<b>Введите сумму пополнения в $</b>', reply_markup=await back_profile_menu())
	await Topup.sum.set()

@vip.message_handler(state=Topup.sum)
async def Topup_sum_state(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	cl = data['cl']
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message_id)
	try:
		if int(call.text) <= 0:
			await cl.message.edit_caption(caption=f'<b>❗Введите натуральное число</b>', reply_markup=await back_profile_menu())
			await state.finish()
		else:
			topup_sum = int(call.text)
			await state.update_data(topup_sum=topup_sum)
			await cl.message.edit_caption(caption=f'<b>❕Выберите валюту платежа</b>', reply_markup=await payment_currency_menu())
			await Topup.currency.set()
	except:
		await cl.message.edit_caption(caption=f'<b>❗ Вводите только цифры</b>', reply_markup=await back_profile_menu())
		await state.finish()

@vip.callback_query_handler(text_startswith='crypto_bot_currency', state=Topup.currency)
async def crypto_bot_currency_msg(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	topup_sum = data['topup_sum']
	cryptopay = AioCryptoPay(cryptopay_token, network=Networks.MAIN_NET)
	invoice = await cryptopay.create_invoice(asset=call.data.split('|')[1], amount=await get_crypto_bot_sum(int(topup_sum), call.data.split('|')[1]))
	await cryptopay.close()
	await call.message.edit_caption(caption=f'<b>🪐 Top Up Market\n\nAmount: {topup_sum}\nСryptocurrency: {call.data.split("|")[1]}\n\n❕Оплатите свой счет, используя приведенную ниже ссылку</b>', reply_markup=await check_crypto(invoice.pay_url, invoice.invoice_id, topup_sum))
	await state.finish()

@vip.callback_query_handler(text_startswith="check_crypto_bot")
async def check_crypto_bot_funds(call: types.CallbackQuery):
	try:
		if await check_crypto_bot_invoice(int(call.data.split('|')[1])):
			user_id = call.from_user.id
			user = await get_user(user_id)
			ammot = float(user[1]) + int(call.data.split('|')[2])
			await edit_user_balanse(int(user_id), float(ammot))
			await bot.answer_callback_query(call.id, f'✅ Счет оплачен успешно + {call.data.split("|")[2]}$', True)
			await call.message.edit_caption(caption=f'<b>Welcome {call.from_user.get_mention()}. Left Shop - Лучшее качество.</b>', reply_markup=await main_menu(call.from_user.id))
			await bot.send_message(logs, text=f'<b>💰 New deposit\n\n◽️User: {call.from_user.get_mention()}\n◽️ID: {user_id}\n◽️Amount: {call.data.split("|")[2]} $\n</b>')
			stats = await stats_bot()
			ammot = float(stats[0]) + int(call.data.split("|")[2])
			await add_stats_profit(ammot)
		else:
			await bot.answer_callback_query(call.id, '❗ Оплата не была произведена', True)
	except Exception as e:
		print(e)

@vip.callback_query_handler(text='information')
async def information_msg(call: types.CallbackQuery):
	await call.message.edit_caption(caption='<b>🏝 Information Left Shop \n\n❔ Все вопросы по замене только с доказательствами. Наш маркет отвечает за качество товара.\n\n🎫 Для пополнения баланса не через Crypto Bot, писать в лс. </b>', reply_markup=await information_menu())

@vip.callback_query_handler(text='referal')
async def referal_msg(call: types.CallbackQuery):
	count_referal = await get_count_referal(call.from_user.id)
	bote = await bot.get_me()
	await call.message.edit_caption(caption=f'<b>👥 Приглашайте активных пользователей к боту и получайте бонусы.\n\n💰 Вы можете получить от 0.1$ до 0.5$.\n\n🤵🏻‍♂️ Your referrals - {count_referal[0]}\n⚡️ Your invitation link - <code>https://t.me/{bote.username}?start={call.from_user.id}</code></b>', reply_markup=await back_menu())



@vip.callback_query_handler(text='catalog', state='*')
async def catalog_msg(call: types.CallbackQuery):
	await call.message.edit_caption(caption=f'<b>📁 Catalog</b>', reply_markup=await catalog_menu())

@vip.callback_query_handler(text_startswith='category', state='*')
async def category_msg(call: types.CallbackQuery):
	category_id = call.data.split(':')[1]
	await call.message.edit_caption(caption=f'<b>📁 Catalog</b>', reply_markup=await subcategories_menu(category_id))

@vip.callback_query_handler(text_startswith='subcategory', state='*')
async def subcategory_msg(call: types.CallbackQuery):
	subcategory_id = call.data.split(':')[1]
	subcategory = await get_subcategory(int(subcategory_id))
	tovars = await get_count_tovars(subcategory[0])
	await call.message.edit_caption(caption=f'<b>{subcategory[1]}\n\n📂 Amount: {len(tovars)}\n💸 Price: {subcategory[3]}$\n\n❔ {subcategory[2]}</b>', reply_markup=await buy_subcategory(subcategory[0], subcategory[3], subcategory[1]))

@vip.callback_query_handler(text_startswith='buy', state='*')
async def subcategory_msg(call: types.CallbackQuery, state: FSMContext):
	id = call.data.split(':')[1]
	price = call.data.split(':')[2]
	name = call.data.split(':')[3]
	
	await state.update_data(id=id)
	await state.update_data(price=price)
	await state.update_data(name=name)
	
	tovars = await get_count_tovars(id)
	if len(tovars) == 0:
		await bot.answer_callback_query(call.id, '❗ Товар отсутствует на складе', True)
	else:
		await call.message.edit_caption(caption=f'<b>Введите количество</b>', reply_markup=await back_menu())
		await Get_ammot.ammot.set()
 

@vip.message_handler(state=Get_ammot.ammot)
async def edit_subcat_name_state(message: types.Message, state: FSMContext):
	try:
		ammot = message.text
		data = await state.get_data()
		tovars = await get_count_tovars(data['id'])
		price = float(data['price']) * int(ammot)
		user = await get_user(message.from_user.id)
		user_balance = float(user[1])
		if int(ammot) > int(len(tovars)):
			await bot.send_message(message.chat.id, '<b>❗Товар отсутствует на складе</b>')
			await state.finish()
		elif int(ammot) <= 0:
			await bot.send_message(message.chat.id, '<b>❗Введите натуральное число</b>')
			await state.finish() 
		else:
			if user_balance < price:
				await bot.send_message(message.chat.id, "<b>❗У вас недостаточно средств, пополните баланс в своем профиле</b>")
				await state.finish()
			else:
				tovars_buy = await buy_tovars(data['id'], ammot)
				text = '<b>🎉 Благодарим вас за покупку</b>\n\n'
				if len(tovars_buy) <= 50:
					for tovar in tovars_buy:
						text += f'<b>{tovar[1]}\n</b>'
						await delete_tovars(tovar[0])
					await bot.send_message(message.chat.id, text=text)
				else:
					for tovar in tovars_buy:
						text += f'{tovar[1]}\n'
						await delete_tovars(tovar[0])
					with open('rick_market.txt', 'w', encoding="utf-8") as f:
						f.write(text)
						f.close()
					await bot.send_document(message.chat.id, open('ftm_market.txt', 'rb'))

				
				balance = float(user_balance) - float(price)
				
				await edit_user_balanse(message.from_user.id, balance)
				await add_stats_tovar_selled(int(ammot), message.from_user.id)
				
				await bot.send_message(logs, f'<b>🛍 Product purchased\n\n◽️ User: {message.from_user.get_mention()}\n◽️ID: {message.from_user.id}\n◽️Product name: {data["name"]}\n◽️Purchase amount: {price}$\n◽️Quantity of item: {ammot} pcs</b>')
				await state.finish()
	except Exception as e:
		print(e)
		await bot.send_message(message.chat.id, text='<b>❗ Вводите только цифры</b>')
		await state.finish()




@vip.callback_query_handler(text='admin', state='*')
async def admin_msg(call: types.CallbackQuery):
	await call.message.edit_caption(caption=f'<b>☕️ Admin Panel</b>', reply_markup=await amdin_menu())

@vip.callback_query_handler(text='control', state='*')
async def control_msg(call: types.CallbackQuery):
	await call.message.edit_caption(caption=f'<b>📌 What will we change</b>', reply_markup=await amdin_list_menu())

@vip.callback_query_handler(text='edit_category', state='*')
async def category_edit_msg(call: types.CallbackQuery):
	await call.message.edit_caption(caption=f'<b>📂 Category edit</b>', reply_markup=await amdin_catalog_menu())

@vip.callback_query_handler(text_startswith='adm_category', state='*')
async def adm_category_msg(call: types.CallbackQuery):
	category_id = call.data.split(':')[1]
	category = await get_category_adm(int(category_id))
	await call.message.edit_caption(caption=f'<b>📂 Category {category[1]}\n\nWhat do we do?</b>', reply_markup=await amdin_catalog_edit_menu(category[0], category[1]))

@vip.callback_query_handler(text_startswith='edit_name', state='*')
async def adm_edit_name_msg(call: types.CallbackQuery, state: FSMContext):
	category = call.data.split(':')
	await state.update_data(id=category[1])
	await call.message.edit_caption(caption=f'<b>👁 Enter new name</b>', reply_markup=await back_menu_adm())
	await Edit.name.set()

@vip.message_handler(state=Edit.name)
async def edit_name_state(message: types.Message, state: FSMContext):
	data = await state.get_data()
	name = message.text

	await edit_category(data['id'], name)
	await message.answer_photo(photo=photo, caption=f'<b>✔️ Edit successful</b>', reply_markup=await amdin_menu())
	await state.finish()

@vip.callback_query_handler(text_startswith='delete', state='*')
async def delete_msg(call: types.CallbackQuery, state: FSMContext):
	category = call.data.split(':')
	await delete_category(int(category[1]))
	await call.message.edit_caption(caption=f'<b>🗑 Delete successful</b>', reply_markup=await back_menu_adm())

@vip.callback_query_handler(text='add_category', state='*')
async def add_category_msg(call: types.CallbackQuery):
	await call.message.edit_caption(caption=f'<b>👁 Enter name category</b>', reply_markup=await back_menu_adm())
	await Add.category.set()

@vip.message_handler(state=Add.category)
async def add_category_state(message: types.Message, state: FSMContext):
	name = message.text
	id = random.randint(100000, 999999)

	await add_category(name, id, 'category')
	await message.answer_photo(photo=photo, caption=f'<b>✔️ Add successful</b>', reply_markup=await amdin_menu())
	await state.finish()


@vip.callback_query_handler(text='edit_subcategories', state='*')
async def category_edit_msg(call: types.CallbackQuery):
	await call.message.edit_caption(caption=f'<b>📄 Subcategories edit</b>', reply_markup=await amdin_catalog_sub_menu())

@vip.callback_query_handler(text_startswith='select_category')
async def adm_category_msg(call: types.CallbackQuery):
	category_id = call.data.split(':')[1]
	await call.message.edit_caption(caption=f'<b>📄 Select a category</b>', reply_markup=await amdin_subcategories_menu(category_id))

@vip.callback_query_handler(text_startswith='adm_subcategory')
async def adm_category_msg(call: types.CallbackQuery):
	subcategory_id = call.data.split(':')[1]
	subcategory = await get_subcategory_adm(int(subcategory_id))
	await call.message.edit_caption(caption=f'<b>📄 Subcategory {subcategory[1]}\n\n💬 Description: {subcategory[2]}\n💸 Price: {subcategory[3]}\n\n❔ What do we do?</b>', reply_markup=await amdin_subcategories_edit_menu(subcategory[0]))

@vip.callback_query_handler(text_startswith='edit_subcategories_name', state='*')
async def adm_edit_subcategories_name_msg(call: types.CallbackQuery, state: FSMContext):
	subcategories = call.data.split(':')
	await state.update_data(id=subcategories[1])
	await call.message.edit_caption(caption=f'<b>Enter new name</b>', reply_markup=await back_menu_adm())
	await Edit_subcat.name.set()

@vip.message_handler(state=Edit_subcat.name)
async def edit_subcat_name_state(message: types.Message, state: FSMContext):
	data = await state.get_data()
	name = message.text

	await edit_subcategories(data['id'], name)
	await message.answer_photo(photo=photo, caption=f'<b>✔️ Edit successful</b>', reply_markup=await amdin_menu())
	await state.finish()

@vip.callback_query_handler(text_startswith='edit_subcategories_description', state='*')
async def adm_edit_subcategories_description_msg(call: types.CallbackQuery, state: FSMContext):
	subcategories = call.data.split(':')
	await state.update_data(id=subcategories[1])
	await call.message.edit_caption(caption=f'<b>💬 Enter new description</b>', reply_markup=await back_menu_adm())
	await Edit_subcat1.description.set()

@vip.message_handler(state=Edit_subcat1.description)
async def edit_subcat_description_state(message: types.Message, state: FSMContext):
	data = await state.get_data()
	description = message.text

	await edit_subcategories_description(data['id'], description)
	await message.answer_photo(photo=photo, caption=f'<b>✔️ Edit successful</b>', reply_markup=await amdin_menu())
	await state.finish()

@vip.callback_query_handler(text_startswith='edit_subcategories_price', state='*')
async def adm_edit_subcategories_price_msg(call: types.CallbackQuery, state: FSMContext):
	subcategories = call.data.split(':')
	await state.update_data(id=subcategories[1])
	await call.message.edit_caption(caption=f'<b>💸 Enter new price</b>', reply_markup=await back_menu_adm())
	await Edit_subcat2.price.set()

@vip.message_handler(state=Edit_subcat2.price)
async def edit_subcategories_price_state(message: types.Message, state: FSMContext):
	data = await state.get_data()
	price = float(message.text)

	await edit_subcategories_price(data['id'], price)
	await message.answer_photo(photo=photo, caption=f'<b>✔️ Edit successful</b>', reply_markup=await amdin_menu())
	await state.finish()

@vip.callback_query_handler(text_startswith='subcategories_delete', state='*')
async def delete_msg(call: types.CallbackQuery, state: FSMContext):
	subcategory = call.data.split(':')
	await delete_subcategory(int(subcategory[1]))
	await call.message.edit_caption(caption=f'<b>🗑 Delete successful</b>', reply_markup=await back_menu_adm())

@vip.callback_query_handler(text_startswith='add_subcategory', state='*')
async def add_subcategory_msg(call: types.CallbackQuery, state: FSMContext):
	type = call.data.split(':')[1]
	await state.update_data(type=type)

	await call.message.edit_caption(caption=f'<b>👁 Enter name</b>')
	await Add_subcat.name.set()

@vip.message_handler(state=Add_subcat.name)
async def add_subcategory_name_state(message: types.Message, state: FSMContext):
	name = message.text
	await state.update_data(name=name)

	await bot.send_message(message.from_user.id, f'<b>💬 Enter description</b>')
	await Add_subcat.description.set()

@vip.message_handler(state=Add_subcat.description)
async def add_subcategory_description_state(message: types.Message, state: FSMContext):
	description = message.text
	await state.update_data(description=description)

	await bot.send_message(message.from_user.id, f'<b>💸 Enter price in $</b>')
	await Add_subcat.price.set()

@vip.message_handler(state=Add_subcat.price)
async def add_subcategory_price_state(message: types.Message, state: FSMContext):
	price = message.text
	id = random.randint(100000, 999999)
	data = await state.get_data()

	await add_subcategory(data['name'], data['description'], float(price), id, data['type'])
	await message.answer_photo(photo=photo, caption=f'<b>✔️ Add successful</b>', reply_markup=await amdin_menu())
	await state.finish()

@vip.callback_query_handler(text_startswith='subcategories_add_product', state='*')
async def adm_subcategories_add_product_msg(call: types.CallbackQuery, state: FSMContext):
	subcategories_id = call.data.split(':')[1]
	await state.update_data(id=subcategories_id)
	await call.message.edit_caption(caption=f'<b>➕ Отправьте продукт, каждый на новой 2 линии</b>', reply_markup=await back_menu_adm())
	await Add_sub.product.set()

@vip.message_handler(state=Add_sub.product)
async def subcategories_add_product_state(message: types.Message, state: FSMContext):
	data = await state.get_data()
	products = message.text.split('\n\n')
	for product in products:
		id = random.randint(1000000, 9999999)
		await add_product(id, product, data['id'])
	
	await message.answer_photo(photo=photo, caption=f'<b>✔️ Adding successful</b>', reply_markup=await amdin_menu())
	await state.finish()

@vip.callback_query_handler(text='statistics')
async def statistics_msg(call: types.CallbackQuery):
	stats = await stats_bot()
	users = len(await get_all_users())
	cryptopay = AioCryptoPay(cryptopay_token)
	b = await cryptopay.get_balance()
	cryptobot = ("{0:.2f}".format(int(b[0].available)))
	await cryptopay.close()
	await call.message.edit_caption(caption=f'<b>📈 Statistics bot\n\n🤵 Users – {users}\n💸 Profit – {stats[0]}$\n🛒 Purchased goods – {stats[1]}\n\n💎 Cryptobot Balanse - {cryptobot}$</b>', reply_markup=await back_menu_adm())

@vip.callback_query_handler(text='finduser')
async def finduser_msg(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(cl=call)
	await call.message.edit_caption(caption='<b>Enter user id to search</b>', reply_markup=await back_menu_adm())
	await Find.user.set()

@vip.message_handler(state=Find.user)
async def Topup_sum_state(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	cl = data['cl']
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message_id)
	try:
		user = await get_user(int(call.text))
		await cl.message.edit_caption(caption=f'<b>🦋 Profile {call.text}\n\n💸 Balanse: {user[1]}$\n📦 Number of purchases: {user[2]}</b>', reply_markup=await find_user_adm(call.text))
		await state.finish()
	except Exception as e:
		print(e)
		await cl.message.edit_caption(caption=f'<b>❗ User not found</b>', reply_markup=await back_menu_adm())
		await state.finish()

@vip.callback_query_handler(text_startswith='user_edit_balanse', state='*')
async def user_edit_balanse_msg(call: types.CallbackQuery, state: FSMContext):
	user_id = call.data.split('|')[1]
	await state.update_data(cl=call)
	await state.update_data(user_id=user_id)
	await call.message.edit_caption(caption='<b>Enter a new balance</b>', reply_markup=await back_menu_adm())
	await Balance.edit.set()

@vip.message_handler(state=Balance.edit)
async def edit_balance_state(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	cl = data['cl']
	user_id = data['user_id']
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message_id)
	try:
		await edit_user_balanse(user_id, float(call.text))
		await cl.message.edit_caption(caption=f'<b>✔️ Balance changed successfully</b>', reply_markup=await back_menu_adm())
		await state.finish()
	except:
		await cl.message.edit_caption(caption=f'<b>❗ Вы ввели не число</b>', reply_markup=await back_menu_adm())
		await state.finish()

async def startup(dp):
	await create_tables()

if __name__ == '__main__':
	executor.start_polling(vip, on_startup=startup, skip_updates=True)