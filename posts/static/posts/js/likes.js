// CSRF-токен из куки
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Универсальная отправка лайка
async function sendLike(url) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        if (!response.ok) {
            if (response.status === 403 || response.redirected) {
                window.location.href = '/accounts/login/';
            }
            return null;
        }

        return await response.json();
    } catch (err) {
        console.error('Ошибка лайка:', err);
        return null;
    }
}

// Обновление внешнего вида кнопки
function updateLikeButton(btn, data) {
    const heart = btn.querySelector('.heart');
    const count = btn.querySelector('.count');

    count.textContent = data.count;
    btn.dataset.liked = data.liked ? 'true' : 'false';

    if (data.liked) {
        heart.classList.add('text-accent-500');
        btn.classList.add('border-accent-500', 'bg-accent-600/10');
    } else {
        heart.classList.remove('text-accent-500');
        btn.classList.remove('border-accent-500', 'bg-accent-600/10');
    }
}

// Красим уже лайкнутые при загрузке
function initLikes() {
    const buttons = document.querySelectorAll('.like-btn, .comment-like-btn, .feed-like-btn');

    buttons.forEach(btn => {
        // Стартовое состояние
        if (btn.dataset.liked === 'true') {
            btn.querySelector('.heart').classList.add('text-accent-500');
            btn.classList.add('border-accent-500', 'bg-accent-600/10');
        }

        // Клик
        btn.addEventListener('click', async (e) => {
            // Не даём клику провалиться в родительскую ссылку
            e.preventDefault();
            e.stopPropagation();

            const data = await sendLike(btn.dataset.url);
            if (data) updateLikeButton(btn, data);
        });
    });
}

// Запуск после загрузки DOM
document.addEventListener('DOMContentLoaded', initLikes);