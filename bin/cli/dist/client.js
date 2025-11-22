"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HttpClient = exports.HomeAssistantApiError = exports.HomeAssistantClient = void 0;
const http_1 = require("./http");
class HomeAssistantClient {
    constructor(config) {
        this.http = new http_1.HttpClient(config);
    }
    static fromConfig(config) {
        return new HomeAssistantClient(config);
    }
    // Core
    getApiOverview() {
        return this.http.getJson('/api/');
    }
    getConfig() {
        return this.http.getJson('/api/config');
    }
    getComponents() {
        return this.http.getJson('/api/components');
    }
    // Events
    getEvents() {
        return this.http.getJson('/api/events');
    }
    fireEvent(eventType, eventData) {
        return this.http.postJson(`/api/events/${encodeURIComponent(eventType)}`, eventData ?? {});
    }
    // Services
    getServices() {
        return this.http.getJson('/api/services');
    }
    callService(domain, service, serviceData) {
        return this.http.postJson(`/api/services/${encodeURIComponent(domain)}/${encodeURIComponent(service)}`, serviceData ?? {});
    }
    // States
    getStates() {
        return this.http.getJson('/api/states');
    }
    getState(entityId) {
        return this.http.getJson(`/api/states/${encodeURIComponent(entityId)}`);
    }
    setState(entityId, state, attributes) {
        return this.http.postJson(`/api/states/${encodeURIComponent(entityId)}`, {
            state,
            attributes: attributes ?? {},
        });
    }
    deleteState(entityId) {
        return this.http.deleteJson(`/api/states/${encodeURIComponent(entityId)}`);
    }
    // History
    getHistory(startTime, params) {
        const query = {};
        if (params?.end_time)
            query.end_time = params.end_time;
        if (params?.filter_entity_id) {
            if (Array.isArray(params.filter_entity_id)) {
                query.filter_entity_id = params.filter_entity_id.join(',');
            }
            else {
                query.filter_entity_id = params.filter_entity_id;
            }
        }
        if (params?.minimal_response !== undefined) {
            query.minimal_response = params.minimal_response;
        }
        if (params?.no_attributes !== undefined) {
            query.no_attributes = params.no_attributes;
        }
        return this.http.getJson(`/api/history/period/${encodeURIComponent(startTime)}`, { query });
    }
    // Logbook
    getLogbook(startTime, params) {
        const query = {};
        if (params?.end_time)
            query.end_time = params.end_time;
        if (params?.entity)
            query.entity = params.entity;
        if (params?.context_id)
            query.context_id = params.context_id;
        return this.http.getJson(`/api/logbook/${encodeURIComponent(startTime)}`, { query });
    }
    // Error log
    getErrorLog() {
        return this.http.getText('/api/error_log');
    }
    // Camera
    getCameraImage(entityId) {
        return this.http.getBinary(`/api/camera_proxy/${encodeURIComponent(entityId)}`);
    }
    // Calendars
    getCalendars() {
        return this.http.getJson('/api/calendars');
    }
    getCalendarEvents(entityId, start, end) {
        const query = {
            start,
            end,
        };
        return this.http.getJson(`/api/calendars/${encodeURIComponent(entityId)}`, { query });
    }
    // Templates
    renderTemplate(request) {
        return this.http.postJson('/api/template', request);
    }
    // Config checks
    checkConfig() {
        return this.http.postJson('/api/config/core/check_config', {});
    }
    // Intents
    handleIntent(request) {
        return this.http.postJson('/api/intent/handle', request);
    }
    // Raw request helper for advanced usage
    rawRequest(method, path, options) {
        return this.http.request(method.toUpperCase(), path, options ?? {});
    }
}
exports.HomeAssistantClient = HomeAssistantClient;
var http_2 = require("./http");
Object.defineProperty(exports, "HomeAssistantApiError", { enumerable: true, get: function () { return http_2.HomeAssistantApiError; } });
Object.defineProperty(exports, "HttpClient", { enumerable: true, get: function () { return http_2.HttpClient; } });
