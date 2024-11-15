# Hava Aracı Üretim Sistemi

## Proje Detayları

### Uygulama Hakkında

Bu proje, uçak üretim sürecini yöneten bir web uygulamasıdır. Sistem, parça üretiminden montajına kadar tüm süreci takip eder ve her aşamada stok kontrolü yaparak eksik parçalar konusunda uyarır.

### Temel Özellikler
- **Takım Bazlı Yetkilendirme**: Her takım sadece kendi sorumlu olduğu parçaları üretebilir.
- **Parça-Uçak Uyumluluğu**: Her parça belirli bir uçak modeli için üretilir ve sadece o modelde kullanılabilir.
- **Stok Takibi**: Anlık stok takibi ve eksik parça uyarı sistemi.
- **Montaj Yönetimi**: Uyumlu parçalarla uçak montajı ve parça kullanım takibi.

### Teknik Özellikler
- **Backend**: Django Rest Framework, PostgreSQL
- **Frontend**: Bootstrap, DataTables (server-side processing)
- **API Dokümantasyonu**: Swagger UI
- **Testler**: Django test suite ve coverage raporları
- **Deployment**: Docker ve Docker Compose
- **Logging**: Detaylı sistem ve kullanıcı logları

### Proje Yapısı
- **Modüler Tasarım**: Core ve Accounts apps
- **Clean Architecture**: Services, Models, Views katmanlı mimari
- **Veritabanı**: İlişkisel tablo yapısı ve database constraints
- **Permission System**: Team-based custom permission yapısı


## Ekran Görüntüleri

![Envanter Takibi](https://raw.githubusercontent.com/MrSipahi/aircraft_manufacturing/refs/heads/main/SS/Envanter.png)
*Envanter Listesi ve Eksik parça gösterim ekranı*

![Parça Listesi](https://github.com/MrSipahi/aircraft_manufacturing/blob/main/SS/part.png?raw=true)
*Parça Listesi*

![Montaj oluşturma](https://raw.githubusercontent.com/MrSipahi/aircraft_manufacturing/refs/heads/main/SS/assembly_create.png)
*Montaj oluşturma ve validasyon işlemleri*

![Montaj Listesi](https://raw.githubusercontent.com/MrSipahi/aircraft_manufacturing/refs/heads/main/SS/assembly.png)
*Montaj Listesi*

![Kullanıcı Listesi](https://raw.githubusercontent.com/MrSipahi/aircraft_manufacturing/refs/heads/main/SS/users.png)
*Kullanıcı listesi ve oluşturma ekranı*



## Kurulum

## Geliştirme Ortamında Çalıştırma

1. Sanal ortam oluşturun:
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

2. Gereksinimleri yükleyin:
```bash
pip install -r requirements.txt
```

3. PostgreSQL veritabanı oluşturun ve .env dosyasını düzenleyin:
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

4. Veritabanı migrasyonlarını ve başlangıç verilerini yükleyin:
```bash
python manage.py migrate
python manage.py setup_initial_data  # Takımlar, kullanıcılar ve örnek veriler
```

5. Geliştirme sunucusunu başlatın:
```bash
python manage.py runserver
```

## Prod Ortamında Çalıştırma (Docker)

1. Docker ve Docker Compose yükleyin

2. .env dosyasını oluşturun:
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

3. Sistemi başlatın:
```bash
docker-compose up --build
```

## .env Yapılandırması

```env
# Django Admin Kullanıcısı
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123

# Örnek Montaj Kullanıcısı
DEFAULT_MONTAJ_USER_USERNAME=montaj
DEFAULT_MONTAJ_USER_EMAIL=montaj@example.com  
DEFAULT_MONTAJ_USER_PASSWORD=montaj123

# Veritabanı Ayarları
POSTGRES_DB= aircraft_manufacturing
POSTGRES_USER=django_user
POSTGRES_PASSWORD=django_password
POSTGRES_HOST=

# Diğer Ayarlar
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DEBUG=True
```

setup_initial_data komutu .env dosyasındaki bilgileri kullanarak:
- Admin kullanıcısı
- Montaj kullanıcısı
- Takımlar (Montaj, Kanat, Gövde, Aviyonik, Kuyruk)
- Parça tipleri ve gereksinimler
- Örnek hava araçları

oluşturur.

## Test

Testleri çalıştırmak için:
```bash
docker-compose exec web python manage.py core.tests

# Covarege raporu için
docker-compose exec web coverage run manage.py test
docker-compose exec web coverage html
# coverage/index.html dosyasını tarayıcıda açın
```



## API Dokümantasyonu

Swagger dokümantasyonuna `/swagger/` adresinden erişilebilir.


