import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { translations } from './translations';

const LANGUAGE_STORAGE_KEY = 'jay-asset-language';
const SUPPORTED_LANGUAGES = new Set(['en', 'ko']);

const LanguageContext = createContext({
  language: 'en',
  setLanguage: () => {},
  t: (key) => key,
});

const resolveDefaultLanguage = () => {
  const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);
  if (stored && SUPPORTED_LANGUAGES.has(stored)) return stored;
  const browser = (navigator.language || 'en').toLowerCase();
  return browser.startsWith('ko') ? 'ko' : 'en';
};

const lookup = (obj, path) =>
  path.split('.').reduce((acc, part) => (acc && Object.prototype.hasOwnProperty.call(acc, part) ? acc[part] : undefined), obj);

const interpolate = (template, params = {}) =>
  String(template).replace(/\{(\w+)\}/g, (_, key) => (params[key] !== undefined ? String(params[key]) : `{${key}}`));

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(resolveDefaultLanguage);

  useEffect(() => {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
    document.documentElement.lang = language;
  }, [language]);

  const value = useMemo(() => {
    const t = (key, params) => {
      const selected = translations[language] || translations.en;
      const fallback = translations.en;
      const raw = lookup(selected, key) ?? lookup(fallback, key) ?? key;
      return typeof raw === 'string' ? interpolate(raw, params) : raw;
    };
    return { language, setLanguage, t };
  }, [language]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
};

export const useLanguage = () => useContext(LanguageContext);

