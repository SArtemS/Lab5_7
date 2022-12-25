import json
import pandas


class BaseCurrenciesList():

    def get_currencies(self, currencies_ids_lst: list) -> dict:
        pass


class CurrenciesList(BaseCurrenciesList):
    """
        aka ConcreteComponent
    """

    def __init__(self, lst=None):
        self._link = 'http://www.cbr.ru/scripts/XML_daily.asp'
        self._currencies_IDs = lst

    def get_list(self):
        import requests
        from xml.etree import ElementTree as ET
        cur_res_str = requests.get(self._link)
        root = ET.fromstring(cur_res_str.content)
        valutes = root.findall("Valute")
        return valutes

    def get_valute(self, vcount):
        valute = {}
        valute_cur_name, valute_cur_val = vcount.find(
            'Name').text, vcount.find('Value').text
        valute_charcode = vcount.find('CharCode').text
        valute_cur_val = float(valute_cur_val.replace(
            ',', '.'))  # Правильный формат значения валюты
        valute[valute_charcode] = (valute_cur_name,
                                   format(valute_cur_val, '.2f'))
        return valute

    @property
    def get_currencies(self):
        result = []
        if self._currencies_IDs:
            for _v in self.get_list():
                if _v.get('ID') in self._currencies_IDs:
                    result.append(self.get_valute(_v))
        return result


class Decorator(BaseCurrenciesList):
    """
    aka Decorator из примера паттерна
    """

    __wrapped_object: BaseCurrenciesList = None

    def __init__(self, currencies_lst: BaseCurrenciesList):
        self.__wrapped_object = currencies_lst

    @property
    def wrapped_object(self) -> str:
        return self.__wrapped_object

    def get_currencies(self) -> dict:
        return self.__wrapped_object.get_currencies


class ConcreteDecoratorJSON(Decorator):

    def get_currencies(self) -> str:  # JSON
        return json.dumps(self.wrapped_object.get_currencies,
                          indent=4,
                          ensure_ascii=False)


class ConcreteDecoratorCSV(Decorator):

    def get_currencies(self) -> dict:
        currencies = self.wrapped_object.get_currencies
        curr_keys = []
        curr_values = []
        for currency in currencies:
            curr_keys.extend(list(currency.keys()))
            curr_values.extend(list(currency.values()))
        df = pandas.Series(data=curr_values, index=curr_keys)
        return df

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.__class__}:{self.name}"


def show_currencies(currencies: BaseCurrenciesList):
    """
       aka client_code() 
    """

    print(currencies.get_currencies)


if __name__ == "__main__":
    curlistdict = CurrenciesList([
        'R01035', 'R01200', 'R01235', 'R01239', 'R01335', 'R01375', 'R01565',
        'R01700J', 'R01760', 'R01820'
    ])
    print("Данные в виде списка словарей:")
    show_currencies(curlistdict)

    print("\nJSON-версия:")

    wrappedcurlist = Decorator(curlistdict)
    wrappedcurlist_json = ConcreteDecoratorJSON(curlistdict)
    json_res = wrappedcurlist_json.get_currencies()
    print(json_res)
    with open('currencies_json.json', 'w', encoding='utf-8') as f:
        f.write(json_res)

    print("Данные успешно записаны в JSON файл!\n\nCSV-версия:")

    wrappedcurlist_csv = ConcreteDecoratorCSV(curlistdict)
    csv_res = wrappedcurlist_csv.get_currencies()
    print(csv_res)
    csv_res.to_csv("currencies_csv.csv", sep=' ', header=False)
    print("Данные успешно записаны в CSV файл!")
