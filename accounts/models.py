from django.db import models
from django.contrib.auth.models import AbstractUser

class TeamPermission(models.Model):
    """Takım yetkileri için özel model"""
    class PermissionTypes(models.TextChoices):
        VIEW_INVENTORY = 'view_inventory', 'Envanter Görüntüleme'
        MANAGE_INVENTORY = 'manage_inventory', 'Envanter Yönetimi'

        VIEW_ASSEMBLY = 'view_assembly', 'Montaj Görüntüleme'
        MANAGE_ASSEMBLY = 'manage_assembly', 'Montaj Yönetimi'

        VIEW_TEAMS = 'view_teams', 'Takım Görüntüleme'
        MANAGE_TEAMS = 'manage_teams', 'Takım Yönetimi'
        
        VIEW_USERS = 'view_users', 'Kullanıcı Görüntüleme'
        MANAGE_USERS = 'manage_users', 'Kullanıcı Yönetimi'
        
        VIEW_PART = 'view_part', 'Parça Görüntüleme'
        CREATE_PART = 'create_part', 'Parça Oluşturma'
        UPDATE_PART = 'update_part', 'Parça Güncelleme'
        DELETE_PART = 'delete_part', 'Parça Silme'


    
    name = models.CharField(
        max_length=50,
        choices=PermissionTypes.choices,
        unique=True,
        verbose_name="Yetki Adı"
    )
    description = models.CharField(
        max_length=200,
        verbose_name="Açıklama"
    )

    class Meta:
        verbose_name = "Takım Yetkisi"
        verbose_name_plural = "Takım Yetkileri"

    def __str__(self):
        return self.get_name_display()

class Team(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Takım Adı"
    )
    part_type = models.ForeignKey(
        'core.PartType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teams',
        verbose_name="Sorumlu Olduğu Parça Tipi"
    )
    is_assembly_team = models.BooleanField(
        default=False,
        verbose_name="Montaj Takımı mı?"
    )
    permissions = models.ManyToManyField(
        TeamPermission,
        verbose_name="Takım Yetkileri",
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi"
    )

    # Yetkileri cachelemek için özel alan
    _permission_cache = None

    class Meta:
        verbose_name = "Takım"
        verbose_name_plural = "Takımlar"
        unique_together = ['part_type', 'is_assembly_team']

    def __str__(self):
        return "Montaj Takımı" if self.is_assembly_team else f"{self.name}"

    def cache_permissions(self):
        if self._permission_cache is None:
            self._permission_cache = set(self.permissions.values_list('name', flat=True))
        return self._permission_cache

    def has_permission(self, permission_name):
        """Takımın belirli bir yetkiye sahip olup olmadığını kontrol eder"""
        return permission_name in self.cache_permissions()

class CustomUser(AbstractUser):
    team = models.ForeignKey(
        'Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        verbose_name="Takım",
        db_index=True
    )

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"
        
    def __str__(self):
        team_info = str(self.team) if self.team else "Takım Atanmamış"
        return f"{self.get_full_name()} - {team_info}"

    def has_team_permission(self, permission_name) -> bool:
        """Kullanıcının takım yetkisine sahip olup olmadığını kontrol eder"""
        if self.is_superuser:
            return True
        if not hasattr(self, 'team') or not self.team:
            return False
        return permission_name in [perm.name for perm in self.team.permissions.all()]

    def can_produce_part(self, part_type) -> bool:
        """Kullanıcının verilen parça tipini üretip üretemeyeceğini kontrol eder"""
        if self.is_superuser:
            return True
        if not hasattr(self, 'team') or not self.team:
            return False
        if self.team.is_assembly_team:
            return False
        return self.team.part_type_id == part_type.id

    def can_assemble(self) -> bool:
        """Kullanıcının montaj yapıp yapamayacağını kontrol eder"""
        if self.is_superuser:
            return True
        if not hasattr(self, 'team') or not self.team:
            return False
        return self.team.is_assembly_team

    @property
    def part_type(self):
        """Kullanıcının takımının sorumlu olduğu parça tipini döndürür"""
        if not hasattr(self, 'team') or not self.team or self.team.is_assembly_team:
            return None
        return self.team.part_type

