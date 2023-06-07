from options import settings


def convert_list_for_int_and_float(list_of_tuples):
    list_of_listet = []
    list_tuple = list(list_of_tuples)
    for items in list_tuple:
        list_items = list(items)
        clear_items = list_items[0]
        int_items = int(clear_items)
        list_of_listet.append(int_items)
    return list_of_listet


