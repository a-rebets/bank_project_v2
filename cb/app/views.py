"""
ДОСЬЕ ЭМИТЕНТА. СИСТЕМА АДМИНИСТРИРОВАНИЯ БАЗЫ ДАННЫХ
------------- версия 0.2.0 от 07.05.18 -------------
Последние изменения в файле:
- 
директория: https://github.com/Platypus98/CB_project_2.0.git
"""

import os
import xlwt
import re
from pandas import *
from collections import namedtuple
from datetime import datetime, timedelta
from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .forms import *
from .models import *

# -------------------
# ПРОВЕРКА НЕОБХОДИМОСТИ БЛОКИРОВКИ НА ВРЕМЯ ОБНОВЛЕНИЯ
# -------------------
def blocking(request):
	data = {'has_excel': False}
	data['has_excel'] = not is_blocked()
	return JsonResponse(data)

def is_blocked(*args):
	try:
		file = open('update/DB.xlsm')
		return False
	except IOError as e:
		return True    

def error_blocking(request):
	return render(request, 'error_blocking.html')

# -------------------
# АВТОРИЗАЦИЯ
# -------------------
def auth_it(request):
	if request.method == 'POST':
		data = {
			'l_in': False,
			'l_out': False
		}
		if not request.user.is_authenticated:
			# print("Ok, let's login")
			username = request.POST.get('username', None)
			password = request.POST.get('password', None)
			user = auth.authenticate(username=username, password=password)
			if user is not None:
				auth.login(request, user)
				data['name'] = user.first_name
				data['nick'] = user.username
				data['l_in'] = True
		else:
			# print("I will log you out")
			auth.logout(request)
			data['l_out'] = True
	else:
		if request.user.is_authenticated:
			# print("Checking? You are already authenticated")
			data = { 'auth_good': True }
		else:
			# print("Checking? You are not authenticated")
			data = { 'auth_good': False }

	return JsonResponse(data)

# -------------------
# ГЛАВНАЯ СТРАНИЦА
# -------------------
def home(request):

	# ---___--- блок обработки истории ---___---
  
	types = {2:'Авторизация пользователя',100:'Ред. карточки',101:'Ред. раскрытия',102:'Ред. административки',103:'Ред. взаимодействия',19:'Обновление базы'}
	icons = {2:'person',19:'file_upload',100:'edit',101:'edit',102:'edit', 103:'edit'}

	entry_list = History.objects.all()

	for entry in entry_list:
		entry.icon = icons[entry.type_id]
		entry.type = types[entry.type_id]
		entry.user = User.objects.get(id = entry.user_id ).first_name + ' ' + User.objects.get(id = entry.user_id ).last_name

	# ---___--- конец блока обработки истории ---___---
	
	count = Data111.objects.all().count()
	context = {
		'count': count,
		'entry_list':entry_list[::-1],
	}

	return render(request, 'base.html', context)

# -------------------
# СТРАНИЦА ПОИСКА
# -------------------
def search(request):
	size_error = False
	data_error = False
	empty_error = False
	form = Data111Form(request.POST or None)
	limit = limitForm(request.POST or None)
	queryset = None
	context = {
		"queryset": queryset,
		"form": form,
		"limit": limit,
		"toomany": size_error,
		"nores": data_error
	}

	if request.method == 'POST':
		if form['naimenovanie'].value() == '' and form['inn'].value() == '' and form['ogrn'].value() == '' and form[
			'cod_emitenta'].value() == '':
			empty_error = True
		else:
			queryset = Data111.objects.all().filter(naimenovanie__icontains=form['naimenovanie'].value(),
													inn__icontains=form['inn'].value(),
													ogrn__icontains=form['ogrn'].value(),
													cod_emitenta__icontains=form['cod_emitenta'].value())
		if queryset is not None and len(queryset) >= 5000:
			size_error = True
		if size_error or empty_error:
			queryset = None
		if not empty_error and not size_error:
			if len(queryset) == 0:
				data_error = True
		context = {
			"queryset": queryset,
			"form": form,
			"limit": limit,
			"toomany": size_error,
			"nores": data_error
		}

	return render(request, 'search.html', context)

# -------------------
# ПРОВЕРКА ПРАВ
# -------------------
def get_group(request):
	checking = int(request.POST.get('send', None))
	print(checking)
	rights_dict = {
		0: (3,),
		1: (2,3,),
		2: (3,),
		3: (3,)
	}
	print(rights_dict[checking])
	user = auth.get_user(request)
	group = request.user.groups.values_list('id', flat=True).first()
	print(group)
	if (group in rights_dict[checking]):
		data = { 'has_rights': True }
	else:
		data = { 'has_rights': False }
	
	return JsonResponse(data)

