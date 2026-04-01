export type TaskStatus = "pending" | "running" | "completed";

export interface SearchSource {
  title: string;
  url: string;
  snippet?: string | null;
  provider?: string | null;
  query?: string | null;
  score?: number;
}

export interface ResearchNote {
  title: string;
  content: string;
  category: "fact" | "source" | "verification" | "impact";
  source_url?: string | null;
  source_title?: string | null;
}

export interface ResearchTaskTrace {
  rewritten_queries: string[];
  provider?: string | null;
  fallback_provider?: string | null;
  used_fallback: boolean;
  result_count: number;
  query_cache_hit: boolean;
  search_cache_hit: boolean;
  note_cache_hit: boolean;
}

export interface ResearchTask {
  id: string;
  title: string;
  status: TaskStatus;
  summary?: string | null;
  sources?: SearchSource[];
  notes?: ResearchNote[];
  trace?: ResearchTaskTrace;
}

export interface ResearchHistoryItem {
  id: string;
  topic: string;
  status: "running" | "completed" | "failed" | "cancelled";
  created_at: string;
  updated_at: string;
  report_ready: boolean;
  error?: string | null;
  reused: boolean;
}

export interface ResearchState {
  researchId: string;
  topic: string;
  progress: number;
  isRunning: boolean;
  logs: string[];
  tasks: ResearchTask[];
  report: string;
  exportPath: string;
  history: ResearchHistoryItem[];
  reused: boolean;
}
