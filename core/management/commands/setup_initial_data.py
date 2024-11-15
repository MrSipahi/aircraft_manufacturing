from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Team, TeamPermission
from core.models.part import PartType, Part
from core.models.aircraft import Aircraft

from dotenv import load_dotenv
import os

class Command(BaseCommand):
    help = 'Initial verileri yükler'

    def handle(self, *args, **options):
        self.stdout.write('Initial veriler yükleniyor...')
        
        load_dotenv()
        

        # Parça tiplerini oluştur
        part_types = {
            'govde': PartType.objects.get_or_create(name="Gövde")[0],
            'kanat': PartType.objects.get_or_create(name="Kanat")[0],
            'aviyonik': PartType.objects.get_or_create(name="Aviyonik")[0],
            'kuyruk': PartType.objects.get_or_create(name="Kuyruk")[0]
        }
        self.stdout.write(self.style.SUCCESS('Parça tipleri oluşturuldu'))

        # Takım yetkilerini oluştur
        # Montaj yetkileri
        montaj_permissions = {
            'view_assembly': TeamPermission.objects.get_or_create(
                name=TeamPermission.PermissionTypes.VIEW_ASSEMBLY,
                defaults={'description': "Montaj Görüntüleme Yetkisi"}
            )[0],
            'manage_assembly': TeamPermission.objects.get_or_create(
                name=TeamPermission.PermissionTypes.MANAGE_ASSEMBLY,
                defaults={'description': "Montaj Yönetim Yetkisi"}
            )[0],
        }

        # Parça yetkileri
        part_permissions = {
            'view_part': TeamPermission.objects.get_or_create(
                name=TeamPermission.PermissionTypes.VIEW_PART,
                defaults={'description': "Parça Görüntüleme Yetkisi"}
            )[0],
            'create_part': TeamPermission.objects.get_or_create(
                name=TeamPermission.PermissionTypes.CREATE_PART,
                defaults={'description': "Parça Oluşturma Yetkisi"}
            )[0],
            'update_part': TeamPermission.objects.get_or_create(
                name=TeamPermission.PermissionTypes.UPDATE_PART,
                defaults={'description': "Parça Güncelleme Yetkisi"}
            )[0],
            'delete_part': TeamPermission.objects.get_or_create(
                name=TeamPermission.PermissionTypes.DELETE_PART,
                defaults={'description': "Parça Silme Yetkisi"}
            )[0],
            'view_inventory': TeamPermission.objects.get_or_create(
                name=TeamPermission.PermissionTypes.VIEW_INVENTORY,
                defaults={'description': "Envanter Görüntüleme Yetkisi"}
            )[0],
        }

        other_permissions = {
           
            'manage_inventory': TeamPermission.objects.get_or_create(
                name=TeamPermission.PermissionTypes.MANAGE_INVENTORY,
                defaults={'description': "Montaj Yönetim Yetkisi"}
            )[0],
            'manage_users': TeamPermission.objects.get_or_create(
                name=TeamPermission.PermissionTypes.MANAGE_USERS,
                defaults={'description': "Kullanıcı Yönetim Yetkisi"}
            )[0],
        }
        self.stdout.write(self.style.SUCCESS('Yetkiler oluşturuldu'))

        # Takımları oluştur
        assembly_team = Team.objects.get_or_create(
            name="Montaj Takımı",
            defaults={'is_assembly_team': True}
        )[0]

        kanat_team = Team.objects.get_or_create(
            name="Kanat Takımı",
            defaults={'is_assembly_team': False, 'part_type': part_types['kanat']}
        )[0]

        govde_team = Team.objects.get_or_create(
            name="Gövde Takımı",
            defaults={'is_assembly_team': False, 'part_type': part_types['govde']}
        )[0]

        aviyonik_team = Team.objects.get_or_create(
            name="Aviyonik Takımı",
            defaults={'is_assembly_team': False, 'part_type': part_types['aviyonik']}
        )[0]

        kuyruk_team = Team.objects.get_or_create(
            name="Kuyruk Takımı",
            defaults={'is_assembly_team': False, 'part_type': part_types['kuyruk']}
        )[0]

        
        # Takımlara yetkileri ekle
        assembly_team.permissions.add(*montaj_permissions.values())
        kanat_team.permissions.add(*part_permissions.values())
        govde_team.permissions.add(*part_permissions.values())
        aviyonik_team.permissions.add(*part_permissions.values())
        kuyruk_team.permissions.add(*part_permissions.values())



        self.stdout.write(self.style.SUCCESS('Takımlar oluşturuldu'))

        # Superuser oluştur
        User = get_user_model()
        if not User.objects.filter(username=os.getenv('DJANGO_SUPERUSER_USERNAME')).exists():
            superuser = User.objects.create_superuser(
                username=os.getenv('DJANGO_SUPERUSER_USERNAME'),                
                email=os.getenv('DJANGO_SUPERUSER_EMAIL'),
                password=os.getenv('DJANGO_SUPERUSER_PASSWORD')
            )
            superuser.first_name = 'Super'
            superuser.last_name = 'User'
            superuser.team = govde_team
            superuser.save()
            self.stdout.write(self.style.SUCCESS('Superuser oluşturuldu'))

        # Default kullanıcılar oluştur
        default_users = [
            {
                'username': os.getenv('DEFAULT_MONTAJ_USER_USERNAME'),
                'first_name': 'Montaj',
                'last_name': 'Kullanıcısı',
                'email': os.getenv('DEFAULT_MONTAJ_USER_EMAIL'),
                'password': os.getenv('DEFAULT_MONTAJ_USER_PASSWORD'),
                'team': assembly_team,
                'is_staff': True
            },
            {
                'username': "kanat_kullanici",
                'first_name': 'Kanat',
                'last_name': 'Kullanıcısı',
                'email': 'kanat@mail.com',
                'password': "kanat123",
                'team': kanat_team,
                'is_staff': True
            },
            {
                'username': "govde_kullanici",
                'first_name': 'Gövde',
                'last_name': 'Kullanıcısı',
                'email': 'govde@mail.com',
                'password': "govde123",
                'team': govde_team,
                'is_staff': True
            },
            {
                'username': "aviyonik_kullanici",
                'first_name': 'Aviyonik',
                'last_name': 'Kullanıcısı',
                'email': 'aviyonik@mail.com',
                'password': "aviyonik123",
                'team': aviyonik_team,
                'is_staff': True
            },
            {
                'username': "kuyruk_kullanici",
                'first_name': 'Kuyruk',
                'last_name': 'Kullanıcısı',
                'email': 'kuyruk@mail.com',
                'password': "kuyruk123",
                'team': kuyruk_team,
                'is_staff': True
            },
        ]

        for user_data in default_users:
            team = user_data.pop('team')
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(**user_data)
                user.team = team
                user.save()
        
        self.stdout.write(self.style.SUCCESS('Default kullanıcılar oluşturuldu'))

        # Uçak tiplerini oluştur
        aircraft_types = [
            "TB2",
            "TB3",
            "AKINCI",
            "KIZILELMA",
        ]

        for aircraft_name in aircraft_types:
            aircraft, created = Aircraft.objects.get_or_create(name=aircraft_name)
            if created:
                self.stdout.write(f'Uçak tipi oluşturuldu: {aircraft_name}')

        

        # Her uçak için gereksinimleri oluştur
        for aircraft in Aircraft.objects.all():
            requirements = {
                'gövde': aircraft.requirements.get_or_create(part_type=part_types['govde'], defaults={'quantity': 1})[0],
                'kanat': aircraft.requirements.get_or_create(part_type=part_types['kanat'], defaults={'quantity': 2})[0],
                'aviyonik': aircraft.requirements.get_or_create(part_type=part_types['aviyonik'], defaults={'quantity': 1})[0],
                'kuyruk': aircraft.requirements.get_or_create(part_type=part_types['kuyruk'], defaults={'quantity': 1})[0]
            }
            self.stdout.write(f'Gereksinimler oluşturuldu: {aircraft.name}')

        self.stdout.write(self.style.SUCCESS('Tüm initial veriler başarıyla yüklendi'))