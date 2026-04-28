document.addEventListener('DOMContentLoaded', () => {
    // --- Custom Modal Logic ---
    function showCustomAlert(title, message, callback = null) {
        const modal = document.getElementById('alert-modal');
        document.getElementById('alert-title').textContent = title;
        document.getElementById('alert-message').textContent = message;
        modal.classList.add('active');
        
        const okBtn = document.getElementById('alert-ok');
        // Remove old listeners
        const newOkBtn = okBtn.cloneNode(true);
        okBtn.parentNode.replaceChild(newOkBtn, okBtn);
        
        newOkBtn.addEventListener('click', () => {
            modal.classList.remove('active');
            if (callback) callback();
        });
    }

    function showCustomConfirm(title, message, onConfirm) {
        const modal = document.getElementById('custom-modal');
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-message').textContent = message;
        modal.classList.add('active');
        
        const confirmBtn = document.getElementById('modal-confirm');
        const cancelBtn = document.getElementById('modal-cancel');
        
        // Remove old listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        const newCancelBtn = cancelBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
        
        newCancelBtn.addEventListener('click', () => {
            modal.classList.remove('active');
        });
        
        newConfirmBtn.addEventListener('click', () => {
            modal.classList.remove('active');
            onConfirm();
        });
    }
    // --- End Custom Modal Logic ---

    // --- Admin Clear Cache Logic (Runs on ALL pages) ---
    const adminClearBtn = document.getElementById('admin-clear-btn');
    if (adminClearBtn) {
        adminClearBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const modal = document.getElementById('admin-modal');
            const passInput = document.getElementById('admin-password-input');
            const confirmBtn = document.getElementById('admin-confirm');
            const cancelBtn = document.getElementById('admin-cancel');
            
            passInput.value = '';
            modal.classList.add('active');
            passInput.focus();
            
            const close = () => modal.classList.remove('active');
            
            cancelBtn.onclick = close;
            
            confirmBtn.onclick = () => {
                const password = passInput.value;
                if (!password) {
                    alert("Please enter a password.");
                    return;
                }
                
                adminClearBtn.textContent = 'Clearing...';
                close();
                
                fetch('/admin/clear-all', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ password: password })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        showCustomAlert('Success', data.message);
                    } else {
                        showCustomAlert('Error', data.message);
                    }
                    adminClearBtn.innerHTML = '<i class="ph ph-trash" style="margin-right: 5px;"></i> Admin: Clear All Cache';
                })
                .catch(err => {
                    showCustomAlert('Error', 'Network Error: ' + err);
                    adminClearBtn.innerHTML = '<i class="ph ph-trash" style="margin-right: 5px;"></i> Admin: Clear All Cache';
                });
            };
        });
    }
    // --- End Admin Logic ---

    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const selectedFilesContainer = document.getElementById('selected-files');
    const fileList = document.getElementById('file-list');
    const toolForm = document.getElementById('tool-form');
    
    const uploadContainer = document.getElementById('upload-container');
    const progressContainer = document.getElementById('progress-container');
    const successContainer = document.getElementById('success-container');
    
    const progressFill = document.getElementById('progress-fill');
    const progressStatus = document.getElementById('progress-status');
    const progressTitle = document.getElementById('progress-title');
    const processingSpinner = document.getElementById('processing-spinner');
    
    const downloadBtn = document.getElementById('download-btn');
    const deleteCacheBtn = document.getElementById('delete-cache-btn');
    
    let currentJobId = null;

    // Early return if not on a tool page
    if (!dropZone) return;

    // --- Tool Page Logic ---
    // Drag and Drop handlers
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFiles, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        handleFiles();
    }

    function handleFiles() {
        const files = fileInput.files;
        if (files.length === 0) return;

        fileList.innerHTML = '';
        for (let i = 0; i < files.length; i++) {
            const li = document.createElement('li');
            li.innerHTML = `<span><i class="ph ph-file-pdf"></i> ${files[i].name}</span> <span>${(files[i].size / 1024 / 1024).toFixed(2)} MB</span>`;
            fileList.appendChild(li);
        }

        dropZone.style.display = 'none';
        selectedFilesContainer.style.display = 'block';
    }

    if(toolForm) {
        toolForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            uploadContainer.style.display = 'none';
            progressContainer.style.display = 'block';
            
            const formData = new FormData(toolForm);
            
            const xhr = new XMLHttpRequest();
            xhr.open('POST', toolRoute, true);
            xhr.responseType = 'json';

            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    progressFill.style.width = percentComplete + '%';
                    progressStatus.textContent = Math.round(percentComplete) + '%';
                    
                    if (percentComplete === 100) {
                        progressTitle.textContent = 'Processing...';
                        progressStatus.textContent = 'This may take a moment.';
                        processingSpinner.style.display = 'block';
                    }
                }
            });

            xhr.onload = function() {
                if (this.status === 200 && this.response.status === 'success') {
                    const result = this.response;
                    currentJobId = result.job_id;
                    
                    downloadBtn.href = `/download/${result.job_id}/${result.filename}`;
                    downloadBtn.download = result.filename; 

                    progressContainer.style.display = 'none';
                    successContainer.style.display = 'block';
                } else {
                    const msg = this.response ? this.response.error : 'Unknown error';
                    showCustomAlert("Error", msg, () => location.reload());
                }
            };

            xhr.onerror = function() {
                showCustomAlert('Error', 'An error occurred during the upload.', () => location.reload());
            };

            xhr.send(formData);
        });
    }

    if (deleteCacheBtn) {
        deleteCacheBtn.addEventListener('click', () => {
            if (!currentJobId) return;
            
            showCustomConfirm('Delete File', 'Are you sure you want to delete this file from the server cache?', () => {
                deleteCacheBtn.textContent = 'Deleting...';
                deleteCacheBtn.disabled = true;
                
                fetch(`/delete/${currentJobId}`, {
                    method: 'DELETE'
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        showCustomAlert('Success', 'Files deleted from cache successfully!', () => location.reload());
                    } else {
                        showCustomAlert('Error', 'Error deleting cache: ' + data.message);
                        deleteCacheBtn.textContent = 'Delete from Cache';
                        deleteCacheBtn.disabled = false;
                    }
                })
                .catch(err => {
                    showCustomAlert('Error', 'Network Error: ' + err);
                    deleteCacheBtn.textContent = 'Delete from Cache';
                    deleteCacheBtn.disabled = false;
                });
            });
        });
    }
});
