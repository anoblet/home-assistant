import { css, html, LitElement, nothing } from "https://unpkg.com/lit?module";
import mergeWith from "https://unpkg.com/lodash-es@4.17.21/mergeWith.js";

class StateCard extends LitElement {
  static get properties() {
    return {
      hass: {},
      config: {},
    };
  }

  constructor() {
    super();

    this.config = {
      show: {
        friendly_name: true,
      },
    };
  }

  render() {
    const stateObj = this.hass.states[this.config.entity];
    return html`
      <ha-card>
        <div class=" flex padding space-between">
          ${stateObj
            ? html`
                ${this.config.show.friendly_name
                  ? html`
                      <span class="label">
                        ${stateObj.attributes.friendly_name}:
                      </span>
                    `
                  : nothing}
                <span class="state">${stateObj.state}</span>
              `
            : html`
                <div class="not-found">
                  Entity ${this.config.entity} not found.
                </div>
              `}
        </div>
      </ha-card>
    `;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("You need to define an entity");
    }

    this.config = mergeWith({}, this.config, config, (a, b) =>
      b === null ? a : undefined
    );
  }

  static get styles() {
    return css`
      :host {
        font-size: var(--state-font-size, 2rem);
      }

      .center {
        align-items: center;
        display: flex;
        justify-content: center;
      }

      .flex {
        display: flex;
      }

      .padding {
        padding: var(--container-padding, 2rem);
      }

      .space-between {
        justify-content: space-between;
      }
    `;
  }
}
customElements.define("state-card", StateCard);
