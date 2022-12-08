import { css, html } from "lit";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

class ButtonsCard extends BaseElement {
  static get styles() {
    return [
      baseStyle,
      css`
        :host {
          display: grid;
          grid-template-columns: repeat(
            auto-fit,
            minmax(var(--grid-template-columns-min, 256px), 1fr)
          );
        }

        :host([divider]) {
          background: #fff;
          grid-gap: 1px;
        }

        ::slotted(*) {
          background: var(--card-background-color);
        }
      `,
    ];
  }

  render() {
    return html` <slot></slot> `;
  }
}
customElements.define("buttons-card", ButtonsCard);
