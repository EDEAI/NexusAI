import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

type PageVisibilityEffectOptions = {
    onBeforeUnload?: (event: BeforeUnloadEvent) => void;
    onRouteChange?: (location: Location) => void;
};
const usePageVisibilityEffect = ({
    onBeforeUnload,
    onRouteChange,
}: PageVisibilityEffectOptions) => {
    const location = useLocation();
    const navigate = useNavigate(); 

    useEffect(() => {
      
        const handleBeforeUnload = event => {
            if (onBeforeUnload) {
                onBeforeUnload(event);
            }
        };

       
        window.addEventListener('beforeunload', handleBeforeUnload);

       
        if (onRouteChange) {
            onRouteChange(location); 
        }

       
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
    }, [location, onBeforeUnload, onRouteChange]);
};

export default usePageVisibilityEffect;
