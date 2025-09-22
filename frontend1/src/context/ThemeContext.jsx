import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';

const ThemeContext = createContext();

const initialState = {
  theme: 'light', // light, dark
  primaryColor: '#4CAF50',
  secondaryColor: '#2196F3',
  accentColor: '#FF9800',
  fontSize: 'medium', // small, medium, large
  language: 'vi' // vi, en
};

const themeReducer = (state, action) => {
  switch (action.type) {
    case 'SET_THEME':
      return {
        ...state,
        theme: action.payload
      };
    case 'SET_PRIMARY_COLOR':
      return {
        ...state,
        primaryColor: action.payload
      };
    case 'SET_SECONDARY_COLOR':
      return {
        ...state,
        secondaryColor: action.payload
      };
    case 'SET_ACCENT_COLOR':
      return {
        ...state,
        accentColor: action.payload
      };
    case 'SET_FONT_SIZE':
      return {
        ...state,
        fontSize: action.payload
      };
    case 'SET_LANGUAGE':
      return {
        ...state,
        language: action.payload
      };
    case 'RESET_THEME':
      return initialState;
    default:
      return state;
  }
};

export const ThemeProvider = ({ children }) => {
  const [state, dispatch] = useReducer(themeReducer, initialState);

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('chatbot-theme');
    if (savedTheme) {
      try {
        const themeData = JSON.parse(savedTheme);
        Object.keys(themeData).forEach(key => {
          if (themeData[key] !== undefined) {
            dispatch({ type: `SET_${key.toUpperCase()}`, payload: themeData[key] });
          }
        });
      } catch (error) {
        console.error('Error loading theme from localStorage:', error);
      }
    }
  }, []);

  // Save theme to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('chatbot-theme', JSON.stringify(state));
  }, [state]);

  const setTheme = useCallback((theme) => {
    dispatch({ type: 'SET_THEME', payload: theme });
  }, []);

  const setPrimaryColor = useCallback((color) => {
    dispatch({ type: 'SET_PRIMARY_COLOR', payload: color });
  }, []);

  const setSecondaryColor = useCallback((color) => {
    dispatch({ type: 'SET_SECONDARY_COLOR', payload: color });
  }, []);

  const setAccentColor = useCallback((color) => {
    dispatch({ type: 'SET_ACCENT_COLOR', payload: color });
  }, []);

  const setFontSize = useCallback((size) => {
    dispatch({ type: 'SET_FONT_SIZE', payload: size });
  }, []);

  const setLanguage = useCallback((language) => {
    dispatch({ type: 'SET_LANGUAGE', payload: language });
  }, []);

  const resetTheme = useCallback(() => {
    dispatch({ type: 'RESET_THEME' });
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme(state.theme === 'light' ? 'dark' : 'light');
  }, [state.theme, setTheme]);

  const value = {
    ...state,
    setTheme,
    setPrimaryColor,
    setSecondaryColor,
    setAccentColor,
    setFontSize,
    setLanguage,
    resetTheme,
    toggleTheme
  };

  return (
    <ThemeContext.Provider value={value}>
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