# -------------------
# СТРАНИЦА ЭМИТЕНТА
# -------------------
@user_passes_test(is_blocked, login_url='/error_blocking')
def edit_kartochka(request, id):
	def new_entry(section):
		query = 'INSERT INTO easyaudit_crudevent (content_type_id, user_id, datetime, object_id,event_type) VALUES (%s,%s,%s,%s,%s)'
		types = {0:100,1:101,2:102,3:103}
		t = (types[section], request.user.id, str(datetime.datetime.now() - timedelta(hours = 3)), id, 2)
		
		cursor = connection.cursor()		
		cursor.execute(query, t)  
		cursor.close()
		
	rights_dict = {
		0: (3,),
		1: (2,3,),
		2: (3,),
		3: (3,)
	}
	title = Data111.objects.get(id=id).naimenovanie
	t = re.search(r'"([^"]*)"', title)
	if t:
		title = '"'+t.group(1)+'"'

	opf = Data111.objects.get(id=id).opf
	user = auth.get_user(request)
	group = request.user.groups.values_list('id', flat=True).first()

	obj = get_object_or_404(Data111, id=id)
	form = Data111Edit_KartochkaForm(request.POST or None, instance=obj)
	form1 = Data111Edit_RaskrytieForm(request.POST or None, instance=obj)
	form2 = Data111Edit_AdministrativkaForm(request.POST or None, instance=obj)
	form3 = Data111Edit_VsaimodejstvieForm(request.POST or None, instance=obj)
	forms = (form, form1, form2, form3,)


	if request.method == 'POST':
		check_changes = request.POST.get('which_changed')
		for _ in range(4):
			if check_changes[_] == 'T':
				new_entry(_)
				forms[_].save()

		return HttpResponseRedirect(f'/edit/kartochka_kompanii/{id}')

	context = {
		"title": title,
		"opf": opf,
		"forms": forms,
		"id": id,
	}


	return render(request, 'edit_kartochka.html', context)

def edit_korp_kontrol(request, id):
	title = Data111.objects.get(id=id).naimenovanie
	obj = get_object_or_404(Data111, id=id)
	obj_1 = get_object_or_404(Data_korp_kontrol, ogrn=Data111.objects.get(id=id).ogrn)
	form = Data111Edit_Korp_KontrolForm(request.POST or None, instance=obj)
	form1 = Data111_second_korp(request.POST or None, instance=obj_1)

	if request.method == 'POST':
		form1.save()
		form.save()

		
	context = {
		"title": title,
		"form": form,
		'form1':form1,
		"id": id,
	}


	return render(request, 'edit_korp_kontrol.html', context)


# -------------------
# СТРАНИЦА ОБНОВЛЕНИЯ
# -------------------
def list(request):
	def russkie_dates(dick):
		'''Русифицирует даты'''
		keylist = tuple(dick.keys())
		datelist = [4,18,24,26,28,32,33,35,37,39,52,55,58,61,62,64,66,68,70,74,76,79,85,94]

		for k in datelist:
			for i in dick[keylist[k]].keys():
				year = dick[keylist[k]][i][:4]
				month = dick[keylist[k]][i][5:7]
				day = dick[keylist[k]][i][8:10]
				if '00:00:00' in dick[keylist[k]][i]:
					dick[keylist[k]][i] = f'{day}.{month}.{year}'

	def dictfetchall(cursor):
		columns = [col[0] for col in cursor.description]
		return [
			dict(zip(columns, row))
			for row in cursor.fetchall()
		]

	try:
		# Загрузчик файла эксель
		if request.method == 'POST':
			data = {
				'parse_ok': False,
			}

			form = DocumentForm(request.POST, request.FILES)
			if form.is_valid():
				newdoc = Document(docfile=request.FILES['docfile'])
				newdoc.save()

				#----Парсинг эксель
				xls = ExcelFile('update/DB.xlsm')


				conv = {i:str for i in range(96)}

				sh1 = xls.parse(xls.sheet_names[0], converters=conv)
				sh1 = sh1.fillna('')
				
				# sh2 = xls.parse(xls.sheet_names[1])
				
				excel_dict1 = sh1.to_dict()
				#------------------

				delete_db_query()
				russkie_dates(excel_dict1)

				cache.set('main_dict', excel_dict1, None)
				

				e_c = []
				for z in excel_dict1:
					e_c.append(z)
				e_c.remove('НАИМЕНОВАНИЕ')


				cache.set('ex_dict', e_c, None)

				data['parse_ok'] = True

			return JsonResponse(data)

		if request.method == 'GET' and request.is_ajax():
			k = int(request.GET.get('k', None))
			data = {
				'update_ok': False,
				'update_err': False
			}

			if k == 0:
				main = cache.get('main_dict')

				#----Первый столбец для дальнейшей индексации  
				cursor = connection.cursor()

				query = "INSERT INTO Data111 (НАИМЕНОВАНИЕ) VALUES (%s);"
				l = [] 
				t = ()

				cursor.execute("BEGIN TRANSACTION;")

				for i in main['ОГРН'].keys():
					l = [] 
					t = ()
					l.append(main['НАИМЕНОВАНИЕ'][i])
					t = tuple(l)
					cursor.execute(query, t)  

				cursor.execute("COMMIT;")

				cursor.close()
				#--------------------
		   
			update(k) #обновление 

			if k == 95:
				delete_file()
				cache.delete('main_dict')
				cache.delete('ex_dict')
				cursor = connection.cursor()
				cursor.execute("BEGIN TRANSACTION;")
				cursor.execute("UPDATE Data111 SET РЕГИСТРАТОР1 = РЕГИСТРАТОР")
				cursor.execute("INSERT INTO app_data_korp_kontrol(ogrn) SELECT Data111.ОГРН FROM Data111 WHERE Data111.ОГРН NOT IN (SELECT app_data_korp_kontrol.ogrn FROM app_data_korp_kontrol );") 
				cursor.execute("DELETE FROM app_data_korp_kontrol WHERE app_data_korp_kontrol.ogrn NOT IN (SELECT Data111.ОГРН FROM Data111 );") 
				cursor.execute("UPDATE Data111 SET НАИМЕНОВАНИЕ = UPPER(НАИМЕНОВАНИЕ)")
				cursor.execute("COMMIT;")
				cursor.close()

			data['update_ok'] = True
			return JsonResponse(data)

	except:
		delete_file()
		cache.delete('main_dict')
		cache.delete('ex_dict')
		data['update_err'] = True
		return JsonResponse(data)
	else:
		form = DocumentForm()  # Пустая форма

		# дата последней загрузки
		cursor = connection.cursor()
		cursor.execute("SELECT datetime FROM easyaudit_crudevent WHERE (content_type_id = 19)")
		last_u = dictfetchall(cursor)
		last_u = last_u[::-1]
		last_upload = last_u[0]['datetime']
		last_upload += timedelta(hours=3)
		cursor.close()
	return render(
		request,
		'db_update.html',
		{ 'form': form,'last_upload':last_upload }
	)

