import { css, html } from "lit";
import { customElement } from "lit/decorators.js";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

@customElement("state-card")
export default class StateCard extends BaseElement {
  _defaultConfig = {
    style: {},
  };

  static get styles() {
    return [
      baseStyle,
      css`
        :host {
        }
      `,
    ];
  }

  render() {
    return html`<div class="center flex grow">${this.entity.state}</div>`;
  }
}
