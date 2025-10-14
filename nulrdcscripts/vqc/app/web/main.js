// ===== MODAL FUNCTIONS =====
let lastFocusedElement = null;

function openLicenseModal() {
    lastFocusedElement = document.activeElement;
    document.getElementById('licenseModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
    trapFocus();
    announceStatus('License dialog opened');
}

function closeLicenseModal() {
    document.getElementById('licenseModal').style.display = 'none';
    document.body.style.overflow = '';
    if (lastFocusedElement) {
        lastFocusedElement.focus();
    }
    announceStatus('License dialog closed');
}

function openStandardsModal() {
    lastFocusedElement = document.activeElement;
    document.getElementById('standardsModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
    trapFocus();
    announceStatus('Standards reference opened');
}

function closeStandardsModal() {
    document.getElementById('standardsModal').style.display = 'none';
    document.body.style.overflow = '';
    if (lastFocusedElement) {
        lastFocusedElement.focus();
    }
    announceStatus('Standards dialog closed');
}

function trapFocus() {
    const modal = document.querySelector('.modal');
    const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (firstElement) {
        firstElement.focus();
    }
}

function announceStatus(message) {
    const statusAnnounce = document.getElementById('statusAnnounce');
    if (statusAnnounce) {
        statusAnnounce.textContent = message;
        setTimeout(() => {
            statusAnnounce.textContent = '';
        }, 1000);
    }
}

// ===== SHARED FUNCTIONS =====
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ===== MAIN APPLICATION =====
document.addEventListener('DOMContentLoaded', function () {
    console.log('=== SCRIPT LOADED ===');
    console.log('DOMContentLoaded fired');
    
    // Test Eel connection
    if (typeof eel !== 'undefined') {
        eel.test_connection()(function(result) {
            console.log('Eel test result:', result);
        });
    }
    
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const folderInput = document.getElementById('folderInput');
    const uploadMenu = document.getElementById('uploadMenu');
    const menuSelectFiles = document.getElementById('menuSelectFiles');
    const menuSelectFolder = document.getElementById('menuSelectFolder');
    const fileList = document.getElementById('fileList');
    const processBtn = document.getElementById('processBtn');
    const uploadSection = document.getElementById('uploadSection');
    const processingSection = document.getElementById('processingSection');
    const resultsSection = document.getElementById('resultsSection');
    const newAnalysisBtn = document.getElementById('newAnalysisBtn');
    const modeBtns = document.querySelectorAll('.mode-btn');
    const uploadInfo = document.getElementById('uploadInfo');
    const manualPathInput = document.getElementById('manualPath');

    console.log('Elements:', {
        uploadArea: !!uploadArea,
        menuSelectFiles: !!menuSelectFiles,
        menuSelectFolder: !!menuSelectFolder,
        modeBtns: modeBtns.length,
        processBtn: !!processBtn
    });

    let selectedFiles = [];
    let currentMode = 'video';

    // ===== MODE SWITCHING =====
    modeBtns.forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Mode button clicked:', btn.dataset.mode);
            
            // Remove active from all buttons
            modeBtns.forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-pressed', 'false');
            });
            
            // Set this button as active
            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');
            currentMode = btn.dataset.mode;
            
            // Store in window object so it's accessible everywhere
            window.currentFileMode = currentMode;
            
            console.log('Mode switched to:', currentMode);
            
            // Tell Python about the mode change
            if (typeof eel !== 'undefined') {
                try {
                    await eel.set_file_mode(currentMode)();
                    console.log('Mode sent to Python:', currentMode);
                } catch (error) {
                    console.error('Error setting mode in Python:', error);
                }
            }

            // Update UI based on mode
            if (currentMode === 'video') {
                fileInput.accept = '.mkv,.mp4';
                uploadInfo.textContent = 'Supports: MKV, MP4 (multiple files supported)';
                announceStatus('Switched to video file mode');
            } else {
                fileInput.accept = '.xml';
                folderInput.accept = '.xml';
                uploadInfo.textContent = 'Supports: XML (QCTools output - multiple files supported)';
                announceStatus('Switched to XML file mode');
            }

            // Clear selected files when switching modes
            selectedFiles = [];
            updateFileList();
        });
    });

    // ===== MANUAL PATH PROCESSING =====
    window.processManualPath = async function() {
        const pathInput = manualPathInput.value.trim();
        
        if (!pathInput) {
            alert('Please enter a file or folder path');
            return;
        }
        
        console.log('Processing manual path:', pathInput);
        announceStatus('Processing path...');
        
        if (typeof eel === 'undefined') {
            alert('Eel backend not connected');
            return;
        }
        
        try {
            // Try to process as file first
            const result = await eel.process_manual_path(pathInput)();
            
            if (result.success) {
                if (result.is_folder && result.files) {
                    // It's a folder with multiple files
                    const newFiles = result.files.map(file => ({
                        name: file.filename,
                        path: file.path,
                        size: file.size
                    }));
                    
                    selectedFiles = [...selectedFiles, ...newFiles];
                    announceStatus(`${result.files.length} file${result.files.length > 1 ? 's' : ''} found in folder`);
                } else if (result.file) {
                    // It's a single file
                    selectedFiles.push({
                        name: result.file.filename,
                        path: result.file.path,
                        size: result.file.size
                    });
                    announceStatus('File added');
                }
                
                updateFileList();
                manualPathInput.value = ''; // Clear input
            } else {
                alert(result.error || 'Invalid path or no valid files found');
                announceStatus('Path processing failed');
            }
        } catch (error) {
            console.error('Error processing manual path:', error);
            alert('Error processing path: ' + error);
            announceStatus('Error processing path');
        }
    };

    // Allow Enter key to submit manual path
    manualPathInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            window.processManualPath();
        }
    });

    // ===== HAMBURGER MENU =====
    const menuToggle = document.getElementById('menuToggle');
    const utilityMenu = document.getElementById('utilityMenu');
    const menuIcon = document.getElementById('menuIcon');
    
    if (menuToggle && utilityMenu) {
        menuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = utilityMenu.classList.contains('active');
            
            if (isOpen) {
                utilityMenu.classList.remove('active');
                menuIcon.textContent = '☰';
                menuToggle.setAttribute('aria-expanded', 'false');
                announceStatus('Menu closed');
            } else {
                utilityMenu.classList.add('active');
                menuIcon.textContent = '✕';
                menuToggle.setAttribute('aria-expanded', 'true');
                announceStatus('Menu opened');
            }
        });
    
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!menuToggle.contains(e.target) && !utilityMenu.contains(e.target)) {
                if (utilityMenu.classList.contains('active')) {
                    utilityMenu.classList.remove('active');
                    menuIcon.textContent = '☰';
                    menuToggle.setAttribute('aria-expanded', 'false');
                }
            }
        });
    
        // Close menu ONLY for menu buttons (Standards and License)
        utilityMenu.querySelectorAll('button').forEach(menuBtn => {
            menuBtn.addEventListener('click', () => {
                utilityMenu.classList.remove('active');
                menuIcon.textContent = '☰';
                menuToggle.setAttribute('aria-expanded', 'false');
            });
        });
    
        // Close menu with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && utilityMenu.classList.contains('active')) {
                utilityMenu.classList.remove('active');
                menuIcon.textContent = '☰';
                menuToggle.setAttribute('aria-expanded', 'false');
                menuToggle.focus();
            }
        });
    }

    // ===== DRAG AND DROP ERROR HANDLING =====
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        // Add error styling
        uploadArea.classList.add('drag-error');
        
        // Show alert
        alert('⚠️ Drag and drop is not supported.\n\nPlease use "Select Files" or "Select Folder" buttons instead.');
        announceStatus('Please use the file selection buttons');
        
        // Remove error styling after animation
        setTimeout(() => {
            uploadArea.classList.remove('drag-error');
        }, 500);
    });

    // ===== FILE LIST =====
    uploadArea.addEventListener('click', (e) => {
        if (e.target.closest('.upload-menu')) return;

        uploadMenu.style.display = 'block';
        uploadMenu.style.left = '50%';
        uploadMenu.style.top = '50%';
        uploadMenu.style.transform = 'translate(-50%, -50%)';
        menuSelectFiles.focus();
        announceStatus('Upload menu opened. Choose files or folder.');
    });

    document.addEventListener('click', (e) => {
        if (!uploadArea.contains(e.target)) {
            uploadMenu.style.display = 'none';
        }
    });

    // ===== FILE SELECTION WITH EEL =====
    menuSelectFiles.addEventListener('click', async (e) => {
        e.stopPropagation();
        uploadMenu.style.display = 'none';
        announceStatus('Opening file selector...');
        
        if (typeof eel === 'undefined') {
            alert('Eel backend not connected');
            return;
        }
        
        try {
            const files = await eel.select_files_dialog()();
            
            if (files && files.length > 0) {
                const newFiles = files.map(filePath => ({
                    name: filePath.split(/[\\/]/).pop(),
                    path: filePath,
                    size: 0
                }));
                
                selectedFiles = [...selectedFiles, ...newFiles];
                announceStatus(`${files.length} file${files.length > 1 ? 's' : ''} selected`);
                updateFileList();
            } else {
                announceStatus('No files selected');
            }
        } catch (error) {
            console.error('Error selecting files:', error);
            announceStatus('Error opening file selector');
        }
    });

    menuSelectFolder.addEventListener('click', async (e) => {
        e.stopPropagation();
        uploadMenu.style.display = 'none';
        announceStatus('Opening folder selector...');
        
        if (typeof eel === 'undefined') {
            alert('Eel backend not connected');
            return;
        }
        
        try {
            const folder = await eel.select_folder_dialog()();
            
            if (folder) {
                const result = await eel.get_folder_contents(folder)();
                
                if (result.success && result.files.length > 0) {
                    const newFiles = result.files.map(file => ({
                        name: file.filename,
                        path: file.path,
                        size: file.size
                    }));
                    
                    selectedFiles = [...selectedFiles, ...newFiles];
                    announceStatus(`${result.files.length} file${result.files.length > 1 ? 's' : ''} found in folder`);
                    updateFileList();
                } else {
                    announceStatus('No valid files found in folder');
                    alert('No valid files found in the selected folder.');
                }
            } else {
                announceStatus('No folder selected');
            }
        } catch (error) {
            console.error('Error selecting folder:', error);
            announceStatus('Error opening folder selector');
        }
    });

    // Menu keyboard navigation
    menuSelectFiles.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            menuSelectFolder.focus();
        } else if (e.key === 'Escape') {
            uploadMenu.style.display = 'none';
            uploadArea.focus();
        }
    });

    menuSelectFolder.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            menuSelectFiles.focus();
        } else if (e.key === 'Escape') {
            uploadMenu.style.display = 'none';
            uploadArea.focus();
        }
    });

    uploadArea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            uploadMenu.style.display = 'block';
            uploadMenu.style.left = '50%';
            uploadMenu.style.top = '50%';
            uploadMenu.style.transform = 'translate(-50%, -50%)';
            menuSelectFiles.focus();
            announceStatus('Upload menu opened. Choose files or folder.');
        }
    });

    // ===== UPLOAD MENU =====
    function updateFileList() {
        console.log('updateFileList called, files:', selectedFiles.length);
        
        if (selectedFiles.length === 0) {
            fileList.classList.add('hidden');
            processBtn.disabled = true;
            processBtn.setAttribute('aria-disabled', 'true');
            console.log('No files, button disabled');
            return;
        }

        fileList.classList.remove('hidden');
        processBtn.disabled = false;
        processBtn.removeAttribute('aria-disabled');
        console.log('Files present, button enabled');

        fileList.innerHTML = selectedFiles.map((file, index) => `
            <div class="file-item" role="listitem">
                <div>
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${formatFileSize(file.size)}</div>
                </div>
                <button class="remove-btn" onclick="removeFile(${index})" aria-label="Remove ${file.name}">Remove</button>
            </div>
        `).join('');
    }

    window.removeFile = function (index) {
        const fileName = selectedFiles[index].name;
        selectedFiles.splice(index, 1);
        announceStatus(`${fileName} removed`);
        updateFileList();
    };

    // ===== PROCESSING WITH EEL BACKEND =====
    processBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        if (selectedFiles.length === 0) {
            alert('Please select files first');
            return;
        }
        
        console.log('Processing', selectedFiles.length, 'files');
        
        // Add loading state
        processBtn.classList.add('btn-loading');
        processBtn.disabled = true;
        const originalText = processBtn.innerHTML;
        processBtn.innerHTML = 'Processing...';
        
        uploadSection.classList.add('hidden');
        processingSection.classList.remove('hidden');
        announceStatus('Processing files. Please wait.');

        if (typeof eel === 'undefined') {
            alert('Eel backend not connected');
            processingSection.classList.add('hidden');
            uploadSection.classList.remove('hidden');
            processBtn.classList.remove('btn-loading');
            processBtn.disabled = false;
            processBtn.innerHTML = originalText;
            return;
        }

        try {
            const results = [];
            
            for (const file of selectedFiles) {
                const result = await eel.process_single_file(file.path)();
                results.push(result);
            }
            
            processingSection.classList.add('hidden');
            displayResults(results);
            announceStatus('Processing complete!');
            
        } catch (error) {
            console.error('Processing error:', error);
            processingSection.classList.add('hidden');
            uploadSection.classList.remove('hidden');
            alert('Error processing files: ' + error);
            announceStatus('Processing failed');
            
            // Remove loading state
            processBtn.classList.remove('btn-loading');
            processBtn.disabled = false;
            processBtn.innerHTML = originalText;
        }
    });

    newAnalysisBtn.addEventListener('click', () => {
        selectedFiles = [];
        fileInput.value = '';
        manualPathInput.value = '';
        resultsSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        announceStatus('Ready for new analysis');
        updateFileList();
        
        // Reset button state
        processBtn.classList.remove('btn-loading');
        processBtn.innerHTML = '<span aria-hidden="true">🔍</span> Process Files';
    });

    // ===== RESULTS DISPLAY =====
    function displayResults(results) {
        const passCount = results.filter(r => r.status === 'PASS').length;
        const failCount = results.filter(r => r.status === 'FAIL').length;
        const errorCount = results.filter(r => r.status === 'ERROR').length;
        const totalCount = results.length;
        
        const resultsHTML = `
            <div class="results">
                <div class="success-icon" aria-hidden="true">✅</div>
                <h2>Processing Complete!</h2>
                
                <div class="summary-stats">
                    <div class="stat-item">
                        <div class="stat-value" style="color: #10b981;">${passCount}</div>
                        <div class="stat-label">Passed</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" style="color: #ef4444;">${failCount}</div>
                        <div class="stat-label">Failed</div>
                    </div>
                    ${errorCount > 0 ? `
                    <div class="stat-item">
                        <div class="stat-value" style="color: #f59e0b;">${errorCount}</div>
                        <div class="stat-label">Errors</div>
                    </div>
                    ` : ''}
                    <div class="stat-item">
                        <div class="stat-value" style="color: rgba(255, 255, 255, 0.9);">${totalCount}</div>
                        <div class="stat-label">Total</div>
                    </div>
                </div>
                
                <div class="results-grid">
                    ${results.map(result => createResultCard(result)).join('')}
                </div>
                
                <button class="btn" id="newAnalysisBtn2" tabindex="0" style="background: rgba(168, 85, 247, 0.2); margin-top: 15px;">
                    <span aria-hidden="true">🔄</span> New Analysis
                </button>
            </div>
        `;
        
        resultsSection.innerHTML = resultsHTML;
        resultsSection.classList.remove('hidden');
        
        // Add event listeners for report buttons using event delegation
        // Remove any existing listeners first
        const newResultsSection = resultsSection.cloneNode(true);
        resultsSection.parentNode.replaceChild(newResultsSection, resultsSection);
        
        newResultsSection.addEventListener('click', (e) => {
            console.log('Click detected on:', e.target.className);
            
            // Check if clicked element or its parent is a button
            const button = e.target.closest('.view-report-btn, .open-report-btn');
            
            if (button) {
                const reportPath = button.getAttribute('data-report-path');
                const filename = button.getAttribute('data-filename');
                
                if (button.classList.contains('view-report-btn')) {
                    console.log('View report clicked:', reportPath, filename);
                    window.viewReportInline(reportPath, filename);
                } else if (button.classList.contains('open-report-btn')) {
                    console.log('Open report clicked:', reportPath);
                    window.openReportFile(reportPath);
                }
            }
        });
        
        newResultsSection.querySelector('#newAnalysisBtn2').addEventListener('click', () => {
            selectedFiles = [];
            fileInput.value = '';
            manualPathInput.value = '';
            newResultsSection.classList.add('hidden');
            uploadSection.classList.remove('hidden');
            announceStatus('Ready for new analysis');
            updateFileList();
            
            // Reset button state
            processBtn.classList.remove('btn-loading');
            processBtn.innerHTML = '<span aria-hidden="true">🔍</span> Process Files';
        });
    }

    function createResultCard(result) {
        console.log('Creating result card for:', result.filename, 'report_path:', result.report_path);
        
        const statusClass = result.status === 'PASS' ? 'pass' : 
                           result.status === 'FAIL' ? 'fail' : 'error';
        
        const statusIcon = result.status === 'PASS' ? '✓' :
                          result.status === 'FAIL' ? '✗' : '⚠';
        
        const borderColor = result.status === 'PASS' ? '#10b981' :
                           result.status === 'FAIL' ? '#ef4444' : '#f59e0b';
        
        const badgeClass = result.status === 'PASS' ? 'status-pass' :
                          result.status === 'FAIL' ? 'status-fail' : 'status-error';
        
        let issuesHTML = '';
        if (result.issues && result.issues.length > 0) {
            issuesHTML = `
                <div class="result-issues">
                    <div class="result-issues-title">⚠️ Issues Detected:</div>
                    <ul class="result-issues-list">
                        ${result.issues.map(issue => `<li>${issue}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        let reportLinkHTML = '';
        if (result.report_path) {
            console.log('Report path exists, creating buttons');
            const videoReportBtn = `
                <button class="report-btn view-report-btn" data-report-path="${result.report_path}" data-filename="${result.filename}" style="flex: 1;">
                    📊 Video Report
                </button>
            `;
            
            const detailedReportBtn = result.detailed_report_path ? `
                <button class="report-btn open-report-btn" data-report-path="${result.detailed_report_path}" style="flex: 1;">
                    📝 Detailed Report
                </button>
            ` : '';
            
            reportLinkHTML = `
                <div style="display: flex; gap: 8px; margin-top: 10px;">
                    ${videoReportBtn}
                    ${detailedReportBtn}
                </div>
            `;
        } else {
            console.log('No report_path found for', result.filename);
        }
        
        return `
            <div class="result-card" style="border-left: 4px solid ${borderColor};">
                <div class="result-card-header">
                    <h4 class="result-filename">${result.filename}</h4>
                    <span class="status-badge ${badgeClass}">${statusIcon} ${result.status}</span>
                </div>
                <div>
                    <p class="result-detail"><strong>Size:</strong> ${formatFileSize(result.size)}</p>
                    <p class="result-detail"><strong>Type:</strong> ${result.extension.toUpperCase()}</p>
                    ${result.status === 'PASS' ? '<p class="result-detail"><strong>Status:</strong> All quality checks passed</p>' : ''}
                    ${issuesHTML}
                    ${reportLinkHTML}
                </div>
            </div>
        `;
    }

    window.openReportFile = async function(reportPath) {
        console.log('openReportFile called with:', reportPath);
        
        if (typeof eel === 'undefined') {
            console.error('Eel not defined');
            alert('Cannot open report: Backend not connected');
            return;
        }
        
        try {
            console.log('Calling eel.open_report_file...');
            const result = await eel.open_report_file(reportPath)();
            console.log('Result:', result);
            announceStatus('Opening report file');
        } catch (error) {
            console.error('Error opening report:', error);
            alert('Could not open report: ' + error);
        }
    };

    // View report inline in modal
    window.viewReportInline = async function(reportPath, filename) {
        console.log('viewReportInline called with:', reportPath, filename);
        
        if (typeof eel === 'undefined') {
            console.error('Eel not defined');
            alert('Cannot load report: Backend not connected');
            return;
        }
        
        try {
            console.log('Calling eel.read_report_file...');
            const reportContent = await eel.read_report_file(reportPath)();
            console.log('Report content received:', reportContent);
            
            if (reportContent.success) {
                openReportModal(filename, reportContent.content);
                announceStatus('Report opened');
            } else {
                console.error('Report read failed:', reportContent.error);
                alert('Could not read report: ' + reportContent.error);
            }
        } catch (error) {
            console.error('Error loading report:', error);
            alert('Error loading report: ' + error);
        }
    };

    function openReportModal(filename, content) {
        // Create modal if it doesn't exist
        let modal = document.getElementById('reportModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'reportModal';
            modal.className = 'modal-overlay';
            modal.style.display = 'none';
            modal.setAttribute('role', 'dialog');
            modal.setAttribute('aria-modal', 'true');
            modal.setAttribute('aria-labelledby', 'reportModalTitle');
            
            modal.onclick = (e) => {
                if (e.target.id === 'reportModal') {
                    closeReportModal();
                }
            };
            
            document.body.appendChild(modal);
        }
        
        const modalHTML = `
            <div class="modal" onclick="event.stopPropagation()" style="max-width: 800px;">
                <button class="modal-close" onclick="closeReportModal();" tabindex="0"
                    aria-label="Close report dialog">×</button>
                <h2 id="reportModalTitle">📄 ${filename}</h2>
                <div class="report-content">
                    <pre style="background: rgba(0, 0, 0, 0.3); padding: 20px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.6; color: rgba(255, 255, 255, 0.9); max-height: 60vh; overflow-y: auto;">${content}</pre>
                </div>
                <button class="btn" onclick="closeReportModal();" tabindex="0"
                    style="margin-top: 20px; background: rgba(20, 184, 166, 0.3); box-shadow: 0 4px 15px rgba(20, 184, 166, 0.4);">
                    <span aria-hidden="true">✓</span> Close
                </button>
            </div>
        `;
        
        modal.innerHTML = modalHTML;
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        lastFocusedElement = document.activeElement;
        
        // Focus first focusable element
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) closeBtn.focus();
    }

    window.closeReportModal = function() {
        const modal = document.getElementById('reportModal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
            if (lastFocusedElement) {
                lastFocusedElement.focus();
            }
            announceStatus('Report dialog closed');
        }
    };

    // ===== ACCESSIBILITY FEATURES =====
    const contrastBtn = document.getElementById('contrastBtn');
    const contrastIcon = document.getElementById('contrastIcon');
    let isHighContrast = false;

    console.log('Contrast button found:', !!contrastBtn);

    if (localStorage) {
        try {
            const savedContrast = localStorage.getItem('medusight-high-contrast');
            if (savedContrast === 'true') {
                document.body.classList.add('high-contrast');
                isHighContrast = true;
                contrastIcon.textContent = '◑';
                contrastBtn.setAttribute('aria-pressed', 'true');
            }
        } catch (e) { }
    }

    if (contrastBtn) {
        contrastBtn.addEventListener('click', () => {
            console.log('Contrast button clicked');
            isHighContrast = !isHighContrast;

            if (isHighContrast) {
                // Turn OFF colorblind mode if it's on
                if (isColorblindMode) {
                    isColorblindMode = false;
                    document.body.classList.remove('colorblind-mode');
                    colorblindIcon.textContent = '👁️';
                    colorblindBtn.setAttribute('aria-pressed', 'false');
                    if (localStorage) {
                        try {
                            localStorage.setItem('medusight-colorblind-mode', false);
                        } catch (e) { }
                    }
                }
                
                document.body.classList.add('high-contrast');
                contrastIcon.textContent = '◑';
                contrastBtn.setAttribute('aria-pressed', 'true');
                announceStatus('High contrast mode enabled');
                console.log('High contrast ON');
            } else {
                document.body.classList.remove('high-contrast');
                contrastIcon.textContent = '◐';
                contrastBtn.setAttribute('aria-pressed', 'false');
                announceStatus('Normal mode enabled');
                console.log('High contrast OFF');
            }

            if (localStorage) {
                try {
                    localStorage.setItem('medusight-high-contrast', isHighContrast);
                } catch (e) { }
            }
        });

        contrastBtn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                contrastBtn.click();
            }
        });
    }

    const colorblindBtn = document.getElementById('colorblindBtn');
    const colorblindIcon = document.getElementById('colorblindIcon');
    let isColorblindMode = false;

    console.log('Colorblind button found:', !!colorblindBtn);

    if (localStorage) {
        try {
            const savedColorblind = localStorage.getItem('medusight-colorblind-mode');
            if (savedColorblind === 'true') {
                document.body.classList.add('colorblind-mode');
                isColorblindMode = true;
                colorblindIcon.textContent = '✓';
                colorblindBtn.setAttribute('aria-pressed', 'true');
            }
        } catch (e) { }
    }

    if (colorblindBtn) {
        colorblindBtn.addEventListener('click', () => {
            console.log('Colorblind button clicked');
            isColorblindMode = !isColorblindMode;

            if (isColorblindMode) {
                // Turn OFF high contrast mode if it's on
                if (isHighContrast) {
                    isHighContrast = false;
                    document.body.classList.remove('high-contrast');
                    contrastIcon.textContent = '◐';
                    contrastBtn.setAttribute('aria-pressed', 'false');
                    if (localStorage) {
                        try {
                            localStorage.setItem('medusight-high-contrast', false);
                        } catch (e) { }
                    }
                }
                
                document.body.classList.add('colorblind-mode');
                colorblindIcon.textContent = '✓';
                colorblindBtn.setAttribute('aria-pressed', 'true');
                announceStatus('Colorblind friendly mode enabled');
                console.log('Colorblind mode ON');
            } else {
                document.body.classList.remove('colorblind-mode');
                colorblindIcon.textContent = '👁️';
                colorblindBtn.setAttribute('aria-pressed', 'false');
                announceStatus('Normal colors enabled');
                console.log('Colorblind mode OFF');
            }

            if (localStorage) {
                try {
                    localStorage.setItem('medusight-colorblind-mode', isColorblindMode);
                } catch (e) { }
            }
        });

        colorblindBtn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                colorblindBtn.click();
            }
        });
    }

    // ESC key to close modals
    document.addEventListener('keydown', (e) => {
        const licenseModal = document.getElementById('licenseModal');
        const standardsModal = document.getElementById('standardsModal');
        const reportModal = document.getElementById('reportModal');

        if (e.key === 'Escape') {
            if (licenseModal && licenseModal.style.display === 'flex') {
                closeLicenseModal();
            } else if (standardsModal && standardsModal.style.display === 'flex') {
                closeStandardsModal();
            } else if (reportModal && reportModal.style.display === 'flex') {
                closeReportModal();
            }
        }
    });
});