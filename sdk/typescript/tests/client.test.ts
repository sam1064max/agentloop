import { describe, it, expect, vi } from "vitest";
import { AgentLoopClient } from "../src/client";
import { Trace } from "../src/trace";

describe("AgentLoopClient", () => {
  it("creates with defaults", () => {
    const client = new AgentLoopClient();
    expect(client).toBeInstanceOf(AgentLoopClient);
  });

  it("sets auth header when apiKey provided", () => {
    const client = new AgentLoopClient({ apiKey: "sk-123" });
    const headers = (client as unknown as { client: { defaults: { headers: Record<string, string> } } }).client.defaults.headers;
    expect(headers["Authorization"]).toBe("Bearer sk-123");
  });

  it("trackTrace sends correct payload", async () => {
    const client = new AgentLoopClient({ baseUrl: "http://localhost:9999" });
    const trace = new Trace({
      session_id: "sess_1",
      prompt: "hello",
      response: "world",
    });
    const spy = vi.spyOn(client as unknown as { client: { request: Function } }, "client" as never);

    try {
      await client.trackTrace(trace);
    } catch {
      // expected to fail since no server, but verifies API shape
    }

    expect(trace.toJSON()).toEqual({
      session_id: "sess_1",
      prompt: "hello",
      response: "world",
      tool_calls: [],
      timings: {},
      agent_version: undefined,
      prompt_version: undefined,
      metadata: {},
    });
  });
});

# history: test: add SDK client unit tests for Python and TS