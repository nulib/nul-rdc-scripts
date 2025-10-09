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
    console.log('=== SCRIPT LOADED ==='); // First thing to run
    console.log('DOMContentLoaded fired');
    
    // Test Eel connection
    eel.test_connection()(function(result) {
        console.log('Eel test result:', result);
    });
    
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

    console.log('Elements:', {
        uploadArea: !!uploadArea,
        menuSelectFiles: !!menuSelectFiles,
        menuSelectFolder: !!menuSelectFolder,
        modeBtns: modeBtns.length
    });

    let selectedFiles = [];
    let currentMode = 'video';

    // ===== MODE SWITCHING =====
    modeBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            modeBtns.forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-pressed', 'false');
            });
            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');
            currentMode = btn.dataset.mode;
            
            // Store in window object so it's accessible everywhere
            window.currentFileMode = currentMode;
            
            console.log('Mode switched to:', currentMode); // Debug log
            
            // Tell Python about the mode change
            try {
                await eel.set_file_mode(currentMode)();
                console.log('Mode sent to Python:', currentMode);
            } catch (error) {
                console.error('Error setting mode in Python:', error);
            }

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

            selectedFiles = [];
            updateFileList();
        });
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
    
        // Close menu when a menu item is clicked
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

    // ===== DRAG AND DROP DISABLED =====
    // Drag and drop doesn't work because browsers don't expose file paths
    // Users must use the native file dialogs instead
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        alert('Drag and drop is not supported. Please use "Select Files" or "Select Folder" buttons.');
        announceStatus('Please use the file selection buttons');
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
                    announceStatus('No QCTools files found in folder');
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
        if (selectedFiles.length === 0) {
            fileList.classList.add('hidden');
            processBtn.disabled = true;
            processBtn.setAttribute('aria-disabled', 'true');
            return;
        }

        fileList.classList.remove('hidden');
        processBtn.disabled = false;
        processBtn.removeAttribute('aria-disabled');

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
        e.preventDefault(); // Prevent any default behavior
        
        if (selectedFiles.length === 0) {
            alert('Please select files first');
            return;
        }
        
        // Disable button to prevent double-clicks
        processBtn.disabled = true;
        
        uploadSection.classList.add('hidden');
        processingSection.classList.remove('hidden');
        announceStatus('Processing files. Please wait.');

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
        } finally {
            // Re-enable button
            processBtn.disabled = false;
        }
    }, { once: false }); // Ensure event doesn't fire twice

    newAnalysisBtn.addEventListener('click', () => {
        selectedFiles = [];
        fileInput.value = '';
        resultsSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        announceStatus('Ready for new analysis');
        updateFileList();
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
                
                <div class="summary-stats" style="display: flex; justify-content: space-around; margin: 30px 0; padding: 20px; background: rgba(168, 85, 247, 0.1); border-radius: 12px;">
                    <div class="stat-item" style="text-align: center;">
                        <div style="font-size: 36px; font-weight: 700; color: #10b981;">${passCount}</div>
                        <div style="color: rgba(255, 255, 255, 0.7); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px;">Passed</div>
                    </div>
                    <div class="stat-item" style="text-align: center;">
                        <div style="font-size: 36px; font-weight: 700; color: #ef4444;">${failCount}</div>
                        <div style="color: rgba(255, 255, 255, 0.7); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px;">Failed</div>
                    </div>
                    ${errorCount > 0 ? `
                    <div class="stat-item" style="text-align: center;">
                        <div style="font-size: 36px; font-weight: 700; color: #f59e0b;">${errorCount}</div>
                        <div style="color: rgba(255, 255, 255, 0.7); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px;">Errors</div>
                    </div>
                    ` : ''}
                    <div class="stat-item" style="text-align: center;">
                        <div style="font-size: 36px; font-weight: 700; color: rgba(255, 255, 255, 0.9);">${totalCount}</div>
                        <div style="color: rgba(255, 255, 255, 0.7); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px;">Total</div>
                    </div>
                </div>
                
                <div class="results-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; margin: 20px 0;">
                    ${results.map(result => createResultCard(result)).join('')}
                </div>
                
                <button class="btn" id="newAnalysisBtn2" tabindex="0" style="background: rgba(168, 85, 247, 0.2); margin-top: 20px;">
                    <span aria-hidden="true">🔄</span> New Analysis
                </button>
            </div>
        `;
        
        resultsSection.innerHTML = resultsHTML;
        resultsSection.classList.remove('hidden');
        
        document.getElementById('newAnalysisBtn2').addEventListener('click', () => {
            selectedFiles = [];
            fileInput.value = '';
            resultsSection.classList.add('hidden');
            uploadSection.classList.remove('hidden');
            announceStatus('Ready for new analysis');
            updateFileList();
        });
    }

    function createResultCard(result) {
        const statusClass = result.status === 'PASS' ? 'pass' : 
                           result.status === 'FAIL' ? 'fail' : 'error';
        
        const statusIcon = result.status === 'PASS' ? '✓' :
                          result.status === 'FAIL' ? '✗' : '⚠';
        
        const borderColor = result.status === 'PASS' ? '#10b981' :
                           result.status === 'FAIL' ? '#ef4444' : '#f59e0b';
        
        const badgeColor = result.status === 'PASS' ? 'background: #10b981; color: white;' :
                          result.status === 'FAIL' ? 'background: #ef4444; color: white;' :
                          'background: #f59e0b; color: #1a1a2e;';
        
        let issuesHTML = '';
        if (result.issues && result.issues.length > 0) {
            issuesHTML = `
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                    <strong style="color: #ef4444; display: block; margin-bottom: 8px;">⚠️ Issues Detected:</strong>
                    <ul style="margin: 0; padding-left: 20px; font-size: 13px;">
                        ${result.issues.map(issue => `<li style="margin: 4px 0; color: rgba(255, 255, 255, 0.8);">${issue}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        let reportLinkHTML = '';
        if (result.report_path) {
            reportLinkHTML = `
                <button onclick="openReportFile('${result.report_path}')" 
                    style="margin-top: 12px; padding: 8px 16px; background: rgba(168, 85, 247, 0.3); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; transition: all 0.3s;">
                    📄 View Full Report
                </button>
            `;
        }
        
        return `
            <div class="result-card" style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 12px; padding: 20px; border-left: 4px solid ${borderColor}; transition: transform 0.2s;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h4 style="color: rgba(255, 255, 255, 0.95); font-size: 16px; word-break: break-word; flex: 1; margin: 0 10px 0 0;">${result.filename}</h4>
                    <span style="padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 700; text-transform: uppercase; white-space: nowrap; ${badgeColor}">${statusIcon} ${result.status}</span>
                </div>
                <div>
                    <p style="margin: 8px 0; color: rgba(255, 255, 255, 0.7); font-size: 14px;"><strong style="color: rgba(255, 255, 255, 0.9);">Size:</strong> ${formatFileSize(result.size)}</p>
                    <p style="margin: 8px 0; color: rgba(255, 255, 255, 0.7); font-size: 14px;"><strong style="color: rgba(255, 255, 255, 0.9);">Type:</strong> ${result.extension.toUpperCase()}</p>
                    ${result.status === 'PASS' ? '<p style="margin: 8px 0; color: rgba(255, 255, 255, 0.7); font-size: 14px;"><strong style="color: rgba(255, 255, 255, 0.9);">Status:</strong> All quality checks passed</p>' : ''}
                    ${issuesHTML}
                    ${reportLinkHTML}
                </div>
            </div>
        `;
    }

    window.openReportFile = async function(reportPath) {
        try {
            await eel.open_report_file(reportPath)();
            announceStatus('Opening report file');
        } catch (error) {
            alert('Could not open report: ' + error);
        }
    };

    // ===== ACCESSIBILITY FEATURES =====
    const contrastBtn = document.getElementById('contrastBtn');
    const contrastIcon = document.getElementById('contrastIcon');
    const contrastText = document.getElementById('contrastText');
    let isHighContrast = false;

    if (localStorage) {
        try {
            const savedContrast = localStorage.getItem('medusight-high-contrast');
            if (savedContrast === 'true') {
                document.body.classList.add('high-contrast');
                isHighContrast = true;
                contrastIcon.textContent = '◑';
                contrastText.textContent = 'Normal Mode';
                contrastBtn.setAttribute('aria-pressed', 'true');
            }
        } catch (e) { }
    }

    contrastBtn.addEventListener('click', () => {
        isHighContrast = !isHighContrast;

        if (isHighContrast) {
            document.body.classList.add('high-contrast');
            contrastIcon.textContent = '◑';
            contrastText.textContent = 'Normal Mode';
            contrastBtn.setAttribute('aria-pressed', 'true');
            announceStatus('High contrast mode enabled');
        } else {
            document.body.classList.remove('high-contrast');
            contrastIcon.textContent = '◐';
            contrastText.textContent = 'High Contrast';
            contrastBtn.setAttribute('aria-pressed', 'false');
            announceStatus('Normal mode enabled');
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

    const colorblindBtn = document.getElementById('colorblindBtn');
    const colorblindIcon = document.getElementById('colorblindIcon');
    const colorblindText = document.getElementById('colorblindText');
    let isColorblindMode = false;

    if (localStorage) {
        try {
            const savedColorblind = localStorage.getItem('medusight-colorblind-mode');
            if (savedColorblind === 'true') {
                document.body.classList.add('colorblind-mode');
                isColorblindMode = true;
                colorblindIcon.textContent = '✓';
                colorblindText.textContent = 'Normal Colors';
                colorblindBtn.setAttribute('aria-pressed', 'true');
            }
        } catch (e) { }
    }

    colorblindBtn.addEventListener('click', () => {
        isColorblindMode = !isColorblindMode;

        if (isColorblindMode) {
            document.body.classList.add('colorblind-mode');
            colorblindIcon.textContent = '✓';
            colorblindText.textContent = 'Normal Colors';
            colorblindBtn.setAttribute('aria-pressed', 'true');
            announceStatus('Colorblind friendly mode enabled');
        } else {
            document.body.classList.remove('colorblind-mode');
            colorblindIcon.textContent = '👁️';
            colorblindText.textContent = 'Colorblind Mode';
            colorblindBtn.setAttribute('aria-pressed', 'false');
            announceStatus('Normal colors enabled');
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

    // ESC key to close modals
    document.addEventListener('keydown', (e) => {
        const licenseModal = document.getElementById('licenseModal');
        const standardsModal = document.getElementById('standardsModal');

        if (e.key === 'Escape') {
            if (licenseModal.style.display === 'flex') {
                closeLicenseModal();
            } else if (standardsModal.style.display === 'flex') {
                closeStandardsModal();
            }
        }
    });
});