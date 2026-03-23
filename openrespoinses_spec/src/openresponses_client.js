/**
 * Runtime ESM client for OpenResponses API.
 *
 * Intended for direct browser usage with:
 * <script type="module">import { OpenResponsesClient } from './openresponses_client.js'</script>
 */

export class OpenResponsesError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = 'OpenResponsesError';
    this.status = options.status ?? null;
    this.code = options.code ?? null;
    this.param = options.param ?? null;
    this.details = options.details ?? null;
  }
}

export class OpenResponsesClient {
  constructor(options = {}) {
    this.baseUrl = (options.baseUrl ?? 'https://api.openai.com/v1').replace(/\/$/, '');
    this.apiKey = options.apiKey ?? null;
    const runtimeFetch = options.fetchImpl ?? globalThis.fetch?.bind(globalThis);
    if (!runtimeFetch) {
      throw new OpenResponsesError('fetch API is not available in this environment.');
    }
    this.fetchImpl = runtimeFetch;
    this.defaultHeaders = { ...(options.defaultHeaders ?? {}) };
  }

  async createResponse(body, options = {}) {
    const response = await this.#postResponses(body, {
      accept: 'application/json',
      signal: options.signal,
      headers: options.headers,
    });
    options.onResponse?.(response);

    const contentType = response.headers.get('content-type') ?? '';
    if (contentType.includes('text/event-stream')) {
      throw new OpenResponsesError(
        'Received event-stream response. Use createResponseStream() for stream mode.',
        { status: response.status }
      );
    }

    return response.json();
  }

  async *createResponseStream(body, options = {}) {
    const streamBody = { ...body, stream: true };
    const response = await this.#postResponses(streamBody, {
      accept: 'text/event-stream',
      signal: options.signal,
      headers: options.headers,
    });
    options.onResponse?.(response);

    const contentType = response.headers.get('content-type') ?? '';
    if (!contentType.includes('text/event-stream')) {
      throw new OpenResponsesError('Expected text/event-stream response.', {
        status: response.status,
      });
    }

    if (!response.body) {
      throw new OpenResponsesError('ReadableStream is not available in this environment.', {
        status: response.status,
      });
    }

    for await (const event of readSseEvents(response.body)) {
      if (!event.data) {
        continue;
      }
      if (event.data === '[DONE]') {
        return;
      }
      try {
        yield JSON.parse(event.data);
      } catch (error) {
        throw new OpenResponsesError('Failed to parse SSE event JSON.', {
          details: { rawData: event.data, cause: String(error) },
        });
      }
    }
  }

  async #postResponses(body, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      Accept: options.accept ?? 'application/json',
      ...this.defaultHeaders,
      ...(options.headers ?? {}),
    };

    if (this.apiKey && !headers.Authorization) {
      headers.Authorization = `Bearer ${this.apiKey}`;
    }

    const response = await this.fetchImpl(`${this.baseUrl}/responses`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      signal: options.signal,
    });

    if (response.ok) {
      return response;
    }

    let payload = null;
    try {
      payload = await response.json();
    } catch {
      try {
        payload = { message: await response.text() };
      } catch {
        payload = null;
      }
    }

    const errorPayload = payload?.error ?? payload ?? null;
    throw new OpenResponsesError(
      errorPayload?.message ?? `HTTP ${response.status}: request failed`,
      {
        status: response.status,
        code: errorPayload?.code ?? null,
        param: errorPayload?.param ?? null,
        details: errorPayload,
      }
    );
  }
}

export function createOpenResponsesClient(options = {}) {
  return new OpenResponsesClient(options);
}

export async function* readSseEvents(stream) {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });

      while (true) {
        const boundary = buffer.search(/\r?\n\r?\n/);
        if (boundary < 0) {
          break;
        }

        const rawEvent = buffer.slice(0, boundary);
        const separatorMatch = buffer.slice(boundary).match(/^\r?\n\r?\n/);
        const separatorLength = separatorMatch ? separatorMatch[0].length : 2;
        buffer = buffer.slice(boundary + separatorLength);

        const parsed = parseSseEvent(rawEvent);
        if (parsed) {
          yield parsed;
        }
      }
    }

    const finalChunk = buffer.trim();
    if (finalChunk) {
      const parsed = parseSseEvent(finalChunk);
      if (parsed) {
        yield parsed;
      }
    }
  } finally {
    reader.releaseLock();
  }
}

function parseSseEvent(rawEvent) {
  const lines = rawEvent.split(/\r?\n/);
  let eventName = null;
  const dataLines = [];

  for (const line of lines) {
    if (!line || line.startsWith(':')) {
      continue;
    }
    if (line.startsWith('event:')) {
      eventName = line.slice(6).trim();
      continue;
    }
    if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trimStart());
    }
  }

  if (dataLines.length === 0) {
    return null;
  }

  return {
    event: eventName ?? 'message',
    data: dataLines.join('\n'),
  };
}
