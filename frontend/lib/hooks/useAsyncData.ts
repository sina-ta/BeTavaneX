"use client";

import { useCallback, useEffect, useState } from "react";
import type { AsyncPageStatus } from "@/types/common";

type UseAsyncDataResult<T> = {
  status: AsyncPageStatus;
  data: T | null;
  error: string | null;
  reload: () => void;
};

export function useAsyncData<T>(
  fetcher: () => Promise<T>,
  isEmpty?: (data: T) => boolean
): UseAsyncDataResult<T> {
  const [status, setStatus] =
    useState<AsyncPageStatus>("loading");
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const reload = useCallback(() => {
    setReloadKey((key) => key + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;

    setStatus("loading");
    setError(null);

    fetcher()
      .then((result) => {
        if (cancelled) {
          return;
        }

        if (isEmpty?.(result)) {
          setData(result);
          setStatus("empty");
          return;
        }

        setData(result);
        setStatus("success");
      })
      .catch((err: unknown) => {
        if (cancelled) {
          return;
        }

        const message =
          err instanceof Error
            ? err.message
            : "An unexpected error occurred";

        setError(message);
        setData(null);
        setStatus("error");
      });

    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  return { status, data, error, reload };
}
