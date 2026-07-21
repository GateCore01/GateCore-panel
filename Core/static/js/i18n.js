// i18n.js – Internationalisierung mit externen JSON-Dateien
const i18n = {
    defaultLanguage: 'en',
    currentLanguage: 'en',
    translations: {},
    loaded: false,
    loading: false,
    queue: []
};

// Alle unterstützten Sprachen für das Dropdown
window.LANGUAGES = {
    'de': 'Deutsch',
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'it': 'Italiano',
    'ru': 'Русский',
    'ja': '日本語',
    'zh-CN': '简体中文',
    'zh-TW': '繁體中文',
    'pt-BR': 'Português (Brasil)',
    'pt-PT': 'Português (Europeu)',
    'ko': '한국어',
    'tr': 'Türkçe',
    'nl': 'Nederlands',
    'pl': 'Polski',
    'sv': 'Svenska',
    'ar': 'العربية',
    'cs': 'Čeština',
    'hu': 'Magyar',
    'el': 'Ελληνικά',
    'bg': 'Български',
    'ro': 'Română',
    'hr': 'Hrvatski',
    'sk': 'Slovenčina',
    'uk': 'Українська',
    'da': 'Dansk',
    'fi': 'Suomi',
    'no': 'Norsk',
    'id': 'Bahasa Indonesia',
    'ms': 'Bahasa Melayu',
    'th': 'ภาษาไทย',
    'vi': 'Tiếng Việt',
    'tl': 'Tagalog',
    'he': 'עברית',
    'ca': 'Català'
};

// Cookie-Hilfen (global)
window.getCookie = function(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
};

window.setCookie = function(name, value, days = 365) {
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = name + "=" + value + ";expires=" + d.toUTCString() + ";path=/";
};

function getLanguage() {
    let lang = window.getCookie('gatecore_language');
    if (!lang) {
        const browserLang = navigator.language || navigator.languages[0];
        
        // Präfix-Mapping für alle Sprachen
        const langMap = {
            'de': 'de', 'en': 'en', 'es': 'es', 'fr': 'fr', 'it': 'it', 'ru': 'ru',
            'ja': 'ja', 'ko': 'ko', 'tr': 'tr', 'nl': 'nl', 'pl': 'pl', 'sv': 'sv',
            'ar': 'ar', 'cs': 'cs', 'hu': 'hu', 'el': 'el', 'bg': 'bg', 'ro': 'ro',
            'hr': 'hr', 'sk': 'sk', 'uk': 'uk', 'da': 'da', 'fi': 'fi', 'no': 'no',
            'id': 'id', 'ms': 'ms', 'th': 'th', 'vi': 'vi', 'tl': 'tl', 'he': 'he',
            'ca': 'ca'
        };
        
        // Spezialfälle mit Region
        if (browserLang.startsWith('zh-CN')) lang = 'zh-CN';
        else if (browserLang.startsWith('zh-TW')) lang = 'zh-TW';
        else if (browserLang.startsWith('pt-BR')) lang = 'pt-BR';
        else if (browserLang.startsWith('pt-PT')) lang = 'pt-PT';
        else {
            const prefix = browserLang.split('-')[0];
            lang = langMap[prefix] || 'en';
        }
        
        window.setCookie('gatecore_language', lang);
    }
    return lang;
}

window.setLanguage = function(lang) {
    if (i18n.translations[lang]) {
        i18n.currentLanguage = lang;
        window.setCookie('gatecore_language', lang);
        translatePage();
    } else {
        loadLanguage(lang).then(() => {
            i18n.currentLanguage = lang;
            window.setCookie('gatecore_language', lang);
            translatePage();
        });
    }
};

async function loadLanguage(lang) {
    if (i18n.translations[lang]) return i18n.translations[lang];
    try {
        const response = await fetch(`/i18n/${lang}.json`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        i18n.translations[lang] = data;
        return data;
    } catch (e) {
        console.warn(`Could not load language ${lang}, falling back to English.`);
        if (lang !== 'en') return loadLanguage('en');
        return {};
    }
}

async function loadDefaultLanguage() {
    const lang = getLanguage();
    await loadLanguage(lang);
    i18n.currentLanguage = lang;
    i18n.loaded = true;
    i18n.queue.forEach(callback => callback());
    i18n.queue = [];
    translatePage();
}

window.translatePage = function() {
    const lang = i18n.currentLanguage;
    const translations = i18n.translations[lang] || i18n.translations[i18n.defaultLanguage] || {};
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        let text = translations[key];
        if (text) {
            const params = el.dataset.i18nParams ? JSON.parse(el.dataset.i18nParams) : {};
            for (const [k, v] of Object.entries(params)) {
                text = text.replace(`{${k}}`, v);
            }
            el.textContent = text;
        }
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        const text = translations[key];
        if (text) el.placeholder = text;
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        const text = translations[key];
        if (text) el.title = text;
    });
    const titleKey = document.querySelector('title')?.getAttribute('data-i18n');
    if (titleKey) {
        const titleText = translations[titleKey];
        if (titleText) document.title = titleText;
    }
};

window.translateWhenReady = function() {
    return new Promise((resolve) => {
        if (i18n.loaded) {
            translatePage();
            resolve();
        } else {
            i18n.queue.push(() => {
                translatePage();
                resolve();
            });
        }
    });
};

document.addEventListener('DOMContentLoaded', loadDefaultLanguage);