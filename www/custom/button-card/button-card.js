import { css, html } from "https://unpkg.com/lit?module";
import { BaseElement } from "../base-element/base-element.js";
import baseStyle from "../base-style.js";

class ButtonCard extends BaseElement {
  render() {
    const entity = this.hass.states[this.config.entity];
    return html``;
  }

  static get styles() {
    return [baseStyle, css``];
  }

  _onClick(e) {}
}
customElements.define("button-card", ButtonCard);
