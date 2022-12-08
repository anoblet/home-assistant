import { css, html } from "lit";
import { customElement } from "lit/decorators.js";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

@customElement("button-card")
export class ButtonCard extends BaseElement {
  
  static get styles() {
    return [baseStyle, css``];
  }

  render() {
    console.log(this.hass);
    return html`<slot></slot>`;
  }

  protected firstUpdated(
    _changedProperties: Map<string | number | symbol, unknown>
  ): void {
    this.__getData();
  }

  async __getData() {
    const [areas, devices, entities] = await Promise.all([
      this.hass.callWS({ type: "config/area_registry/list" }),
      this.hass.callWS({ type: "config/device_registry/list" }),
      this.hass.callWS({ type: "config/entity_registry/list" }),
    ]);

    console.log(areas, devices, entities);
  }
}
