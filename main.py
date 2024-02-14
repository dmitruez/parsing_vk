import logging
import os
import random
import time
import traceback
from datetime import date, datetime

import vk_api
from rich.console import Console
from rich.table import Table



cities = {
	1: "Россия",
	2: "Украина",
	3: "Беларусь",
	4: "Казахстан",
	5: "Азейбарджан",
	6: "Армения",
	7: "Грузия",
	11: "Кыргызстан",
	15: "Молдова",
	18: "Узбекистан"
	}


def get_wall_posts(vk, link, group_id):
	try:
		vk.groups.join(group_id=group_id)
	except Exception as e:
		print(f"Что то пошло не так... пробуем снова: {e}")
	if "vk.com" in link:
		domain = link.replace("https://vk.com/", "")
	else:
		domain = link.replace("https://vk.ru/", "")
	wall_all = vk.wall.get(domain=domain, count=100)
	count = len(list(filter(lambda m: m.get("comments") is not None, wall_all["items"])))
	post_ids = []
	if count == 0:
		return None
	wall = vk.wall.get(domain=domain, count=10)
	print(f"Комментим в группу: https://vk.com/public{group_id}")
	for post in wall["items"]:
		if post.get("comments"):
			post_ids.append(post["id"])
	return post_ids
	






def get_with_photo_ids(vk, group_id):
	offset = 0
	banned = 0
	applied = 0
	ids = []
	all_members = vk.groups.getMembers(group_id=group_id)
	count = all_members["count"]
	os.system('cls')
	
	while offset < count:
		members = vk.groups.getMembers(group_id=group_id, offset=offset, fields="photo_100")
		for member in members.get("items"):
			if "deactivated" and member.get("photo_100").endswith(".png"):
				banned += 1
			else:
				if not member.get("photo_100").endswith(".png"):
					applied += 1
					user_id = member["id"]
					print(user_id)
					ids.append(user_id)
		offset += 1000
	
	return ids, banned, applied




def get_group_id_by_key(vk):
	to_print = '| '
	for key, value in cities.items():
		to_print += f'{key} - {value} | '
	print(to_print)
	while True:
		what1 = int(input("\nПарсинг групп по ключевому слову\n\n1 - Глобальный поиск\n2 - Выбрать страну\n\nВвод:"))
		if what1 == 2:
			
			country_id = int(input("\nНапишите номер желаемой страны:"))
			what = int(input("\n\n1 - Делать парсинг по всей стране\n2 - Выбрать город\n\nВвод:"))
			if what == 2:
				cit = vk.database.getCities(country_id=country_id)["items"]
				to_print = '| '
				for city in cit:
					to_print += f'{city["id"]} - {city["title"]} | '
				print(to_print)
				city_id = int(input("Напишите номер желаемого города:"))
				q = input("Введите ключевое слово:")
				groups = vk.groups.search(q=q, city_id=city_id, count=100, sort=6)
			else:
				q = input("Введите ключевое слово:")
				groups = vk.groups.search(q=q, country_id=country_id, count=100, sort=6)
		else:
			q = input("Введите ключевое слово:")
			groups = vk.groups.search(q=q, count=100, sort=6)
		if len(groups) != 0:
			all_groups = groups.get("items")
			with open("link_group.txt", "a") as f:
				for num, group in enumerate(all_groups):
					try:
						href = f"https://vk.com/{group['screen_name']}"
						f.write(f"{href}\n")
						name = f"{num + 1}. {group['name']}"
						print(f'{name:<55} | {href}')
					except Exception as e:
						print(f"Группа со скрытыми участниками, пропускаю... {e}")
				group_num = int(input("\nНапишите номер нужной вам группы:")) - 1
				group_id = all_groups[group_num]["id"]
				os.system('cls')
				count_group = vk.groups.getMembers(group_id=group_id)["count"]
				print(
					f"Выбрана группа: {all_groups[group_num]['name']} | кол-во чел.: {count_group} | https://vk.com/"
					f"{all_groups[group_num].get('screen_name')}"
					)
				
				curnt_group = vk.groups.getById(group_id=group_id)
				
				group_all_info = curnt_group[0]  # выводит всю информацию о группе
				group_id = group_all_info['id']  # выводит айди
				break
		else:
			print("По этому запросу не нашлось ни одной группы( ")
	return group_id


