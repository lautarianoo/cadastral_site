from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
import pyexcel
import random
from sele import parsing_cadastral
import openpyxl

def get_cadastral_data(cadastral):
    DATA = parsing_cadastral(cadastral)

    directions = ["Северная сторона", "Северо - Восточная сторона", "Восточная сторона", "Юго - Восточная сторона",
                  "Южная сторона", "Юго - Западная сторона", "Западная сторона", "Северо - Западная сторона"]
    wb = openpyxl.load_workbook("data.xlsx")
    sheet = wb["Лист1"]
    sheet.delete_cols(0, 100)
    sheet["A1"] = f"Объект ОНВ расположен по адресу: {DATA.get('main_object').get('address')}, участок с кадастровым номером: {cadastral} площадь {DATA.get('main_object').get('square')} и окружен:"
    i = 0
    for cellObj in sheet['A2':'H2']:
        for cell in cellObj:
            cell.value = directions[i]
            i += 1
    n = 3
    ne = 3
    e = 3
    se = 3
    s = 3
    sw = 3
    w = 3
    nw = 3
    for cad in DATA.get("objects"):
        if cad.get("direction") == "north":
            sheet[f"A{n}"] = f"{cad.get('cadastral_num')}, {cad.get('address')}, {cad.get('square')}. {cad.get('task')}"
            n += 1
        if cad.get("direction") == "northeast":
            sheet[f"B{ne}"] = f"{cad.get('cadastral_num')}, {cad.get('address')}, {cad.get('square')}. {cad.get('task')}"
            ne += 1
        if cad.get("direction") == "east":
            sheet[f"C{e}"] = f"{cad.get('cadastral_num')}, {cad.get('address')}, {cad.get('square')}. {cad.get('task')}"
            e += 1
        if cad.get("direction") == "southeastern":
            sheet[f"D{se}"] = f"{cad.get('cadastral_num')}, {cad.get('address')}, {cad.get('square')}. {cad.get('task')}"
            se += 1
        if cad.get("direction") == "south":
            sheet[f"E{s}"] = f"{cad.get('cadastral_num')}, {cad.get('address')}, {cad.get('square')}. {cad.get('task')}"
            s += 1
        if cad.get("direction") == "southwest":
            sheet[f"F{sw}"] = f"{cad.get('cadastral_num')}, {cad.get('address')}, {cad.get('square')}. {cad.get('task')}"
            sw += 1
        if cad.get("direction") == "west":
            sheet[f"G{w}"] = f"{cad.get('cadastral_num')}, {cad.get('address')}, {cad.get('square')}. {cad.get('task')}"
            w += 1
        if cad.get("direction") == "northwest":
            sheet[f"H{nw}"] = f"{cad.get('cadastral_num')}, {cad.get('address')}, {cad.get('square')}. {cad.get('task')}"
            nw += 1
    wb.save("data.xlsx")

class MainView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "mainapp/main.html", {})

    def post(self, request, *args, **kwargs):
        get_cadastral_data(request.POST.get("c_number"))
        with open("data.xlsx", "rb") as fh:
            response = HttpResponse(fh.read(), content_type='application/vnd.ms-excel;charset=utf-8')
            response['Content-Disposition'] = "attachment; filename=data.xls"
            return response
