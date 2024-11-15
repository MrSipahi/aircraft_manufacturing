from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models.assembly import Assembly
from ..models.aircraft import Aircraft
from ..models.part import Part,PartType
from accounts.models import TeamPermission
from accounts.models import Team

class AssemblyTests(APITestCase):
    """
    Montaj sistemi için test suite'i.
    
    Test edilen temel işlevler:
    - Montaj oluşturma
    - Montaj listeleme
    - Montaj silme
    - İzin kontrolleri
    - Validasyon kuralları
    """

    def setUp(self):
        """
        Her test öncesi çalışacak hazırlık metodu.
        Test için gerekli örnek verileri oluşturur.
        """

        # Sistem kullanıcısı (superuser) oluşturma
        User = get_user_model()
        self.system_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

        # Takım yetkilerini oluştur
        self.permissions = {
            'view_assembly': TeamPermission.objects.create(
                name=TeamPermission.PermissionTypes.VIEW_ASSEMBLY,
                description="Montaj Görüntüleme Yetkisi"
            ),
            'manage_assembly': TeamPermission.objects.create(
                name=TeamPermission.PermissionTypes.MANAGE_ASSEMBLY,
                description="Montaj Yönetim Yetkisi"
            ),
            'view_part': TeamPermission.objects.create(
                name=TeamPermission.PermissionTypes.VIEW_PART,
                description="Parça Görüntüleme Yetkisi"
            ),
            'create_part': TeamPermission.objects.create(
                name=TeamPermission.PermissionTypes.CREATE_PART,
                description="Parça Oluşturma Yetkisi"
            ),
            'update_part': TeamPermission.objects.create(
                name=TeamPermission.PermissionTypes.UPDATE_PART,
                description="Parça Güncelleme Yetkisi"
            ),
            'delete_part': TeamPermission.objects.create(
                name=TeamPermission.PermissionTypes.DELETE_PART,
                description="Parça Silme Yetkisi"
            ),
        }

        # Takım oluşturma
        self.assembly_team = Team.objects.create(
            name="Montaj Takımı",
            is_assembly_team=True
        )
        
        # Montaj takımına yetkileri ekle
        self.assembly_team.permissions.add(
            self.permissions['view_assembly'],
            self.permissions['manage_assembly'],
            self.permissions['view_part'],
            self.permissions['create_part'],
            self.permissions['update_part'],
            self.permissions['delete_part']
        )

        # Test kullanıcısı oluşturma
        self.user_password = 'testpass123'
        self.user = User.objects.create_user(
            username='testuser',
            password=self.user_password,
            team=self.assembly_team
        )
        
        # Test için giriş yapma
        self.login_user()
        
        # Uçak tipi oluşturma
        self.aircraft = Aircraft.objects.create(
            name="Test Uçağı",
        )
        
       # Parça tipleri oluşturma
        self.part_types = {
            'gövde': PartType.objects.create(name="Gövde"),
            'kanat': PartType.objects.create(name="Kanat"),
            'aviyonik': PartType.objects.create(name="Aviyonik"),
            'kuyruk': PartType.objects.create(name="Kuyruk")
        }
        
        # Gereksinim tanımlama
        self.requirements = {
            'gövde': self.aircraft.requirements.create(part_type=self.part_types['gövde'], quantity=2),
            'kanat': self.aircraft.requirements.create(part_type=self.part_types['kanat'], quantity=2),
            'aviyonik': self.aircraft.requirements.create(part_type=self.part_types['aviyonik'], quantity=1),
            'kuyruk': self.aircraft.requirements.create(part_type=self.part_types['kuyruk'], quantity=1)
        }
        
        # Test parçaları oluşturma
        self.parts = []

         # 2 Gövde parçası
        for i in range(2):
            self.parts.append(Part.objects.create(
                type=self.part_types['gövde'],
                aircraft_type=self.aircraft,
                created_by=self.user,
                name=f"GVD-{i}"
            ))
        
        # 2 Kanat parçası
        for i in range(2):
            self.parts.append(Part.objects.create(
                type=self.part_types['kanat'],
                aircraft_type=self.aircraft,
                created_by=self.user,
                name=f"KNT-{i}"
            ))
        
        # 1 Aviyonik parçası
        self.parts.append(Part.objects.create(
            type=self.part_types['aviyonik'],
            aircraft_type=self.aircraft,
            created_by=self.user,
            name="AVY-0"
        ))
        
        # 1 Kuyruk parçası
        self.parts.append(Part.objects.create(
            type=self.part_types['kuyruk'],
            aircraft_type=self.aircraft,
            created_by=self.user,
            name="KYK-0"
        ))

    def login_user(self):
        """
        Test kullanıcısı için login işlemi yapar ve token alır.
        """
        url = reverse('login')
        data = {
            'username': self.user.username,
            'password': self.user_password
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('tokens' in response.data)
        
        # Access token'ı client'a ekle
        token = response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_assembly(self):
        """
        Yeni montaj oluşturma testi.
        URL: /assembly/ (POST)
        """
        url = reverse('assembly')
        data = {
            'aircraft_type': self.aircraft.id,
            'parts': [part.id for part in self.parts],
            'notes': 'Test montajı'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assembly.objects.count(), 1)
        
        # Parçaların kullanıldı olarak işaretlendiğini kontrol et
        for part in self.parts:
            part.refresh_from_db()
            self.assertTrue(part.is_used)

    def test_list_assemblies(self):
        """
        Montaj listesi görüntüleme testi.
        URL: /assembly/ (GET)
        """

        # Örnek montaj oluştur
        assembly = Assembly.objects.create(
            aircraft_type=self.aircraft,
            assembled_by=self.user,
            is_complete=True
        )
        assembly.parts.set(self.parts)
        
        url = reverse('assembly')
        # Datatable için 
        response_with_datatable = self.client.get(url, {'format': 'json'}, headers={'Content-Type': 'application/json'})
        # HTML render
        response_with_html = self.client.get(url)
        
        self.assertEqual(response_with_datatable.status_code, status.HTTP_200_OK)
        self.assertEqual(response_with_html.status_code, status.HTTP_200_OK)

    
    def test_detail_assemblies(self):
        """
        Montaj detay görüntüleme testi.
        URL: /assembly/{id} (GET)
        """

        # Örnek montaj oluştur
        assembly = Assembly.objects.create(
            aircraft_type=self.aircraft,
            assembled_by=self.user,
            is_complete=True
        )
        assembly.parts.set(self.parts)
        
        url = reverse('assembly_detail', args=[assembly.id])
        response = self.client.get(url, {'format': 'json'}, headers={'Content-Type': 'application/json'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_assembly(self):
        """
        Montaj silme testi.
        URL: /assembly/{id}/ (DELETE)
        """
        # Örnek montaj oluştur
        assembly = Assembly.objects.create(
            aircraft_type=self.aircraft,
            assembled_by=self.user,
            is_complete=True
        )
        assembly.parts.set(self.parts)
        
        url = reverse('assembly_detail', args=[assembly.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Assembly.objects.count(), 0)
        
        # Parçaların kullanılabilir duruma döndüğünü kontrol et
        for part in self.parts:
            part.refresh_from_db()
            self.assertFalse(part.is_used)

    def test_validation_rules(self):
        """
        Montaj validasyon kuralları testi.
        URL: /assembly/ (POST)
        """
        url = reverse('assembly')
        
        # Eksik parça ile montaj oluşturma denemesi
        data = {
            'aircraft_type': self.aircraft.id,
            'parts': [self.parts[0].id],  # Sadece bir motor
            'notes': 'Eksik parçalı montaj'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permission_check(self):
        """
        İzin kontrolleri testi.
        URL: /assembly/ (POST)
        """

        # Montaj yapamayan takım oluştur
        non_assembly_team = Team.objects.create(
            name="Test Takımı",
            is_assembly_team=False
        )
        
        # Kullanıcıyı montaj yapamayan takıma ata
        self.user.team = non_assembly_team
        self.user.save()
        
        url = reverse('assembly')
        data = {
            'aircraft_type': self.aircraft.id,
            'parts': [part.id for part in self.parts],
            'notes': 'İzinsiz montaj denemesi'
        }
        
        response = self.client.post(url, data, format='json')


        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)