import { css, html, LitElement } from "lit";
import { property } from "lit/decorators.js";
import { StyleMixin } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

class DefaultView extends StyleMixin(LitElement) {
  setConfig(_config) {}

  @property({ type: Array }) cards = [];

  static get styles() {
    return [
      baseStyle,
      css`
        :host {
          --padding: 1rem;
          --primary-color: hsl(200, 100%, 50%);

          height: 100%;
          padding: var(--padding);
          position: relative;
        }

        hui-entities-card {
          overflow: hidden;
        }
      `,
    ];
  }

  render() {
    return html`
      <div class="gap grid grow">${this.cards?.map((card) => html`${card}`)}</div>
    `;
  }
}

customElements.define("default-view", DefaultView);