def get_group_id_by_link(vk, link):
	try:
		if "vk.com" in link:
			link_replace = link.replace('https://vk.com/', '')
		else:
			link_replace = link.replace('https://vk.ru/', '')
		
		# Получение id по короткому имени сообщества
		group_info = vk.utils.resolveScreenName(screen_name=link_replace)
		group_id = group_info['object_id']
		
		# Получение информации о сообществе
		group = vk.groups.getById(group_id=group_id)
		
		group_all_info = group[0]  # выводит всю информацию о группе
		group_id = group_all_info['id']  # выводит айди
		return group_id
	
	except Exception as ex:
		print('произошла ошибка при парсинге группы', ex)


def get_age_ids(vk, group_id):
	offset = 0
	banned = 0
	applied = 0
	ids = []
	all_members = vk.groups.getMembers(group_id=group_id)
	count = all_members["count"]
	os.system('cls')
	age = int(input("Введите возраст:"))
	what = int(input(f"Выберите пункт парсинга по дате\n\n1 - До {age} лет\n2 - Свыше {age} лет\n\nВвод:"))
	now = datetime.now()
	curl_year = now.year
	year = curl_year - age
	month = now.month
	day = now.day
	date_border = date(year, month, day)
	while offset < count:
		members = vk.groups.getMembers(group_id=group_id, offset=offset, fields="bdate")
		for member in members["items"]:
			if "deactivated" in member:
				banned += 1
			else:
				if "bdate" in member:
					dates = member["bdate"].split('.')
					if len(dates) != 3:
						pass
					else:
						day1 = int(dates[0])
						month1 = int(dates[1])
						year1 = int(dates[2])
						bdate = date(year1, month1, day1)
						if what == 1:
							if bdate > date_border:
								applied += 1
								user_id = member["id"]
								print(user_id)
								ids.append(user_id)
						elif what == 2:
							if bdate < date_border:
								applied += 1
								user_id = member["id"]
								print(user_id)
								ids.append(user_id)
		offset += 1000
	
	return ids, banned, applied


def get_sex_ids(vk, group_id):
	offset = 0
	banned = 0
	applied = 0
	ids = []
	all_members = vk.groups.getMembers(group_id=group_id)
	count = all_members["count"]
	sex = int(input("Введите нужный пункт\n\n1 - Женщины\n2 - Мужчины\n\nВвод:"))
	while offset < count:
		members = vk.groups.getMembers(group_id=group_id, offset=offset, fields="sex")
		for member in members["items"]:
			if "deactivated" in member and member["sex"] == sex:
				banned += 1
			else:
				if member["sex"] == sex:
					applied += 1
					user_id = member["id"]
					print(user_id)
					ids.append(user_id)
		offset += 1000
	
	return ids, banned, applied


def get_online_ids(vk, group_id):
	offset = 0
	banned = 0
	applied = 0
	ids = []
	all_members = vk.groups.getMembers(group_id=group_id)
	count = all_members["count"]
	while offset < count:
		members = vk.groups.getMembers(group_id=group_id, offset=offset, fields="online")
		for member in members["items"]:
			if "deactivated" in member and member["online"] == 1:
				banned += 1
			else:
				if member["online"] == 1:
					applied += 1
					user_id = member["id"]
					print(user_id)
					ids.append(user_id)
		offset += 1000
	
	return ids, banned, applied


def get_all_ids(vk, group_id):
	offset = 0
	banned = 0
	applied = 0
	ids = []
	all_members = vk.groups.getMembers(group_id=group_id)
	count = all_members["count"]
	while offset < count:
		members = vk.groups.getMembers(group_id=group_id, offset=offset, fields="lists")
		for member in members["items"]:
			if "deactivated" in member:
				banned += 1
			else:
				applied += 1
				user_id = member["id"]
				print(user_id)
				ids.append(user_id)
		offset += 1000
	
	return ids, banned, applied


