document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    print("currentpath",currentPath)

    if (currentPath === '/login' || currentPath === '/') {
        setupLoginForm();
    } else if (currentPath === '/register') {
        setupRegisterForm();
    } else if (currentPath === '/dashboard') {
        setupDashboard();
    } else if (currentPath === '/create') {
        setupCreateTodoForm();
    } else if (currentPath.startsWith('/edit/')) {
        const todoId = int(currentPath.split('/').pop());
        print(todoId)
        setupEditTodoForm(todoId);
    }

    setupLogoutButton();
});

function setupLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user', JSON.stringify({
                    email: email,
                    name: data.sub || email.split('@')[0]
                }));
                window.location.href = '/dashboard';
            } else {
                alert('Login failed: ' + (data.detail || 'Unknown error'));
            }
        } catch (error) {
            alert('Login error: ' + error.message);
        }
    });
}

function setupRegisterForm() {
    const registerForm = document.getElementById('registerForm');
    if (!registerForm) return;

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, email, password })
            });

            const data = await response.json();

            if (response.ok) {
                alert('Registration successful! You can now login.');
                window.location.href = '/login';
            } else {
                alert('Registration failed: ' + (data.detail || 'Unknown error'));
            }
        } catch (error) {
            alert('Registration error: ' + error.message);
        }
    });
}

function setupDashboard() {
    const todosContainer = document.getElementById('todosContainer');
    const userNameElement = document.getElementById('userName');
    const filterButtons = document.querySelectorAll('.filter-btn');

    if (!todosContainer) return;

    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (userNameElement && user.name) {
        userNameElement.textContent = user.name;
    }

    fetchTodos();

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            const filterType = button.dataset.filter;
            filterTodos(filterType);
        });
    });

    todosContainer.addEventListener('click', async (e) => {
        if (e.target.classList.contains('btn-delete')) {
            const todoId = e.target.dataset.id;
            if (confirm('Are you sure you want to delete this todo?')) {
                await deleteTodo(todoId);
            }
        } else if (e.target.classList.contains('btn-toggle-status')) {
            const todoId = e.target.dataset.id;
            const isCompleted = e.target.dataset.completed === 'true';

            const todoElement = document.querySelector(`.todo-item[data-id="${todoId}"]`);
            const todoTitle = todoElement.querySelector('.todo-title').textContent;
            const todoDesc = todoElement.querySelector('.todo-desc').textContent;
            const todoPriority = todoElement.querySelector('.todo-priority').textContent.split(': ')[1];

            await updateTodoStatus(todoId, {
                title: todoTitle,
                desc: todoDesc,
                priority: parseInt(todoPriority),
                completed: !isCompleted
            });
        }
    });
}

async function fetchTodos() {
    const todosContainer = document.getElementById('todosContainer');
    const token = localStorage.getItem('token');

    try {
        const response = await fetch('/todos', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const todos = await response.json();

            todosContainer.innerHTML = '';

            if (todos.length === 0) {
                todosContainer.innerHTML = '<p class="no-todos">No todos found. Create one!</p>';
                return;
            }

            todos.forEach(todo => {
                const todoElement = createTodoElement(todo);
                todosContainer.appendChild(todoElement);
            });
        } else {
            if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = '/login';
            } else {
                const error = await response.json();
                alert('Failed to fetch todos: ' + (error.detail || 'Unknown error'));
            }
        }
    } catch (error) {
        alert('Error fetching todos: ' + error.message);
    }
}

function createTodoElement(todo) {
    const todoDiv = document.createElement('div');
    todoDiv.className = 'todo-item';
    todoDiv.dataset.id = todo.id;
    todoDiv.dataset.completed = todo.completed;

    todoDiv.innerHTML = `
        <div class="todo-content">
            <h3 class="todo-title">${todo.title}</h3>
            <p class="todo-desc">${todo.desc}</p>
            <div class="todo-meta">
                <span class="todo-priority">Priority: ${todo.priority}</span>
                <span class="todo-status">
                    Status: ${todo.completed ? 'Completed' : 'Active'}
                </span>
            </div>
        </div>
        <div class="todo-actions">
            <a href="/edit/${todo.id}" class="btn btn-edit">Edit</a>
            <button class="btn btn-delete" data-id="${todo.id}">Delete</button>
            <button class="btn btn-toggle-status" data-id="${todo.id}" data-completed="${todo.completed}">
                ${todo.completed ? 'Mark Incomplete' : 'Mark Complete'}
            </button>
        </div>
    `;

    return todoDiv;
}

