"use client";

import { create } from "zustand";
import { persist, createJSONStorage, type StateStorage } from "zustand/middleware";
import type { AlgorithmResultRecord, DatasetSession, MethodType } from "@/types/api";

const STORAGE_NAME = "smart-analytics-session-v1";
const LIVE_SESSION_KEY = "smart-analytics-live-session";

function browserSessionStorage(): StateStorage {
  return {
    getItem: (name) => {
      if (typeof window === "undefined") return null;
      return window.sessionStorage.getItem(name);
    },
    setItem: (name, value) => {
      if (typeof window === "undefined") return;
      window.sessionStorage.setItem(name, value);
      window.localStorage.setItem(name, value);
    },
    removeItem: (name) => {
      if (typeof window === "undefined") return;
      window.sessionStorage.removeItem(name);
      window.localStorage.removeItem(name);
    }
  };
}

export function ensureSessionBoundary() {
  if (typeof window === "undefined") return;
  if (!window.sessionStorage.getItem(LIVE_SESSION_KEY)) {
    window.localStorage.removeItem(STORAGE_NAME);
    window.sessionStorage.setItem(LIVE_SESSION_KEY, crypto.randomUUID());
  }
}

export interface AnalyticsState {
  dataset: DatasetSession | null;
  results: Record<string, AlgorithmResultRecord>;
  history: DatasetSession[];
  setDataset: (dataset: DatasetSession) => void;
  setAllowedMethods: (methods: MethodType[]) => void;
  addResult: (key: string, result: AlgorithmResultRecord) => void;
  clearSession: () => void;
}

export const useAnalyticsStore = create<AnalyticsState>()(
  persist(
    (set, get) => ({
      dataset: null,
      results: {},
      history: [],
      setDataset: (dataset) =>
        set((state) => ({
          dataset,
          history: [dataset, ...state.history.filter((item) => item.uploadId !== dataset.uploadId)].slice(0, 8)
        })),
      setAllowedMethods: (methods) => {
        const current = get().dataset;
        if (!current) return;
        set({ dataset: { ...current, methodTypes: methods } });
      },
      addResult: (key, result) =>
        set((state) => ({
          results: {
            ...state.results,
            [key]: result
          }
        })),
      clearSession: () => set({ dataset: null, results: {}, history: [] })
    }),
    {
      name: STORAGE_NAME,
      storage: createJSONStorage(browserSessionStorage),
      partialize: (state) => ({ dataset: state.dataset, results: state.results, history: state.history })
    }
  )
);
