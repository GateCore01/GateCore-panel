// i18n.js – Internationalisierung mit externen JSON-Dateien
const i18n = {
    defaultLanguage: 'en',
    currentLanguage: 'en',
    translations: {},
    loaded: false,
    loading: false,
    queue: []
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
        if (browserLang.startsWith('de')) lang = 'de';
        else if (browserLang.startsWith('es')) lang = 'es';
        else if (browserLang.startsWith('fr')) lang = 'fr';
        else if (browserLang.startsWith('it')) lang = 'it';
        else if (browserLang.startsWith('ru')) lang = 'ru';
        else lang = 'en';
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
        // Korrekter Pfad: /i18n/datei.json (nicht /i18n/)
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