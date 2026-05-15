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
  resultsBySession: Record<string, Record<string, AlgorithmResultRecord>>;
  history: DatasetSession[];
  setDataset: (dataset: DatasetSession) => void;
  setAllowedMethods: (methods: MethodType[]) => void;
  addResult: (key: string, result: AlgorithmResultRecord) => void;
  clearSession: () => void;
  setHistory: (history: DatasetSession[]) => void;
  setActiveSession: (uploadId: string) => void;
}

export const useAnalyticsStore = create<AnalyticsState>()(
  persist(
    (set, get) => ({
      dataset: null,
      resultsBySession: {},
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
        set((state) => {
          const current = state.dataset;
          if (!current) return state;
          const currentResults = state.resultsBySession[current.uploadId] ?? {};
          return {
            resultsBySession: {
              ...state.resultsBySession,
              [current.uploadId]: {
                ...currentResults,
                [key]: result
              }
            }
          };
        }),
      clearSession: () =>
        set((state) => {
          const current = state.dataset;
          if (!current) {
            return { dataset: null };
          }
          const { [current.uploadId]: _, ...remaining } = state.resultsBySession;
          return {
            dataset: null,
            resultsBySession: remaining,
            history: state.history.filter((item) => item.uploadId !== current.uploadId)
          };
        }),
      setHistory: (history) => set({ history }),
      setActiveSession: (uploadId) =>
        set((state) => {
          const match = state.history.find((item) => item.uploadId === uploadId);
          if (!match) return state;
          return { dataset: match };
        })
    }),
    {
      name: STORAGE_NAME,
      storage: createJSONStorage(browserSessionStorage),
      partialize: (state) => ({ dataset: state.dataset, resultsBySession: state.resultsBySession, history: state.history })
    }
  )
);
