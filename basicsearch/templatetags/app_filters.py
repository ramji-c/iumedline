from django import template

register = template.Library()


@register.filter(name='inc')
def inc_page_num(page_num):
    print(type(page_num))
    return int(page_num) + 1


@register.filter(name='dec')
def dec_page_num(page_num):
    print(type(page_num))
    return page_num - 1