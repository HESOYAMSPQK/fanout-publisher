// API конфигурация
const API_BASE = window.location.origin;

// DOM элементы
const videoForm = document.getElementById('videoForm');
const videoFileInput = document.getElementById('videoFile');
const fileLabel = document.getElementById('fileLabel');
const fileName = document.getElementById('fileName');
const uploadFormDiv = document.getElementById('uploadForm');
const uploadProgressDiv = document.getElementById('uploadProgress');
const resultDiv = document.getElementById('result');
const successResult = document.getElementById('successResult');
const errorResult = document.getElementById('errorResult');
const submitBtn = document.getElementById('submitBtn');
const submitText = document.getElementById('submitText');
const submitLoader = document.getElementById('submitLoader');

// Текущая выбранная платформа
let selectedPlatform = 'youtube';

// Обработка выбора файла
videoFileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = `📁 ${file.name} (${formatFileSize(file.size)})`;
        fileName.style.display = 'block';
        fileLabel.textContent = 'Файл выбран:';
        
        // Проверка размера файла (2 ГБ)
        if (file.size > 2 * 1024 * 1024 * 1024) {
            alert('⚠️ Файл слишком большой! Максимальный размер: 2 ГБ');
            videoFileInput.value = '';
            fileName.textContent = '';
            fileName.style.display = 'none';
            fileLabel.textContent = 'Выберите видео или перетащите сюда';
        }
    }
});

// Drag & Drop
const fileInputWrapper = document.querySelector('.file-input-wrapper');

fileInputWrapper.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileInputWrapper.style.borderColor = 'var(--secondary-color)';
    fileInputWrapper.style.background = 'rgba(6, 95, 212, 0.1)';
});

fileInputWrapper.addEventListener('dragleave', (e) => {
    e.preventDefault();
    fileInputWrapper.style.borderColor = 'var(--border-color)';
    fileInputWrapper.style.background = 'var(--bg-color)';
});

fileInputWrapper.addEventListener('drop', (e) => {
    e.preventDefault();
    fileInputWrapper.style.borderColor = 'var(--border-color)';
    fileInputWrapper.style.background = 'var(--bg-color)';
    
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('video/')) {
        videoFileInput.files = e.dataTransfer.files;
        const event = new Event('change');
        videoFileInput.dispatchEvent(event);
    } else {
        alert('⚠️ Пожалуйста, выберите видео файл');
    }
});

// Переключение между вкладками платформ
const platformTabs = document.querySelectorAll('.platform-tab');
const platformForms = document.querySelectorAll('.platform-form');

platformTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const platform = tab.dataset.platform;
        
        // Убираем active со всех вкладок и форм
        platformTabs.forEach(t => t.classList.remove('active'));
        platformForms.forEach(f => f.classList.remove('active'));
        
        // Добавляем active к выбранным
        tab.classList.add('active');
        document.getElementById(`${platform}-form`).classList.add('active');
        
        // Сохраняем выбранную платформу
        selectedPlatform = platform;
        
        // Обновляем текст кнопки
        updateSubmitButton();
    });
});

// Обновление текста кнопки
function updateSubmitButton() {
    const platformNames = {
        'youtube': 'YouTube',
        'vk': 'VK',
        'tiktok': 'TikTok'
    };
    submitText.textContent = `🚀 Загрузить на ${platformNames[selectedPlatform]}`;
}

// Показать ошибку валидации поля
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.classList.add('field-error');
        
        // Создаем или находим сообщение об ошибке
        let errorMsg = field.parentElement.querySelector('.error-message');
        if (!errorMsg) {
            errorMsg = document.createElement('div');
            errorMsg.className = 'error-message';
            field.parentElement.appendChild(errorMsg);
        }
        errorMsg.textContent = message;
        errorMsg.classList.add('show');
        
        // Скроллим к полю
        field.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Очистить ошибки валидации
function clearFieldErrors() {
    document.querySelectorAll('.field-error').forEach(field => {
        field.classList.remove('field-error');
    });
    document.querySelectorAll('.error-message.show').forEach(msg => {
        msg.classList.remove('show');
    });
}

