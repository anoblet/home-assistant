import { css, html, LitElement } from "https://unpkg.com/lit?module";
import baseStyle from "../base-style.js";

class DefaultView extends LitElement {
  setConfig(_config) {}

  static get properties() {
    return {
      cards: { type: Array, attribute: false },
    };
  }

  static get styles() {
    return [
      baseStyle,
      css`
        :host {
          --padding: 2rem;
        }
      `,
    ];
  }

  render() {
    return html`
      <div class="grid grid-gap padding">
        ${this.cards?.map((card) => html`${card}`)}
      </div>
    `;
  }
}

customElements.define("default-view", DefaultView);
