import { useEffect, useState } from "react";
import { getUsers } from "../api/ecommerceApi";

export function useUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    getUsers()
      .then((data) => {
        if (cancelled) return;
        setUsers(Array.isArray(data) ? data : []);
      })
      .catch(() => {
        if (cancelled) return;
        setUsers([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { users, loading };
}