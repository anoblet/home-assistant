import { css, html } from "https://unpkg.com/lit?module";
import { BaseElement } from "../base-element/base-element.js";
import baseStyle from "../base-style.js";

class ButtonCard extends BaseElement {
  @property({type: String}) label;
  @property({type: String}) icon;
  @property({type: String}) value;

  render() {
    const entity = this.hass.states[this.config.entity];
    return html`
      Test
      ${this.config.label}
      ${this.config.icon}
      ${this.config.value}
    `;
  }

  static get styles() {
    return [baseStyle, css``];
  }

  _onClick(e) {}
}

customElements.define("button-card", ButtonCard);
