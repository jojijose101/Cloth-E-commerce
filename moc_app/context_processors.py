from moc_app.models import Category


def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)
