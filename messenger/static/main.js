document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const messagesDiv = document.getElementById('messages');
    const usersDiv = document.getElementById('users');
    const authDiv = document.getElementById('auth');
    const chatAppDiv = document.getElementById('chatApp');
    const createChatForm = document.getElementById('createChatForm');
    const chatNameInput = document.getElementById('chatName');
    const chatTitle = document.getElementById('chatTitle');
    const profileForm = document.getElementById('profileForm');
    const profileDiv = document.getElementById('profile')

    let token = '';
    let currentChatId = null;
    let socket = null
    let currentUser = { login: 'Unknown', profilePhoto: '/media/profilePhoto/unknownProfilePhoto.jpg'};

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const login = document.getElementById('login').value;
        const password = document.getElementById('password').value;

        fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ login, password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.access) {
                token = data.access;
                console.log('Token received:', token);
                authDiv.style.display = 'none';
                chatAppDiv.style.display = 'flex';
                profileDiv.style.display = 'block';
                fetchCurrentUser();
                loadUsers();
                loadChats();
            } else {
                alert('Неправильный логин или пароль');
            }
        })
        .catch(error => console.error('Error:', error));
    });

    registerForm.addEventListener('submit', function(e){
        e.preventDefault();
        const formData = new FormData();
        formData.append('login', document.getElementById('regLogin').value);
        formData.append('password', document.getElementById('regPassword').value);
        formData.append('firstName', document.getElementById('regFirstName').value);
        formData.append('lastName', document.getElementById('regLastName').value);
        formData.append('profilePhoto', document.getElementById('regProfilePhoto').files[0]);

        fetch('/api/users/register/',{
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert('Пользователь зарегистрирован');
        })
        .catch(error => console.error('Error: ', error));
    });

    createChatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const chatName = chatNameInput.value.trim();

        if (chatName) {
            fetch('/api/chats/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: chatName })
            })
            .then(response => response.json())
            .then(chat => {
                if (chat.id) {
                    console.log('Чат создан ', chat);
                    loadChats();
                } else {
                    console.error('Неудалось создать чат', chat);
                }
            })
            .catch(error => console.error('Error:', error));
        } else {
            console.error('Нужно имя чата.');
        }
    });

    profileForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const profileData = {
            firstName: document.getElementById('profileFirstName').value,
            lastName: document.getElementById('profileLastName').value
        };
        if (document.getElementById('profilePhoto').files.length > 0) {
            profileData.profilePhoto = document.getElementById('profilePhoto').files[0];
        }

        fetch('/api/users/me/', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(profileData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error("Произошла ошибка"); });
            }
            return response.json();
        })
        .then(data => {
            console.log('Profile updated:', data);
            alert('Изменения сохранены');
            fetchCurrentUser(); 
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка, не удалось изменить профиль');
        });
    });
    function fetchCurrentUser() {
        if (!token) {
            console.warn('Нет токена, пропускаем загрузку профиля');
            return;
        }

        console.log('Загружаем пользователя');
        fetch('/api/users/me/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error('Неудалось получить данные пользователя');
            }
            return response.json();
        })
        .then(data => {
            console.log('Current user data:', data);
            currentUser = {
                username: data.username || 'Unknown',
                avatar: data.avatar || '/media/avatars/default-avatar.jpeg'
            };

            document.getElementById('profileUsername').value = data.login || '';
            document.getElementById('profileFirstName').value = data.firstName || '';
            document.getElementById('profileLastName').value = data.lastName || '';

        })
        .catch(error => {
            console.error('Ошибка загрузки пользователя', error);
            currentUser = { login: 'Unknown', profilePhoto: '/media/profilePhoto/unknownProfilePhoto.jpg'};
        });
    }

    function loadUsers() {
        if (!token) {
            console.warn('Нет токена, пропускаем загрузку пользователей.');
            return;
        }

        fetch('/api/users/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data)) {
                usersDiv.innerHTML = '';
                data.forEach(user => {
                    const userDiv = document.createElement('div');
                    userDiv.textContent = user.login;
                    userDiv.onclick = () => openChat(user.id);
                    usersDiv.appendChild(userDiv);
                });
            } else {
                console.error('Ошибка загрузки списка пользователей', data);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function loadChats() {
        if (!token) {
            console.warn('Нет токена. Пропускаем загрузку чатов');
            return;
        }

        fetch('/api/chats/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data)) {
                chatsDiv.innerHTML = '';
                data.forEach(chat => {
                    const chatDiv = document.createElement('div');
                    chatDiv.className = 'chat-item';
                    chatDiv.textContent = chat.title;
                    chatDiv.setAttribute('data-chat-id', chat.id);
                    chatDiv.onclick = () => openChat(chat.id);
                    chatsDiv.appendChild(chatDiv);
                });
            } else {
                console.error('Неудалось загрузить чаты', data);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function openChat(chatId) {
        if (!token) {
            console.warn('No token found. Skipping openChat.');
            return;
        }

        fetch(`/api/chats/${chatId}/messages/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to fetch messages');
            }
        })
        .then(data => {
            if (Array.isArray(data)) {
                currentChatId = chatId;

                const chat = document.querySelector(`.chat-item[data-chat-id="${chatId}"]`);
                if (chat) {
                    chatTitle.textContent = `Chat: ${chat.textContent}`;
                } else {
                    chatTitle.textContent = 'Chat: Unknown';
                }

                messagesDiv.innerHTML = '';
                data.forEach(message => addMessage(message));
                connectWebSocket(currentChatId);
            } else {
                console.error('Failed to load messages:', data);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function addMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
    
        const profilePhotoImage = document.createElement('img');
        profilePhotoImage.src = message.user.profilePhoto || '/media/profilePhoto/unknownProfilePhoto.jpg';
        profilePhotoImage.alt = `${message.user.login}'s profile photo`;
        profilePhotoImage.width = 50;
        profilePhotoImage.height = 50;
    
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `<div class="message-author">${message.user.login}</div><div>${message.content}</div>`;
    
        messageDiv.appendChild(profilePhotoImage);
        messageDiv.appendChild(contentDiv);
    
        messagesDiv.prepend(messageDiv);
    }

    function connectWebSocket(chatId) {
        if (socket) {
            socket.close();
        }
    
        socket = new WebSocket(`ws://${window.location.hostname}:8001/ws/chat/${chatId}/`);
    
        socket.onopen = function(event) {
            console.log('Соединение установлено');
        };
    
        socket.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                if (data.chat_id === currentChatId) {  
                    addMessage({
                        user: data.user,
                        content: data.message,
                    });
                }
            } catch (e) {
                console.error('Ошибка парсинга сообщения', e);
            }
        };
    
        socket.onerror = function(event) {
            console.error('Ошибка WebSocket', event);
        };
    
        socket.onclose = function(event) {
            console.error('Соединение прервано', event);
            setTimeout(() => connectWebSocket(chatId), 5000);
        };
    }

    sendButton.addEventListener('click', function() {
        const message = messageInput.value.trim();

        if (currentChatId && socket && message) {
            socket.send(JSON.stringify({ message: message }));
            messageInput.value = '';
        } else {
            console.error('Неудалось отправить сообщение. Проверьте соединение и текущий чат.');
        }
    });

    fetchCurrentUser(); 

})