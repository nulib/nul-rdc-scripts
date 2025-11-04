// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function () {
    console.log('Tessera JavaScript loaded');

    let cues = [];
    let currentContext = null;
    let cueIdCounter = 0;
    let currentAudioURL = null;
    let editingCueId = null;

    // Memory protection variables
    let sessionStartTime = Date.now();
    let totalAudioLoaded = 0;
    let hasShownMemoryWarning = false;

    const audio = document.getElementById('audio');
    const audioFile = document.getElementById('audioFile');
    const audioUploadBox = document.getElementById('audioUploadBox');
    const timeDisplay = document.getElementById('timeDisplay');
    const cueList = document.getElementById('cueList');
    const vttOutput = document.getElementById('vttOutput');
    const previewContent = document.getElementById('previewContent');
    const cueCount = document.getElementById('cueCount');
    const contextDisplay = document.getElementById('contextDisplay');

    console.log('Elements loaded:', {
        audio: !!audio,
        themeBtn: !!document.getElementById('themeDropdownBtn'),
        hamburger: !!document.getElementById('hamburgerBtn')
    });

    // Audio upload
    audioUploadBox.addEventListener('click', () => audioFile.click());
    audioUploadBox.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            audioFile.click();
        }
    });

    audioFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            if (currentAudioURL) {
                URL.revokeObjectURL(currentAudioURL);
            }

            // Track total audio loaded for memory management
            totalAudioLoaded += file.size;
            const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
            const totalLoadedMB = (totalAudioLoaded / (1024 * 1024)).toFixed(2);
            console.log(`Loading audio file: ${file.name} (${fileSizeMB} MB)`);
            console.log(`Total audio loaded this session: ${totalLoadedMB} MB`);

            // Warning for single large file (>2GB)
            if (file.size > 2 * 1024 * 1024 * 1024) {
                if (!confirm(`⚠️ Large File Warning\n\nThis file is ${fileSizeMB} MB, which may cause performance issues.\n\nContinue loading?`)) {
                    e.target.value = ''; // Clear the file input
                    return;
                }
            }

            // Memory warning if multiple large files loaded OR session is long (>3 hours)
            const sessionDurationHours = (Date.now() - sessionStartTime) / (1000 * 60 * 60);
            if (!hasShownMemoryWarning && (totalAudioLoaded > 3 * 1024 * 1024 * 1024 || sessionDurationHours > 3)) {
                hasShownMemoryWarning = true;

                // Auto-save session before showing warning
                if (cues.length > 0) {
                    const session = { cues, currentContext, cueIdCounter };
                    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
                    const blob = new Blob([JSON.stringify(session, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `tessera_autosave_${timestamp}.json`;
                    a.click();
                    URL.revokeObjectURL(url);

                    const userResponse = confirm(
                        '💾 Auto-Save Complete!\n\n' +
                        'Your session has been automatically saved as:\n' +
                        `"tessera_autosave_${timestamp}.json"\n\n` +
                        '⚠️ MEMORY WARNING ⚠️\n' +
                        'To prevent performance issues and potential data loss, this application will automatically close in 2 minutes.\n\n' +
                        'Click OK to close now, or Cancel to continue working.\n' +
                        '(Application will close automatically in 2 minutes if you continue working)'
                    );

                    if (userResponse) {
                        window.close();
                    } else {
                        let countdown = 120;
                        const countdownInterval = setInterval(() => {
                            countdown--;
                            if (countdown === 60) {
                                alert('⏱️ 1 minute until automatic close.\n\nYour work is saved. Please close the application and reopen to load your session.');
                            } else if (countdown === 30) {
                                alert('⏱️ 30 seconds until automatic close.\n\nYour work is saved.');
                            } else if (countdown === 10) {
                                alert('⏱️ 10 seconds until automatic close.\n\nClosing to protect your system memory...');
                            } else if (countdown <= 0) {
                                clearInterval(countdownInterval);
                                window.close();
                            }
                        }, 1000);
                    }
                } else {
                    alert(
                        '💾 Memory Tip: You\'ve been working for a while or loaded multiple large files.\n\n' +
                        'For best performance:\n' +
                        '1. Save your session (Ctrl/Cmd+S)\n' +
                        '2. Close and reopen the application\n' +
                        '3. Load your saved session to continue\n\n' +
                        'This clears memory and prevents slowdowns.'
                    );
                }
            }

            audioUploadBox.innerHTML = '<div>⏳ Loading audio file...</div>';
            currentAudioURL = URL.createObjectURL(file);
            audio.src = currentAudioURL;

            audio.addEventListener('loadedmetadata', () => {
                audio.style.display = 'block';
                timeDisplay.style.display = 'block';
                audioUploadBox.style.display = 'none';
                const minutes = Math.floor(audio.duration / 60);
                const seconds = Math.floor(audio.duration % 60);
                console.log(`✅ Audio loaded successfully. Duration: ${minutes}m ${seconds}s`);
            }, { once: true });

            audio.addEventListener('error', (err) => {
                console.error('❌ Error loading audio:', err);
                alert('❌ Error loading audio file!\n\nPlease check:\n• File format (MP3, WAV, OGG, M4A)\n• File is not corrupted\n• Sufficient system memory');
                audioUploadBox.innerHTML = `
                <div><span style="color: var(--accent); font-size: 24px;">♪</span> Click or Drop Audio File</div>
                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 5px;">MP3, WAV, OGG, M4A</div>
            `;
                e.target.value = ''; // Clear the file input
            }, { once: true });
        }
    });

    // Time update
    audio.addEventListener('timeupdate', () => {
        const t = audio.currentTime;
        const m = Math.floor(t / 60);
        const s = Math.floor(t % 60);
        const ms = Math.floor((t % 1) * 1000);
        timeDisplay.textContent = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}.${ms.toString().padStart(3, '0')}`;
    });

    // Cleanup on unload
    window.addEventListener('beforeunload', () => {
        if (currentAudioURL) {
            URL.revokeObjectURL(currentAudioURL);
        }
    });

    // Theme handling
    document.getElementById('themeDropdownBtn').addEventListener('click', (e) => {
        e.stopPropagation();
        const dropdown = document.getElementById('themeDropdown');
        const btn = document.getElementById('themeDropdownBtn');
        const isExpanded = dropdown.classList.toggle('show');
        btn.setAttribute('aria-expanded', isExpanded.toString());
    });

    document.querySelectorAll('.theme-option').forEach(opt => {
        opt.addEventListener('click', () => {
            const theme = opt.dataset.theme;
            if (theme === 'tessera') {
                document.body.removeAttribute('data-theme');
            } else {
                document.body.dataset.theme = theme;
            }
            document.querySelectorAll('.theme-option').forEach(o => o.classList.remove('active'));
            opt.classList.add('active');
            document.getElementById('currentTheme').textContent = opt.textContent;
            localStorage.setItem('theme', theme);
            document.getElementById('themeDropdown').classList.remove('show');
            document.getElementById('themeDropdownBtn').setAttribute('aria-expanded', 'false');
        });

        opt.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                opt.click();
            }
        });
    });

    document.addEventListener('click', () => {
        const themeDropdown = document.getElementById('themeDropdown');
        const hamburgerDropdown = document.getElementById('hamburgerDropdown');

        if (themeDropdown.classList.contains('show')) {
            themeDropdown.classList.remove('show');
            document.getElementById('themeDropdownBtn').setAttribute('aria-expanded', 'false');
        }

        if (hamburgerDropdown.classList.contains('show')) {
            hamburgerDropdown.classList.remove('show');
            document.getElementById('hamburgerBtn').setAttribute('aria-expanded', 'false');
        }
    });

    // Hamburger menu
    document.getElementById('hamburgerBtn').addEventListener('click', (e) => {
        e.stopPropagation();
        const dropdown = document.getElementById('hamburgerDropdown');
        const btn = document.getElementById('hamburgerBtn');
        const isExpanded = dropdown.classList.toggle('show');
        btn.setAttribute('aria-expanded', isExpanded.toString());
    });

    document.getElementById('readmeOption').addEventListener('click', () => {
        document.getElementById('readmeModal').classList.add('show');
        document.getElementById('hamburgerDropdown').classList.remove('show');
        document.getElementById('hamburgerBtn').setAttribute('aria-expanded', 'false');
    });

    document.getElementById('licenseOption').addEventListener('click', () => {
        document.getElementById('licenseModal').classList.add('show');
        document.getElementById('hamburgerDropdown').classList.remove('show');
        document.getElementById('hamburgerBtn').setAttribute('aria-expanded', 'false');
    });

    document.querySelectorAll('.menu-option').forEach(opt => {
        opt.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                opt.click();
            }
        });
    });

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'tessera';
    if (savedTheme !== 'tessera') {
        document.body.dataset.theme = savedTheme;
    }
    const savedOpt = document.querySelector(`[data-theme="${savedTheme}"]`);
    if (savedOpt) {
        savedOpt.classList.add('active');
        document.getElementById('currentTheme').textContent = savedOpt.textContent;
    }

    // Context management
    document.getElementById('editContextBtn').addEventListener('click', () => {
        if (currentContext) {
            document.getElementById('contextTitle').value = currentContext.title || '';
            document.getElementById('contextPerformers').value = currentContext.performers || '';
            document.getElementById('contextDate').value = currentContext.date || '';
            document.getElementById('contextConductor').value = currentContext.conductor || '';
            document.getElementById('contextComposer').value = currentContext.composer || '';
            document.getElementById('contextInfo').value = currentContext.info || '';
        } else {
            document.getElementById('contextTitle').value = '';
            document.getElementById('contextPerformers').value = '';
            document.getElementById('contextDate').value = '';
            document.getElementById('contextConductor').value = '';
            document.getElementById('contextComposer').value = '';
            document.getElementById('contextInfo').value = '';
        }
        document.getElementById('contextModal').classList.add('show');
    });

    // New Context button - clears ONLY the context, NOT the captions
    // This is for adding a new piece on the same recording (e.g., next song on a tape)
    document.getElementById('newContextBtn').addEventListener('click', () => {
        // Clear the current context (but keep all captions!)
        currentContext = null;
        updateContextDisplay();

        // Clear the add caption form
        document.getElementById('movementName').value = '';
        document.getElementById('startTime').value = '';
        document.getElementById('endTime').value = '';
        document.getElementById('overridePerformers').value = '';
        document.getElementById('overrideDate').value = '';
        document.getElementById('overrideConductor').value = '';
        document.getElementById('notes').value = '';
        document.getElementById('overrideDetails').removeAttribute('open');

        // Open context modal for new piece context
        document.getElementById('contextTitle').value = '';
        document.getElementById('contextPerformers').value = '';
        document.getElementById('contextDate').value = '';
        document.getElementById('contextConductor').value = '';
        document.getElementById('contextComposer').value = '';
        document.getElementById('contextInfo').value = '';
        document.getElementById('contextModal').classList.add('show');
    });

    // Modal functions
    function closeModal(id) {
        document.getElementById(id).classList.remove('show');
    }

    function saveContext() {
        const title = document.getElementById('contextTitle').value.trim();
        const performers = document.getElementById('contextPerformers').value.trim();

        if (!title) {
            alert('⚠️ Title is required!\n\nPlease enter the title of the piece.');
            return;
        }

        currentContext = {
            title,
            performers,
            date: document.getElementById('contextDate').value.trim(),
            conductor: document.getElementById('contextConductor').value.trim(),
            composer: document.getElementById('contextComposer').value.trim(),
            info: document.getElementById('contextInfo').value.trim()
        };

        updateContextDisplay();
        closeModal('contextModal');
        console.log('Context saved:', currentContext);
    }

    document.querySelectorAll('[data-modal-close]').forEach(btn => {
        btn.addEventListener('click', () => {
            closeModal(btn.getAttribute('data-modal-close'));
        });
    });

    document.getElementById('saveContextBtn').addEventListener('click', saveContext);

    function updateContextDisplay() {
        if (!currentContext) {
            contextDisplay.innerHTML = '<div class="context-empty">No piece context set. Click "Edit Piece Context" to begin.</div>';
            return;
        }

        let html = '';
        if (currentContext.title) {
            html += `<div class="context-row"><span class="context-label">Title:</span><span>${currentContext.title}</span></div>`;
        }
        if (currentContext.performers) {
            html += `<div class="context-row"><span class="context-label">Performers:</span><span>${currentContext.performers}</span></div>`;
        }
        if (currentContext.date) {
            html += `<div class="context-row"><span class="context-label">Date:</span><span>${currentContext.date}</span></div>`;
        }
        if (currentContext.conductor) {
            html += `<div class="context-row"><span class="context-label">Conductor:</span><span>${currentContext.conductor}</span></div>`;
        }
        if (currentContext.composer) {
            html += `<div class="context-row"><span class="context-label">Composer:</span><span>${currentContext.composer}</span></div>`;
        }
        if (currentContext.info) {
            html += `<div class="context-row"><span class="context-label">Info:</span><span>${currentContext.info}</span></div>`;
        }

        contextDisplay.innerHTML = html;
    }

    // Add caption
    document.getElementById('addBtn').addEventListener('click', addCue);

    function addCue() {
        if (!currentContext) {
            alert('⚠️ Please set piece context first!\n\nClick "Edit Piece Context" to enter the title and performers.');
            document.getElementById('contextModal').classList.add('show');
            return;
        }

        const movementName = document.getElementById('movementName').value.trim();
        const start = document.getElementById('startTime').value.trim();
        const end = document.getElementById('endTime').value.trim();

        if (!start || !end) {
            alert('⚠️ Start and end times are required!\n\nUse the I and O keys to mark times while playing audio.');
            return;
        }

        const startSec = parseTime(start);
        const endSec = parseTime(end);

        if (startSec === null || endSec === null) {
            alert('⚠️ Invalid time format!\n\nPlease use HH:MM:SS.mmm format\n\nExample: 00:03:45.250');
            return;
        }

        if (endSec <= startSec) {
            alert('⚠️ End time must be after start time!\n\nStart: ' + start + '\nEnd: ' + end);
            return;
        }

        const performers = document.getElementById('overridePerformers').value.trim() || currentContext.performers;
        const date = document.getElementById('overrideDate').value.trim() || currentContext.date;
        const conductor = document.getElementById('overrideConductor').value.trim() || currentContext.conductor;

        const cue = {
            id: cueIdCounter++,
            start: startSec,
            end: endSec,
            startStr: start,
            endStr: end,
            title: currentContext.title,
            movement: movementName,
            performers,
            date,
            conductor,
            composer: currentContext.composer,
            info: currentContext.info,
            notes: document.getElementById('notes').value.trim()
        };

        cues.push(cue);
        cues.sort((a, b) => a.start - b.start);

        document.getElementById('movementName').value = '';
        document.getElementById('startTime').value = '';
        document.getElementById('endTime').value = '';
        document.getElementById('overridePerformers').value = '';
        document.getElementById('overrideDate').value = '';
        document.getElementById('overrideConductor').value = '';
        document.getElementById('notes').value = '';
        document.getElementById('overrideDetails').removeAttribute('open');

        renderCues();
        generateVTT();

        console.log('Caption added:', cue);
    }

    function parseTime(str) {
        const match = str.match(/(\d+):(\d+):(\d+)\.(\d+)/);
        if (!match) return null;
        return parseInt(match[1]) * 3600 + parseInt(match[2]) * 60 + parseInt(match[3]) + parseInt(match[4]) / 1000;
    }

    function formatTime(sec) {
        const h = Math.floor(sec / 3600);
        const m = Math.floor((sec % 3600) / 60);
        const s = Math.floor(sec % 60);
        const ms = Math.floor((sec % 1) * 1000);
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}.${ms.toString().padStart(3, '0')}`;
    }

    function renderCues() {
        if (cues.length === 0) {
            cueList.innerHTML = '<div class="empty">No captions yet<br><small>Set piece context and add captions</small></div>';
            cueCount.textContent = '0';
            return;
        }

        cueCount.textContent = cues.length;

        const groups = {};
        cues.forEach(cue => {
            const key = cue.title;
            if (!groups[key]) {
                groups[key] = {
                    title: cue.title,
                    performers: cue.performers,
                    date: cue.date,
                    conductor: cue.conductor,
                    cues: []
                };
            }
            groups[key].cues.push(cue);
        });

        cueList.innerHTML = '';

        Object.values(groups).forEach(group => {
            const header = document.createElement('div');
            header.className = 'piece-group';
            let metaText = group.performers;
            if (group.conductor) metaText += ` • ${group.conductor}, Conductor`;
            if (group.date) metaText += ` • ${group.date}`;
            header.innerHTML = `
            <strong>${group.title}</strong>
            <div class="meta">${metaText}</div>
        `;
            cueList.appendChild(header);

            group.cues.forEach(cue => {
                const div = document.createElement('div');
                div.className = 'cue';
                let movementDisplay;
                if (cue.movement) {
                    movementDisplay = cue.movement;
                } else {
                    movementDisplay = '<em style="color: var(--accent-light);">Entire piece</em>';
                }
                div.innerHTML = `
                <div class="cue-header">
                    <span class="cue-time clickable-time" data-start-time="${cue.start}" title="Click to jump to ${cue.startStr}">${cue.startStr} → ${cue.endStr}</span>
                    <div style="display: flex; gap: 4px;">
                        <button class="btn-small btn-edit" data-cue-id="${cue.id}">✏️</button>
                        <button class="btn-small btn-danger btn-delete" data-cue-id="${cue.id}">✕</button>
                    </div>
                </div>
                <div class="cue-text">${movementDisplay}</div>
            `;
                cueList.appendChild(div);
            });
        });

        renderPreview();
    }

    cueList.addEventListener('click', (e) => {
        const deleteBtn = e.target.closest('.btn-delete');
        const editBtn = e.target.closest('.btn-edit');
        const timeStamp = e.target.closest('.clickable-time');

        if (deleteBtn) {
            e.stopPropagation();
            const id = parseInt(deleteBtn.dataset.cueId);
            deleteCue(id);
        } else if (editBtn) {
            e.stopPropagation();
            const id = parseInt(editBtn.dataset.cueId);
            editCue(id);
        } else if (timeStamp) {
            e.stopPropagation();
            const startTime = parseFloat(timeStamp.dataset.startTime);
            if (audio.src && !isNaN(startTime)) {
                audio.currentTime = startTime;
                audio.play();
            }
        }
    });

    function deleteCue(id) {
        if (confirm('Delete this caption?')) {
            cues = cues.filter(c => c.id !== id);
            renderCues();
            generateVTT();
        }
    }

    function editCue(id) {
        const cue = cues.find(c => c.id === id);
        if (!cue) return;

        editingCueId = id;

        document.getElementById('editMovementName').value = cue.movement || '';
        document.getElementById('editStartTime').value = cue.startStr;
        document.getElementById('editEndTime').value = cue.endStr;
        document.getElementById('editTitle').value = cue.title || '';
        document.getElementById('editPerformers').value = cue.performers || '';
        document.getElementById('editDate').value = cue.date || '';
        document.getElementById('editConductor').value = cue.conductor || '';
        document.getElementById('editComposer').value = cue.composer || '';
        document.getElementById('editInfo').value = cue.info || '';
        document.getElementById('editNotes').value = cue.notes || '';

        document.getElementById('editModal').classList.add('show');
    }

    function saveEdit() {
        if (editingCueId === null) return;

        const movementName = document.getElementById('editMovementName').value.trim();
        const start = document.getElementById('editStartTime').value.trim();
        const end = document.getElementById('editEndTime').value.trim();
        const title = document.getElementById('editTitle').value.trim();
        const performers = document.getElementById('editPerformers').value.trim();

        if (!start || !end) {
            alert('⚠️ Start and end times are required!');
            return;
        }

        if (!title) {
            alert('⚠️ Title is required!');
            return;
        }

        const startSec = parseTime(start);
        const endSec = parseTime(end);

        if (startSec === null || endSec === null) {
            alert('⚠️ Invalid time format!\n\nPlease use HH:MM:SS.mmm format\n\nExample: 00:03:45.250');
            return;
        }

        if (endSec <= startSec) {
            alert('⚠️ End time must be after start time!\n\nStart: ' + start + '\nEnd: ' + end);
            return;
        }

        const cueIndex = cues.findIndex(c => c.id === editingCueId);
        if (cueIndex !== -1) {
            cues[cueIndex] = {
                id: editingCueId,
                start: startSec,
                end: endSec,
                startStr: start,
                endStr: end,
                title: title,
                movement: movementName,
                performers: performers,
                date: document.getElementById('editDate').value.trim(),
                conductor: document.getElementById('editConductor').value.trim(),
                composer: document.getElementById('editComposer').value.trim(),
                info: document.getElementById('editInfo').value.trim(),
                notes: document.getElementById('editNotes').value.trim()
            };

            cues.sort((a, b) => a.start - b.start);
            renderCues();
            generateVTT();
            console.log('Caption updated:', cues[cueIndex]);
        }

        editingCueId = null;
        closeModal('editModal');
    }

    // IMPORTANT: Add event listener for saveEditBtn
    document.getElementById('saveEditBtn').addEventListener('click', saveEdit);

    function generateVTT() {
        if (cues.length === 0) {
            vttOutput.value = 'WEBVTT\n\nSet piece context and add captions...';
            return;
        }

        let vtt = 'WEBVTT\n\n';

        cues.forEach((cue, i) => {
            let text = '';
            
            if (cue.movement) {
                text = cue.title;
                text += `. <i>${cue.movement}</i>`;
                if (cue.performers) {
                    text += `. ${cue.performers}`;
                }
                if (cue.conductor) {
                    text += `. ${cue.conductor}, Conductor`;
                }
                if (cue.date) {
                    text += `. ${cue.date}`;
                }
            } else {
                text = cue.title;
                if (cue.performers) {
                    text += `. ${cue.performers}`;
                }
                if (cue.conductor) {
                    text += `. ${cue.conductor}, Conductor`;
                }
                if (cue.date) {
                    text += `. ${cue.date}`;
                }
            }

            vtt += `${cue.startStr} --> ${cue.endStr}\n${text}\n\n`;
        });

        vttOutput.value = vtt;
    }

    function renderPreview() {
        if (cues.length === 0) {
            previewContent.innerHTML = '<div class="empty">No captions to preview</div>';
            return;
        }

        previewContent.innerHTML = '';

        const groups = {};
        cues.forEach(cue => {
            const key = cue.title;
            if (!groups[key]) {
                groups[key] = {
                    title: cue.title,
                    performers: cue.performers,
                    date: cue.date,
                    conductor: cue.conductor,
                    cues: []
                };
            }
            groups[key].cues.push(cue);
        });

        Object.values(groups).forEach(group => {
            const header = document.createElement('div');
            header.className = 'piece-group';
            let metaText = group.performers;
            if (group.conductor) metaText += ` • ${group.conductor}, Conductor`;
            if (group.date) metaText += ` • ${group.date}`;
            header.innerHTML = `
            <strong>${group.title}</strong>
            <div class="meta">${metaText}</div>
        `;
            previewContent.appendChild(header);

            group.cues.forEach(cue => {
                const div = document.createElement('div');
                div.className = 'cue';
                let movementDisplay;
                if (cue.movement) {
                    movementDisplay = cue.movement;
                } else {
                    movementDisplay = '<em style="color: var(--accent-light);">Entire piece</em>';
                }
                div.innerHTML = `
                <div class="cue-time clickable-time" data-start-time="${cue.start}" title="Click to jump to ${cue.startStr}">${cue.startStr} → ${cue.endStr}</div>
                <div class="cue-text">${movementDisplay}</div>
            `;
                previewContent.appendChild(div);
            });
        });
    }

    // Tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab + 'Tab').classList.add('active');
        });
    });

    // Add click handler for timestamps in Preview tab
    previewContent.addEventListener('click', (e) => {
        const timeStamp = e.target.closest('.clickable-time');
        if (timeStamp) {
            e.stopPropagation();
            const startTime = parseFloat(timeStamp.dataset.startTime);
            if (audio.src && !isNaN(startTime)) {
                audio.currentTime = startTime;
                audio.play();
            }
        }
    });

    // Fallback save function for older browsers
    function fallbackSave(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    // Save session with timestamp to prevent overwrites
    document.getElementById('saveBtn').addEventListener('click', async () => {
        try {
            const session = { cues, currentContext, cueIdCounter };
            const jsonString = JSON.stringify(session, null, 2);

            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            let baseFilename = 'tessera_session';
            
            if (currentContext && currentContext.title) {
                const cleanTitle = currentContext.title
                    .replace(/[<>:"/\\|?*]/g, '')
                    .replace(/\s+/g, '_')
                    .substring(0, 40);
                baseFilename = cleanTitle;
            }
            
            const suggestedName = `${baseFilename}_${timestamp}.json`;

            if ('showSaveFilePicker' in window) {
                try {
                    const handle = await window.showSaveFilePicker({
                        suggestedName: suggestedName,
                        types: [{
                            description: 'JSON Session File',
                            accept: { 'application/json': ['.json'] }
                        }],
                        startIn: 'documents'
                    });
                    const writable = await handle.createWritable();
                    await writable.write(jsonString);
                    await writable.close();
                    console.log('Session saved successfully as:', suggestedName);
                    alert('✅ Session saved successfully!\n\nFile: ' + suggestedName);
                } catch (err) {
                    if (err.name === 'AbortError') {
                        console.log('Save cancelled by user');
                    } else {
                        console.error('Error saving session with file picker:', err);
                        alert('⚠️ File picker failed. Falling back to download method.');
                        const blob = new Blob([jsonString], { type: 'application/json' });
                        fallbackSave(blob, suggestedName);
                    }
                }
            } else {
                const blob = new Blob([jsonString], { type: 'application/json' });
                fallbackSave(blob, suggestedName);
            }
        } catch (err) {
            console.error('Critical error in save function:', err);
            alert('❌ Error saving session: ' + err.message + '\n\nPlease check console for details.');
        }
    });

    // Export VTT with timestamp to prevent overwrites
    document.getElementById('exportBtn').addEventListener('click', async () => {
        try {
            if (cues.length === 0) {
                alert('⚠️ No captions to export!\n\nPlease add at least one caption before exporting.');
                return;
            }

            const vttContent = vttOutput.value;

            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            let baseFilename = 'captions';
            
            if (currentContext && currentContext.title) {
                const cleanTitle = currentContext.title
                    .replace(/[<>:"/\\|?*]/g, '')
                    .replace(/\s+/g, '_')
                    .substring(0, 40);
                baseFilename = cleanTitle;
            }
            
            const suggestedName = `${baseFilename}_${timestamp}.vtt`;

            if ('showSaveFilePicker' in window) {
                try {
                    const handle = await window.showSaveFilePicker({
                        suggestedName: suggestedName,
                        types: [{
                            description: 'WebVTT Caption File',
                            accept: { 'text/vtt': ['.vtt'] }
                        }],
                        startIn: 'documents'
                    });
                    const writable = await handle.createWritable();
                    await writable.write(vttContent);
                    await writable.close();
                    console.log('VTT exported successfully as:', suggestedName);
                    alert('✅ WebVTT exported successfully!\n\nFile: ' + suggestedName + '\n\nCaptions: ' + cues.length);
                } catch (err) {
                    if (err.name === 'AbortError') {
                        console.log('Export cancelled by user');
                    } else {
                        console.error('Error exporting VTT with file picker:', err);
                        alert('⚠️ File picker failed. Falling back to download method.');
                        const blob = new Blob([vttContent], { type: 'text/vtt' });
                        fallbackSave(blob, suggestedName);
                    }
                }
            } else {
                const blob = new Blob([vttContent], { type: 'text/vtt' });
                fallbackSave(blob, suggestedName);
            }
        } catch (err) {
            console.error('Critical error in export function:', err);
            alert('❌ Error exporting VTT: ' + err.message + '\n\nPlease check console for details.');
        }
    });

    // Load session button
    document.getElementById('loadBtn').addEventListener('click', () => {
        document.getElementById('loadFile').click();
    });

    // Load session file handler
    document.getElementById('loadFile').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        if (!file.name.endsWith('.json')) {
            alert('Please select a valid JSON session file');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const session = JSON.parse(e.target.result);
                
                if (!session.hasOwnProperty('cues') || !Array.isArray(session.cues)) {
                    throw new Error('Invalid session file structure');
                }

                cues = session.cues || [];
                currentContext = session.currentContext || null;
                cueIdCounter = session.cueIdCounter || 0;
                
                updateContextDisplay();
                renderCues();
                generateVTT();
                
                alert(`Session loaded successfully!\n\n• ${cues.length} caption(s) loaded\n• Context: ${currentContext ? currentContext.title : 'None'}\n\nDon't forget to reload your audio file if needed.`);
                
                console.log(`Session loaded: ${cues.length} cues, context: ${currentContext ? 'Yes' : 'No'}`);
            } catch (err) {
                console.error('Error loading session:', err);
                alert('Error loading session file. Please make sure this is a valid Tessera session file.\n\nError: ' + err.message);
            }
        };
        
        reader.onerror = () => {
            alert('Error reading file. Please try again.');
        };
        
        reader.readAsText(file);
        e.target.value = '';
    });

    // Sort & Clear
    document.getElementById('sortBtn').addEventListener('click', () => {
        cues.sort((a, b) => a.start - b.start);
        renderCues();
        generateVTT();
    });

    document.getElementById('clearBtn').addEventListener('click', () => {
        if (cues.length === 0) return;
        if (confirm('Clear all captions? (Context will be preserved)')) {
            cues = [];
            renderCues();
            generateVTT();
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        const isTyping = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA';

        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                modal.classList.remove('show');
            });

            const themeDropdown = document.getElementById('themeDropdown');
            const hamburgerDropdown = document.getElementById('hamburgerDropdown');

            if (themeDropdown && themeDropdown.classList.contains('show')) {
                themeDropdown.classList.remove('show');
                document.getElementById('themeDropdownBtn').setAttribute('aria-expanded', 'false');
            }

            if (hamburgerDropdown && hamburgerDropdown.classList.contains('show')) {
                hamburgerDropdown.classList.remove('show');
                document.getElementById('hamburgerBtn').setAttribute('aria-expanded', 'false');
            }
            return;
        }

        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            document.getElementById('saveBtn').click();
            return;
        }

        if ((e.ctrlKey || e.metaKey) && e.key === 'o') {
            e.preventDefault();
            document.getElementById('loadBtn').click();
            return;
        }

        if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
            e.preventDefault();
            document.getElementById('exportBtn').click();
            return;
        }

        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            document.getElementById('newContextBtn').click();
            return;
        }

        if (!isTyping && audio.src) {
            if (e.key === ' ') {
                e.preventDefault();
                if (audio.paused) {
                    audio.play();
                } else {
                    audio.pause();
                }
                return;
            }

            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                let skipAmount = 1;
                if (e.shiftKey) skipAmount = 0.1;
                if (e.ctrlKey || e.metaKey) skipAmount = 5;
                audio.currentTime = Math.max(0, audio.currentTime - skipAmount);
                return;
            }

            if (e.key === 'ArrowRight') {
                e.preventDefault();
                let skipAmount = 1;
                if (e.shiftKey) skipAmount = 0.1;
                if (e.ctrlKey || e.metaKey) skipAmount = 5;
                audio.currentTime = Math.min(audio.duration, audio.currentTime + skipAmount);
                return;
            }

            if (e.key === 'ArrowUp') {
                e.preventDefault();
                audio.volume = Math.min(1, audio.volume + 0.1);
                return;
            }

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                audio.volume = Math.max(0, audio.volume - 0.1);
                return;
            }

            if (e.key === 'm' || e.key === 'M') {
                e.preventDefault();
                audio.muted = !audio.muted;
                return;
            }

            if (e.key === 'i' || e.key === 'I') {
                e.preventDefault();
                document.getElementById('startTime').value = formatTime(audio.currentTime);
                return;
            }

            if (e.key === 'o' || e.key === 'O') {
                e.preventDefault();
                document.getElementById('endTime').value = formatTime(audio.currentTime);
                return;
            }

            if (e.key === 'j' || e.key === 'J') {
                e.preventDefault();
                audio.currentTime = Math.max(0, audio.currentTime - 10);
                return;
            }

            if (e.key === 'l' || e.key === 'L') {
                e.preventDefault();
                audio.currentTime = Math.min(audio.duration, audio.currentTime + 10);
                return;
            }

            if (e.key === 'k' || e.key === 'K') {
                e.preventDefault();
                if (audio.paused) {
                    audio.play();
                } else {
                    audio.pause();
                }
                return;
            }

            if (e.key === ',') {
                e.preventDefault();
                audio.currentTime = Math.max(0, audio.currentTime - 0.033);
                return;
            }

            if (e.key === '.') {
                e.preventDefault();
                audio.currentTime = Math.min(audio.duration, audio.currentTime + 0.033);
                return;
            }
        }
    });

    updateContextDisplay();

});