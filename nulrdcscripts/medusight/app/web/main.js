// ===== GLOBAL STATE =====
let selectedFiles = [];
let currentMode = 'video';
let lastFocusedElement = null;
let isHighContrast = false;
let isColorblindMode = false;

// ===== UTILITY FUNCTIONS =====
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
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

function trapFocus(modal) {
    const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (firstElement) {
        firstElement.focus();
    }

    const handleTabKey = (e) => {
        if (e.key === 'Tab') {
            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    };

    modal.addEventListener('keydown', handleTabKey);
}

// ===== MODAL FUNCTIONS =====
function openLicenseModal() {
    lastFocusedElement = document.activeElement;
    const modal = document.getElementById('licenseModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        trapFocus(modal);
        announceStatus('License dialog opened');
    }
}

function closeLicenseModal() {
    const modal = document.getElementById('licenseModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }
        announceStatus('License dialog closed');
    }
}

function openStandardsModal() {
    lastFocusedElement = document.activeElement;
    const modal = document.getElementById('standardsModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        trapFocus(modal);
        announceStatus('Standards reference opened');
    }
}

function closeStandardsModal() {
    const modal = document.getElementById('standardsModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }
        announceStatus('Standards dialog closed');
    }
}

function openReportModal(filename, content) {
    let modal = document.getElementById('reportModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'reportModal';
        modal.className = 'modal-overlay';
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
            <div class="report-modal-header">
                <h2 id="reportModalTitle" style="color: #14b8a6; margin-bottom: 8px; font-size: 22px;">
                    <span class="report-icon" style="font-size: 28px;">📊</span>
                    Video Quality Report
                </h2>
                <div class="report-filename" style="color: rgba(255, 255, 255, 0.6); font-size: 13px; font-family: 'Courier New', monospace;">${filename}</div>
            </div>
            <div class="report-content" style="flex: 1; overflow-y: auto; margin: 20px 0; background: rgba(0, 0, 0, 0.3); border-radius: 8px; padding: 20px; max-height: 50vh;">
                <pre class="report-text" style="font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.6; color: rgba(255, 255, 255, 0.9); white-space: pre-wrap; word-wrap: break-word; margin: 0;">${content}</pre>
            </div>
            <div style="display: flex; gap: 10px;">
                <button class="modal-btn btn-copy" onclick="copyReportToClipboard();" tabindex="0"
                    style="flex: 1; padding: 12px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; background: rgba(168, 85, 247, 0.3); color: white;">
                    📋 Copy to Clipboard
                </button>
                <button class="modal-btn btn-close-modal" onclick="closeReportModal();" tabindex="0"
                    style="flex: 1; padding: 12px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; background: rgba(20, 184, 166, 0.3); color: white;">
                    ✓ Close
                </button>
            </div>
        </div>
    `;

    modal.innerHTML = modalHTML;
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    lastFocusedElement = document.activeElement;

    const closeBtn = modal.querySelector('.modal-close');
    if (closeBtn) closeBtn.focus();
}

function closeReportModal() {
    const modal = document.getElementById('reportModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }
        announceStatus('Report dialog closed');
    }
}

function copyReportToClipboard() {
    const reportText = document.querySelector('.report-text');
    if (reportText) {
        const text = reportText.textContent;
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                announceStatus('Report copied to clipboard');
                alert('Report copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy:', err);
                fallbackCopyTextToClipboard(text);
            });
        } else {
            fallbackCopyTextToClipboard(text);
        }
    }
}

function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        const successful = document.execCommand('copy');
        if (successful) {
            announceStatus('Report copied to clipboard');
            alert('Report copied to clipboard!');
        }
    } catch (err) {
        console.error('Fallback: Could not copy text', err);
    }

    document.body.removeChild(textArea);
}

// Make modal functions global
window.openLicenseModal = openLicenseModal;
window.closeLicenseModal = closeLicenseModal;
window.openStandardsModal = openStandardsModal;
window.closeStandardsModal = closeStandardsModal;
window.closeReportModal = closeReportModal;
window.copyReportToClipboard = copyReportToClipboard;

// ===== SETTINGS FUNCTIONS =====
function getProcessingSettings() {
    // Default settings - no UI controls for now, using sensible defaults
    return {
        cropMode: 'auto',
        manualCrop: null,
        sampleInterval: 900,
        analyzeAudio: true,
        audioStandard: 'broadcast',
        targetLufs: null,
        maxTruePeak: null
    };
}

// ===== FILE LIST FUNCTIONS =====
function updateFileList() {
    const fileList = document.getElementById('fileList');
    const processBtn = document.getElementById('processBtn');

    if (!fileList || !processBtn) return;

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
            <button class="remove-btn" onclick="removeFile(${index})" 
                aria-label="Remove ${file.name}">Remove</button>
        </div>
    `).join('');
}

window.removeFile = function (index) {
    if (index >= 0 && index < selectedFiles.length) {
        const fileName = selectedFiles[index].name;
        selectedFiles.splice(index, 1);
        announceStatus(`${fileName} removed`);
        updateFileList();
    }
};

// ===== RESULTS DISPLAY =====
function displayResults(results) {
    const resultsSection = document.getElementById('resultsSection');
    if (!resultsSection) return;

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
            
            <button class="btn" id="newAnalysisBtn2" tabindex="0" 
                style="background: rgba(168, 85, 247, 0.2); margin-top: 15px;">
                <span aria-hidden="true">🔄</span> New Analysis
            </button>
        </div>
    `;

    resultsSection.innerHTML = resultsHTML;
    resultsSection.classList.remove('hidden');

    // Add event listeners
    resultsSection.addEventListener('click', handleResultsClick);

    const newAnalysisBtn2 = document.getElementById('newAnalysisBtn2');
    if (newAnalysisBtn2) {
        newAnalysisBtn2.addEventListener('click', resetToUpload);
    }
}

function handleResultsClick(e) {
    const button = e.target.closest('.view-report-btn, .open-report-btn');

    if (button) {
        const reportPath = button.getAttribute('data-report-path');
        const filename = button.getAttribute('data-filename');

        if (button.classList.contains('view-report-btn')) {
            viewReportInline(reportPath, filename);
        } else if (button.classList.contains('open-report-btn')) {
            openReportFile(reportPath);
        }
    }
}

function createResultCard(result) {
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
        const videoReportBtn = `
            <button class="report-btn view-report-btn" 
                data-report-path="${result.report_path}" 
                data-filename="${result.filename}" 
                style="flex: 1; background: rgba(168, 85, 247, 0.2); border: 1px solid rgba(168, 85, 247, 0.4); color: white; padding: 10px 12px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500; transition: all 0.3s ease;">
                📊 Video Report
            </button>
        `;

        const framesReportBtn = result.frames_report_path ? `
            <button class="report-btn view-report-btn" 
                data-report-path="${result.frames_report_path}" 
                data-filename="${result.filename}" 
                style="flex: 1; background: rgba(20, 184, 166, 0.2); border: 1px solid rgba(20, 184, 166, 0.4); color: white; padding: 10px 12px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500; transition: all 0.3s ease;">
                🎞️ Frames Report
            </button>
        ` : '';

        const audioReportBtn = result.audio_report_path ? `
            <button class="report-btn view-report-btn" 
                data-report-path="${result.audio_report_path}" 
                data-filename="${result.filename}" 
                style="flex: 1; background: rgba(139, 92, 246, 0.2); border: 1px solid rgba(139, 92, 246, 0.4); color: white; padding: 10px 12px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500; transition: all 0.3s ease;">
                🔊 Audio Report
            </button>
        ` : '';

        reportLinkHTML = `
            <div class="report-buttons-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; margin-top: 12px;">
                ${videoReportBtn}
                ${framesReportBtn}
                ${audioReportBtn}
            </div>
        `;
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

// ===== REPORT FUNCTIONS =====
async function openReportFile(reportPath) {
    if (typeof eel === 'undefined') {
        alert('Cannot open report: Backend not connected');
        return;
    }

    try {
        await eel.open_report_file(reportPath)();
        announceStatus('Opening report file');
    } catch (error) {
        console.error('Error opening report:', error);
        alert('Could not open report: ' + error);
    }
}

async function viewReportInline(reportPath, filename) {
    if (typeof eel === 'undefined') {
        alert('Cannot load report: Backend not connected');
        return;
    }

    try {
        const reportContent = await eel.read_report_file(reportPath)();

        if (reportContent.success) {
            openReportModal(filename, reportContent.content);
            announceStatus('Report opened');
        } else {
            alert('Could not read report: ' + reportContent.error);
        }
    } catch (error) {
        console.error('Error loading report:', error);
        alert('Error loading report: ' + error);
    }
}

window.openReportFile = openReportFile;
window.viewReportInline = viewReportInline;

// ===== RESET FUNCTIONS =====
function resetToUpload() {
    selectedFiles = [];
    const fileInput = document.getElementById('fileInput');
    const manualPathInput = document.getElementById('manualPath');

    if (fileInput) fileInput.value = '';
    if (manualPathInput) manualPathInput.value = '';

    const resultsSection = document.getElementById('resultsSection');
    const uploadSection = document.getElementById('uploadSection');
    const processBtn = document.getElementById('processBtn');

    if (resultsSection) resultsSection.classList.add('hidden');
    if (uploadSection) uploadSection.classList.remove('hidden');
    if (processBtn) {
        processBtn.classList.remove('btn-loading');
        processBtn.disabled = false;
        processBtn.innerHTML = '<span aria-hidden="true">🔍</span> Process Files';
    }

    announceStatus('Ready for new analysis');
    updateFileList();
}

// ===== PROCESSING =====
async function processFiles() {
    const processBtn = document.getElementById('processBtn');
    const uploadSection = document.getElementById('uploadSection');
    const processingSection = document.getElementById('processingSection');

    if (selectedFiles.length === 0) {
        alert('Please select files first');
        return;
    }

    const settings = getProcessingSettings();

    // Add loading state
    processBtn.classList.add('btn-loading');
    processBtn.disabled = true;
    const originalText = processBtn.innerHTML;
    processBtn.innerHTML = '<span class="spinner" style="display: inline-block; width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 1s linear infinite;"></span> Processing...';

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
            const result = await eel.process_single_file(
                file.path,
                settings.cropMode,
                settings.manualCrop,
                settings.sampleInterval,
                settings.analyzeAudio,
                settings.audioStandard,
                settings.targetLufs,
                settings.maxTruePeak
            )();
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

        processBtn.classList.remove('btn-loading');
        processBtn.disabled = false;
        processBtn.innerHTML = originalText;
    }
}

// ===== MANUAL PATH FUNCTIONS (EMERGENCY FALLBACK ONLY) =====

function toggleManualPathInput() {
    const manualPathSection = document.getElementById('manualPathSection');

    if (manualPathSection) {
        if (manualPathSection.style.display === 'none') {
            manualPathSection.style.display = 'block';
            announceStatus('Manual path input enabled');

            // Auto-focus the input
            const manualPathInput = document.getElementById('manualPath');
            if (manualPathInput) {
                setTimeout(() => manualPathInput.focus(), 100);
            }
        } else {
            manualPathSection.style.display = 'none';
            announceStatus('Manual path input hidden');
        }
    }

    // Close the utility menu
    const utilityMenu = document.getElementById('utilityMenu');
    const menuToggle = document.getElementById('menuToggle');
    const menuIcon = document.getElementById('menuIcon');

    if (utilityMenu && utilityMenu.classList.contains('active')) {
        utilityMenu.classList.remove('active');
        if (menuIcon) menuIcon.textContent = '☰';
        if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
    }
}

async function processManualPath() {
    const manualPathInput = document.getElementById('manualPath');
    const pathValue = manualPathInput ? manualPathInput.value.trim() : '';

    if (!pathValue) {
        alert('Please enter a file or folder path');
        return;
    }

    const settings = getProcessingSettings();

    // Show loading state
    const processBtn = document.getElementById('processBtn');
    const uploadSection = document.getElementById('uploadSection');
    const processingSection = document.getElementById('processingSection');

    if (processBtn) {
        processBtn.classList.add('btn-loading');
        processBtn.disabled = true;
    }

    if (uploadSection) uploadSection.classList.add('hidden');
    if (processingSection) processingSection.classList.remove('hidden');

    announceStatus('Processing manual path. Please wait.');

    if (typeof eel === 'undefined') {
        alert('Eel backend not connected');
        if (processingSection) processingSection.classList.add('hidden');
        if (uploadSection) uploadSection.classList.remove('hidden');
        if (processBtn) {
            processBtn.classList.remove('btn-loading');
            processBtn.disabled = false;
        }
        return;
    }

    try {
        const result = await eel.process_manual_path(
            pathValue,
            settings.cropMode,
            settings.manualCrop,
            settings.sampleInterval,
            settings.analyzeAudio,
            settings.audioStandard,
            settings.targetLufs,
            settings.maxTruePeak
        )();

        if (result.success) {
            if (result.is_folder) {
                // Folder was entered - add files to selection and return to upload view
                const newFiles = result.files.map(file => ({
                    name: file.filename,
                    path: file.path,
                    size: file.size
                }));

                selectedFiles = [...selectedFiles, ...newFiles];

                // Clear the manual path input
                if (manualPathInput) manualPathInput.value = '';

                // Return to upload view
                if (processingSection) processingSection.classList.add('hidden');
                if (uploadSection) uploadSection.classList.remove('hidden');
                if (processBtn) {
                    processBtn.classList.remove('btn-loading');
                    processBtn.disabled = false;
                }

                updateFileList();
                announceStatus(`Added ${newFiles.length} files from folder`);
            } else {
                // Single file was processed - show results
                if (processingSection) processingSection.classList.add('hidden');
                displayResults([result.result]);

                // Clear the manual path input
                if (manualPathInput) manualPathInput.value = '';
            }
        } else {
            alert('Error: ' + result.error);

            // Return to upload view
            if (processingSection) processingSection.classList.add('hidden');
            if (uploadSection) uploadSection.classList.remove('hidden');
            if (processBtn) {
                processBtn.classList.remove('btn-loading');
                processBtn.disabled = false;
            }
        }
    } catch (error) {
        console.error('Error processing path:', error);
        alert('Error processing path: ' + error);

        // Return to upload view
        if (processingSection) processingSection.classList.add('hidden');
        if (uploadSection) uploadSection.classList.remove('hidden');
        if (processBtn) {
            processBtn.classList.remove('btn-loading');
            processBtn.disabled = false;
        }
    }
}

// Make functions globally accessible
window.toggleManualPathInput = toggleManualPathInput;
window.processManualPath = processManualPath;

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function () {
    console.log('=== MeduSight Initialized ===');

    // Test Eel connection
    if (typeof eel !== 'undefined') {
        eel.test_connection()((result) => {
            console.log('Eel connection:', result);
        });
    }

    // Get DOM elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadMenu = document.getElementById('uploadMenu');
    const menuSelectFiles = document.getElementById('menuSelectFiles');
    const menuSelectFolder = document.getElementById('menuSelectFolder');
    const processBtn = document.getElementById('processBtn');
    const newAnalysisBtn = document.getElementById('newAnalysisBtn');
    const modeBtns = document.querySelectorAll('.mode-btn');
    const uploadInfo = document.getElementById('uploadInfo');

    // ===== MODE SWITCHING =====
    modeBtns.forEach(btn => {
        btn.addEventListener('click', async function (e) {
            e.preventDefault();
            e.stopPropagation();

            modeBtns.forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-pressed', 'false');
            });

            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');
            currentMode = btn.dataset.mode;

            if (typeof eel !== 'undefined') {
                try {
                    await eel.set_file_mode(currentMode)();
                    console.log('Mode set to:', currentMode);
                } catch (error) {
                    console.error('Error setting mode:', error);
                }
            }

            if (currentMode === 'video') {
                if (fileInput) fileInput.accept = '.mkv,.mp4';
                if (uploadInfo) uploadInfo.textContent = 'Supports: MKV, MP4 (multiple files supported)';
                announceStatus('Switched to video file mode');
            } else {
                if (fileInput) fileInput.accept = '.xml';
                if (uploadInfo) uploadInfo.textContent = 'Supports: XML (QCTools output - multiple files supported)';
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

        document.addEventListener('click', (e) => {
            if (!menuToggle.contains(e.target) && !utilityMenu.contains(e.target)) {
                if (utilityMenu.classList.contains('active')) {
                    utilityMenu.classList.remove('active');
                    menuIcon.textContent = '☰';
                    menuToggle.setAttribute('aria-expanded', 'false');
                }
            }
        });

        utilityMenu.querySelectorAll('button').forEach(menuBtn => {
            menuBtn.addEventListener('click', () => {
                utilityMenu.classList.remove('active');
                menuIcon.textContent = '☰';
                menuToggle.setAttribute('aria-expanded', 'false');
            });
        });

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
    if (uploadArea) {
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.add('drag-error');
            alert('⚠️ Drag and drop is not supported.\n\nPlease use "Select Files" or "Select Folder" buttons instead.');
            announceStatus('Please use the file selection buttons');
            setTimeout(() => {
                uploadArea.classList.remove('drag-error');
            }, 500);
        });

        // Upload area click
        uploadArea.addEventListener('click', (e) => {
            if (e.target.closest('.upload-menu')) return;
            if (uploadMenu) {
                uploadMenu.style.display = 'block';
                uploadMenu.style.left = '50%';
                uploadMenu.style.top = '50%';
                uploadMenu.style.transform = 'translate(-50%, -50%)';
                if (menuSelectFiles) menuSelectFiles.focus();
                announceStatus('Upload menu opened. Choose files or folder.');
            }
        });

        uploadArea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                if (uploadMenu) {
                    uploadMenu.style.display = 'block';
                    uploadMenu.style.left = '50%';
                    uploadMenu.style.top = '50%';
                    uploadMenu.style.transform = 'translate(-50%, -50%)';
                    if (menuSelectFiles) menuSelectFiles.focus();
                    announceStatus('Upload menu opened. Choose files or folder.');
                }
            }
        });
    }

    // Close upload menu when clicking outside
    document.addEventListener('click', (e) => {
        if (uploadArea && uploadMenu && !uploadArea.contains(e.target)) {
            uploadMenu.style.display = 'none';
        }
    });

    // ===== FILE SELECTION =====
    if (menuSelectFiles) {
        menuSelectFiles.addEventListener('click', async (e) => {
            e.stopPropagation();
            if (uploadMenu) uploadMenu.style.display = 'none';
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

        menuSelectFiles.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (menuSelectFolder) menuSelectFolder.focus();
            } else if (e.key === 'Escape') {
                if (uploadMenu) uploadMenu.style.display = 'none';
                if (uploadArea) uploadArea.focus();
            }
        });
    }

    if (menuSelectFolder) {
        menuSelectFolder.addEventListener('click', async (e) => {
            e.stopPropagation();
            if (uploadMenu) uploadMenu.style.display = 'none';
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

        menuSelectFolder.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (menuSelectFiles) menuSelectFiles.focus();
            } else if (e.key === 'Escape') {
                if (uploadMenu) uploadMenu.style.display = 'none';
                if (uploadArea) uploadArea.focus();
            }
        });
    }

    // ===== PROCESS BUTTON =====
    if (processBtn) {
        processBtn.addEventListener('click', processFiles);
    }

    // ===== NEW ANALYSIS BUTTON =====
    if (newAnalysisBtn) {
        newAnalysisBtn.addEventListener('click', resetToUpload);
    }

    // ===== ACCESSIBILITY FEATURES =====
    const contrastBtn = document.getElementById('contrastBtn');
    const contrastIcon = document.getElementById('contrastIcon');

    // Load saved high contrast preference
    if (localStorage) {
        try {
            const savedContrast = localStorage.getItem('medusight-high-contrast');
            if (savedContrast === 'true') {
                document.body.classList.add('high-contrast');
                isHighContrast = true;
                if (contrastIcon) contrastIcon.textContent = '◑';
                if (contrastBtn) contrastBtn.setAttribute('aria-pressed', 'true');
            }
        } catch (e) {
            console.error('localStorage error:', e);
        }
    }

    if (contrastBtn) {
        contrastBtn.addEventListener('click', () => {
            isHighContrast = !isHighContrast;

            if (isHighContrast) {
                // Turn off colorblind mode if active
                if (isColorblindMode) {
                    isColorblindMode = false;
                    document.body.classList.remove('colorblind-mode');
                    const colorblindIcon = document.getElementById('colorblindIcon');
                    const colorblindBtn = document.getElementById('colorblindBtn');
                    if (colorblindIcon) colorblindIcon.textContent = '👁️';
                    if (colorblindBtn) colorblindBtn.setAttribute('aria-pressed', 'false');
                    if (localStorage) {
                        try {
                            localStorage.setItem('medusight-colorblind-mode', 'false');
                        } catch (e) { }
                    }
                }

                document.body.classList.add('high-contrast');
                if (contrastIcon) contrastIcon.textContent = '◑';
                contrastBtn.setAttribute('aria-pressed', 'true');
                announceStatus('High contrast mode enabled');
            } else {
                document.body.classList.remove('high-contrast');
                if (contrastIcon) contrastIcon.textContent = '◐';
                contrastBtn.setAttribute('aria-pressed', 'false');
                announceStatus('Normal mode enabled');
            }

            if (localStorage) {
                try {
                    localStorage.setItem('medusight-high-contrast', isHighContrast.toString());
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

    // Load saved colorblind preference
    if (localStorage) {
        try {
            const savedColorblind = localStorage.getItem('medusight-colorblind-mode');
            if (savedColorblind === 'true') {
                document.body.classList.add('colorblind-mode');
                isColorblindMode = true;
                if (colorblindIcon) colorblindIcon.textContent = '✓';
                if (colorblindBtn) colorblindBtn.setAttribute('aria-pressed', 'true');
            }
        } catch (e) {
            console.error('localStorage error:', e);
        }
    }

    if (colorblindBtn) {
        colorblindBtn.addEventListener('click', () => {
            isColorblindMode = !isColorblindMode;

            if (isColorblindMode) {
                // Turn off high contrast if active
                if (isHighContrast) {
                    isHighContrast = false;
                    document.body.classList.remove('high-contrast');
                    if (contrastIcon) contrastIcon.textContent = '◐';
                    if (contrastBtn) contrastBtn.setAttribute('aria-pressed', 'false');
                    if (localStorage) {
                        try {
                            localStorage.setItem('medusight-high-contrast', 'false');
                        } catch (e) { }
                    }
                }

                document.body.classList.add('colorblind-mode');
                if (colorblindIcon) colorblindIcon.textContent = '✓';
                colorblindBtn.setAttribute('aria-pressed', 'true');
                announceStatus('Colorblind friendly mode enabled');
            } else {
                document.body.classList.remove('colorblind-mode');
                if (colorblindIcon) colorblindIcon.textContent = '👁️';
                colorblindBtn.setAttribute('aria-pressed', 'false');
                announceStatus('Normal colors enabled');
            }

            if (localStorage) {
                try {
                    localStorage.setItem('medusight-colorblind-mode', isColorblindMode.toString());
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

    // ===== KEYBOARD SHORTCUT FOR EMERGENCY MANUAL PATH =====
    // Ctrl+Shift+M or Cmd+Shift+M to toggle manual path input
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'M') {
            e.preventDefault();
            toggleManualPathInput();
        }
    });

    // ===== GLOBAL KEYBOARD SHORTCUTS =====
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

    // ===== INITIAL SETUP =====
    updateFileList();

    console.log('=== Initialization Complete ===');
});