def get_city_ids(vk, group_id):
	offset = 0
	banned = 0
	applied = 0
	ids = []
	citiess = []
	all_members_city = vk.groups.getMembers(group_id=group_id, offset=offset, fields="city")
	count = all_members_city["count"]
	for member in all_members_city["items"]:
		if "deactivated" in member:
			pass
		else:
			if "city" in member:
				city = member["city"]["title"]
				if city not in citiess:
					citiess.append(city)
	
	spisok_cities = ', '.join(citiess)
	print("Доступные города: " + spisok_cities + '\n')
	gorod = input("Напишите название города из предложенных:")
	while offset < count:
		all_members = vk.groups.getMembers(group_id=group_id, offset=offset, fields="city")
		for member in all_members["items"]:
			if "city" in member:
				if "deactivated" in member and member["city"]["title"] == gorod:
					banned += 1
					pass
				else:
					if member["city"]["title"] == gorod:
						applied += 1
						user_id = member["id"]
						print(user_id)
						ids.append(user_id)
		offset += 1000
	
	return ids, banned, applied


def get_users_with_parametrs(vk, group_id, action):
	if action == 2:
		ids, banned, applied = get_online_ids(vk, group_id)
	elif action == 3:
		ids, banned, applied = get_sex_ids(vk, group_id)
	elif action == 4:
		ids, banned, applied = get_city_ids(vk, group_id)
	elif action == 5:
		ids, banned, applied = get_age_ids(vk, group_id)
	elif action == 6:
		ids, banned, applied = get_with_photo_ids(vk, group_id)
	else:
		ids, banned, applied = get_all_ids(vk, group_id)
	
	return ids, banned, applied


def func_posting(vk, list_id_group):
	os.system('cls')
	text_send_message = input(
		"Введите текст для рассылки\n\nМожно рандомизировать текст: текст 1 | текст 2 | текст 3\nСофт будет брать один текст рандомно\n\nВведите текст:"
		)
	time_1 = int(input('Введите 1 число ОТ скольки должно браться время в сек:'))
	time_2 = int(input('Введите 2 число ДО скольки должно браться время в сек:'))
	
	for l_id_group in list_id_group:
		try:
			time_sleep = random.randint(time_1, time_2)  # выбираем время задержки
			word = random.choice(text_send_message.split(' | '))
			print(list_id_group)
			vk.wall.post(owner_id='-' + str(l_id_group), message=word)
			print(f'Запись успешно оставлена. Айди группы: {l_id_group}')
			time.sleep(time_sleep)
		except Exception as ex:
			print('Произошла ошибка при добавлении записи на стенку. Пропускаю группу...', ex)


def func_message_send(vk, id_user_all):  # по лс юзерам
	os.system('cls')
	photo_used = input('Использовать фото?\n\n1 - да\n2 - нет\n3 - отмена рассылки \n\nВведите цифру:')
	photo_used = int(photo_used)
	if photo_used == 1:  # использовать фото
		photo_url = input('вставьте ссылку на фото:')
		message_text = input(
			'Введите текст для отправки сообщения:\n\nтекст 1 | текст 2 | текст 3\nБудет выбран один случайный текст\n\nВведите текст, для рандомных сообщений вставьте символ | :'
			)
		
		i_1 = input('Введите время от скольки рандомизировать время в сек:')
		i_2 = input('Введите время до скольки рандомизировать время в сек:')
		
		i_1 = int(i_1)
		i_2 = int(i_2)
		
		for user_id in id_user_all:
			try:
				time_random = random.randint(i_1, i_2)
				print(f'Время задержки составляет: {time_random}')
				time.sleep(time_random)
				
				word = random.choice(message_text.split(' | '))
				vk.messages.send(peer_id=user_id, random_id=0, message=word, attachment=photo_url)
				print(f'user_id: {user_id} message: {word}\nУспешно!')
			except Exception as ex:
				print('Ошибка, пропускаю группу...', ex)
		menu(vk)
	
	if photo_used == 2:
		message_text = input(
			'Введите текст для отправки сообщения:\n\nтекст 1 | текст 2 | текст 3\nБудет выбран один случайный текст\n\nВведите текст, для рандомных сообщений вставьте символ |:'
			)
		
		i_1 = int(input('Введите время от скольки рандомизировать время в сек:'))
		i_2 = int(input('Введите время до скольки рандомизировать время в сек:'))
		
		
		for user_id in id_user_all:
			try:
				time_random = random.randint(i_1, i_2)
				print(f'Время задержки составляет: {time_random}')
				time.sleep(time_random)
				
				word = random.choice(message_text.split(' | '))
				vk.messages.send(peer_id=user_id, random_id=0, message=word)
				print(f'user_id: {user_id} message: {word}\nУспешно!')
			except Exception as ex:
				print('Ошибка, пропускаю группу...', ex)
		menu(vk)
	
	if photo_used == 3:
		menu(vk)


