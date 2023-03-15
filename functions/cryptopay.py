from aiocryptopay import AioCryptoPay, Networks

from data.config import *


async def get_crypto_bot_sum(summa: float, currency: str):
	cryptopay = AioCryptoPay(cryptopay_token, network=Networks.MAIN_NET)
	courses = await cryptopay.get_exchange_rates()
	await cryptopay.close()
	for course in courses:
		if course.source == currency and course.target == 'USD':
			return summa / course.rate


async def check_crypto_bot_invoice(invoice_id: int):
	cryptopay = AioCryptoPay(cryptopay_token, network=Networks.MAIN_NET)
	invoice = await cryptopay.get_invoices(invoice_ids=invoice_id)
	await cryptopay.close()
	if invoice.status == 'paid':
		return True
	else:
		return False