// CSRF-токен
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Рендер строки альбома в списке
function renderAlbumRow(album) {
    const checked = album.has_post ? 'checked' : '';
    return `
        <label class="flex items-center gap-3 px-3 py-3 rounded-lg
                      hover:bg-surface-700 cursor-pointer transition group">
            <input type="checkbox"
                   class="album-toggle w-5 h-5 rounded accent-accent-600 cursor-pointer"
                   data-album-id="${album.id}"
                   ${checked}>
            <div class="flex-1 min-w-0">
                <div class="text-ink-100 font-medium truncate">${album.title}</div>
                <div class="text-ink-500 text-xs">
                    ${album.posts_count} постов
                    ${album.is_public ? '' : '· 🔒 Приватный'}
                </div>
            </div>
        </label>
    `;
}

// Загрузка списка альбомов
async function loadAlbums(postId) {
    const list = document.getElementById('album-modal-list');
    list.innerHTML = '<p class="text-ink-500 text-sm text-center py-6">Загрузка...</p>';

    try {
        const response = await fetch(`/albums/api/list/?post=${postId}`);
        if (!response.ok) throw new Error('Ошибка загрузки');
        const data = await response.json();

        if (data.albums.length === 0) {
            list.innerHTML = `
                <p class="text-ink-500 text-sm text-center py-6">
                    У тебя пока нет альбомов.<br>Создай первый ниже 👇
                </p>
            `;
            return;
        }

        list.innerHTML = data.albums.map(renderAlbumRow).join('');
        list.querySelectorAll('.album-toggle').forEach(bindToggle);
    } catch (err) {
        console.error(err);
        list.innerHTML = '<p class="text-red-400 text-sm text-center py-6">Ошибка загрузки</p>';
    }
}

// Обработка клика по чекбоксу
function bindToggle(checkbox) {
    checkbox.addEventListener('change', async (e) => {
        const albumId = checkbox.dataset.albumId;
        const postId = document.getElementById('album-modal').dataset.postId;

        checkbox.disabled = true;

        try {
            const response = await fetch('/albums/api/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ album_id: albumId, post_id: postId }),
            });

            if (!response.ok) throw new Error('Ошибка');
            const data = await response.json();
            checkbox.checked = data.has_post;

            // Обновляем счётчик постов в подписи
            const subtitle = checkbox.parentElement.querySelector('.text-xs');
            subtitle.textContent = subtitle.textContent.replace(
                /^\d+/,
                data.posts_count
            );
        } catch (err) {
            console.error(err);
            // Откат — возвращаем как было
            checkbox.checked = !checkbox.checked;
        } finally {
            checkbox.disabled = false;
        }
    });
}

// Создание нового альбома
async function createAlbum() {
    const input = document.getElementById('album-modal-new-title');
    const btn = document.getElementById('album-modal-new-create');
    const title = input.value.trim();

    if (!title) {
        input.focus();
        return;
    }

    const postId = document.getElementById('album-modal').dataset.postId;
    btn.disabled = true;
    btn.textContent = '...';

    try {
        const response = await fetch('/albums/api/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ title, post_id: postId, is_public: true }),
        });

        if (!response.ok) throw new Error('Ошибка');
        const album = await response.json();

        // Добавляем новую строку в начало списка
        const list = document.getElementById('album-modal-list');
        // Если раньше было "нет альбомов" — очищаем
        if (list.querySelector('.text-center')) list.innerHTML = '';

        list.insertAdjacentHTML('afterbegin', renderAlbumRow(album));
        const newCheckbox = list.querySelector('.album-toggle');
        bindToggle(newCheckbox);

        input.value = '';
    } catch (err) {
        console.error(err);
        alert('Не удалось создать альбом');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Создать';
    }
}

// Открытие/закрытие модалки
function initAlbumModal() {
    const btn = document.getElementById('save-to-album-btn');
    const modal = document.getElementById('album-modal');
    if (!btn || !modal) return;

    const close = document.getElementById('album-modal-close');
    const postId = modal.dataset.postId;

    btn.addEventListener('click', () => {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';   // блокируем скролл body
        loadAlbums(postId);
    });

    function hideModal() {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }

    close.addEventListener('click', hideModal);

    // Клик по фону — закрыть
    modal.addEventListener('click', (e) => {
        if (e.target === modal) hideModal();
    });

    // Esc — закрыть
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
            hideModal();
        }
    });

    // Создание нового альбома
    document.getElementById('album-modal-new-create').addEventListener('click', createAlbum);
    document.getElementById('album-modal-new-title').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); createAlbum(); }
    });
}

document.addEventListener('DOMContentLoaded', initAlbumModal);