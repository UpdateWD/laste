import pytz
import random
import datetime
import aiosqlite
from aiosqlite import connect

zone = pytz.timezone('Europe/Kiev')

path = "data/base/FTM_Market.sqlite"


async def create_tables():
	async with aiosqlite.connect(path) as db:
		await db.execute("CREATE TABLE IF NOT EXISTS users("
						"user_id INTEGER, balanse TEXT, purchases INTEGER, referal_id INTEGER)")
		
		await db.execute("CREATE TABLE IF NOT EXISTS bot_categories("
						"id INTEGER, name TEXT, type TEXT)")
		
		await db.execute("CREATE TABLE IF NOT EXISTS bot_subcategories("
						"id INTEGER, name TEXT, description TEXT, price INTEGER, type TEXT)")
		
		await db.execute("CREATE TABLE IF NOT EXISTS bot_product("
						"id INTEGER, product TEXT, type TEXT)")

		await db.execute("CREATE TABLE IF NOT EXISTS bot_stats("
						"profit INTEGER, tovar_selled INTEGER)")
		
		await db.execute("INSERT INTO bot_stats "
						 "(profit, tovar_selled) "
						 "VALUES (?, ?)",
						 [0, 0])
		await db.commit()

async def add_stats_profit(amount):
	async with aiosqlite.connect(path) as db:
		try:
			await db.execute(f"UPDATE bot_stats SET profit = '{amount}'")
			await db.commit()
		except Exception as e:
			print(e)

async def add_stats_tovar_selled(amount, user_id):
	async with aiosqlite.connect(path) as db:
		try:
			user = await db.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
			user = await user.fetchone()
			stats = await db.execute(f"SELECT * FROM bot_stats")
			stats = await stats.fetchone()
			await db.execute(f"UPDATE bot_stats SET tovar_selled = '{int(stats[1])+int(amount)}'")
			await db.execute(f"UPDATE users SET purchases = '{int(user[2])+int(amount)}' WHERE user_id = '{user_id}'")
			await db.commit()
		except Exception as e:
			print(e)

async def register_user(user_id, referal_id):
	async with aiosqlite.connect(path) as db:
		if referal_id != None:
			await db.execute("INSERT INTO users "
							 "(user_id, balanse, purchases, referal_id) "
							 "VALUES (?, ?, ?, ?)",
							 [user_id, 0, 0, referal_id])
		else:
			await db.execute("INSERT INTO users "
							 "(user_id, balanse, purchases, referal_id) "
							 "VALUES (?, ?, ?, ?)",
							 [user_id, 0, 0, 0])
		await db.commit()

async def get_user(user_id):
	async with aiosqlite.connect(path) as db:
		profile = await db.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
		return await profile.fetchone()

async def get_count_referal(user_id):
	async with aiosqlite.connect(path) as db:
		result = await db.execute(f"SELECT COUNT('user_id') as count FROM users WHERE referal_id = ?", (user_id,))
		return await result.fetchone()

async def edit_user_balanse(user_id, amount):
	async with aiosqlite.connect(path) as db:
		try:
			await db.execute(f"UPDATE users SET balanse = '{amount}' WHERE user_id = '{user_id}'")
			await db.commit()
		except Exception as e:
			print(e)

async def stats_bot():
	async with aiosqlite.connect(path) as db:
		stats = await db.execute(f"SELECT * FROM bot_stats")
		return await stats.fetchone()

async def add_seled(summ):
	async with aiosqlite.connect(path) as db:
		try:
			stats = await db.execute(f"SELECT * FROM bot_stats")
			stats = await stats.fetchone()
			
			selled = stats[1] + summ
			
			await db.execute(f"UPDATE bot_stats SET tovar_selled = '{selled}'")
			await db.commit()
		except Exception as e:
			print(e)

async def get_all_users():
	async with aiosqlite.connect(path) as db:
		users = await db.execute(f"SELECT * FROM users")
		return await users.fetchall()

async def get_categories():
	async with aiosqlite.connect(path) as db:
		category = await db.execute(f"SELECT * FROM bot_categories WHERE type = ?", ('category',))
		return await category.fetchall()

