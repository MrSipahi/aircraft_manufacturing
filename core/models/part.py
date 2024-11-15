from django.db import models, transaction
from django.conf import settings
from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .inventory import Inventory


class PartType(models.Model):
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Parça Tipi Adı"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi"
    )
    
    class Meta:
        verbose_name = "Parça Tipi"
        verbose_name_plural = "Parça Tipleri"
        ordering = ['name']

    def __str__(self):
        return self.name

class Part(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Parça Adı"
    )
    type = models.ForeignKey(
        PartType,
        on_delete=models.PROTECT,
        related_name='parts',
        verbose_name="Parça Tipi"
    )
    aircraft_type = models.ForeignKey(
        'Aircraft',
        on_delete=models.CASCADE,
        related_name='parts',
        verbose_name="Hava Aracı"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='produced_parts',
        verbose_name="Üreten Personel"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Üretim Tarihi"
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name="Kullanıldı mı?"
    )

    class Meta:
        verbose_name = "Parça"
        verbose_name_plural = "Parçalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.aircraft_type}"




# Yeni parça oluşturulduğunda veya güncellendiğinde envanteri günceller
@receiver(post_save, sender=Part)
def update_inventory_on_save(sender, instance, created, **kwargs):
    with transaction.atomic():
        if created:
            # Yeni parça eklendiğinde envanteri güncelle
            inventory, _ = Inventory.objects.get_or_create(
                part_type=instance.type,
                aircraft_type=instance.aircraft_type
                )
            inventory.quantity += 1
            inventory.save()

        elif instance.is_used:
            # Parça kullanıldı olarak işaretlendiyse envanteri azalt
            inventory = Inventory.objects.get(
                part_type=instance.type,
                aircraft_type=instance.aircraft_type
                )
            inventory.quantity -= 1
            inventory.save()




# Parça silindiğinde envanteri günceller
@receiver(post_delete, sender=Part)
def update_inventory_on_delete(sender, instance, **kwargs):
    if not instance.is_used:
        with transaction.atomic():
            # Kullanılmamış parça silindiğinde envanteri güncelle
            inventory = Inventory.objects.get(
                part_type=instance.type,
                aircraft_type=instance.aircraft_type
                )
            inventory.quantity -= 1
            inventory.save()