def message_group(vk, list_id_group):  #
	
	message_text = input(
		'Введите текст для отправки сообщения:\n\nтекст 1 | текст 2 | текст 3\n\nБудет выбран один случайный текст:'
		)
	
	i_1 = int(input('Введите время от скольки рандомизировать время в сек:'))
	i_2 = int(input('Введите время до скольки рандомизировать время в сек:'))
	
	for group_message_send in list_id_group:
		try:
			time_random = random.randint(i_1, i_2)
			print(f'Время задержки составляет: {time_random}')
			time.sleep(time_random)
			
			word = random.choice(message_text.split(' | '))
			vk.messages.send(peer_id=-group_message_send, random_id=0, message=word)
			print(f'группа: https://vk.com/public{group_message_send} сообщение: {word}\nУспешно!')
		except Exception as ex:
			print('Ошибка, пропускаю группу...', ex)
	menu(vk)



def message_group_comments(vk, list_links_ids_group):  # отправка коментариев под посты
	print("\n\tВ эти группы будут отправлены коментарии под посты\n")
	
	what = int(input("\n1 - Ввести текст\n2 - Выйти из рассылки\n\nВвод:"))
	if what == 1:
		message_text = input(
			'Введите текст для отправки сообщения:\nтекст 1 | текст 2 | текст 3\nБудет выбран один случайный текст:'
			)
		
		for link, group_id in list_links_ids_group:
			post_ids = get_wall_posts(vk, link, group_id)
			if post_ids:
				for post_id in post_ids:
					try:
						word = random.choice(message_text.split(' | '))
						vk.wall.createComment(owner_id=-group_id, post_id=post_id, message=word)
						print(f'пост : https://vk.com/public{group_id}?w=wall-{group_id}_{post_id} сообщение: '
						      f'{word}\nУспешно!\n')
						if not post_id == post_ids[-1]:
							time.sleep(2)
					except Exception as ex:
						print('Ошибка, пропускаю группу...', ex)
				print("Ожидание новой группы | Время ожидания 25 секунд")
				vk.groups.leave(group_id=group_id)
				time.sleep(25)
			
	else:
		pass
	menu(vk)

# прекольны пост мне нрав | ого чисто яя | да бывааает))
def func_parsing(vk, group_id):
	
	while True:
		try:
			action = int(
				input(
					'\nВведите номер парсинга\n\n'
					'1 - Всех пользователей\n'
					'2 - Активных онлайн\n'
					'3 - По полу\n'
					'4 - По городу\n'
					'5 - По возрасту\n'
					'6 - Только с фото\n\nВвод:'
					)
				)
			break
		except Exception as e:
			print(f'произошла ошибка {e}')
	
	# Выводим идентификаторы активных участников
	ids, banned, applied = get_users_with_parametrs(vk, group_id, action)
	
	with open('user_group_result.txt', 'w+') as f:
		for user_id in ids:
			f.write(f'{user_id}\n')
	
	
	menu(vk, (banned, applied, ids))


