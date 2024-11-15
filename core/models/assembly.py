from django.db import models
from django.conf import settings
from .aircraft import Aircraft


class Assembly(models.Model):
    aircraft_type = models.ForeignKey(
        Aircraft,
        on_delete=models.PROTECT,
        related_name='assemblies',
        verbose_name="Hava Aracı"
    )
    parts = models.ManyToManyField(
        'Part',
        related_name='assemblies',
        verbose_name="Parçalar",
        limit_choices_to={'is_used': False}
    )
    assembled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='assembled_aircrafts',
        verbose_name="Montaj Personeli"
    )
    assembled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Montaj Tarihi"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Montaj Notları"
    )
    is_complete = models.BooleanField(
        default=False,
        verbose_name="Montaj Tamamlandı mı?"
    )

    class Meta:
        verbose_name = "Montaj"
        verbose_name_plural = "Montajlar"
        ordering = ['-assembled_at']

    def __str__(self):
        return f"{self.aircraft_type} Montajı - {self.assembled_at}"
                    