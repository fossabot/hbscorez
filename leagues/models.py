import re

from django.conf import settings
from django.core import validators
from django.db import models
from django.urls import reverse

from districts.models import District


class Season(models.Model):
    start_year = models.PositiveIntegerField(unique=True, validators=[
        validators.MinValueValidator(1990),
        validators.MaxValueValidator(2050)])

    def __str__(self):
        return '{}/{}'.format(self.start_year, self.start_year + 1)


class League(models.Model):
    name = models.TextField()
    abbreviation = models.TextField()
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    bhv_id = models.IntegerField(unique=True)

    class Meta:
        unique_together = (('name', 'district'), ('abbreviation', 'district'))

    def __str__(self):
        return '{} {}'.format(self.name, self.season)

    def get_absolute_url(self):
        return reverse('leagues:detail', kwargs={'bhv_id': self.bhv_id})

    @staticmethod
    def build_source_url(bhv_id):
        return settings.ROOT_SOURCE_URL + 'Spielbetrieb/index.php?orgGrpID=1&all=1&score={}'.format(bhv_id)

    def source_url(self):
        return self.build_source_url(self.bhv_id)

    @staticmethod
    def is_youth_league(name):
        return re.search('MJ', name) \
               or re.search('WJ', name) \
               or re.search('Jugend', name) \
               or re.search('Mini', name)
