import { css, html, nothing } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

@customElement("collapse-card")
export class CollapseCard extends BaseElement {
  @property({ reflect: true, type: Boolean }) open;

  static get styles() {
    return [
      baseStyle,
      css`
        :host {
          padding: var(--padding);
        }

        .header {
          border-radius: var(--border-radius, 1rem);
          cursor: pointer;
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--padding);
        }

        .header:hover {
          backdrop-filter: brightness(200%);
        }

        .header .icon {
          color: #fff;
        }
      `,
    ];
  }

  render() {
    return html`
      <div class="gap grid">
        <span @click=${this.__toggleOpen} class="header">
          ${this.config.summary}
          <span class="icon">
            <ha-icon icon="mdi:${this.open ? "chevron-up" : "chevron-down"}">
            </ha-icon>
          </span>
        </span>
        ${this.open
          ? html`
              <hr />
              <slot></slot>
            `
          : nothing}
      </div>
    `;
  }

  __toggleOpen() {
    this.open = !this.open;
  }
}