def update(k):
	'''Обновляет ка + первый столбцец БД'''
	db_columns =  ['ИНН','ОГРН','КПП','ДАТА_РЕГИСТРАЦИИ','ОПФ','КОД_ЭМИТEHТA','УСТАВНЫЙ_КАПИТАЛ',
	'Количество_лицевых_счетов_в_реестре','Количество_номинальных_держателей_в_реестре','Сведения_об_открытии_счета_номинального_держателя_центрального_депозитария',
	'РЕГИОН','АДРЕС','ЕДИНОЛИЧНЫЙ_ИСПОЛНИТЕЛЬНЫЙ_ОРГАН','КОНТАКТНЫЕ_ДАННЫЕ','ВИД_ДЕЯТЕЛЬНОСТИ','СТАТУС','ДВИЖЕНИЕ_ДЕНЕЖНЫХ_СРЕДСТВ','ДАТА_ПОСЛЕДНЕЙ_ОПЕРАЦИИ','ОТЧЕТНОСТЬ',
	'ЗАДОЛЖЕННОСТЬ_ПЕРЕД_ФНС','КАРТОЧКА_КОМПАНИИ','РЕГИСТРАТОР','НАИМЕНОВАНИЕ_РЕГИСТРАТОРА','ДАТА_ПРЕДПИСАНИЯ_О_ПРЕДСТАВЛЕНИИ_ДОКУМЕНТОВ',
	'НОМЕР_ПРЕДПИСАНИЯ_О_ПРЕДСТАВЛЕНИИ_ДОКУМЕНТОВ','ДАТА_ЗАПРОСА_ПО_РЕЕСТРУ','НОМЕР_ЗАПРОСА_ПО_РЕЕСТРУ','ДАТА_ПРЕДПИСАНИЯ_ПО_РЕЕСТРУ',
	'НОМЕР_ПРЕДПИСАНИЯ_ПО_РЕЕСТРУ','ПРОВЕРКИ_ГОСА_ПО_РАСКРЫТИЮ','ПРОВЕРКИ_ГОСА_ПО_ЗАПРОСУ','ДАТА_ПРОВЕДЕНИЯ_ГОСА','ДАТА_ЗАПРОСА_ПО_ГОСА',
	'НОМЕР_ЗАПРОСА_ПО_ГОСА','ДАТА_ПРЕДПИСАНИЯ_О_ПРЕДСТАВЛЕНИИ_ДОКУМЕНТОВ_ГОСА','НОМЕР_ПРЕДПИСАНИЯ_О_ПРЕДСТАВЛЕНИИ_ДОКУМЕНТОВ_ГОСА','ДАТА_ПРОВЕРКИ_ГОСА','ПРОВЕРКА_1_ВЫПУСК','ДАТА_ПРЕДПИСАНИЯ_ПО_1_ВЫПУСКУ','НОМЕР_ПРЕДПИСАНИЯ_ПО_1_ВЫПУСКУ','НРД',
	'ПРОВЕРКИ_НРД','ОАО_на_22_06_2015','КОРП_КОНТРОЛЬ','ПАО_В_СИЛУ_ПРИЗНАКОВ_СТ_30','ПАО_В_СИЛУ_ПРИЗНАКОВ_БЕЗ_СТ_30','ПАО_В_СИЛУ_НАЗВАНИЯ_СТ_30',
	'ПАО_В_СИЛУ_НАЗВАНИЯ_БЕЗ_СТ_30','НАО_СО_СТ_30','НАО_БЕЗ_СТ_30','НАО_ОСУЩЕСТВИВШЕЕ_ОСУЩЕСТВЛЯЮЩЕЕ_ПУБЛИЧНОЕ_РАЗМЕЩЕНИЕ_ОБЛИГАЦИЙ_ИЛИ_ИНЫХ_ЦЕННЫХ_БУМАГ',
	'ДАТА_ОПРЕДЕЛЕНИЯ_СТАТУСА','ОТКАЗ_В_РЕГИСТРАЦИИ_ВЫПУСКА','ОСВОБОЖДЕНЫ_ОТ_РАСКРЫТИЯ','ДАТА_РЕШЕНИЯ_ОБ_ОСВОБОЖДЕНИИ','НОМЕР_РЕШЕНИЯ_ОБ_ОСВОБОЖДЕНИИ',
	'ОТКАЗ_В_ОСВОБОЖДЕНИИ_ОТ_РАСКРЫТИЯ','ДАТА_ОТКАЗА_В_ОСВОБОЖДЕНИИ_ОТ_РАСКРЫТИЯ','НОМЕР_ОТКАЗА_В_ОСВОБОЖДЕНИИ_ОТ_РАСКРЫТИЯ','ПРОВЕРКА_РАСКРЫТИЯ',
	'ДАТА_ПРОВЕРКИ','ДАТА_ЗАПРОСА_ПО_НЕ_РАСКРЫТИЮ_ИНФОРМАЦИИ','НОМЕР_ЗАПРОСА_ПО_НЕ_РАСКРЫТИЮ_ИНФОРМАЦИИ','ДАТА_ПРЕДПИСАНИЯ_ПО_НЕ_РАСКРЫТИЮ_ИНФОРМАЦИИ',
	'НОМЕР_ПРЕДПИСАНИЯ_ПО_НЕ_РАСКРЫТИЮ_ИНФОРМАЦИИ','ДАТА_ПРЕДПИСАНИЯ_О_ПРЕДСТАВЛЕНИИ_ДОКУМЕНТОВ_РАСКРЫТИЕ','НОМЕР_ПРЕДПИСАНИЯ_О_ПРЕДСТАВЛЕНИИ_ДОКУМЕНТОВ_РАСКРЫТИЕ',
	'ДАТА_ЗАПРОСА_О_РЕЗУЛЬТАТАХ_ПРОВЕДЕНИЯ_ТОРГОВ_В_ОБЩЕСТВЕ','НОМЕР_ЗАПРОСА_О_РЕЗУЛЬТАТАХ_ПРОВЕДЕНИЯ_ТОРГОВ_В_ОБЩЕСТВЕ',
	'ДАТА_ОТВЕТА_НА_ЗАПРОСА_О_РЕЗУЛЬТАТАХ_ПРОВЕДЕНИЯ_ТОРГОВ_В_ОБЩЕСТВЕ','НОМЕР_ОТВЕТА_НА_ЗАПРОСА_О_РЕЗУЛЬТАТАХ_ПРОВЕДЕНИЯ_ТОРГОВ_В_ОБЩЕСТВЕ','ВЫВОД',
	'РАСКРЫТИЕ','ДАТА_ЗАКЛЮЧЕНИЯ_ЮРИСТАМ','НОМЕР_ЗАКЛЮЧЕНИЯ_ЮРИСТАМ','ДАТА_ПРОТОКОЛА','НОМЕР_ПРОТОКОЛА','СТАТЬЯ_КОАП','ДАТА_ПОСТАНОВЛЕНИЯ','НОМЕР_ПОСТАНОВЛЕНИЯ',
	'РЕЗУЛЬТАТ','РАЗМЕР_ШТРАФА','АДМИНИСТРАТИВКА','ФНС','ДАТА_ПИСЬМА_В_ФНС','НОМЕР_ПИСЬМА_В_ФНС','ИНФОРМАЦИЯ_О_ПОЛУЧЕНИИ_ОТВЕТА_ОТ_ФНС','ВХ_НОМЕР_ОТВЕТА',
	'СОДЕРЖАНИЕ_ОТВЕТА','ОТВЕТ_ФНС_ОБ_АДРЕСЕ','СВЕДЕНИЯ_ОБ_АДРЕСЕ_НЕ_ДОСТОВЕРНЫ','ВЗАИМОДЕЙСТВИЕ_С_ФНС_НА_ЕЖЕКВАРТАЛЬНОЙ_ОСНОВЕ',
	'ВЗАИМОДЕЙСТВИЕ_С_ФНС_НА_ЕЖЕКВАРТАЛЬНОЙ_ОСНОВЕ_НОМЕР_ПИСЬМА','ВЗАИМОДЕЙСТВИЕ_С_ФНС_НА_ЕЖЕКВАРТАЛЬНОЙ_ОСНОВЕ_ДАТА_ПИСЬМА','ДАТА_ВНЕСЕНИЯ_ЗАПИСИ',
	'ВЗАИМОДЕЙСТВИЕ_С_ГОС_ОРГАНАМИ']

   #получение словарей из кэша
	dick = cache.get('main_dict')
	excel_columns = cache.get('ex_dict')

   #обновление столбца
	cursor = connection.cursor()
	query = "UPDATE Data111 SET {} = %s WHERE id = %s;".format(db_columns[k])
	l = [] 
	t = ()

	cursor.execute("BEGIN TRANSACTION;")

	for i in dick['ОГРН'].keys():
		l = [] 
		t = ()
		l.append(dick[excel_columns[k]][i])
		l.append(i+1)
		t = tuple(l)
		cursor.execute(query, t)  
			
	cursor.execute("COMMIT;")

	cursor.close()