// Сбор данных из формы в зависимости от платформы
function collectFormData(platform) {
    // Очищаем предыдущие ошибки
    clearFieldErrors();
    
    const formData = new FormData();
    const file = videoFileInput.files[0];
    
    if (!file) {
        alert('⚠️ Выберите видео файл');
        throw new Error('Выберите видео файл');
    }
    
    formData.append('video', file);
    formData.append('platforms', JSON.stringify([platform]));
    
    if (platform === 'youtube') {
        const title = document.getElementById('youtube-title').value.trim();
        const description = document.getElementById('youtube-description').value.trim();
        const tags = document.getElementById('youtube-tags').value.trim();
        const hashtags = document.getElementById('youtube-hashtags').value.trim();
        const privacy = document.getElementById('youtube-privacy').value;
        
        if (!title) {
            showFieldError('youtube-title', 'Это обязательное поле');
            throw new Error('Введите название видео для YouTube');
        }
        
        // Для YouTube добавляем хештеги к названию
        const fullTitle = hashtags ? `${title} ${hashtags}` : title;
        
        formData.append('title', fullTitle);
        formData.append('description', description);
        formData.append('tags', JSON.stringify(tags.split(',').map(t => t.trim()).filter(t => t)));
        formData.append('hashtags', ''); // Хештеги уже в названии
        formData.append('privacy', privacy);
        
    } else if (platform === 'vk') {
        const title = document.getElementById('vk-title').value.trim();
        const description = document.getElementById('vk-description').value.trim();
        const hashtags = document.getElementById('vk-hashtags').value.trim();
        const privacy = document.getElementById('vk-privacy').value;
        
        if (!title) {
            showFieldError('vk-title', 'Это обязательное поле');
            throw new Error('Введите название видео для VK');
        }
        
        // Для VK добавляем хештеги к описанию
        const fullDescription = hashtags ? `${description}\n\n${hashtags}`.trim() : description;
        
        formData.append('title', title);
        formData.append('description', fullDescription);
        formData.append('tags', JSON.stringify([]));
        formData.append('hashtags', ''); // Хештеги уже в описании
        formData.append('privacy', privacy);
        
    } else if (platform === 'tiktok') {
        const caption = document.getElementById('tiktok-caption').value.trim();
        const disableComment = document.getElementById('tiktok-disable-comment').checked;
        const disableDuet = document.getElementById('tiktok-disable-duet').checked;
        const disableStitch = document.getElementById('tiktok-disable-stitch').checked;
        const privacy = document.getElementById('tiktok-privacy').value;
        
        if (!caption) {
            showFieldError('tiktok-caption', 'Это обязательное поле! Введите текст для видео.');
            throw new Error('Введите текст видео (caption) для TikTok - это обязательное поле!');
        }
        
        console.log('TikTok caption length:', caption.length);
        console.log('TikTok caption:', caption);
        
        // Для TikTok используем caption как title (основное содержимое)
        formData.append('title', caption);
        formData.append('description', ''); // Всё в title
        formData.append('tags', JSON.stringify([]));
        formData.append('hashtags', ''); // Хештеги уже в caption
        formData.append('privacy', privacy);
        
        // Дополнительные параметры TikTok (можно передать через description если нужно)
        const tiktokSettings = {
            disable_comment: disableComment,
            disable_duet: disableDuet,
            disable_stitch: disableStitch
        };
        console.log('TikTok settings:', tiktokSettings);
    }
    
    return formData;
}

