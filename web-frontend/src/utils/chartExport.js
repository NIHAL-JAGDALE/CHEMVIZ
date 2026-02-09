/**
 * Chart Export Utility
 * Functions to export Chart.js charts as PNG/SVG images
 */

/**
 * Export a chart canvas to PNG
 * @param {HTMLCanvasElement} canvas - The chart canvas element
 * @param {string} filename - Name for the downloaded file (without extension)
 * @param {Object} options - Export options
 */
export function exportChartAsPNG(canvas, filename = 'chart', options = {}) {
    const {
        backgroundColor = '#ffffff',
        scale = 2, // Higher scale for better quality
        padding = 20
    } = options;

    // Create a new canvas with padding and background
    const exportCanvas = document.createElement('canvas');
    const ctx = exportCanvas.getContext('2d');

    exportCanvas.width = (canvas.width + padding * 2) * scale;
    exportCanvas.height = (canvas.height + padding * 2) * scale;

    // Fill background
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);

    // Scale and draw the chart
    ctx.scale(scale, scale);
    ctx.drawImage(canvas, padding, padding);

    // Create download link
    const link = document.createElement('a');
    link.download = `${filename}.png`;
    link.href = exportCanvas.toDataURL('image/png', 1.0);
    link.click();
}

/**
 * Export a chart canvas to SVG (converted from canvas)
 * Note: This creates a high-quality PNG since Chart.js uses canvas
 * @param {HTMLCanvasElement} canvas - The chart canvas element
 * @param {string} filename - Name for the downloaded file
 */
export function exportChartAsHighQuality(canvas, filename = 'chart') {
    // Export at 4x scale for print quality
    exportChartAsPNG(canvas, filename, {
        scale: 4,
        backgroundColor: '#ffffff',
        padding: 30
    });
}

/**
 * Copy chart to clipboard as image
 * @param {HTMLCanvasElement} canvas - The chart canvas element
 */
export async function copyChartToClipboard(canvas) {
    try {
        const blob = await new Promise(resolve => {
            canvas.toBlob(resolve, 'image/png', 1.0);
        });

        await navigator.clipboard.write([
            new ClipboardItem({ 'image/png': blob })
        ]);

        return { success: true, message: 'Chart copied to clipboard!' };
    } catch (error) {
        console.error('Failed to copy chart:', error);
        return { success: false, message: 'Failed to copy chart to clipboard' };
    }
}

/**
 * Create a styled export button component
 */
export const ExportButtonStyles = {
    container: {
        display: 'flex',
        gap: '0.5rem',
        marginLeft: 'auto'
    },
    button: {
        padding: '0.35rem 0.75rem',
        fontSize: '0.75rem',
        borderRadius: '6px',
        border: '1px solid var(--border-color)',
        background: 'var(--bg-card)',
        color: 'var(--text-secondary)',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '0.35rem',
        transition: 'all 0.2s ease',
    },
    buttonHover: {
        background: 'var(--primary-color)',
        color: 'white',
        borderColor: 'var(--primary-color)'
    }
};