async def get_category_adm(id: int):
	async with aiosqlite.connect(path) as db:
		res = await db.execute(f"SELECT * FROM bot_categories WHERE id = ?", (id,))
		return await res.fetchone()

async def edit_category(id, name):
	async with aiosqlite.connect(path) as db:
		try:
			await db.execute(f"UPDATE bot_categories SET name = '{name}' WHERE id = '{id}'")
			await db.commit()
		except Exception as e:
			print(e)

async def delete_category(id):
	async with aiosqlite.connect(path) as db:
		try:
			await db.execute(f"DELETE FROM bot_categories WHERE id = '{id}'")
			await db.commit()
		except Exception as e:
			print(e)

async def add_category(name, id, type):
	async with aiosqlite.connect(path) as db:
		try:
			await db.execute("INSERT INTO bot_categories "
							 "(id, name, type) "
							 "VALUES (?, ?, ?)",
							 [id, name, type])
			await db.commit()
		except Exception as e:
			print(e)

async def get_subcategories(type):
	async with aiosqlite.connect(path) as db:
		subcategorie = await db.execute(f"SELECT * FROM bot_subcategories WHERE type = ?", (type,))
		return await subcategorie.fetchall()

async def get_subcategory(id: int):
	async with aiosqlite.connect(path) as db:
		category = await db.execute(f"SELECT * FROM bot_subcategories WHERE id = ?", (id,))
		return await category.fetchone()

async def get_subcategory_adm(id: int):
	async with aiosqlite.connect(path) as db:
		res = await db.execute(f"SELECT * FROM bot_subcategories WHERE id = ?", (id,))
		return await res.fetchone()

async def get_count_tovars(type):
	async with aiosqlite.connect(path) as db:
		tovars = await db.execute(f"SELECT * FROM bot_product WHERE type = ?", (type,))
		return await tovars.fetchall()

async def edit_subcategories(id, name):
	async with aiosqlite.connect(path) as db:
		try:
			await db.execute(f"UPDATE bot_subcategories SET name = '{name}' WHERE id = '{id}'")
			await db.commit()
		except Exception as e:
			print(e)

async def edit_subcategories_description(id, description):
	async with aiosqlite.connect(path) as db:
		try:
			await db.execute(f"UPDATE bot_subcategories SET description = '{description}' WHERE id = '{id}'")
			await db.commit()
		except Exception as e:
			print(e)

async def edit_subcategories_price(id, price):
	async with aiosqlite.connect(path) as db:
		try:
			await db.execute(f"UPDATE bot_subcategories SET price = '{price}' WHERE id = '{id}'")
			await db.commit()
		except Exception as e:
			print(e)

async def add_subcategory(name, description, price, id, type):
	async with aiosqlite.connect(path) as db:
		try:
			await db.execute("INSERT INTO bot_subcategories "
							 "(id, name, description, price, type) "
							 "VALUES (?, ?, ?, ?, ?)",
							 [id, name, description, price, type])
			await db.commit()
		except Exception as e:
			print(e)

async def delete_subcategory(id):
	async with aiosqlite.connect(path) as db:
		try:
			await db.execute(f"DELETE FROM bot_subcategories WHERE id = '{id}'")
			await db.commit()
		except Exception as e:
			print(e)

async def buy_tovars(type, amount):
	async with aiosqlite.connect(path) as db:
		tovars = await db.execute(f"SELECT * FROM bot_product WHERE type = ? LIMIT ?", (type, amount,))
		return await tovars.fetchall()

async def delete_tovars(id):
	async with aiosqlite.connect(path) as db:
		await db.execute(f"DELETE FROM bot_product WHERE id = ?", (id,))
		await db.commit()

async def add_product(id, product, type):
	async with aiosqlite.connect(path) as db:
		try:
			await db.execute("INSERT INTO bot_product "
							 "(id, product, type) "
							 "VALUES (?, ?, ?)",
							 [id, product, type])
			await db.commit()
		except Exception as e:
			print(e)