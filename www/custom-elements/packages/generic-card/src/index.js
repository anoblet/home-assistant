import { css, html, nothing } from "lit";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

class GenericCard extends BaseElement {
  _defaultConfig = {
    title: "",
  };

  static get styles() {
    return [
      baseStyle,
      css`
        :host {
          background-color: var(--card-background-color);
          border-color: var(--generic-card-border-color);
          border-style: var(--generic-card-border-style);
          border-width: var(--generic-card-border-width);
          display: flex;
          position: relative;
        }

        .custom-rows {
          grid-template-rows: max-content max-content auto;
        }

        #footer {
          display: contents;
        }
      `,
    ];
  }

  render() {
    return html`
      <div class="custom-rows grid gap grow">
        ${this.config.title
          ? html`
              <div class="center" id="title">${this.config.title}</div>
              <hr />
            `
          : nothing}
        <div class="relative">
          <slot></slot>
        </div>
      </div>
    `;
  }
}
customElements.define("generic-card", GenericCard);
