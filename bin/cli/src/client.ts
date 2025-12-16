import type { HttpClientOptions, RequestOptions } from './http.ts';
import { HttpClient } from './http.ts';

export interface ApiOverview {
  message: string;
}

export interface HaConfig {
  components: string[];
  config_dir: string;
  elevation: number;
  latitude: number;
  location_name: string;
  longitude: number;
  time_zone: string;
  unit_system: Record<string, unknown>;
  version: string;
  [key: string]: unknown;
}

export interface HaEventDescription {
  event: string;
  listener_count: number;
  [key: string]: unknown;
}

export interface HaServiceField {
  description?: string;
  example?: unknown;
  required?: boolean;
}

export interface HaServiceDescription {
  name?: string;
  description?: string;
  fields?: Record<string, HaServiceField>;
  [key: string]: unknown;
}

export type HaServicesResponse = Record<string, Record<string, HaServiceDescription>>;

export interface HaContext {
  id: string;
  parent_id: string | null;
  user_id: string | null;
  [key: string]: unknown;
}

export interface HaState {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
  last_changed: string;
  last_updated: string;
  context: HaContext;
  [key: string]: unknown;
}

export interface HistoryQueryParams {
  end_time?: string;
  filter_entity_id?: string | string[];
  minimal_response?: boolean;
  no_attributes?: boolean;
}

export type HistoryResponse = HaState[][];

export interface LogbookQueryParams {
  end_time?: string;
  entity?: string;
  context_id?: string;
}

export interface LogbookEntry {
  name: string;
  message: string;
  domain: string;
  when: string;
  entity_id?: string;
  context_id?: string;
  [key: string]: unknown;
}

export interface CalendarInfo {
  entity_id: string;
  name: string;
  [key: string]: unknown;
}

export interface CalendarEventDateTime {
  dateTime?: string;
  date?: string;
}

export interface CalendarEvent {
  summary?: string;
  start: CalendarEventDateTime;
  end: CalendarEventDateTime;
  [key: string]: unknown;
}

export interface TemplateRenderRequest {
  template: string;
  entity_id?: string | string[];
  variables?: Record<string, unknown>;
}

export interface CheckConfigResult {
  result: 'valid' | 'invalid';
  errors?: string;
  [key: string]: unknown;
}

export interface IntentHandleRequest {
  name: string;
  data?: Record<string, unknown>;
}

export interface IntentHandleResponse {
  speech?: {
    plain?: {
      speech: string;
      extra_data?: unknown;
    };
  };
  card?: Record<string, unknown>;
  data?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface HomeAssistantClientConfig extends HttpClientOptions {}

export class HomeAssistantClient {
  private readonly http: HttpClient;

  constructor(config: HomeAssistantClientConfig) {
    this.http = new HttpClient(config);
  }

  static fromConfig(config: HomeAssistantClientConfig): HomeAssistantClient {
    return new HomeAssistantClient(config);
  }

  // Core
  getApiOverview(): Promise<ApiOverview> {
    return this.http.getJson<ApiOverview>('/api/');
  }

  getConfig(): Promise<HaConfig> {
    return this.http.getJson<HaConfig>('/api/config');
  }

  getComponents(): Promise<string[]> {
    return this.http.getJson<string[]>('/api/components');
  }

  // Events
  getEvents(): Promise<HaEventDescription[]> {
    return this.http.getJson<HaEventDescription[]>('/api/events');
  }

  fireEvent(
    eventType: string,
    eventData?: Record<string, unknown>
  ): Promise<Record<string, unknown>> {
    return this.http.postJson<Record<string, unknown>>(
      `/api/events/${encodeURIComponent(eventType)}`,
      eventData ?? {}
    );
  }

  // Services
  getServices(): Promise<HaServicesResponse> {
    return this.http.getJson<HaServicesResponse>('/api/services');
  }

