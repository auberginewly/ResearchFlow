import { reactive } from "vue";

import {
  fetchResearchDetail,
  fetchResearchHistory,
  getResearchExportUrl,
  streamResearch,
} from "../api/research";
import type { ResearchState, ResearchTask } from "../types/research";

const initialState = (): ResearchState => ({
  researchId: "",
  topic: "",
  progress: 0,
  isRunning: false,
  logs: [],
  tasks: [],
  report: "",
  exportPath: "",
  history: [],
  reused: false,
});

const state = reactive<ResearchState>(initialState());

export function useResearch() {
  const updateTask = (incomingTask: ResearchTask) => {
    const taskIndex = state.tasks.findIndex((task) => task.id === incomingTask.id);
    if (taskIndex >= 0) {
      state.tasks[taskIndex] = incomingTask;
      return;
    }
    state.tasks.push(incomingTask);
  };

  const startResearch = async (topic: string) => {
    Object.assign(state, initialState());
    state.topic = topic;
    state.isRunning = true;

    try {
      await streamResearch(topic, (event, payload) => {
        const message = typeof payload.message === "string" ? payload.message : "";
        if (message) state.logs.push(message);

        if (typeof payload.research_id === "string") {
          state.researchId = payload.research_id;
          state.exportPath = getResearchExportUrl(payload.research_id);
        }

        if (payload.reused === true) {
          state.reused = true;
        }

        if (event === "planning" && Array.isArray(payload.tasks)) {
          state.tasks = payload.tasks as ResearchTask[];
        }

        if (event === "history_reused") {
          if (Array.isArray(payload.tasks)) {
            state.tasks = payload.tasks as ResearchTask[];
          }
          if (typeof payload.report === "string") {
            state.report = payload.report;
          }
          state.progress = 100;
          state.isRunning = false;
        }

        if (
          (event === "task_started" ||
            event === "task_completed" ||
            event === "task_log") &&
          payload.task
        ) {
          updateTask(payload.task as ResearchTask);
        }

        if (typeof payload.progress === "number") {
          state.progress = payload.progress;
        }

        if (event === "report_ready" && typeof payload.report === "string") {
          state.report = payload.report;
        }

        if (event === "error" || event === "done") {
          state.isRunning = false;
        }
      });
      await refreshHistory();
    } catch (error) {
      state.logs.push(error instanceof Error ? error.message : "研究流程失败");
      state.isRunning = false;
    }
  };

  const refreshHistory = async () => {
    try {
      state.history = await fetchResearchHistory();
    } catch (error) {
      state.logs.push(error instanceof Error ? error.message : "无法获取研究历史");
    }
  };

  const loadHistoryItem = async (researchId: string) => {
    try {
      const detail = await fetchResearchDetail(researchId);
      state.researchId = detail.researchId;
      state.topic = detail.topic;
      state.progress = detail.progress;
      state.isRunning = detail.isRunning;
      state.tasks = detail.tasks;
      state.report = detail.report;
      state.exportPath = detail.exportPath;
      state.reused = false;
      state.logs = [`已载入研究记录：${detail.topic}`];
    } catch (error) {
      state.logs.push(error instanceof Error ? error.message : "无法载入研究记录");
    }
  };

  return {
    state,
    startResearch,
    refreshHistory,
    loadHistoryItem,
  };
}
