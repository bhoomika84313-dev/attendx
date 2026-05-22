const API = 'http://127.0.0.1:5000';

// Format date nicely
function formatDate() {
    return new Date().toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Show success alert
function showSuccess(id, message) {
    const alert = document.getElementById(id);
    if (alert) {
        alert.textContent = '✅ ' + message;
        alert.style.display = 'block';
        setTimeout(() => {
            alert.style.display = 'none';
        }, 3000);
    }
}

// Show error alert
function showError(id, message) {
    const alert = document.getElementById(id);
    if (alert) {
        alert.textContent = '❌ ' + message;
        alert.style.display = 'block';
        setTimeout(() => {
            alert.style.display = 'none';
        }, 3000);
    }
}

// Get all students
async function getStudents() {
    try {
        const res = await fetch(`${API}/students`);
        return await res.json();
    } catch(e) {
        console.error('Error fetching students:', e);
        return [];
    }
}

// Get all courses
async function getCourses() {
    try {
        const res = await fetch(`${API}/courses`);
        return await res.json();
    } catch(e) {
        console.error('Error fetching courses:', e);
        return [];
    }
}

// Get shortage students
async function getShortage() {
    try {
        const res = await fetch(`${API}/attendance/shortage`);
        return await res.json();
    } catch(e) {
        console.error('Error fetching shortage:', e);
        return [];
    }
}

// Check if backend is running
async function checkBackend() {
    try {
        await fetch(`${API}/students`);
        console.log('✅ Backend connected!');
    } catch(e) {
        alert('⚠️ Backend is not running! Please start python app.py first.');
    }
}

// Run on every page
checkBackend();