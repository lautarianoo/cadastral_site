from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
import pyexcel
import random
import requests

headers = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
    'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8'},

    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64;) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112',
    'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8'},

    {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8'}
]

def get_cadastral_data(cadastral):
    cadastral_split = cadastral.split(":")
    number = []
    for i in cadastral_split:
        number.append(str(int(i)))
    number = ":".join(number)
    url = f"https://rosreestr.gov.ru/api/online/fir_object/{number}"

    data = {"get_object": None, "result": [], "data": ["строительства, реконструкции и последующей эксплуатации автобазы с выкупом права аренды", "эксплуатации улично-дорожной сети", "организации открытой приобъектной (к зданиям складской базы) автостоянки", "эксплуатации и под обслуживание автотехцентра", "использование территории под эксплуатацию ремонтно-производственной базы", "размещения производственной базы предприятия", "Земельные участки гаражных кооперативов.", "эксплуатации автостоянки по приему-выгрузке большегрузного автотранспорта", "эксплуатации производственно-складских зданий", "под производственные цели (проведение ремонтных работ и работ по техническому обслуживанию автомобильной и иной промышленной техники)", "дальнейшей эксплуатации территории под крытую автостоянку", "земельные участки, предназначенные для размещения зданий, строений, сооружений материально-технического снабжения, сбыта и заготовок"]}
    resp = requests.get(url, headers=headers[0],  verify=False)
    print(resp)
    if resp.status_code == 200:
        data["get_object"] = resp.json()
        print(resp.json())
        new_cadastral_number = number.split(":")
        counter = 0
        title = f"Объект ОНВ расположен по адресу: {resp.json().get('objectData').get('addressNote')}, участок с кадастровым номером: {number} площадь {resp.json().get('parcelData').get('areaValue')} кв.м. и окружен:"
        contents = []
        data_2d_dict = {}
        for i in range(1, 6000):
            if len(contents) < 120:
                counter+=1
                del new_cadastral_number[-1]
                new_cadastral_number.append(str(random.randint(1, 6000)))
                number = ':'.join(new_cadastral_number)
                url_2 = f"https://rosreestr.gov.ru/api/online/fir_object/{number}"
                resp2 =requests.get(url_2, headers=headers[1], verify=False)
                if resp2.status_code == 200:
                    if resp2.json().get('parcelData').get('categoryTypeValue'):
                        content = f"{number} {resp2.json().get('parcelData').get('categoryTypeValue')}. {resp2.json().get('parcelData').get('areaValue')} кв.м."
                    elif resp2.json().get('parcelData').get('utilByDoc'):
                        content = f"{number} {resp2.json().get('parcelData').get('utilByDoc')}"
                    elif resp2.json().get('parcelData').get('utilCodeDesc'):
                        content = f"{number} {resp2.json().get('parcelData').get('utilCodeDesc')}"
                    else:
                        content = f"{number} {resp2.json().get('objectData').get('addressNote')}. {resp2.json().get('parcelData').get('areaValue')} кв.м."
                    contents.append(content)

        data_2d_dict["Лист1"] = [[title], ["Северная сторона", "Северо - Восточная сторона", "Восточная сторона",
                                         "Юго - Восточная сторона", "Южная сторона", "Юго - Западная сторона",
                                         "Западная сторона", "Северо - Западная сторона"], [contents[i] for i in range(0, 20)], [contents[i] for i in range(20, 40)],
                                                                                            [contents[i] for i in range(40, 50)], [contents[i] for i in range(50, 65)], [contents[i] for i in range(65, 80)],
                                                                                            [contents[i] for i in range(80, 93)], [contents[i] for i in range(93, 105)], [contents[i] for i in range(105, 120)]]
        pyexcel.save_book_as(bookdict=data_2d_dict, dest_file_name="data.xls")

class MainView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "mainapp/main.html", {})

    def post(self, request, *args, **kwargs):
        get_cadastral_data(request.POST.get("c_number"))
        with open("data.xls", "rb") as fh:
            response = HttpResponse(fh.read(), content_type='application/vnd.ms-excel;charset=utf-8')
            response['Content-Disposition'] = "attachment; filename=data.xls"
            return response