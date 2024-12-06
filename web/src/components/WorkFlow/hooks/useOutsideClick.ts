import { useEffect } from 'react';

/**
 * A custom hook to listen for clicks outside of a given element.
 * @param {React.MutableRefObject} ref - The ref of the element to check clicks against.
 * @param {Function} onOutsideClick - The callback function to call when a click occurs outside the element.
 */
function useOutsideClick(ref, onOutsideClick) {
    useEffect(() => {
        function handleClickOutside(event) {
            if (ref.current && !ref.current.contains(event.target)) {
                onOutsideClick(event);
            }
        }

        // Add event listeners in the capture phase
        document.addEventListener('mousedown', handleClickOutside, true);
        document.addEventListener('touchstart', handleClickOutside, true);
        document.addEventListener('mouseup', handleClickOutside, true);
        document.addEventListener('touchend', handleClickOutside, true);

        return () => {
            // Remove event listeners in the capture phase
            document.removeEventListener('mousedown', handleClickOutside, true);
            document.removeEventListener('touchstart', handleClickOutside, true);
            document.removeEventListener('mouseup', handleClickOutside, true);
            document.removeEventListener('touchend', handleClickOutside, true);
        };
    }, [ref, onOutsideClick]);
}

export default useOutsideClick;