def id_link(vk, menu_start):
	os.system('cls')
	if menu_start == 1:  # рассылка
		user_group = int(input(
			'Вы хотите сделать рассылку\n\n1 - В личку пользователям\n2 - В личные сообщения группам\n3 - Под '
			'последнии 10 постов группы'
			'\n\nВведите цифру:'
			))
		
		if user_group == 2:
			os.system('cls')
			print('Преобразуем ссылки в id\n\nПожалуйста подождите...')
			list_id_group = []  # айди группы преобразованные из ссылки
			
			with open('link_group.txt', 'r') as group_list:
				for link in group_list:
					try:
						group_id = get_group_id_by_link(vk, link)
						print(f'Айди группы: {group_id:>12} | Ссылка: {link}')
						list_id_group.append(group_id)
					except Exception as e:
						print(f'произошла ошибка {e}, пропускаю группу...')
			message_group(vk, list_id_group)
		
		if user_group == 1:  # по лс юзерам
			os.system('cls')
			print('Преобразуем ссылки в id\n\nПожалуйста подождите...')
			id_user_all = []
			with open('link_user.txt', 'r') as user_list:
				for id in user_list:
					try:
						group_id = int(id[:-2])
						print(f'Айди участника: {group_id:>12} | Ссылка: https://vk.com/id{id}')
						id_user_all.append(group_id)
					except Exception as e:
						print(f'произошла ошибка {e}, пропускаю пользователя...')
				func_message_send(vk, id_user_all)
		
		if user_group == 3:
			os.system('cls')
			print('Преобразуем ссылки в id\n\nПожалуйста подождите...')
			list_links_ids_group = []  # айди группы преобразованные из ссылки
			
			with open('link_group.txt', 'r') as group_list:
				for link in group_list:
					try:
						group_id = get_group_id_by_link(vk, link)
						print(f'Айди группы: {group_id:>12} | Ссылка: {link[:-2]}')
						list_links_ids_group.append((link, group_id))
					except Exception as e:
						print(f'произошла ошибка {e}, пропускаю группу...')
			message_group_comments(vk, list_links_ids_group)
			
	
	if menu_start == 2:  # парсинг
		os.system('cls')
		what = int(input("Парсинг группы\n\n1 - Найти группу по ключевому слову\n2 - Вставить свою ссылку\n\nВвод:"))
		
		if what == 1:
			group_id = get_group_id_by_key(vk)
		else:
			link_parsing = input('Введите ссылку на группу:')
			group_id = get_group_id_by_link(vk, link_parsing)
		
		func_parsing(vk, group_id)
	
	if menu_start == 3:  # ПОСТИНГ НА СТЕНКУ ЗАПИСИ
		os.system('cls')
		print('Преобразуем ссылки в id\n\nПожалуйста подождите...')
		list_id_group = []  # айди группы преобразованные из ссылки
		group_list = open('post_group.txt', 'r')
		for group_id_info in group_list:
			try:
				group_id = get_group_id_by_link(vk, group_id_info)
				list_id_group.append(group_id)
			
			except Exception as e:
				print(f'произошла ошибка {e}, пропускаю группу...')
				continue
		func_posting(vk, list_id_group)


def menu(vk, last_pars=None):
	os.system('cls')
	if last_pars is not None:
		print(f'Забанненых аккаунтов: {last_pars[0]}')
		print(f'Всего спаршенных: {last_pars[1]}')
		count_of_link_users = int(input("\nВведите сколько человек вы хотите сохранить для рассылки:"))
		
		with open('link_user.txt.txt', 'a') as f:
			for user_id in last_pars[2][:count_of_link_users]:
				f.write(f'{user_id}\n')
	console = Console()
	console.print("ПРОГРАММА ВКОНТАКТЕ", style="bold yellow", justify="center")
	table = Table(title="\nФУНКЦИОНАЛ ПРОГРАММЫ")
	table.add_column("№ Функции", justify="right", style="cyan")
	table.add_column("Название функции", style="sandy_brown")
	table.add_column("Описание функции", justify="right", style="green")
	table.add_row(
		"1", "Рассылка", "1 - Рассылка в личку пользователям\n2 - Рассылка в личные сообщения группе\n3 - Под "
		                 "последнии 10 постов группы",
		end_section=True
		)
	table.add_row(
		"2", "Парсинг групп", "1 - Всех пользователей\n2 - Активных онлайн\n3 - По полу\n4 - По городу\n5 - По возрасту\n6 - Только с фото",
		end_section=True
		)
	table.add_row("3", "Постинг на стену групп", "Оставляет запись на стенах групп", end_section=True)
	
	console.print(table, justify="center")
	console.print("Напишите цифру которая указана в таблице:", style="bold red", justify="center")
	menu_start = int(input('Введите цифру:'))
	
	if menu_start in [1, 2, 3]:
		id_link(vk, menu_start)


def auth1():
	while True:
		try:
			token = input(
				"Вставьте ссюда access_token:"
				)
			logging.basicConfig(level=logging.INFO)
			# авторизация аккаунта
			vk_session = vk_api.VkApi(app_id=2685278, token=token)
			vk = vk_session.get_api()
			os.system('cls')
			menu(vk)
		except Exception as e:
			print(e)
			traceback.print_exc()
			input('Нажмите что бы заного авторизоватся...')


auth1()