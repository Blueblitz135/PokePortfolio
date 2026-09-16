/** Own, persist, and distribute portfolio display preferences to the React tree. */
import {
  useCallback,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { PortfolioPreferencesContext } from "./PortfolioPreferencesContext";
import {
  DEFAULT_PORTFOLIO_PREFERENCES,
  parsePortfolioPreferences,
  readPortfolioPreferences,
  writePortfolioPreferences,
  type PortfolioPreferences,
} from "./portfolioPreferences";

interface PortfolioPreferencesProviderProps {
  children: ReactNode;
}

/** Initialize preferences once and expose memoized save/reset operations. */
export function PortfolioPreferencesProvider({
  children,
}: PortfolioPreferencesProviderProps) {
  const [initialRead] = useState(() => readPortfolioPreferences());
  const [preferences, setPreferences] = useState(
    initialRead.preferences,
  );
  const [storageAvailable, setStorageAvailable] = useState(
    initialRead.storageAvailable,
  );

  const savePreferences = useCallback(
    (nextPreferences: PortfolioPreferences) => {
      const validatedPreferences = parsePortfolioPreferences(nextPreferences);
      setPreferences(validatedPreferences);

      const didPersist = writePortfolioPreferences(validatedPreferences);
      setStorageAvailable(didPersist);
      return didPersist;
    },
    [],
  );

  const resetPreferences = useCallback(() => {
    const defaults = parsePortfolioPreferences(
      DEFAULT_PORTFOLIO_PREFERENCES,
    );
    setPreferences(defaults);

    const didPersist = writePortfolioPreferences(defaults);
    setStorageAvailable(didPersist);
    return didPersist;
  }, []);

  const contextValue = useMemo(
    () => ({
      preferences,
      storageAvailable,
      savePreferences,
      resetPreferences,
    }),
    [
      preferences,
      resetPreferences,
      savePreferences,
      storageAvailable,
    ],
  );

  return (
    <PortfolioPreferencesContext.Provider value={contextValue}>
      {children}
    </PortfolioPreferencesContext.Provider>
  );
}
