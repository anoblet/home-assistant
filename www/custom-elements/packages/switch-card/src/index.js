import { css, html } from "lit";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

class SwitchCard extends BaseElement {
  static get properties() {
    return {
      icon: {},
      label: {},
      value: {},
    };
  }

  static get styles() {
    return [
      baseStyle,
      css`
        span {
          display: flex;
          justify-content: center;
          align-items: center;
        }

        button {
          display: grid !important;
        }

        #icon {
          color: var(--primary-color);
        }

        .border {
          /* border: 1px solid var(--border-color, #ccc); */
          border-radius: var(--border-radius, 1rem);
          margin: var(--margin, 1rem);
          padding: var(--padding, 1rem);
        }

        .border:hover {
          backdrop-filter: brightness(200%);
          background: #333 !important;
          cursor: pointer;
        }
      `,
    ];
  }

  render() {
    return html`
      <div class="border">
        <div class="gap grid">
          <span id="friendly_name"
            >${this.config.label || this.entity.attributes.friendly_name}</span
          >
          <span id="icon">
            <ha-icon id="flash" icon=${this.entity.attributes.icon}></ha-icon>
          </span>
          <span id="state" class="capitalize">${this.entity.state}</span>
        </div>
      </div>
    `;
  }

  _onClick() {
    this.hass.callService("switch", "toggle", {
      entity_id: this.config.entity,
    });
  }

  firstUpdated() {
    this.addEventListener("click", this._onClick);
  }
}

customElements.define("switch-card", SwitchCard);
