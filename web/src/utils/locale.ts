import { getLocale, setLocale } from '@umijs/max';

/**
 * Map backend language codes to frontend locale identifiers.
 */
export const mapLanguageToLocale = (language?: string | null) => {
    if (!language) {
        return undefined;
    }
    const normalized = language.toLowerCase();
    if (normalized.startsWith('en')) {
        return 'en-US';
    }
    if (normalized.startsWith('zh')) {
        return 'zh-CN';
    }
    return undefined;
};

/**
 * Map frontend locale identifiers back to backend language codes.
 */
export const mapLocaleToLanguage = (locale?: string | null) => {
    if (!locale) {
        return undefined;
    }
    const normalized = locale.toLowerCase();
    if (normalized === 'en-us' || normalized === 'en_us') {
        return 'en';
    }
    if (normalized === 'zh-cn' || normalized === 'zh_hans') {
        return 'zh';
    }
    return undefined;
};

/**
 * Ensure the application locale matches the provided backend language code.
 * Returns the resolved locale string so callers can reuse it if needed.
 */
export const syncLocaleWithLanguage = (language?: string | null) => {
    const targetLocale = mapLanguageToLocale(language);
    if (!targetLocale) {
        return undefined;
    }
    if (typeof window === 'undefined') {
        return targetLocale;
    }
    const currentLocale = getLocale();
    if (currentLocale !== targetLocale) {
        // Disable hard reloads to avoid unnecessary flicker during locale sync
        setLocale(targetLocale, false);
    }
    return targetLocale;
};
