import { css, html } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

@customElement("area-card")
export class AreaCard extends BaseElement {
  @state() __devices;
  @state() __entities;
  @property() id: string;

  static get styles() {
    return [baseStyle, css``];
  }

  render() {
    return html`
      <ul>
        ${this.__devices?.map((device) => html`<li>${device.name}</li>`)}
      </ul>
      <ul>
        ${this.__entities?.map((entity) => html`<li>${entity.name}</li>`)}
      </ul>
    `;
  }

  protected firstUpdated(
    _changedProperties: Map<string | number | symbol, unknown>
  ): void {
    this.__getDevices();
    this.__getEntities();
  }

  async __getDevices() {
    this.__devices = (
      await this.hass.callWS({
        type: "config/device_registry/list",
      })
    ).filter((device) => device.area_id === this.id);

    console.log(this.__devices);
  }

  async __getEntities() {
    this.__entities = (
      await this.hass.callWS({
        type: "config/entity_registry/list",
      })
    ).filter((entity) => entity.area_id === this.id);

    console.log(this.__entities);
  }
}
