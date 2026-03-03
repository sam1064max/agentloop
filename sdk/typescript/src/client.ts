import axios, { AxiosInstance, AxiosRequestConfig } from "axios";
import { Trace, TraceData } from "./trace";
import { Outcome, OutcomeData } from "./outcome";
import { Feedback, FeedbackData } from "./feedback";
import { Experiment, ExperimentData } from "./experiment";
import { Version, VersionData } from "./version";

export interface ClientConfig {
  baseUrl?: string;
  apiKey?: string;
  timeout?: number;
  maxRetries?: number;
}

export class AgentLoopClient {
  private readonly client: AxiosInstance;
  private readonly maxRetries: number;

  constructor(config: ClientConfig = {}) {
    const baseURL = config.baseUrl ?? "https://api.agentloop.dev";
    this.maxRetries = config.maxRetries ?? 3;

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (config.apiKey) {
      headers["Authorization"] = `Bearer ${config.apiKey}`;
    }

    this.client = axios.create({
      baseURL,
      headers,
      timeout: config.timeout ?? 30_000,
    });
  }

  private async request<T>(method: string, path: string, data?: unknown): Promise<T> {
    let lastError: unknown;
    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const config: AxiosRequestConfig = { method, url: path };
        if (data !== undefined) {
          config.data = data;
        }
        const response = await this.client.request<T>(config);
        return response.data;
      } catch (err) {
        lastError = err;
        if (attempt < this.maxRetries - 1) {
          const delay = 1000 * Math.pow(2, attempt);
          await new Promise((resolve) => setTimeout(resolve, delay));
        }
      }
    }
    throw lastError;
  }

  async trackTrace(trace: Trace): Promise<Record<string, unknown>> {
    return this.request("POST", "/v1/traces", trace.toJSON());
  }

  async trackOutcome(outcome: Outcome): Promise<Record<string, unknown>> {
    return this.request("POST", "/v1/outcomes", outcome.toJSON());
  }

  async trackFeedback(feedback: Feedback): Promise<Record<string, unknown>> {
    return this.request("POST", "/v1/feedback", feedback.toJSON());
  }

  async trackExperiment(experiment: Experiment): Promise<Record<string, unknown>> {
    return this.request("POST", "/v1/experiments", experiment.toJSON());
  }

  async trackVersion(version: Version): Promise<Record<string, unknown>> {
    return this.request("POST", "/v1/versions", version.toJSON());
  }

  async trackTracesBatch(traces: Trace[]): Promise<Record<string, unknown>> {
    return this.request("POST", "/v1/traces/batch", traces.map((t) => t.toJSON()));
  }

  async trackOutcomesBatch(outcomes: Outcome[]): Promise<Record<string, unknown>> {
    return this.request("POST", "/v1/outcomes/batch", outcomes.map((o) => o.toJSON()));
  }
}

# history: feat: implement TypeScript SDK client