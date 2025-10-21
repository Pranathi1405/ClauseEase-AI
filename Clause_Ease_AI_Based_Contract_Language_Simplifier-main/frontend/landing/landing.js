const API_BASE_URL = 'http://localhost:5000/api';
let selectedFile = null;

if (history.scrollRestoration) {
    history.scrollRestoration = 'manual';
}
window.scrollTo(0, 0);

document.addEventListener('DOMContentLoaded', () => {
    window.scrollTo(0, 0);
    
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    
    if (!token || !username) {
        window.location.href = '../auth/index.html#login';
        return;
    }
    
    document.getElementById('user-greeting').textContent = `Welcome, ${username}!`;
    
    const fileInput = document.getElementById('file-input');
    fileInput.addEventListener('change', handleFileSelect);
    
    setTimeout(() => window.scrollTo(0, 0), 100);
});

function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    sessionStorage.clear();
    window.location.href = '../auth/index.html#login';
}

function openFileUpload() {
    const uploadSection = document.getElementById('demo');
    const navbarHeight = 80;
    const elementPosition = uploadSection.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - navbarHeight - 40;
    
    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

function triggerFileInput() {
    document.getElementById('file-input').click();
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedFile = file;
        document.getElementById('filename').textContent = file.name;
        document.getElementById('file-selected').style.display = 'block';
    }
}

async function processDocument() {
    if (!selectedFile) {
        alert('Please select a file first');
        return false;
    }

    const token = localStorage.getItem('token');
    if (!token) {
        alert('Session expired. Please login again.');
        window.location.href = '../auth/index.html#login';
        return false;
    }

    document.querySelector('.btn-process').style.display = 'none';
    document.getElementById('progress-section').style.display = 'block';
    
    const progressFill = document.getElementById('progress-fill');
    const progressPercentage = document.getElementById('progress-percentage');
    const progressTitle = document.querySelector('.progress-title');
    const progressSubtitle = document.querySelector('.progress-subtitle');
    
    progressTitle.textContent = 'AI is converting your legal document into simple language';
    progressSubtitle.textContent = 'Sit tight while we translate complex clauses into plain English.';
    progressTitle.style.color = '';
    progressSubtitle.style.color = '';
    progressFill.style.background = 'linear-gradient(90deg, #667eea, #764ba2)';
    
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 2;
        if (progress <= 90) {
            progressFill.style.width = progress + '%';
            progressPercentage.textContent = progress + '%';
        }
    }, 100);

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const response = await fetch(`${API_BASE_URL}/process`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        progressPercentage.textContent = '100%';

        if (!response.ok) {
            let errorMessage;
            try {
                const errorText = await response.text();
                try {
                    const error = JSON.parse(errorText);
                    errorMessage = error.message || 'Processing failed';
                } catch {
                    errorMessage = errorText || `Server error (${response.status})`;
                }
            } catch (e) {
                errorMessage = `Server error (${response.status}): ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        
        if (!data.clauses || data.clauses.length === 0) {
            throw new Error('No clauses extracted from document');
        }
        
        progressTitle.textContent = '✅ Success! Redirecting to results...';
        progressSubtitle.textContent = 'Your simplified insights are ready.';
        progressTitle.style.color = '#10b981';
        progressSubtitle.style.color = '#10b981';
        
        sessionStorage.clear();
        sessionStorage.setItem('processedResults', JSON.stringify(data));
        sessionStorage.setItem('processedFilename', selectedFile.name);
        
        setTimeout(() => {
            window.location.href = '../results/results.html';
        }, 1500);
        
        return false;
        
    } catch (error) {
        clearInterval(progressInterval);
        
        progressTitle.textContent = '❌ Error: ' + error.message;
        progressSubtitle.textContent = 'Please check the steps below and try again.';
        progressTitle.style.color = '#ef4444';
        progressSubtitle.style.color = '#ef4444';
        progressFill.style.background = 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)';
        progressFill.style.width = '100%';
        
        alert('Processing failed: ' + error.message + '\n\nPlease check:\n1. Backend server is running at http://localhost:5000\n2. File is a valid PDF/DOCX/TXT\n3. You are logged in properly\n4. Check browser console (F12) for details');
        
        setTimeout(() => {
            document.querySelector('.btn-process').style.display = 'inline-flex';
            document.getElementById('progress-section').style.display = 'none';
            progressTitle.style.color = '';
            progressSubtitle.style.color = '';
            progressFill.style.background = '';
        }, 3000);
        
        return false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const navbarHeight = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - navbarHeight;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
});
