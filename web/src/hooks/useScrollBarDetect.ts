/*
 * @LastEditors: biz
 */
import { useEffect, useState } from 'react';
/**
 * Detects whether an element has a scrollbar.
 *
 * @param {React.RefObject} ref - The reference of the element to be detected.
 * @returns {boolean} - Whether the element has a scrollbar.
 */
const useScrollBarDetect = ref => {
    const [hasScrollBar, setHasScrollBar] = useState(false);

    useEffect(() => {
        const element = ref.current;
        if (!element) return;
        const checkScrollBar = () => {
            const hasVerticalScrollbar = element.scrollHeight > element.clientHeight;
            const hasHorizontalScrollbar = element.scrollWidth > element.clientWidth;
            setHasScrollBar(hasVerticalScrollbar || hasHorizontalScrollbar);
        };

        checkScrollBar();

        const observer = new MutationObserver(checkScrollBar);
        observer.observe(element, { attributes: true, childList: true, subtree: true });

        return () => observer.disconnect();
    }, [ref]);

    return hasScrollBar;
};
export default useScrollBarDetect;

/**
 * A Hook that listens for when an element scrolls to the bottom.
 *
 * @param {React.RefObject} ref - The reference of the element to be listened.
 * @param {Function} callback - The callback function triggered when scrolled to the bottom.
 * @param {number} offset - The number of pixels from the bottom when the callback is triggered.
 */
export const useScrollToBottom = (ref, callback, offset = 0) => {
    useEffect(() => {
        const element = ref.current;
        if (!element) return;

        const handleScroll = () => {
            const { scrollTop, scrollHeight, clientHeight } = element;
            if (scrollHeight - scrollTop - clientHeight <= offset) {
                callback();
            }
        };

        element.addEventListener('scroll', handleScroll);

        return () => {
            element.removeEventListener('scroll', handleScroll);
        };
    }, [ref, callback, offset]);
};
