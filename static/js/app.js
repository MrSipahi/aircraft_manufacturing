

$(document).ready(function() {
    // Logout butonuna tıklanırsa
    $('#logout-button').on('click', function(event) {
        event.preventDefault();  // Sayfanın yenilenmesini engelle
        
        // Logout işlemi için AJAX isteği gönder
        $.ajax({
            url: '/accounts/logout/',  // Logout işleminin yapılacağı URL
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')  // CSRF token'ı başlıkta gönder
            },
            success: function(response) {
                // Çıkış işlemi başarılıysa kullanıcıyı login sayfasına yönlendir
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/accounts/login/';
            },
            error: function(xhr, errmsg, err) {
                // Hata durumu
                alert('Logout işleminde bir hata oluştu: ' + errmsg);
            }
        });
    });

    // CSRF token'ı almak için yardımcı fonksiyon
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});