function filterTodos(filterType) {
    const todoItems = document.querySelectorAll('.todo-item');

    todoItems.forEach(item => {
        const isCompleted = item.dataset.completed === 'true';

        if (filterType === 'all') {
            item.style.display = 'flex';
        } else if (filterType === 'active' && !isCompleted) {
            item.style.display = 'flex';
        } else if (filterType === 'completed' && isCompleted) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

function setupCreateTodoForm() {
    const createTodoForm = document.getElementById('createTodoForm');
    if (!createTodoForm) return;

    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    createTodoForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const title = document.getElementById('title').value;
        const desc = document.getElementById('desc').value;
        const priority = parseInt(document.getElementById('priority').value);
        const completed = document.getElementById('completed').checked;

        try {
            const response = await fetch('/todos/create-todo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    title,
                    desc,
                    priority,
                    completed
                })
            });

            if (response.ok) {
                alert('Todo created successfully!');
                window.location.href = '/dashboard';
            } else {
                const error = await response.json();
                alert('Failed to create todo: ' + (error.detail || 'Unknown error'));
            }
        } catch (error) {
            alert('Error creating todo: ' + error.message);
        }
    });
}

function setupEditTodoForm(todoId) {
    const editTodoForm = document.getElementById('editTodoForm');
    const deleteTodoBtn = document.getElementById('deleteTodoBtn');

    if (!editTodoForm) return;

    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    fetchTodoDetails(todoId);

    editTodoForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const title = document.getElementById('title').value;
        const desc = document.getElementById('desc').value;
        const priority = parseInt(document.getElementById('priority').value);
        const completed = document.getElementById('completed').checked;

        try {
            const response = await fetch(`/todos/${todo_id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    title,
                    desc,
                    priority,
                    completed
                })
            });

            if (response.ok) {
                alert('Todo updated successfully!');
                window.location.href = '/dashboard';
            } else {
                const error = await response.json();
                alert('Failed to update todo: ' + (error.detail || 'Unknown error'));
            }
        } catch (error) {
            alert('Error updating todo: ' + error.message);
        }
    });

    if (deleteTodoBtn) {
        deleteTodoBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to delete this todo?')) {
                await deleteTodo(todoId);
            }
        });
    }
}

async function fetchTodoDetails(todoId) {
    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`/todos/${todoId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const todo = await response.json();

            document.getElementById('title').value = todo.title;
            document.getElementById('desc').value = todo.desc;
            document.getElementById('priority').value = todo.priority;
            document.getElementById('completed').checked = todo.completed;
        } else {
            if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = '/login';
            } else {
                const error = await response.json();
                alert('Failed to fetch todo details: ' + (error.detail || 'Unknown error'));
                window.location.href = '/dashboard';
            }
        }
    } catch (error) {
        alert('Error fetching todo details: ' + error.message);
        window.location.href = '/dashboard';
    }
}

async function deleteTodo(todoId) {
    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`/todos/${todoId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert('Todo deleted successfully!');

            if (window.location.pathname.startsWith('/edit/')) {
                window.location.href = '/dashboard';
            } else {
                fetchTodos();
            }
        } else {
            const error = await response.json();
            alert('Failed to delete todo: ' + (error.detail || 'Unknown error'));
        }
    } catch (error) {
        alert('Error deleting todo: ' + error.message);
    }
}

async function updateTodoStatus(todoId, todoData) {
    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`/todos/${todoId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(todoData)
        });

        if (response.ok) {
            fetchTodos();
        } else {
            const error = await response.json();
            alert('Failed to update todo status: ' + (error.detail || 'Unknown error'));
        }
    } catch (error) {
        alert('Error updating todo status: ' + error.message);
    }
}

function setupLogoutButton() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (!logoutBtn) return;

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
    });
}