import type { ResearchHistoryItem, ResearchState } from "../types/research";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function streamResearch(
  topic: string,
  onEvent: (event: string, payload: Record<string, unknown>) => void,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/research/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({ topic }),
  });

  if (!response.ok || !response.body) {
    throw new Error("无法连接研究服务");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const messages = buffer.split("\n\n");
    buffer = messages.pop() ?? "";

    for (const message of messages) {
      const eventLine = message
        .split("\n")
        .find((line) => line.startsWith("event:"));
      const dataLine = message
        .split("\n")
        .find((line) => line.startsWith("data:"));

      if (!eventLine || !dataLine) continue;

      const event = eventLine.replace("event:", "").trim();
      const data = JSON.parse(dataLine.replace("data:", "").trim()) as Record<
        string,
        unknown
      >;

      onEvent(event, data);
    }
  }
}

export async function fetchResearchHistory(): Promise<ResearchHistoryItem[]> {
  const response = await fetch(`${API_BASE_URL}/research/history`);
  if (!response.ok) {
    throw new Error("无法获取研究历史");
  }
  return (await response.json()) as ResearchHistoryItem[];
}

export async function fetchResearchDetail(researchId: string): Promise<ResearchState> {
  const response = await fetch(`${API_BASE_URL}/research/history/${researchId}`);
  if (!response.ok) {
    throw new Error("无法获取研究详情");
  }
  const data = (await response.json()) as Record<string, unknown>;
  return {
    researchId: String(data.id ?? researchId),
    topic: String(data.topic ?? ""),
    progress: data.status === "completed" ? 100 : 0,
    isRunning: data.status === "running",
    logs: [],
    tasks: (data.tasks ?? []) as ResearchState["tasks"],
    report: String(data.report ?? ""),
    exportPath: `${API_BASE_URL}/research/history/${researchId}/export`,
    history: [],
    reused: false,
  };
}

export function getResearchExportUrl(researchId: string): string {
  return `${API_BASE_URL}/research/history/${researchId}/export`;
}

export function getResearchPdfExportUrl(researchId: string): string {
  return `${API_BASE_URL}/research/history/${researchId}/export/pdf`;
}
