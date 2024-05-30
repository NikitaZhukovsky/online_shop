from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram import Router, F
from django.conf import settings
from django.core.management.base import BaseCommand
from catalog.models import Category, Seller, Product
from asgiref.sync import sync_to_async
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import aiohttp
import asyncio


class SomeState(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


class CartState(StatesGroup):
    waiting_for_product_id = State()
    waiting_for_product_count = State()
    waiting_for_login_product = State()
    waiting_for_password_product = State()


bot = Bot(token=settings.TELEGRAM_API_KEY)
storage = MemoryStorage()
router = Router()
dp = Dispatcher(storage=storage)

button_categories = KeyboardButton(text='Show categories')
button_sellers = KeyboardButton(text='Show sellers')
button_shor_cart = KeyboardButton(text='Show cart')
button_add_to_cart = KeyboardButton(text='Add to Cart')
keyboard = ReplyKeyboardMarkup(
    keyboard=[[button_categories], [button_sellers], [button_shor_cart], [button_add_to_cart]],
    resize_keyboard=True,
    one_time_keyboard=False
)


@sync_to_async
def get_categories():
    return list(Category.objects.all())

@sync_to_async
def get_product(product_id):
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None


async def add_to_cart(login, password, product_id, count):
    cart_url = settings.CART_URL
    auth_url = settings.AUTH_URL

    async with aiohttp.ClientSession() as session:
        auth_data = {"email": login, "password": password}
        async with session.post(auth_url, json=auth_data) as auth_response:
            if auth_response.status == 200:
                auth_content = await auth_response.json()
                token = auth_content.get('access')

                cart_data = {"product_id": product_id, "count": count}
                headers = {"Authorization": f"Bearer {token}"}
                async with session.post(cart_url, headers=headers, json=cart_data) as cart_response:
                    if cart_response.status == 200:
                        return True
                    else:
                        return False
            else:
                return False


async def fetch_user_cart(login, password):
    cart_url = settings.CART_URL
    auth_url = settings.AUTH_URL

    async with aiohttp.ClientSession() as session:
        auth_data = {"email": login, "password": password}
        async with session.post(auth_url, json=auth_data) as auth_response:
            if auth_response.status == 200:
                auth_content = await auth_response.json()
                token = auth_content.get('access')

                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(cart_url, headers=headers) as cart_response:
                    cart_content = await cart_response.json()
                    return cart_content
            else:
                return None


@router.message(F.text == '/start')
async def command_start(message: types.Message):
    await message.answer('Hello!', reply_markup=keyboard)


@router.message(F.text == 'Show categories')
async def show_categories(message: types.Message):
    categories = await get_categories()
    msg_to_answer = ''
    for category in categories:
        msg_to_answer += (f"Category: {category.name}\n"
                          f"Description: {category.description}\n"
                          f"------------------------------------\n")
    await bot.send_message(message.chat.id, msg_to_answer)


@router.message(F.text == 'Show sellers')
async def show_sellers(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(settings.SELLERS_URL, timeout=10) as response:
            msg_to_answer = ''
            sellers = await response.json()
            for seller in sellers:
                msg_to_answer += (f"Category: {seller['name']}\n"
                                  f"Description: {seller['description']}\n"
                                  f"Contact: {seller['contact']}\n"
                                  f"------------------------------------\n")

        await bot.send_message(message.chat.id, msg_to_answer)


@router.message(F.text == 'Show cart')
async def ask_for_login(message: types.Message, state: FSMContext):
    await message.reply("Enter your login: ")
    await state.set_state(SomeState.waiting_for_login)


@router.message(SomeState.waiting_for_login)
async def capture_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.reply('Enter your password: ')
    await state.set_state(SomeState.waiting_for_password)


@router.message(SomeState.waiting_for_password)
async def capture_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data['login']
    password = message.text

    user_cart_data = await fetch_user_cart(login, password)

    if user_cart_data:
        msg_to_answer = ''
        products = user_cart_data['products']
        for product in products:
            msg_to_answer += f"Product: {product['name']}, count: {product['count']}\n"
        msg_to_answer += f'Result price: {user_cart_data['result_price']}'
        await bot.send_message(message.chat.id, msg_to_answer)
    else:
        await bot.send_message(message.chat.id, 'Something Wrong')


@router.message(F.text == 'Add to Cart')
async def ask_for_login(message: types.Message, state: FSMContext):
    await message.reply("Enter your login: ")
    await state.set_state(CartState.waiting_for_login_product)


@router.message(CartState.waiting_for_login_product)
async def capture_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.reply('Enter your password: ')
    await state.set_state(CartState.waiting_for_password_product)


@router.message(CartState.waiting_for_password_product)
async def ask_for_product_id(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.reply("Enter the product ID: ")
    await state.set_state(CartState.waiting_for_product_id)


@router.message(CartState.waiting_for_product_id)
async def capture_product_id(message: types.Message, state: FSMContext):
    product_id = message.text
    await state.update_data(product_id=product_id)
    await message.reply('Enter the product count: ')
    await state.set_state(CartState.waiting_for_product_count)


@router.message(CartState.waiting_for_product_count)
async def capture_product_count(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data['login']
    password = user_data['password']
    product_id = user_data['product_id']
    product_count = message.text

    product = await get_product(product_id)
    if product:
        try:
            result = await add_to_cart(login, password, product_id, product_count)
            if result:
                await bot.send_message(message.chat.id, f"Product '{product.name}' added to the cart.")
            else:
                await bot.send_message(message.chat.id, "Failed to add product to the cart. Please check your login and password.")
        except Exception as e:
            await bot.send_message(message.chat.id, f"An error occurred: {str(e)}")
    else:
        await bot.send_message(message.chat.id, "Product not found.")

    await state.clear()


async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


class Command(BaseCommand):
    help = 'TG Bot for online shop'

    def handle(self, *args, **options):
        asyncio.run(main())




