document.addEventListener('DOMContentLoaded', () => {
    // --- Custom Modal Logic ---
    function showCustomAlert(title, message, callback = null) {
        const modal = document.getElementById('alert-modal');
        document.getElementById('alert-title').textContent = title;
        document.getElementById('alert-message').textContent = message;
        modal.classList.add('active');
        
        const okBtn = document.getElementById('alert-ok');
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

    // --- IndexedDB Logic ---
    const DB_NAME = 'pdf_tools_history';
    const DB_VERSION = 1;
    const STORE_NAME = 'files';

    function openDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);
            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);
            request.onupgradeneeded = (e) => {
                const db = e.target.result;
                if (!db.objectStoreNames.contains(STORE_NAME)) {
                    db.createObjectStore(STORE_NAME, { keyPath: 'id' });
                }
            };
        });
    }

    function saveToHistory(record) {
        return openDB().then(db => {
            return new Promise((resolve, reject) => {
                const tx = db.transaction(STORE_NAME, 'readwrite');
                const store = tx.objectStore(STORE_NAME);
                store.put(record);
                tx.oncomplete = () => resolve();
                tx.onerror = () => reject(tx.error);
            });
        });
    }

    function getAllHistory() {
        return openDB().then(db => {
            return new Promise((resolve, reject) => {
                const tx = db.transaction(STORE_NAME, 'readonly');
                const store = tx.objectStore(STORE_NAME);
                const request = store.getAll();
                request.onsuccess = () => resolve(request.result.sort((a,b) => b.timestamp - a.timestamp));
                request.onerror = () => reject(request.error);
            });
        });
    }

    function deleteHistory(id) {
        return openDB().then(db => {
            return new Promise((resolve, reject) => {
                const tx = db.transaction(STORE_NAME, 'readwrite');
                const store = tx.objectStore(STORE_NAME);
                store.delete(id);
                tx.oncomplete = () => resolve();
                tx.onerror = () => reject(tx.error);
            });
        });
    }

    function clearAllHistory() {
        return openDB().then(db => {
            return new Promise((resolve, reject) => {
                const tx = db.transaction(STORE_NAME, 'readwrite');
                const store = tx.objectStore(STORE_NAME);
                store.clear();
                tx.oncomplete = () => resolve();
                tx.onerror = () => reject(tx.error);
            });
        });
    }
    
    function formatBytes(bytes, decimals = 2) {
        if (!+bytes) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
    }

    // --- History UI Logic ---
    const historyModal = document.getElementById('history-modal');
    const openHistoryBtn = document.getElementById('open-history-btn');
    const closeHistoryBtn = document.getElementById('history-close-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const historyList = document.getElementById('history-list');

    function renderHistory() {
        getAllHistory().then(records => {
            historyList.innerHTML = '';
            if (records.length === 0) {
                historyList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No history found.</p>';
                return;
            }
            
            records.forEach(record => {
                const item = document.createElement('div');
                item.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid var(--border-color);';
                
                const info = document.createElement('div');
                const date = new Date(record.timestamp).toLocaleString();
                info.innerHTML = `<strong>${record.toolName.toUpperCase()}</strong><br>
                                  <small>${record.filename} (${formatBytes(record.blob.size)})</small><br>
                                  <small style="color: var(--text-secondary);">${date}</small>`;
                
                const actions = document.createElement('div');
                actions.style.cssText = 'display: flex; gap: 0.5rem;';
                
                const dlBtn = document.createElement('button');
                dlBtn.className = 'btn btn-primary';
                dlBtn.style.padding = '0.5rem';
                dlBtn.innerHTML = '<i class="ph ph-download-simple"></i>';
                dlBtn.onclick = () => {
                    try {
                        const url = URL.createObjectURL(record.blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = record.filename;
                        a.click();
                        URL.revokeObjectURL(url);
                    } catch (e) {
                        showCustomAlert("Error", "File not found or corrupted in browser storage.");
                    }
                };
                
                const delBtn = document.createElement('button');
                delBtn.className = 'btn btn-secondary';
                delBtn.style.padding = '0.5rem';
                delBtn.innerHTML = '<i class="ph ph-trash" style="color: #ff3b30;"></i>';
                delBtn.onclick = () => {
                    showCustomConfirm("Delete History", "Remove this file from your browser history?", () => {
                        deleteHistory(record.id).then(() => renderHistory());
                    });
                };
                
                actions.appendChild(dlBtn);
                actions.appendChild(delBtn);
                item.appendChild(info);
                item.appendChild(actions);
                historyList.appendChild(item);
            });
        });
    }

    if (openHistoryBtn) {
        openHistoryBtn.addEventListener('click', (e) => {
            e.preventDefault();
            renderHistory();
            historyModal.classList.add('active');
        });
    }

    if (closeHistoryBtn) {
        closeHistoryBtn.addEventListener('click', () => {
            historyModal.classList.remove('active');
        });
    }

    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', () => {
            showCustomConfirm("Clear All History", "Are you sure you want to permanently delete all stored files from your browser?", () => {
                clearAllHistory().then(() => renderHistory());
            });
        });
    }

    // --- Admin Clear Cache Logic (Secret Shortcut) ---
    document.addEventListener('keydown', (e) => {
        // Trigger on Ctrl + Shift + X (or Cmd + Shift + X)
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'x') {
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
                
                const originalText = confirmBtn.textContent;
                confirmBtn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Clearing...';
                
                fetch('/admin/clear-all', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ password: password })
                })
                .then(res => res.json())
                .then(data => {
                    close();
                    confirmBtn.textContent = originalText;
                    if (data.status === 'success') {
                        showCustomAlert('Success', data.message);
                    } else {
                        showCustomAlert('Error', data.message);
                    }
                })
                .catch(err => {
                    close();
                    confirmBtn.textContent = originalText;
                    showCustomAlert('Error', 'Network Error: ' + err);
                });
            };
        }
    });
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
    
    // Early return if not on a tool page
    if (!dropZone) return;

    // --- Tool Page Logic ---
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
        fileInput.files = dt.files;
        handleFiles();
    }

    let draftJobId = null;
    let estimateTimeout = null;

    const compRadios = document.querySelectorAll('input[name="quality_preset"]');
    const compSlider = document.getElementById('quality-slider');
    const sliderContainer = document.getElementById('slider-container');
    const sliderValDisplay = document.getElementById('slider-val-display');
    const estSizeDisplay = document.getElementById('est-size');

    function estimateSize() {
        if (!draftJobId) return;
        estSizeDisplay.textContent = 'Calculating...';
        
        let preset = document.querySelector('input[name="quality_preset"]:checked').value;
        let quality = compSlider ? compSlider.value : 50;
        
        let estimateUrl = toolRoute + 'estimate/' + draftJobId + '?preset=' + preset + '&quality=' + quality;
        
        fetch(estimateUrl)
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    estSizeDisplay.textContent = formatBytes(data.estimated_size);
                } else {
                    estSizeDisplay.textContent = 'Error';
                }
            }).catch(() => estSizeDisplay.textContent = 'Error');
    }

    if (compRadios.length > 0) {
        compRadios.forEach(r => r.addEventListener('change', (e) => {
            if (e.target.value === 'custom') {
                sliderContainer.style.display = 'block';
            } else {
                sliderContainer.style.display = 'none';
            }
            estimateSize();
        }));
    }

    if (compSlider) {
        compSlider.addEventListener('input', (e) => {
            sliderValDisplay.textContent = e.target.value;
            clearTimeout(estimateTimeout);
            estimateTimeout = setTimeout(estimateSize, 300);
        });
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

        const isCompressionTool = toolRoute.includes('compress');
        if (isCompressionTool) {
            const formData = new FormData();
            for(let i = 0; i < files.length; i++) {
                formData.append(fileInput.name, files[i]);
            }
            
            fetch(toolRoute + 'draft', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    draftJobId = data.job_id;
                    estimateSize();
                } else {
                    showCustomAlert("Error", "Failed to create draft: " + data.error);
                }
            })
            .catch(err => console.error("Draft error:", err));
        }
    }

    if(toolForm) {
        toolForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            uploadContainer.style.display = 'none';
            progressContainer.style.display = 'block';
            
            const isCompressionTool = toolRoute.includes('compress');
            const formData = new FormData(toolForm);
            const xhr = new XMLHttpRequest();
            
            if (isCompressionTool) {
                if (!draftJobId) {
                    showCustomAlert("Wait", "Still preparing file. Please try again in a second.", () => location.reload());
                    return;
                }
                xhr.open('POST', toolRoute + 'process/' + draftJobId, true);
                formData.delete('file');
                formData.delete('files');
            } else {
                xhr.open('POST', toolRoute, true);
            }
            
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
                    
                    progressTitle.textContent = 'Saving to Browser...';
                    progressStatus.textContent = 'Caching file locally';
                    
                    fetch(`/download/${result.job_id}/${result.filename}`)
                        .then(res => {
                            if (!res.ok) throw new Error("File not found");
                            return res.blob();
                        })
                        .then(blob => {
                            const recordId = Date.now().toString();
                            const toolName = toolRoute.replace(/\//g, '') || 'tool';
                            const originalName = fileInput.files[0] ? fileInput.files[0].name : 'unknown';
                            
                            const record = {
                                id: recordId,
                                timestamp: new Date().getTime(),
                                toolName: toolName,
                                originalFilename: originalName,
                                filename: result.filename,
                                blob: blob
                            };
                            
                            saveToHistory(record).then(() => {
                                // Delete from server immediately for statelessness
                                fetch(`/delete/${result.job_id}`, { method: 'DELETE' });
                                
                                const url = URL.createObjectURL(blob);
                                downloadBtn.href = url;
                                downloadBtn.download = result.filename;
                                
                                progressContainer.style.display = 'none';
                                successContainer.style.display = 'block';
                            }).catch(() => {
                                showCustomAlert("Error", "Failed to save to local history.");
                            });
                        })
                        .catch(err => {
                            showCustomAlert("Error", "Failed to download processed file: " + err);
                        });
                        
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
});
