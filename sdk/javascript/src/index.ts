/**
 * OpenWA JavaScript/TypeScript SDK
 *
 * Official client library for the OpenWA WhatsApp API Gateway.
 */

// ── Custom Errors ──────────────────────────────────────────────────

export class OpenWAError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'OpenWAError';
  }
}

export class OpenWAAPIError extends OpenWAError {
  constructor(
    public readonly statusCode: number,
    message: string,
  ) {
    super(`API Error ${statusCode}: ${message}`);
    this.name = 'OpenWAAPIError';
  }
}

// ── Client Configuration ──────────────────────────────────────────

export interface OpenWAClientConfig {
  /** Base URL of the OpenWA API (e.g., 'http://localhost:2785') */
  baseUrl?: string;

  /** API key for authentication */
  apiKey?: string;

  /** Request timeout in milliseconds (default: 30000) */
  timeout?: number;
}

// ── Response Types ────────────────────────────────────────────────

export interface MessageResponse {
  messageId: string;
  timestamp: number;
}

export interface Session {
  id: string;
  name: string;
  status: string;
  phone: string | null;
  pushName: string | null;
}

export interface ApiKey {
  id: string;
  name: string;
  keyPrefix: string;
  fullKey?: string;
  role: string;
}

export interface Webhook {
  id: string;
  url: string;
  events: string[];
}

export interface Contact {
  id: string;
  name: string;
  number: string;
}

export interface Group {
  id: string;
  subject: string;
  participants: string[];
}

// ── Client Class ──────────────────────────────────────────────────

export class OpenWAClient {
  private readonly config: Required<OpenWAClientConfig>;

  constructor(config?: OpenWAClientConfig) {
    const baseUrl = config?.baseUrl || (typeof process !== 'undefined' ? process.env.OPENWA_BASE_URL : undefined);
    const apiKey = config?.apiKey || (typeof process !== 'undefined' ? process.env.OPENWA_API_KEY : undefined);

    if (!baseUrl) {
      throw new OpenWAError('baseUrl must be provided or set via OPENWA_BASE_URL environment variable.');
    }
    if (!apiKey) {
      throw new OpenWAError('apiKey must be provided or set via OPENWA_API_KEY environment variable.');
    }

    this.config = {
      baseUrl: baseUrl.replace(/\/$/, ''),
      apiKey,
      timeout: config?.timeout || 30000,
    };
  }

  get sessions() {
    return {
      list: () => this.request<Session[]>('GET', '/api/sessions'),
      get: (id: string) => this.request<Session>('GET', `/api/sessions/${id}`),
      create: (data: { name: string }) => this.request<Session>('POST', '/api/sessions', data),
      start: (id: string) => this.request<Session>('POST', `/api/sessions/${id}/start`),
      stop: (id: string) => this.request<Session>('POST', `/api/sessions/${id}/stop`),
      delete: (id: string) => this.request<void>('DELETE', `/api/sessions/${id}`),
      qr: (id: string) => this.request<{ qrCode: string; status: string }>('GET', `/api/sessions/${id}/qr`),
      markChatUnread: (id: string, chatId: string) =>
        this.request<{ status: string; result: any }>('POST', `/api/sessions/${id}/chats/unread`, { chatId }),
    };
  }

  get messages() {
    return {
      list: (sessionId: string) => this.request<any[]>('GET', `/api/sessions/${sessionId}/messages`),
      sendText: (sessionId: string, data: { chatId: string; text: string }) =>
        this.request<MessageResponse>('POST', `/api/sessions/${sessionId}/messages/send-text`, data),
    };
  }

  get webhooks() {
    return {
      listAll: () => this.request<Webhook[]>('GET', '/api/webhooks'),
      create: (sessionId: string, data: Partial<Webhook>) =>
        this.request<Webhook>('POST', `/api/sessions/${sessionId}/webhooks`, data),
      update: (sessionId: string, webhookId: string, data: Partial<Webhook>) =>
        this.request<Webhook>('PUT', `/api/sessions/${sessionId}/webhooks/${webhookId}`, data),
      delete: (sessionId: string, webhookId: string) =>
        this.request<void>('DELETE', `/api/sessions/${sessionId}/webhooks/${webhookId}`),
    };
  }

  get apiKeys() {
    return {
      list: () => this.request<ApiKey[]>('GET', '/api/auth/api-keys'),
      create: (data: { name: string; role: string }) => this.request<ApiKey>('POST', '/api/auth/api-keys', data),
      revoke: (keyId: string) => this.request<ApiKey>('POST', `/api/auth/api-keys/${keyId}/revoke`),
      rotate: (keyId: string) => this.request<ApiKey>('POST', `/api/auth/api-keys/${keyId}/rotate`),
      delete: (keyId: string) => this.request<void>('DELETE', `/api/auth/api-keys/${keyId}`),
    };
  }

  get contacts() {
    return {
      list: (sessionId: string) => this.request<Contact[]>('GET', `/api/sessions/${sessionId}/contacts`),
      get: (sessionId: string, contactId: string) =>
        this.request<Contact>('GET', `/api/sessions/${sessionId}/contacts/${contactId}`),
      checkNumber: (sessionId: string, number: string) =>
        this.request<{ exists: boolean; whatsappId: string | null }>(
          'GET',
          `/api/sessions/${sessionId}/contacts/check/${number}`,
        ),
      block: (sessionId: string, contactId: string) =>
        this.request<{ success: boolean }>('POST', `/api/sessions/${sessionId}/contacts/${contactId}/block`),
    };
  }

  get groups() {
    return {
      list: (sessionId: string) => this.request<Group[]>('GET', `/api/sessions/${sessionId}/groups`),
      create: (sessionId: string, data: { name: string; participants: string[] }) =>
        this.request<Group>('POST', `/api/sessions/${sessionId}/groups`, data),
      addParticipants: (sessionId: string, groupId: string, data: { participants: string[] }) =>
        this.request<any>('POST', `/api/sessions/${sessionId}/groups/${groupId}/participants`, data),
      removeParticipants: (sessionId: string, groupId: string, data: { participants: string[] }) =>
        this.request<any>('DELETE', `/api/sessions/${sessionId}/groups/${groupId}/participants`, data),
      setSubject: (sessionId: string, groupId: string, data: { subject: string }) =>
        this.request<any>('PUT', `/api/sessions/${sessionId}/groups/${groupId}/subject`, data),
    };
  }

  // ── Internal HTTP client ──────────────────────────────────────────

  private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const url = `${this.config.baseUrl}${path}`;

    const fetchOptions: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.config.apiKey,
      },
      signal: AbortSignal.timeout(this.config.timeout),
    };

    if (body !== undefined) {
      fetchOptions.body = JSON.stringify(body);
    }

    let response: Response;
    try {
      response = await fetch(url, fetchOptions);
    } catch (err: any) {
      if (err.name === 'AbortError' || err.name === 'TimeoutError') {
        throw new OpenWAError(`Request timed out after ${this.config.timeout}ms`);
      }
      throw new OpenWAError(`Network request failed: ${err.message}`);
    }

    if (!response.ok) {
      let errorMessage = response.statusText;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        try {
          errorMessage = (await response.text()) || errorMessage;
        } catch {
          // Ignore
        }
      }
      throw new OpenWAAPIError(response.status, errorMessage);
    }

    // Handle empty responses (204 No Content)
    if (response.status === 204) {
      return undefined as unknown as T;
    }

    return response.json() as Promise<T>;
  }
}

export default OpenWAClient;
