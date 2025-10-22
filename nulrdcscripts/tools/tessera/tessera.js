// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function () {
    console.log('Tessera JavaScript loaded');

    let cues = [];
    let currentContext = null;
    let cueIdCounter = 0;
    let currentAudioURL = null;

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
                if (!confirm(`This file is ${fileSizeMB} MB, which may cause performance issues. Continue?`)) {
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
                    const blob = new Blob([JSON.stringify(session, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'tessera_autosave_session.json';
                    a.click();
                    URL.revokeObjectURL(url);

                    const userResponse = confirm(
                        '💾 Auto-Save Complete!\n\n' +
                        'Your session has been automatically saved as:\n' +
                        '"tessera_autosave_session.json"\n\n' +
                        '⚠️ MEMORY WARNING ⚠️\n' +
                        'To prevent performance issues and potential data loss, this application will automatically close in 2 minutes.\n\n' +
                        'Click OK to close now, or Cancel to continue working.\n' +
                        '(Application will close automatically in 2 minutes if you continue working)'
                    );

                    if (userResponse) {
                        // User clicked OK - close immediately
                        window.close();
                    } else {
                        // User clicked Cancel - set 2 minute timer to auto-close
                        let countdown = 120; // 2 minutes in seconds
                        const countdownInterval = setInterval(() => {
                            countdown--;

                            // Show warning at 1 minute, 30 seconds, and 10 seconds
                            if (countdown === 60) {
                                alert('⏱️ 1 minute until automatic close.\n\nYour work is saved. Please close the application and reopen to load your session.');
                            } else if (countdown === 30) {
                                alert('⏱️ 30 seconds until automatic close.\n\nYour work is saved as: tessera_autosave_session.json');
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
                console.log(`Audio loaded successfully. Duration: ${Math.floor(audio.duration / 60)}m ${Math.floor(audio.duration % 60)}s`);
            }, { once: true });

            audio.addEventListener('error', (err) => {
                console.error('Error loading audio:', err);
                alert('Error loading audio file.');
                audioUploadBox.innerHTML = `
                <div><span style="color: var(--accent); font-size: 24px;">♪</span> Click or Drop Audio File</div>
                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 5px;">MP3, WAV, OGG, M4A</div>
            `;
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

        const startInput = document.getElementById('startTime');
        const endInput = document.getElementById('endTime');
        if (!startInput.value) startInput.value = formatTime(t);
        if (!endInput.value) endInput.value = formatTime(t + 5);
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

        // Keyboard support
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

    // Keyboard support for hamburger menu
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

    // Modal functions
    function closeModal(id) {
        document.getElementById(id).classList.remove('show');
    }

    function saveContext() {
        const title = document.getElementById('contextTitle').value.trim();
        const performers = document.getElementById('contextPerformers').value.trim();

        if (!title || !performers) {
            alert('Title and Performers are required');
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
    }

    // Modal close button handlers
    document.querySelectorAll('[data-modal-close]').forEach(btn => {
        btn.addEventListener('click', () => {
            closeModal(btn.getAttribute('data-modal-close'));
        });
    });

    // Save context button
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
            alert('Please set piece context first');
            document.getElementById('contextModal').classList.add('show');
            return;
        }

        const movementName = document.getElementById('movementName').value.trim();
        const start = document.getElementById('startTime').value.trim();
        const end = document.getElementById('endTime').value.trim();

        if (!start || !end) {
            alert('Start and end times are required');
            return;
        }

        const startSec = parseTime(start);
        const endSec = parseTime(end);

        if (startSec === null || endSec === null) {
            alert('Invalid time format. Use HH:MM:SS.mmm');
            return;
        }

        if (endSec <= startSec) {
            alert('End time must be after start time');
            return;
        }

        // Use overrides if provided, otherwise use context
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

        // Clear form
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

        // Group by piece
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
            // Piece header
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

            // Cues
            group.cues.forEach(cue => {
                const div = document.createElement('div');
                div.className = 'cue';
                div.innerHTML = `
                <div class="cue-header">
                    <span class="cue-time">${cue.startStr} → ${cue.endStr}</span>
                    <div style="display: flex; gap: 4px;">
                        <button class="btn-small btn-edit" data-cue-id="${cue.id}">✏️</button>
                        <button class="btn-small btn-danger btn-delete" data-cue-id="${cue.id}">✕</button>
                    </div>
                </div>
                <div class="cue-text">${cue.movement || '[No movement name]'}</div>
            `;
                cueList.appendChild(div);
            });
        });

        renderPreview();
    }

    // Event delegation for edit and delete buttons
    cueList.addEventListener('click', (e) => {
        const deleteBtn = e.target.closest('.btn-delete');
        const editBtn = e.target.closest('.btn-edit');

        if (deleteBtn) {
            e.stopPropagation();
            const id = parseInt(deleteBtn.dataset.cueId);
            deleteCue(id);
        } else if (editBtn) {
            e.stopPropagation();
            const id = parseInt(editBtn.dataset.cueId);
            editCue(id);
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

        document.getElementById('movementName').value = cue.movement || '';
        document.getElementById('startTime').value = cue.startStr;
        document.getElementById('endTime').value = cue.endStr;
        document.getElementById('notes').value = cue.notes || '';

        deleteCue(id);
        document.querySelector('.card:nth-child(2)').scrollIntoView({ behavior: 'smooth' });
    }

    function generateVTT() {
        if (cues.length === 0) {
            vttOutput.value = 'WEBVTT\n\nSet piece context and add captions...';
            return;
        }

        let vtt = 'WEBVTT\n\n';

        cues.forEach((cue, i) => {
            // Build caption text
            let text = cue.title;
            if (cue.movement) {
                text += `. ${cue.movement}`;
            }
            text += `. ${cue.performers}`;
            if (cue.conductor) {
                text += `. ${cue.conductor}, Conductor`;
            }
            if (cue.date) {
                text += `. ${cue.date}`;
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
                div.innerHTML = `
                <div class="cue-time">${cue.startStr} → ${cue.endStr}</div>
                <div class="cue-text">${cue.movement || '[No movement name]'}</div>
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

    // Export
    document.getElementById('exportBtn').addEventListener('click', () => {
        const blob = new Blob([vttOutput.value], { type: 'text/vtt' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'captions.vtt';
        a.click();
        URL.revokeObjectURL(url);
    });

    // Save/Load session
    document.getElementById('saveBtn').addEventListener('click', () => {
        const session = { cues, currentContext, cueIdCounter };
        const blob = new Blob([JSON.stringify(session, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'session.json';
        a.click();
        URL.revokeObjectURL(url);
    });

    document.getElementById('loadBtn').addEventListener('click', () => {
        document.getElementById('loadFile').click();
    });

    document.getElementById('loadFile').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const session = JSON.parse(e.target.result);
                cues = session.cues || [];
                currentContext = session.currentContext || null;
                cueIdCounter = session.cueIdCounter || 0;
                updateContextDisplay();
                renderCues();
                generateVTT();
                alert('Session loaded successfully!');
            } catch (err) {
                console.error('Error loading session:', err);
                alert('Error loading session file');
            }
        };
        reader.readAsText(file);
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
        // Don't trigger shortcuts if user is typing in an input/textarea
        const isTyping = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA';

        // ESC key to close modals and dropdowns (works always)
        if (e.key === 'Escape') {
            // Close any open modals
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                modal.classList.remove('show');
            });

            // Close dropdowns
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

        // Save session (works always)
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            document.getElementById('saveBtn').click();
            return;
        }
        // Export VTT (works always)
        if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
            e.preventDefault();
            document.getElementById('exportBtn').click();
            return;
        }

        // Audio controls (only when NOT typing)
        if (!isTyping && audio.src) {
            // Spacebar: Play/Pause
            if (e.key === ' ') {
                e.preventDefault();
                if (audio.paused) {
                    audio.play();
                } else {
                    audio.pause();
                }
                return;
            }

            // Arrow Left: Rewind (1s normal, 0.1s with Shift, 5s with Ctrl)
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                let skipAmount = 1; // Default: 1 second
                if (e.shiftKey) skipAmount = 0.1; // Fine: 100ms
                if (e.ctrlKey || e.metaKey) skipAmount = 5; // Coarse: 5 seconds
                audio.currentTime = Math.max(0, audio.currentTime - skipAmount);
                return;
            }

            // Arrow Right: Forward (1s normal, 0.1s with Shift, 5s with Ctrl)
            if (e.key === 'ArrowRight') {
                e.preventDefault();
                let skipAmount = 1; // Default: 1 second
                if (e.shiftKey) skipAmount = 0.1; // Fine: 100ms
                if (e.ctrlKey || e.metaKey) skipAmount = 5; // Coarse: 5 seconds
                audio.currentTime = Math.min(audio.duration, audio.currentTime + skipAmount);
                return;
            }

            // Arrow Up: Increase volume 10%
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                audio.volume = Math.min(1, audio.volume + 0.1);
                return;
            }

            // Arrow Down: Decrease volume 10%
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                audio.volume = Math.max(0, audio.volume - 0.1);
                return;
            }

            // M: Mute/Unmute
            if (e.key === 'm' || e.key === 'M') {
                e.preventDefault();
                audio.muted = !audio.muted;
                return;
            }

            // I: Insert start time (current position)
            if (e.key === 'i' || e.key === 'I') {
                e.preventDefault();
                document.getElementById('startTime').value = formatTime(audio.currentTime);
                return;
            }

            // O: Insert end time (current position)
            if (e.key === 'o' || e.key === 'O') {
                e.preventDefault();
                document.getElementById('endTime').value = formatTime(audio.currentTime);
                return;
            }

            // J: Jump back 10 seconds
            if (e.key === 'j' || e.key === 'J') {
                e.preventDefault();
                audio.currentTime = Math.max(0, audio.currentTime - 10);
                return;
            }

            // L: Jump forward 10 seconds
            if (e.key === 'l' || e.key === 'L') {
                e.preventDefault();
                audio.currentTime = Math.min(audio.duration, audio.currentTime + 10);
                return;
            }

            // K: Toggle play/pause (alternative to spacebar)
            if (e.key === 'k' || e.key === 'K') {
                e.preventDefault();
                if (audio.paused) {
                    audio.play();
                } else {
                    audio.pause();
                }
                return;
            }

            // Comma (,): Frame back (0.033s ~1 frame at 30fps)
            if (e.key === ',') {
                e.preventDefault();
                audio.currentTime = Math.max(0, audio.currentTime - 0.033);
                return;
            }

            // Period (.): Frame forward (0.033s ~1 frame at 30fps)
            if (e.key === '.') {
                e.preventDefault();
                audio.currentTime = Math.min(audio.duration, audio.currentTime + 0.033);
                return;
            }
        }
    });

    // Initial render
    updateContextDisplay();

}); // End DOMContentLoaded