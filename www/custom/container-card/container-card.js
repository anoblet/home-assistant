import { css, html } from "https://unpkg.com/lit?module";
import { BaseElement } from "../base-element/base-element.js";
import baseStyle from "../base-style.js";

class ContainerCard extends BaseElement {
  _defaultConfig = {};

  _requiredConfig = [];

  static get styles() {
    return [baseStyle, css``];
  }

  render() {
    const entity = this.hass.states[this.config.entity];
    return html`
      <div class="padding">
        <slot></slot>
      </div>
    `;
  }
}
customElements.define("container-card", ContainerCard);