def namedtuplefetchall(cursor):
	'''Делает хорошо итерируемый лист для
	работы с результами курсора'''
	desc = cursor.description
	nt_result = namedtuple('Result', [col[0] for col in desc])
	return [nt_result(*row) for row in cursor.fetchall()]

def delete_db_query():
	'''Стирает все значения БД'''
	cursor = connection.cursor()
	cursor.execute("DELETE FROM Data111 WHERE id >= (SELECT min(id) FROM Data111)")
	cursor.close()

def delete_file():
	'''Удаляет файл эксель с БД из media'''
	try:
		os.remove('update/DB.xlsm')
	except:
		pass

# -------------------
# СТРАНИЦА ВЫБОРКИ
# -------------------
def selections(request):
	a = []
	b = []
	filter_list = []
	k = 0
	queryset = Data111.objects.all()

	columns_to_display = Data111FormSelection.Meta.fields

	form = Data111FormSelection(request.POST or None)
	form_filter_opf = Filter_opf(request.POST or None)
	form_filter_kolichestvo_schetov = Filter_kolichestvo_licevyh_schetov_v_reestre(request.POST or None)
	form_filter_region = Filter_region(request.POST or None)
	form_filter_status = Filter_status(request.POST or None)
	form_filter_dvizhenie_denezhnyh_sredstv = Filter_dvizhenie_denezhnyh_sredstv(request.POST or None)
	form_filter_otchetnost = Filter_otchetnost(request.POST or None)
	form_filter_zadolzhennost_pered_fns = Filter_zadolzhennost_pered_fns(request.POST or None)
	form_filter_registrator = Filter_registrator(request.POST or None)
	form_filter_proverka_gosa_po_raskratiu = Filter_proverka_gosa_po_raskratiu(request.POST or None)
	form_filter_proverky_gosa_po_zaprosu = Filter_proverky_gosa_po_zaprosu(request.POST or None)
	form_filter_nrd = Filter_nrd(request.POST or None)
	form_filter_proverki_nrd = Filter_proverky_nrd(request.POST or None)
	form_filter_oao_na_22062015 = Filter_oao_na_22062015(request.POST or None)
	form_filter_data_zaprosa_po_reestru = Filter_data_zaprosa_po_reestru(request.POST or None)

	context = {
		"form": form,
		"queryset": queryset,
		"form_filter_opf": form_filter_opf,
		"form_filter_kolichestvo_schetov": form_filter_kolichestvo_schetov,
		"form_filter_region": form_filter_region,
		"form_filter_status": form_filter_status,
		"form_filter_dvizhenie_denezhnyh_sredstv": form_filter_dvizhenie_denezhnyh_sredstv,
		"form_filter_otchetnost": form_filter_otchetnost,
		"form_filter_zadolzhennost_pered_fns": form_filter_zadolzhennost_pered_fns,
		"form_filter_registrator": form_filter_registrator,
		"form_filter_proverka_gosa_po_raskratiu": form_filter_proverka_gosa_po_raskratiu,
		"form_filter_proverky_gosa_po_zaprosu": form_filter_proverky_gosa_po_zaprosu,
		"form_filter_nrd": form_filter_nrd,
		"form_filter_proverki_nrd": form_filter_proverki_nrd,
		"form_filter_oao_na_22062015": form_filter_oao_na_22062015,
		"form_filter_data_zaprosa_po_reestru": form_filter_data_zaprosa_po_reestru,

	}

	# Отображение в браузере
	if request.method == 'POST':

		table_headers = map(lambda a: Data111._meta.get_field(a).help_text, columns_to_display)

		for i in form._meta.fields:
			if form[i].value():
				a.append(form[i].label)

		for i in form._meta.fields:
			if form[i].value():
				b.append(i)


		# Фильтры ОПФ
		if form['opf'].value():
			for i in ['ao', 'aozt', 'aoot', 'zao', 'nao', 'oao', 'pao']:
				if form_filter_opf[i].value():
					filter_list.append(form_filter_opf[i].label)
			if filter_list == []:
				pass
			else:
				filter_ = Data111.objects.filter(opf__in=filter_list)
				k = 1

		filter_list = []
		# Фильтры количество лицевых счетов
		if form['kolichestvo_licevyh_schetov_v_reestre'].value():
			if k == 1:
				if form_filter_kolichestvo_schetov['bolshe_50'].value():
					filter_ = filter_.filter(kolichestvo_licevyh_schetov_v_reestre__gte=50)
				elif form_filter_kolichestvo_schetov['menshe_50'].value():
					filter_ = filter_.filter(kolichestvo_licevyh_schetov_v_reestre__lte=50)
			else:
				if form_filter_kolichestvo_schetov['bolshe_50'].value():
					filter_ = Data111.objects.filter(kolichestvo_licevyh_schetov_v_reestre__gte=50)
					k = 1
				elif form_filter_kolichestvo_schetov['menshe_50'].value():
					filter_ = Data111.objects.filter(kolichestvo_licevyh_schetov_v_reestre__lte=2)
					k = 1

		# Фильтры регион
		if form['region'].value():
			if k == 1:
				for i in ['moskva', 'moskovskaya']:
					if form_filter_region[i].value():
						filter_list.append(form_filter_region[i].label)
				if filter_list == []:
					pass
				else:
					filter_ = filter_.filter(region__in=filter_list)
				filter_list = []
			else:
				for i in ['moskva', 'moskovskaya']:
					if form_filter_region[i].value():
						filter_list.append(form_filter_region[i].label)
				if filter_list == []:
					pass
				else:
					filter_ = Data111.objects.filter(region__in=filter_list)
					k = 1
				filter_list = []

		# Фильтры статус
		if form['status'].value():
			if k == 1:
				for i in ['bankrotstvo', 'deistvyushaya', 'nahoditca_v_processe_reorganizacii_v_forme_videlenya',
						  'nahoditca_v_processe_reorganizacii_v_forme_videlenya_osyshestvlyaemoe_odnovremenno_s_videleniem',
						  'nahoditca_v_processe_reorganizacii_v_forme_preobrazovanya',
						  'nahoditca_v_processe_reorganizacii_v_forme_prisoedinenya_k_drygomy_ul',
						  'nahoditca_v_processe_reorganizacii_v_forme_prisoedinenya_k_nemy_drygih_ul',
						  'nahoditca_v_processe_reorganizacii_v_forme_prisoedinenya_osychestvlyaemoy_odnovremenno_s_videleniem',
						  'nahoditca_v_processe_reorganizacii_v_forme_razdelenya_osychestvlyaemoy_odnovremenno_s_prisoedineniem',
						  'nahoditca_v_processe_reorganizacii_v_forme_sliyaniya',
						  'nahoditca_v_processe_reorganizacii_v_forme_razdelenya', 'nahoditca_v_stadii_likvidacii',
						  'prinyato_reshenie_o_predostoyashem_iskluchenii_nedeystvyushego_ul_iz_egrul']:
					if form_filter_status[i].value():
						filter_list.append(form_filter_status[i].label)
				if filter_list == []:
					pass
				else:
					filter_ = filter_.filter(status__in=filter_list)
				filter_list = []
			else:
				for i in ['bankrotstvo', 'deistvyushaya', 'nahoditca_v_processe_reorganizacii_v_forme_videlenya',
						  'nahoditca_v_processe_reorganizacii_v_forme_videlenya_osyshestvlyaemoe_odnovremenno_s_videleniem',
						  'nahoditca_v_processe_reorganizacii_v_forme_preobrazovanya',
						  'nahoditca_v_processe_reorganizacii_v_forme_prisoedinenya_k_drygomy_ul',
						  'nahoditca_v_processe_reorganizacii_v_forme_prisoedinenya_k_nemy_drygih_ul',
						  'nahoditca_v_processe_reorganizacii_v_forme_prisoedinenya_osychestvlyaemoy_odnovremenno_s_videleniem',
						  'nahoditca_v_processe_reorganizacii_v_forme_razdelenya_osychestvlyaemoy_odnovremenno_s_prisoedineniem',
						  'nahoditca_v_processe_reorganizacii_v_forme_sliyaniya',
						  'nahoditca_v_processe_reorganizacii_v_forme_razdelenya', 'nahoditca_v_stadii_likvidacii',
						  'prinyato_reshenie_o_predostoyashem_iskluchenii_nedeystvyushego_ul_iz_egrul']:
					if form_filter_status[i].value():
						filter_list.append(form_filter_status[i].label)
				if filter_list == []:
					pass
				else:
					filter_ = Data111.objects.filter(status__in=filter_list)
					k = 1
				filter_list = []

		# Фильтры движение денежных средств
		if form['dvizhenie_denezhnyh_sredstv'].value():
			if k == 1:
				for i in ['da', 'net']:
					if form_filter_dvizhenie_denezhnyh_sredstv[i].value():
						filter_list.append(form_filter_dvizhenie_denezhnyh_sredstv[i].label)
				if filter_list == []:
					pass
				else:
					filter_ = filter_.filter(dvizhenie_denezhnyh_sredstv__in=filter_list)
				filter_list = []
			else:
				for i in ['da', 'net']:
					if form_filter_dvizhenie_denezhnyh_sredstv[i].value():
						filter_list.append(form_filter_dvizhenie_denezhnyh_sredstv[i].label)
				if filter_list == []:
					pass
				else:
					filter_ = Data111.objects.filter(dvizhenie_denezhnyh_sredstv__in=filter_list)
					k = 1
				filter_list = []

		# Фильтры отчетность
		if form['otchetnost'].value():
			if k == 1:
				if form_filter_otchetnost['nepustaia'].value():
					filter_ = filter_.exclude(otchetnost__exact="")
				elif form_filter_otchetnost['pustaia'].value():
					filter_ = filter_.filter(otchetnost__exact="")
			else:
				if form_filter_otchetnost['nepustaia'].value():
					filter_ = Data111.objects.exclude(otchetnost__exact="")
					k = 1
				elif form_filter_otchetnost['pustaia'].value():
					filter_ = Data111.objects.filter(otchetnost__exact="")
					k = 1

		# Фильтры задолженность перед ФНС
		if form['zadolzhennost_pered_fns'].value():
			if k == 1:
				if form_filter_zadolzhennost_pered_fns['nepustaia'].value():
					filter_ = filter_.exclude(zadolzhennost_pered_fns__exact="")
				elif form_filter_zadolzhennost_pered_fns['pustaia'].value():
					filter_ = filter_.filter(zadolzhennost_pered_fns__exact="")
			else:
				if form_filter_zadolzhennost_pered_fns['nepustaia'].value():
					filter_ = Data111.objects.exclude(zadolzhennost_pered_fns__exact="")
					k = 1
				elif form_filter_zadolzhennost_pered_fns['pustaia'].value():
					filter_ = Data111.objects.filter(zadolzhennost_pered_fns__exact="")
					k = 1

		# Корп контроль
		# Фильтры дата запроса по реестру
		if form['data_zaprosa_po_reestru'].value():
			if k == 1:
				if form_filter_data_zaprosa_po_reestru["from_"] and form_filter_data_zaprosa_po_reestru['to']:
					for i in range(Data111.objects.raw("SELECT count(id) FROM Data111")):
						if (datetime.date(Data111.objects.all()[i].data_zaprosa_po_reestru) >= datetime.date(
								form_filter_data_zaprosa_po_reestru["from_"])) and (
								datetime.date(Data111.objects.all()[i].data_zaprosa_po_reestru) <= datetime.date(
								form_filter_data_zaprosa_po_reestru["to"])):
							pass
						else:
							filter_ = filter_.exclude(id=i)
			else:
				if form_filter_data_zaprosa_po_reestru["from_"] and form_filter_data_zaprosa_po_reestru['to']:
					for i in range(Data111.objects.all().count()):
						date_str = Data111.objects.all()[i].data_zaprosa_po_reestru
						date_str_from = form_filter_data_zaprosa_po_reestru["from_"].value().split('-')
						for k in range(len(date_str_from)):
							if date_str_from[k][0] == "0":
								date_str_from[k] = date_str_from[k][1]
						date_str_to = form_filter_data_zaprosa_po_reestru["to"].value().split('-')
						for k in range(len(date_str_to)):
							if date_str_to[k][0] == "0":
								date_str_to[k] = date_str_to[k][1]
						if "\n" in date_str:
							date_str = date_str.split("\n")
							for i in date_str:
								date_str_1 = i.split('.')
								for j in range(len(date_str_1)):
									if date_str_1[j][0] == "0":
										date_str_1[j] = date_str_1[j][1]
								if (datetime.date(int(date_str_1[2]), int(date_str_1[1]),
												  int(date_str_1[0])) > datetime.date(int(date_str_from[0]),
																					  int(date_str_from[1]),
																					  int(date_str_from[2]))) and (
										datetime.date(int(date_str_1[2]), int(date_str_1[1]),
													  int(date_str_1[0])) < datetime.date(int(date_str_to[0]),
																						  int(date_str_to[1]),
																						  int(date_str_to[2]))):
									check = 1

								if i == 0:
									filter_ = Data111.objects.exclude(id=i)
								else:
									filter_ = filter_.exclude(id=i)
						else:
							date_str = Data111.objects.all()[i].data_zaprosa_po_reestru.split('.')
							if date_str == [""]:
								if i == 0:
									filter_ = Data111.objects.exclude(id=i)
								else:
									filter_ = filter_.exclude(id=i)
								continue

							if (datetime.date(int(date_str[2]), int(date_str[1]), int(date_str[0])) > datetime.date(
									int(date_str_from[0]), int(date_str_from[1]), int(date_str_from[2]))) and (
									datetime.date(int(date_str[2]), int(date_str[1]), int(date_str[0])) < datetime.date(
									int(date_str_to[0]), int(date_str_to[1]), int(date_str_to[2]))):
								pass
							else:
								if i == 0:
									filter_ = Data111.objects.exclude(id=i)
								else:
									filter_ = filter_.exclude(id=i)
				k = 1

		# Фильтры Регистратор
		if form['registrator'].value():
			if k == 1:
				for i in ["da", "net", "egrul", "chranenie_reestra"]:
					if form_filter_registrator[i].value():
						filter_list.append(form_filter_registrator[i].label)
				if filter_list == []:
					pass
				else:
					filter_ = filter_.filter(registrator__in=filter_list)
				filter_list = []
			else:
				for i in ["da", "net", "egrul", "chranenie_reestra"]:
					if form_filter_registrator[i].value():
						filter_list.append(form_filter_registrator[i].label)
				if filter_list == []:
					pass
				else:
					filter_ = Data111.objects.filter(registrator__in=filter_list)
					k = 1
				filter_list = []

		# Фильтры Проверка ГОСА по раскрытию
		if form["proverky_gosa_po_raskritiyu"].value():
			if k == 1:
				for i in ["maxi", "mini", "avr", "pusto"]:
					if form_filter_proverka_gosa_po_raskratiu[i].value():
						filter_list.append(form_filter_proverka_gosa_po_raskratiu[i].label)
				if filter_list == []:
					pass
				else:
					if "Пустая" in filter_list:
						filter_list.remove("Пустая")
						filter_list.append("")
					filter_ = filter_.filter(proverky_gosa_po_raskritiyu__in=filter_list)
				filter_list = []
			else:
				for i in ["maxi", "mini", "avr", "pusto"]:
					if form_filter_proverka_gosa_po_raskratiu[i].value():
						filter_list.append(form_filter_proverka_gosa_po_raskratiu[i].label)
				if filter_list == []:
					pass
				else:
					if "Пустая" in filter_list:
						filter_list.remove("Пустая")
						filter_list.append("")
					filter_ = Data111.objects.filter(proverky_gosa_po_raskritiyu__in=filter_list)
					k = 1
				filter_list = []

		# Фильтры Проверка ГОСА по запросу
		if form["proverky_gosa_po_zaprosu"].value():
			if k == 1:
				for i in ["akt", "k_proverke", "pusto"]:
					if form_filter_proverky_gosa_po_zaprosu[i].value():
						filter_list.append(form_filter_proverky_gosa_po_zaprosu[i].label)
				if filter_list == []:
					pass
				else:
					if "Пустая" in filter_list:
						filter_list.remove("Пустая")
						filter_list.append("")
					filter_ = filter_.filter(proverky_gosa_po_zaprosu__in=filter_list)
				filter_list = []
			else:
				for i in ["akt", "k_proverke", "pusto"]:
					if form_filter_proverky_gosa_po_zaprosu[i].value():
						filter_list.append(form_filter_proverky_gosa_po_zaprosu[i].label)
				if filter_list == []:
					pass
				else:
					if "Пустая" in filter_list:
						filter_list.remove("Пустая")
						filter_list.append("")
					filter_ = Data111.objects.filter(proverky_gosa_po_zaprosu__in=filter_list)
					k = 1
				filter_list = []

		# Фильтр НРД
		if form['nrd'].value():
			if k == 1:
				if form_filter_nrd['da'].value():
					filter_ = filter_.filter(nrd__exact="ДА")
				elif form_filter_nrd['pusto'].value():
					filter_ = filter_.filter(nrd__exact="")
			else:
				if form_filter_nrd['da'].value():
					filter_ = Data111.objects.filter(nrd__exact="ДА")
					k = 1
				elif form_filter_nrd['pusto'].value():
					filter_ = Data111.objects.filter(nrd__exact="")
					k = 1

		# Фильтры проверки НРД
		if form['proverki_nrd'].value():
			if k == 1:
				for i in ["da", "net_scheta", "pusto"]:
					if form_filter_proverki_nrd[i].value():
						filter_list.append(form_filter_proverki_nrd[i].label)
				if filter_list == []:
					pass
				else:
					if "Пустая" in filter_list:
						filter_list.remove("Пустая")
						filter_list.append("")
					filter_ = filter_.filter(proverki_nrd__in=filter_list)
				filter_list = []
			else:
				for i in ["da", "net_scheta", "pusto"]:
					if form_filter_proverki_nrd[i].value():
						filter_list.append(form_filter_proverki_nrd[i].label)
				if filter_list == []:
					pass
				else:
					if "Пустая" in filter_list:
						filter_list.remove("Пустая")
						filter_list.append("")
					filter_ = Data111.objects.filter(proverki_nrd__in=filter_list)
					k = 1
				filter_list = []

		# Фильтры ОАО на 22.06.2015
		if form["oao_na_22_06_2015"].value():
			if k == 1:
				for i in ["da", "pusto"]:
					if form_filter_oao_na_22062015[i].value():
						filter_list.append(form_filter_oao_na_22062015[i].label)
				if filter_list == []:
					pass
				else:
					if "Пустая" in filter_list:
						filter_list.remove("Пустая")
						filter_list.append("")
					filter_ = filter_.filter(oao_na_22_06_2015__in=filter_list)
				filter_list = []
			else:
				for i in ["da", "pusto"]:
					if form_filter_oao_na_22062015[i].value():
						filter_list.append(form_filter_oao_na_22062015[i].label)
				if filter_list == []:
					pass
				else:
					if "Пустая" in filter_list:
						filter_list.remove("Пустая")
						filter_list.append("")
					filter_ = Data111.objects.filter(oao_na_22_06_2015__in=filter_list)
					k = 1
				filter_list = []

		if k == 1:
			table_rows = filter_.values(*b)
		else:
			table_rows = Data111.objects.all().values(*b)

		# a.remove('Export to CSV')

		context = {
			"form": form,
			"a": a,
			"b": b,
			"table_rows": table_rows,
			"table_headers": table_headers,
			"queryset": queryset,
			"form_filter_opf": form_filter_opf,
			"form_filter_kolichestvo_schetov": form_filter_kolichestvo_schetov,
			"form_filter_region": form_filter_region,
			"form_filter_status": form_filter_status,
			"form_filter_dvizhenie_denezhnyh_sredstv": form_filter_dvizhenie_denezhnyh_sredstv,
			"form_filter_otchetnost": form_filter_otchetnost,
			"form_filter_zadolzhennost_pered_fns": form_filter_zadolzhennost_pered_fns,
			"form_filter_registrator": form_filter_registrator,
			"form_filter_proverka_gosa_po_raskratiu": form_filter_proverka_gosa_po_raskratiu,
			"form_filter_proverky_gosa_po_zaprosu": form_filter_proverky_gosa_po_zaprosu,
			"form_filter_nrd": form_filter_nrd,
			"form_filter_proverki_nrd": form_filter_proverki_nrd,
			"form_filter_oao_na_22062015": form_filter_oao_na_22062015,
			"form_filter_data_zaprosa_po_reestru": form_filter_data_zaprosa_po_reestru,

		}

	# Экспорт в Excel
	if form['export'].value() == True:

		response = HttpResponse(content_type='application/ms-excel')

		response['Content-Disposition'] = 'attachment; filename=selection.xls'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet("Data111")

		row_num = 0

		columns = a

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num])

		font_style = xlwt.XFStyle()
		font_style.alignment.wrap = 1

		if k == 1:
			queryset_1 = filter_.all()
		else:
			queryset_1 = Data111.objects.all()

		for obj in queryset_1:
			row_num += 1
			row = []
			for i in b:
				row.append(getattr(obj, i))

			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

		ws.col(0).width = 20000
		wb.save(response)
		return response
	# Конец экспорта в Excel

	return render(request, 'selections.html', context)
