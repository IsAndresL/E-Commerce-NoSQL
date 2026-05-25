import { useEffect, useState } from "react";

const STORAGE_KEY = "ecocart.currentUserId";

const LEGACY_USER_IDS = {
  luisa: "1",
  carlos: "2",
  "juan garcia": "jgarcia",
  "juan garcía": "jgarcia",
};

const normalizeSessionUserId = (value) => {
  const text = String(value || "").trim();
  if (!text) return null;
  return LEGACY_USER_IDS[text.toLowerCase()] || text;
};

const readStoredUserId = () => {
  if (typeof window === "undefined") return null;

  try {
    return normalizeSessionUserId(window.localStorage.getItem(STORAGE_KEY));
  } catch {
    return null;
  }
};

export function useSession() {
  const [userId, setUserId] = useState(() => readStoredUserId());

  useEffect(() => {
    if (typeof window === "undefined") return;

    try {
      if (userId) {
        window.localStorage.setItem(STORAGE_KEY, userId);
      } else {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    } catch {
      // Ignore storage errors in private/incognito modes.
    }
  }, [userId]);

  return {
    userId,
    isAuthenticated: Boolean(userId),
    signIn: (nextUserId) => setUserId(normalizeSessionUserId(nextUserId)),
    signOut: () => setUserId(null),
  };
}