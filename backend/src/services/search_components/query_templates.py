class QueryTemplates:
    def build(self, task_title: str) -> list[str]:
        task = task_title.strip()
        lowered = task.lower()

        if any(keyword in task for keyword in ["泄漏", "源码", "事故", "争议", "回应", "事件"]):
            return [
                f"{task} 原始来源 时间线",
                f"{task} 官方回应 真实性",
                f"{task} 影响范围 证据",
            ]

        if any(keyword in lowered for keyword in ["mcp", "agent", "protocol", "function calling"]):
            return [
                f"{task} official specification",
                f"{task} architecture comparison",
                f"{task} GitHub implementation",
            ]

        return [
            task,
            f"{task} 核心机制",
            f"{task} 应用场景 风险",
        ]
