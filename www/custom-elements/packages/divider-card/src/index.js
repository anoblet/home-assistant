import { css, html } from "lit";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

class DividerCard extends BaseElement {
  static get styles() {
    return [baseStyle, css`
      hr {
        color: var(--divider-card-color, #fff);
        width: var(--divider-card-width, 100%);
      }
    `];
  }

  render() {
    return html`
      <hr />
    `;
  }
}

customElements.define("divider-card", DividerCard);
