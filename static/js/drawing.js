document.addEventListener('DOMContentLoaded', function () {
    // Canvas element setup
    const canvasElement = document.getElementById('drawing-canvas');
    if (!canvasElement) {
        console.error('Canvas element not found!');
        return;
    }

    const container = canvasElement.parentElement;
    const artworkForm = document.getElementById('artwork-form');
    const saveButton = document.getElementById('save-artwork-btn');

    let isEditMode = false;
    let artworkId = null;
    let resizeTimeout;

    // Initialize Fabric.js Canvas
    const canvas = new fabric.Canvas('drawing-canvas', {
        isDrawingMode: true,
        preserveObjectStacking: true,
        fireRightClick: true
    });

    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg 
            ${type === 'success' ? 'bg-green-100 text-green-800' : 
             type === 'error' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    // Initialize brushes
    let currentMode = 'pencil';
    const drawingBrush = new fabric.PencilBrush(canvas);
    const erasingBrush = new fabric.PencilBrush(canvas);

    // JSON handling
    function safeJSONParse(data) {
        try {
            const sanitized = data
                .replace(/'/g, '"')
                .replace(/False/g, 'false')
                .replace(/True/g, 'true')
                .replace(/None/g, 'null');
            return JSON.parse(sanitized);
        } catch (error) {
            console.error('JSON parse error:', error);
            return null;
        }
    }

    // Canvas sizing
    function getAspectRatio() {
        return window.innerWidth < 768 ? 9/16 : 16/9;
    }

    function resizeCanvas() {
        const containerWidth = container.clientWidth;
        const aspectRatio = getAspectRatio();
        const newHeight = containerWidth * aspectRatio;

        canvas.setDimensions({
            width: containerWidth,
            height: newHeight
        });
        canvas.renderAll();
    }

    // Event handlers
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(resizeCanvas, 100);
    });

    function initializeBrushes() {
        erasingBrush.color = 'white';
        erasingBrush.globalCompositeOperation = 'destination-out';
        drawingBrush.color = getValueSafe('color-picker', '#000000');
        drawingBrush.width = parseInt(getValueSafe('brush-size', '5'), 10);
        erasingBrush.width = drawingBrush.width;
        canvas.backgroundColor = getValueSafe('background-color', '#ffffff');
        canvas.renderAll();
    }

    function loadCanvasState(data) {
        canvas.clear().loadFromJSON(data, () => {
            if (data.background) {
                canvas.setBackgroundColor(data.background, canvas.renderAll.bind(canvas));
            }
            resizeCanvas();
            initializeBrushes();
        });
    }

    // Selection handling
    function disableSelection() {
        canvas.selection = false;
        canvas.forEachObject(obj => {
            obj.selectable = false;
            obj.hasControls = false;
            obj.hasBorders = false;
        });
    }

    function enableSelection() {
        canvas.selection = true;
        canvas.forEachObject(obj => {
            obj.selectable = true;
            obj.hasControls = true;
            obj.hasBorders = true;
        });
    }

    // Tools
    const tools = {
        pencil: () => {
            currentMode = 'pencil';
            canvas.isDrawingMode = true;
            canvas.freeDrawingBrush = drawingBrush;
            canvasElement.classList.add('cursor-pencil');
            canvasElement.classList.remove('cursor-eraser');
            disableSelection();
        },
        eraser: () => {
            currentMode = 'eraser';
            canvas.isDrawingMode = true;
            canvas.freeDrawingBrush = erasingBrush;
            canvasElement.classList.add('cursor-eraser');
            canvasElement.classList.remove('cursor-pencil');
            disableSelection();
        },
        selection: () => {
            currentMode = 'selection';
            canvas.isDrawingMode = false;
            canvasElement.classList.remove('cursor-pencil', 'cursor-eraser');
            enableSelection();
        }
    };

    // Safe element value getter
    function getValueSafe(id, defaultValue = '') {
        const el = document.getElementById(id);
        return el ? el.value : defaultValue;
    }

    // Event listeners
    document.getElementById('pencil-tool')?.addEventListener('click', tools.pencil);
    document.getElementById('eraser-tool')?.addEventListener('click', tools.eraser);
    document.getElementById('selection-tool')?.addEventListener('click', tools.selection);

    document.getElementById('brush-size')?.addEventListener('input', (e) => {
        const size = parseInt(e.target.value, 10);
        drawingBrush.width = size;
        erasingBrush.width = size;
        if (canvas.isDrawingMode) canvas.freeDrawingBrush.width = size;
    });

    document.getElementById('color-picker')?.addEventListener('change', (e) => {
        drawingBrush.color = e.target.value;
        if (currentMode === 'pencil') canvas.freeDrawingBrush.color = e.target.value;
    });

    document.getElementById('background-color')?.addEventListener('change', (e) => {
        canvas.setBackgroundColor(e.target.value, () => canvas.renderAll());
    });

    // Form handling
    async function handleArtworkSubmission(isUpdate = false) {
        if (isUpdate && !artworkId) {
            showNotification('Invalid artwork ID', 'error');
            return;
        }

        const formData = new FormData();
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        if (!csrfToken) {
            showNotification('Missing CSRF token', 'error');
            return;
        }

        // Handle collaborators safely
        const collaboratorsSelect = document.getElementById('collaborators');
        const collaborators = collaboratorsSelect ? 
            Array.from(collaboratorsSelect.selectedOptions).map(opt => opt.value).join(',') : 
            '';

        formData.append('title', getValueSafe('artwork-title', 'Untitled'));
        formData.append('description', getValueSafe('artwork-description'));
        formData.append('collaborators', collaborators);
        formData.append('canvas_data', JSON.stringify(canvas.toJSON()));
        formData.append('background_color', canvas.backgroundColor);
        formData.append('brush_size', getValueSafe('brush-size', '5'));
        formData.append('drawing_color', getValueSafe('color-picker', '#000000'));
        formData.append('csrfmiddlewaretoken', csrfToken);

        try {
            const pngDataUrl = canvas.toDataURL("image/png");
            const response = await fetch(pngDataUrl);
            const blob = await response.blob();
            formData.append('image', blob, `artwork-${Date.now()}.png`);

            const endpoint = isUpdate ? `/drawing/edit/${encodeURIComponent(artworkId)}/` : '/drawing/save/';
            const method = isUpdate ? 'PUT' : 'POST';

            const saveResponse = await fetch(endpoint, {
                method: method,
                body: formData,
                headers: {'X-CSRFToken': csrfToken}
            });

            const contentType = saveResponse.headers.get('content-type');
            if (!saveResponse.ok || !contentType?.includes('application/json')) {
                throw new Error(await saveResponse.text());
            }

            const result = await saveResponse.json();
            
            if (result.success) {
                showNotification('Artwork saved successfully!', 'success');
                if (!isUpdate && result.artwork_id) {
                    artworkId = result.artwork_id;
                    window.history.replaceState({}, '', `/drawing/edit/${artworkId}/`);
                }
            } else {
                showNotification(result.message || 'Error saving artwork', 'error');
            }
        } catch (error) {
            console.error('Save Error:', error);
            showNotification(
                error.message.startsWith('<') ? 'Server error - check console' : error.message,
                'error'
            );
        }
    }

    // Initialization
    function initializeApplication() {
        resizeCanvas();
        initializeBrushes();
        disableSelection();

        if (artworkForm) {
            isEditMode = artworkForm.dataset.artworkId !== undefined;
            artworkId = artworkForm.dataset.artworkId || null;
        }

        if (saveButton) {
            saveButton.addEventListener('click', (e) => {
                e.preventDefault();
                handleArtworkSubmission();
            });
        }

        if (artworkForm) {
            artworkForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await handleArtworkSubmission(true);
            });

            if (isEditMode && artworkId) {
                const canvasData = document.getElementById('canvas-data')?.value;
                if (canvasData) {
                    const parsedData = safeJSONParse(canvasData);
                    if (parsedData) loadCanvasState(parsedData);
                }
            }
        }

        if (window.$ && document.getElementById('collaborators')) {
            $('#collaborators').select2({
                placeholder: "Add collaborators...",
                allowClear: true
            });
        }
    }

    initializeApplication();
});