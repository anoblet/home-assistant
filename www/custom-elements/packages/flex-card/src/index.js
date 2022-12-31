import { css, html } from "lit";
import { customElement } from "lit/decorators.js";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

@customElement("flex-card")
export default class FlexCard extends BaseElement {
  _defaultConfig = {
    style: {},
  };

  static get styles() {
    return [
      baseStyle,
      css`
        :host {
          display: flex;
          flex-direction: row;
          flex-wrap: wrap;
        }

        ::slotted(*) {
          flex: 1;
          min-width: var(--flex-card-min-width, 0);
        }
      `,
    ];
  }

  render() {
    return html`<slot></slot>`;
  }
}
