"use client";

/**
 * Project scope: selected project + server-backed authorized project list
 * (Stage 17 query layer). Selection persists in localStorage but is validated
 * against projects returned from GET /runtime/projects.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";

import { listProjects } from "@/lib/api/phase1/runtime";
import type { Project } from "@/lib/api/phase1/types";

const STORAGE_KEY = "selected_project_id";

type ProjectsLoadStatus = "idle" | "loading" | "ready" | "error";

type ProjectContextValue = {
  selectedProjectId: string | null;
  setSelectedProjectId: (projectId: string | null) => void;
  authorizedProjects: Project[];
  projectsStatus: ProjectsLoadStatus;
  refreshAuthorizedProjects: () => Promise<void>;
  isProjectAuthorized: (projectId: string) => boolean;
};

const ProjectContext = createContext<ProjectContextValue | null>(null);

export function ProjectProvider({ children }: { children: ReactNode }) {
  const [selectedProjectId, setSelectedProjectIdState] = useState<
    string | null
  >(null);
  const [authorizedProjects, setAuthorizedProjects] = useState<Project[]>([]);
  const [projectsStatus, setProjectsStatus] =
    useState<ProjectsLoadStatus>("idle");

  const refreshAuthorizedProjects = useCallback(async () => {
    setProjectsStatus("loading");
    try {
      const page = await listProjects({ limit: 200, sort_dir: "desc" });
      setAuthorizedProjects(page.items);
      setProjectsStatus("ready");
      return;
    } catch {
      setProjectsStatus("error");
    }
  }, []);

  useEffect(() => {
    void refreshAuthorizedProjects();
  }, [refreshAuthorizedProjects]);

  useEffect(() => {
    if (typeof window === "undefined" || projectsStatus !== "ready") {
      return;
    }
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      if (authorizedProjects.some((project) => project.id === stored)) {
        setSelectedProjectIdState(stored);
      } else {
        localStorage.removeItem(STORAGE_KEY);
        setSelectedProjectIdState(null);
      }
      return;
    }
    if (authorizedProjects.length === 1) {
      const only = authorizedProjects[0].id;
      setSelectedProjectIdState(only);
      localStorage.setItem(STORAGE_KEY, only);
    }
  }, [projectsStatus, authorizedProjects]);

  const isProjectAuthorized = useCallback(
    (projectId: string) =>
      authorizedProjects.some((project) => project.id === projectId),
    [authorizedProjects]
  );

  const setSelectedProjectId = useCallback(
    (projectId: string | null) => {
      if (
        projectId &&
        projectsStatus === "ready" &&
        !authorizedProjects.some((project) => project.id === projectId)
      ) {
        return;
      }
      setSelectedProjectIdState(projectId);
      if (typeof window === "undefined") {
        return;
      }
      if (projectId) {
        localStorage.setItem(STORAGE_KEY, projectId);
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    },
    [authorizedProjects, projectsStatus]
  );

  const value = useMemo<ProjectContextValue>(
    () => ({
      selectedProjectId,
      setSelectedProjectId,
      authorizedProjects,
      projectsStatus,
      refreshAuthorizedProjects,
      isProjectAuthorized,
    }),
    [
      selectedProjectId,
      setSelectedProjectId,
      authorizedProjects,
      projectsStatus,
      refreshAuthorizedProjects,
      isProjectAuthorized,
    ]
  );

  return (
    <ProjectContext.Provider value={value}>
      {children}
    </ProjectContext.Provider>
  );
}

export function useProject(): ProjectContextValue {
  const context = useContext(ProjectContext);
  if (context === null) {
    throw new Error("useProject must be used within a ProjectProvider");
  }
  return context;
}
