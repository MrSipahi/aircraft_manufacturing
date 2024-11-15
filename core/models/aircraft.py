from django.db import models




class Aircraft(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Hava Aracı Adı"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi"
    )
    
    class Meta:
        verbose_name = "Hava Aracı"
        verbose_name_plural = "Hava Araçları"

    def __str__(self):
        return self.name

class AircraftRequirement(models.Model):
    aircraft_type = models.ForeignKey(
        Aircraft,
        on_delete=models.CASCADE,
        related_name='requirements',
        verbose_name="Hava Aracı"
    )
    part_type = models.ForeignKey(
        'PartType',
        on_delete=models.PROTECT,
        related_name='required_for_aircrafts',
        verbose_name="Parça Tipi"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Gerekli Adet"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notlar"
    )

    class Meta:
        verbose_name = "Hava Aracı Gereksinimi"
        verbose_name_plural = "Hava Aracı Gereksinimleri"
        unique_together = ['aircraft_type', 'part_type']  # Bir uçak tipi için bir parça tipi yalnızca bir kez tanımlanabilir
        ordering = ['aircraft_type', 'part_type']

    def __str__(self):
        return f"{self.aircraft_type} - {self.part_type} ({self.quantity} adet)"



