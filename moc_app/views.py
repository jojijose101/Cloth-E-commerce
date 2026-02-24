from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from moc_app.models import Category, Product


# Create your views here.
def index(request,c_slug=None):
    c_page = None
    products = None
    if c_slug != None:
        c_page = get_object_or_404(Category,slug= c_slug)
        products_list = Product.objects.all().filter(category=c_page)
    else:
        products_list = Product.objects.all()
    pagenator = Paginator(products_list,8)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page=1
    try:
        products = pagenator.page(page)
    except(InvalidPage,EmptyPage):
        products = pagenator.page(pagenator.num_pages)


    return render(request,'index.html',{'category':c_page,'products':products})


def product(request,c_slug,p_slug):
    try:
        product = Product.objects.get(category__slug=c_slug, slug=p_slug)
    except Exception as e:
        raise e

    return render(request,'product.html',{'product':product})