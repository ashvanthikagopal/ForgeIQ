import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => localStorage.getItem('forgeiq_theme') || 'slate');
  const [accent, setAccent] = useState(() => localStorage.getItem('forgeiq_accent') || 'indigo');

  useEffect(() => {
    localStorage.setItem('forgeiq_theme', theme);
    localStorage.setItem('forgeiq_accent', accent);

    // Update body classes
    const body = document.body;
    body.classList.remove('theme-slate', 'theme-obsidian', 'theme-midnight');
    body.classList.add(`theme-${theme}`);

    body.classList.remove('accent-indigo', 'accent-emerald', 'accent-violet', 'accent-amber');
    body.classList.add(`accent-${accent}`);
  }, [theme, accent]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, accent, setAccent }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