  callService(
    domain: string,
    service: string,
    serviceData?: Record<string, unknown>
  ): Promise<unknown> {
    return this.http.postJson<unknown>(
      `/api/services/${encodeURIComponent(domain)}/${encodeURIComponent(service)}`,
      serviceData ?? {}
    );
  }

  // States
  getStates(): Promise<HaState[]> {
    return this.http.getJson<HaState[]>('/api/states');
  }

  getState(entityId: string): Promise<HaState> {
    return this.http.getJson<HaState>(`/api/states/${encodeURIComponent(entityId)}`);
  }

  setState(
    entityId: string,
    state: string,
    attributes?: Record<string, unknown>
  ): Promise<HaState> {
    return this.http.postJson<HaState>(`/api/states/${encodeURIComponent(entityId)}`, {
      state,
      attributes: attributes ?? {},
    });
  }

  deleteState(entityId: string): Promise<void> {
    return this.http.deleteJson<void>(`/api/states/${encodeURIComponent(entityId)}`);
  }

  // History
  getHistory(startTime: string, params?: HistoryQueryParams): Promise<HistoryResponse> {
    const query: Record<string, string | number | boolean | undefined> = {};

    if (params?.end_time) query.end_time = params.end_time;
    if (params?.filter_entity_id) {
      if (Array.isArray(params.filter_entity_id)) {
        query.filter_entity_id = params.filter_entity_id.join(',');
      } else {
        query.filter_entity_id = params.filter_entity_id;
      }
    }
    if (params?.minimal_response !== undefined) {
      query.minimal_response = params.minimal_response;
    }
    if (params?.no_attributes !== undefined) {
      query.no_attributes = params.no_attributes;
    }

    return this.http.getJson<HistoryResponse>(
      `/api/history/period/${encodeURIComponent(startTime)}`,
      { query }
    );
  }

  // Logbook
  getLogbook(startTime: string, params?: LogbookQueryParams): Promise<LogbookEntry[]> {
    const query: Record<string, string | number | boolean | undefined> = {};

    if (params?.end_time) query.end_time = params.end_time;
    if (params?.entity) query.entity = params.entity;
    if (params?.context_id) query.context_id = params.context_id;

    return this.http.getJson<LogbookEntry[]>(`/api/logbook/${encodeURIComponent(startTime)}`, {
      query,
    });
  }

  // Error log
  getErrorLog(): Promise<string> {
    return this.http.getText('/api/error_log');
  }

  // Camera
  getCameraImage(entityId: string): Promise<Uint8Array> {
    return this.http.getBinary(`/api/camera_proxy/${encodeURIComponent(entityId)}`);
  }

  // Calendars
  getCalendars(): Promise<CalendarInfo[]> {
    return this.http.getJson<CalendarInfo[]>('/api/calendars');
  }

  getCalendarEvents(entityId: string, start: string, end: string): Promise<CalendarEvent[]> {
    const query: Record<string, string> = {
      start,
      end,
    };

    return this.http.getJson<CalendarEvent[]>(`/api/calendars/${encodeURIComponent(entityId)}`, {
      query,
    });
  }

  // Templates
  renderTemplate(request: TemplateRenderRequest): Promise<unknown> {
    return this.http.postJson<unknown>('/api/template', request);
  }

  // Config checks
  checkConfig(): Promise<CheckConfigResult> {
    return this.http.postJson<CheckConfigResult>('/api/config/core/check_config', {});
  }

  // Intents
  handleIntent(request: IntentHandleRequest): Promise<IntentHandleResponse> {
    return this.http.postJson<IntentHandleResponse>('/api/intent/handle', request);
  }

  // Raw request helper for advanced usage
  rawRequest<T = unknown>(method: string, path: string, options?: RequestOptions): Promise<T> {
    return this.http.request<T>(method.toUpperCase(), path, options ?? {});
  }
}
export { HomeAssistantApiError, HttpClient } from './http.ts';
export type { HttpClientOptions, RequestOptions } from './http.ts';
