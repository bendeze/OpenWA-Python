/// <reference types="jest" />
import { OpenWAClient } from '../../../sdk/javascript/src/index';

describe('OpenWAClient', () => {
  let client: OpenWAClient;

  beforeEach(() => {
    // Mock the global fetch
    global.fetch = jest.fn();
    client = new OpenWAClient({
      apiKey: 'test-api-key',
      baseUrl: 'http://localhost:2785',
    });
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should initialize with provided config', () => {
    expect(client).toBeDefined();
  });

  it('should make an HTTP POST request to create a session', async () => {
    const mockResponse = {
      ok: true,
      json: jest.fn().mockResolvedValue({ id: 1, name: 'test-session', status: 'created' }),
    };
    (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

    const session = await client.sessions.create({ name: 'test-session' });

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:2785/api/sessions',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          'X-API-Key': 'test-api-key',
        }),
        body: JSON.stringify({ name: 'test-session' }),
      })
    );
    expect(session.name).toBe('test-session');
  });

  it('should list sessions', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue([{ id: '1', name: 'sess' }]),
    });
    const result = await client.sessions.list();
    expect(result).toHaveLength(1);
    expect(global.fetch).toHaveBeenCalledWith('http://localhost:2785/api/sessions', expect.any(Object));
  });

  it('should make an HTTP POST request to send text', async () => {
    const mockResponse = {
      ok: true,
      json: jest.fn().mockResolvedValue({ messageId: 'msg_1', timestamp: 12345 }),
    };
    (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

    const result = await client.messages.sendText('1', { chatId: '123@c.us', text: 'hello test' });

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:2785/api/sessions/1/messages/send-text',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ chatId: '123@c.us', text: 'hello test' }),
      })
    );
    expect(result.messageId).toBe('msg_1');
  });
});
});