// Отправка формы
videoForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Показываем лоадер
    submitBtn.disabled = true;
    submitText.style.display = 'none';
    submitLoader.style.display = 'block';
    
    try {
        // Собираем данные формы
        const formData = collectFormData(selectedPlatform);
        
        // Показываем прогресс
        uploadFormDiv.style.display = 'none';
        uploadProgressDiv.style.display = 'block';
        
        // Загружаем файл с отслеживанием прогресса
        const response = await uploadWithProgress(formData);
        
        if (response.ok) {
            const result = await response.json();
            showSuccess(result);
            
            // Начинаем отслеживание статуса для всех submission_id
            if (result.submissions && result.submissions.length > 0) {
                result.submissions.forEach(sub => {
                    pollStatus(sub.submission_id);
                });
            }
        } else {
            let errorMessage = 'Ошибка при загрузке видео';
            try {
                const error = await response.json();
                // Обработка различных форматов ошибок
                if (typeof error === 'string') {
                    errorMessage = error;
                } else if (error.detail) {
                    errorMessage = error.detail;
                } else if (error.message) {
                    errorMessage = error.message;
                } else if (error.error) {
                    errorMessage = error.error;
                } else {
                    errorMessage = JSON.stringify(error);
                }
            } catch (e) {
                // Если не удалось распарсить JSON, используем текст ответа
                errorMessage = `Ошибка сервера: ${response.status} ${response.statusText}`;
            }
            showError(errorMessage);
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showError(`Ошибка: ${error.message || error}`);
    } finally {
        submitBtn.disabled = false;
        submitText.style.display = 'block';
        submitLoader.style.display = 'none';
    }
});

// Загрузка с прогрессом
async function uploadWithProgress(formData) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        
        // Прогресс загрузки
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                updateProgress(percentComplete, 'Загрузка файла...');
            }
        });
        
        // Завершение
        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve({
                    ok: true,
                    json: () => Promise.resolve(JSON.parse(xhr.responseText))
                });
            } else {
                resolve({
                    ok: false,
                    status: xhr.status,
                    statusText: xhr.statusText,
                    json: () => Promise.resolve(JSON.parse(xhr.responseText))
                });
            }
        });
        
        // Ошибка
        xhr.addEventListener('error', () => {
            reject(new Error('Ошибка сети'));
        });
        
        xhr.open('POST', `${API_BASE}/upload`);
        xhr.send(formData);
    });
}

// Обновление прогресса
function updateProgress(percent, status) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const statusText = document.getElementById('statusText');
    
    progressFill.style.width = `${percent}%`;
    progressText.textContent = `${Math.round(percent)}%`;
    statusText.textContent = status;
}

// Показать успех
function showSuccess(result) {
    uploadProgressDiv.style.display = 'none';
    resultDiv.style.display = 'block';
    successResult.style.display = 'block';
    errorResult.style.display = 'none';
    
    // Показываем информацию обо всех созданных заявках
    if (result.submissions && result.submissions.length > 0) {
        const submissionInfo = result.submissions.map(sub => 
            `<div><strong>${getPlatformName(sub.platform)}:</strong> <code>${sub.submission_id}</code></div>`
        ).join('');
        document.getElementById('submissionId').innerHTML = submissionInfo;
        document.getElementById('jobStatus').textContent = result.status || 'В очереди';
    } else {
        // Обратная совместимость
        document.getElementById('submissionId').textContent = result.submission_id || 'Н/Д';
        document.getElementById('jobStatus').textContent = result.status || 'В очереди';
    }
    
    // Обновляем список
    loadRecentJobs();
}

// Показать ошибку
function showError(message) {
    uploadProgressDiv.style.display = 'none';
    resultDiv.style.display = 'block';
    successResult.style.display = 'none';
    errorResult.style.display = 'block';
    
    document.getElementById('errorMessage').textContent = message;
}

// Сброс формы
function resetForm() {
    videoForm.reset();
    fileName.textContent = '';
    fileName.style.display = 'none';
    fileLabel.textContent = 'Выберите видео или перетащите сюда';
    
    uploadFormDiv.style.display = 'block';
    uploadProgressDiv.style.display = 'none';
    resultDiv.style.display = 'none';
    
    // Сбрасываем поля TikTok на дефолтные значения
    document.getElementById('tiktok-caption').value = '';
    document.getElementById('tiktok-disable-comment').checked = false;
    document.getElementById('tiktok-disable-duet').checked = false;
    document.getElementById('tiktok-disable-stitch').checked = false;
}

