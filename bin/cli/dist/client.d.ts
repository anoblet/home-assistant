import { HttpClientOptions, RequestOptions } from './http';
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
export interface HomeAssistantClientConfig extends HttpClientOptions {
}
export declare class HomeAssistantClient {
    private readonly http;
    constructor(config: HomeAssistantClientConfig);
    static fromConfig(config: HomeAssistantClientConfig): HomeAssistantClient;
    getApiOverview(): Promise<ApiOverview>;
    getConfig(): Promise<HaConfig>;
    getComponents(): Promise<string[]>;
    getEvents(): Promise<HaEventDescription[]>;
    fireEvent(eventType: string, eventData?: Record<string, unknown>): Promise<Record<string, unknown>>;
    getServices(): Promise<HaServicesResponse>;
    callService(domain: string, service: string, serviceData?: Record<string, unknown>): Promise<unknown>;
    getStates(): Promise<HaState[]>;
    getState(entityId: string): Promise<HaState>;
    setState(entityId: string, state: string, attributes?: Record<string, unknown>): Promise<HaState>;
    deleteState(entityId: string): Promise<void>;
    getHistory(startTime: string, params?: HistoryQueryParams): Promise<HistoryResponse>;
    getLogbook(startTime: string, params?: LogbookQueryParams): Promise<LogbookEntry[]>;
    getErrorLog(): Promise<string>;
    getCameraImage(entityId: string): Promise<Uint8Array>;
    getCalendars(): Promise<CalendarInfo[]>;
    getCalendarEvents(entityId: string, start: string, end: string): Promise<CalendarEvent[]>;
    renderTemplate(request: TemplateRenderRequest): Promise<unknown>;
    checkConfig(): Promise<CheckConfigResult>;
    handleIntent(request: IntentHandleRequest): Promise<IntentHandleResponse>;
    rawRequest<T = unknown>(method: string, path: string, options?: RequestOptions): Promise<T>;
}
export { HomeAssistantApiError, HttpClient } from './http';
export type { HttpClientOptions, RequestOptions } from './http';
