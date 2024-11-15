# core/models/inventory.py
from django.db import models
from django.core.validators import MinValueValidator


class Inventory(models.Model):
    part_type = models.ForeignKey(
        'PartType',
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name="Parça Tipi"
    )
    aircraft_type = models.ForeignKey(
        'Aircraft',
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name="Hava Aracı"
    )
    quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Mevcut Adet"
    )
    minimum_quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Minimum Adet"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Son Güncelleme"
    )

    class Meta:
        verbose_name = "Envanter"
        verbose_name_plural = "Envanter"
        unique_together = ['part_type', 'aircraft_type']

    def __str__(self):
        return f"{self.aircraft_type} - {self.part_type} ({self.quantity})"