// Отслеживание статуса публикации
async function pollStatus(submissionId) {
    let attempts = 0;
    const maxAttempts = 20; // 10 минут (30 сек * 20)
    
    const interval = setInterval(async () => {
        attempts++;
        
        try {
            const response = await fetch(`${API_BASE}/api/status/${submissionId}`);
            
            if (response.ok) {
                const data = await response.json();
                const statusBadge = document.getElementById('jobStatus');
                
                // Обновляем статус
                statusBadge.textContent = getStatusText(data.status);
                statusBadge.className = `badge badge-${data.status.toLowerCase()}`;
                
                if (data.status === 'COMPLETED') {
                    clearInterval(interval);
                    
                    // Показываем ссылку
                    if (data.public_url) {
                        const urlContainer = document.getElementById('urlContainer');
                        const videoUrl = document.getElementById('videoUrl');
                        videoUrl.href = data.public_url;
                        videoUrl.textContent = data.public_url;
                        urlContainer.style.display = 'block';
                    }
                    
                    // Обновляем список
                    loadRecentJobs();
                    
                } else if (data.status === 'FAILED') {
                    clearInterval(interval);
                    statusBadge.className = 'badge badge-failed';
                    
                    if (data.error_message) {
                        const errorP = document.createElement('p');
                        errorP.className = 'error-text';
                        errorP.textContent = `Ошибка: ${data.error_message}`;
                        successResult.appendChild(errorP);
                    }
                }
            }
            
        } catch (error) {
            console.error('Error polling status:', error);
        }
        
        if (attempts >= maxAttempts) {
            clearInterval(interval);
        }
        
    }, 30000); // Каждые 30 секунд
}

// Загрузка последних загрузок
async function loadRecentJobs() {
    const jobsList = document.getElementById('jobsList');
    
    try {
        const response = await fetch(`${API_BASE}/api/jobs?limit=10`);
        
        if (response.ok) {
            const jobs = await response.json();
            
            if (jobs.length === 0) {
                jobsList.innerHTML = '<p class="loading">Пока нет загрузок</p>';
                return;
            }
            
            jobsList.innerHTML = jobs.map(job => `
                <div class="job-item ${job.status.toLowerCase()}">
                    <h3>${escapeHtml(job.title)}</h3>
                    <p><strong>Платформа:</strong> ${getPlatformName(job.platform)}</p>
                    <p><strong>Статус:</strong> <span class="badge badge-${job.status.toLowerCase()}">${getStatusText(job.status)}</span></p>
                    <p><strong>Создано:</strong> ${formatDate(job.created_at)}</p>
                    ${job.public_url ? `<p><strong>Ссылка:</strong> <a href="${job.public_url}" target="_blank">${job.public_url}</a></p>` : ''}
                    ${job.error_message ? `<p class="error-text">Ошибка: ${escapeHtml(job.error_message)}</p>` : ''}
                </div>
            `).join('');
            
        } else {
            jobsList.innerHTML = '<p class="loading">Ошибка загрузки данных</p>';
        }
        
    } catch (error) {
        console.error('Error loading jobs:', error);
        jobsList.innerHTML = '<p class="loading">Ошибка загрузки данных</p>';
    }
}

// Утилиты
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU');
}

function getStatusText(status) {
    const statusMap = {
        'PENDING': 'В очереди',
        'PROCESSING': 'Обработка',
        'COMPLETED': 'Завершено',
        'FAILED': 'Ошибка'
    };
    return statusMap[status] || status;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getPlatformName(platform) {
    const platformMap = {
        'youtube': 'YouTube',
        'vk': 'ВКонтакте (VK)',
        'tiktok': 'TikTok'
    };
    return platformMap[platform] || platform.toUpperCase();
}

// Загрузка при старте
document.addEventListener('DOMContentLoaded', () => {
    loadRecentJobs();
    updateSubmitButton();
});
