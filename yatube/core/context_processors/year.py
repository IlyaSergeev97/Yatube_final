from django.utils import timezone


def year(request):
    year = timezone.now()
    year = year.year
    return {'year': year}
