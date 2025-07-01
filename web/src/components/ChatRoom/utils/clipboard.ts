/*
 * @LastEditors: biz
 */
/**
 * Clipboard utility functions using native Clipboard API
 */

/**
 * Copy text to clipboard using native Clipboard API with fallback
 * @param text - Text to copy
 * @returns Promise<boolean> - Success status
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
    try {
        // Modern browsers - use Clipboard API
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(text);
            return true;
        }
        
        // Fallback for older browsers
        return fallbackCopyToClipboard(text);
    } catch (error) {
        console.error('Failed to copy using Clipboard API:', error);
        // Try fallback method
        return fallbackCopyToClipboard(text);
    }
};

/**
 * Fallback copy method for browsers that don't support Clipboard API
 * @param text - Text to copy
 * @returns boolean - Success status
 */
const fallbackCopyToClipboard = (text: string): boolean => {
    try {
        // Create a textarea element
        const textArea = document.createElement('textarea');
        textArea.value = text;
        
        // Make sure it's not visible
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        textArea.style.opacity = '0';
        
        // Add to DOM, select, copy, and remove
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        return successful;
    } catch (error) {
        console.error('Fallback copy failed:', error);
        return false;
    }
}; 