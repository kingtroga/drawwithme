document.addEventListener('DOMContentLoaded', function () {
    const canvasElement = document.getElementById('drawing-canvas');
    const container = canvasElement.parentElement;

    const canvas = new fabric.Canvas('drawing-canvas', {
        isDrawingMode: true // Enable drawing mode by default
    });

    let currentMode = 'pencil'; // Default mode

    // Responsive Canvas Resizing Function
    function resizeCanvas() {
        const containerWidth = container.clientWidth;
        const isMobile = window.innerWidth < 768; // Adjust for mobile breakpoints
        const aspectRatio = isMobile ? 9 / 16 : 16 / 9; // Mobile: 9:16, Desktop: 16:9

        const width = containerWidth;
        const height = width * aspectRatio;

        canvas.setWidth(width);
        canvas.setHeight(height);
        canvas.setZoom(1);
    }

    // Disable selection on all objects
    function disableSelection() {
        canvas.selection = false;
        canvas.getObjects().forEach(obj => {
            obj.selectable = false;
            obj.hasControls = false;
            obj.hasBorders = false;
        });
    }

    // Initial resize and listen for window changes
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Enable selection on all objects
    function enableSelection() {
        canvas.selection = true;
        canvas.getObjects().forEach(obj => {
            obj.selectable = true;
            obj.hasControls = true;
            obj.hasBorders = true;
        });
    }

    // Initialize brushes
    const drawingBrush = new fabric.PencilBrush(canvas);
    const erasingBrush = new fabric.PencilBrush(canvas);
    
    // Configure erasing brush
    erasingBrush.color = 'white';
    erasingBrush.width = 5;
    erasingBrush.globalCompositeOperation = 'destination-out';

    // Set initial drawing brush settings
    drawingBrush.width = 5;
    drawingBrush.color = '#000000';

    // Tool handlers
    document.getElementById('selection-tool').onclick = () => {
        currentMode = 'selection';
        canvas.isDrawingMode = false;
        enableSelection();
    };

    document.getElementById('pencil-tool').onclick = () => {
        currentMode = 'pencil';
        canvas.isDrawingMode = true;
        canvas.freeDrawingBrush = drawingBrush;
        canvas.freeDrawingBrush.width = parseInt(document.getElementById('brush-size').value, 10);
        canvas.freeDrawingBrush.color = document.getElementById('color-picker').value;
        disableSelection();
    };

    document.getElementById('eraser-tool').onclick = () => {
        currentMode = 'eraser';
        canvas.isDrawingMode = true;
        canvas.freeDrawingBrush = erasingBrush;
        canvas.freeDrawingBrush.width = parseInt(document.getElementById('brush-size').value, 10);
        disableSelection();
    };

    // Handle brush size changes
    document.getElementById('brush-size').addEventListener('input', (e) => {
        const size = parseInt(e.target.value, 10);
        if (canvas.freeDrawingBrush) {
            canvas.freeDrawingBrush.width = size;
            
            // Update both brushes
            drawingBrush.width = size;
            erasingBrush.width = size;
        }
    });

    // Handle color changes
    document.getElementById('color-picker').addEventListener('change', (e) => {
        if (currentMode === 'pencil') {
            drawingBrush.color = e.target.value;
            if (canvas.freeDrawingBrush === drawingBrush) {
                canvas.freeDrawingBrush.color = e.target.value;
            }
        }
    });

    // Handle background color changes
    document.getElementById('background-color').addEventListener('change', (e) => {
        canvas.backgroundColor = e.target.value;
        canvas.renderAll();
    });

    document.getElementById('save-artwork-btn').addEventListener('click', () => {
        const title = document.getElementById('artwork-title').value || 'Untitled';
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const canvasData = canvas.toJSON();
        console.log("Hello World"); 
        // Convert canvas to PNG
        const pngDataUrl = canvas.toDataURL("image/png");
        console.log("Generated PNG Data URL:", pngDataUrl); // Debugging
    
        const data = new FormData();  // Use FormData for image uploads
        data.append('title', title);
        data.append('canvas', JSON.stringify(canvasData));
        data.append('csrfmiddlewaretoken', csrfToken);
        
        // Convert base64 PNG to Blob and append to FormData
        fetch(pngDataUrl)
            .then(res => res.blob())
            .then(blob => {
                console.log("Converted Blob:", blob); // Debugging
                data.append('image', blob, 'artwork.png');  // Attach image file
    
                // If the artwork_id exists, send it
                if (window.artworkId) {
                    data.append('artwork_id', window.artworkId);
                }
    
                return fetch('/drawing/save/', {
                    method: 'POST',
                    body: data,
                    headers: {
                        'X-CSRFToken': csrfToken  // CSRF token needed for Django
                    }
                });
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Artwork saved successfully!');
                    window.artworkId = data.artwork_id;  // Store artwork ID for updates
                } else {
                    alert(data.message || 'Error saving artwork');
                }
            })
            .catch(error => {
                console.error('Save Error:', error);
                alert('Unable to save artwork. Please try again.');
            });
    });
    
});   