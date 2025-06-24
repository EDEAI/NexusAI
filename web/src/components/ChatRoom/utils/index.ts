/*
 * @LastEditors: biz
 */
import React, { ReactNode } from 'react';

// Download file utility function
export const downloadFile = (url: string, filename: string) => {
    try {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (e) {}
};

// Extract text from React element
export const extractTextFromElement = (element: ReactNode): string => {
    if (typeof element === 'string') {
        return element;
    }
    if (Array.isArray(element)) {
        return element.map(extractTextFromElement).join('');
    }
    if (React.isValidElement(element)) {
        return extractTextFromElement(element.props.children);
    }
    return '';
};

// Extract text from array
export const extractTextFromArray = (arr: any) => {
    return extractTextFromElement(arr);
}; 