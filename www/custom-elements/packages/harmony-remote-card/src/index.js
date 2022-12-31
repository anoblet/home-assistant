import { css, html, nothing } from "lit";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";
import { device as SamsungTV } from "./devices/SamsungTV";
import { device as FrigidaireClimateControl } from "./devices/FrigidaireClimateControl";

const devices = {
  SamsungTV,
  FrigidaireClimateControl,
};

class HarmonyRemoteCard extends BaseElement {
  static get properties() {
    return {
      device: {},
    };
  }

  _defaultConfig = {
    show: {
      icon: false,
      label: true,
    },
  };

  firstUpdated() {
    (async () => {
      this.device = devices[this.config.device];
    })();
  }

  render() {
    return html`
      <div class="grid grid-gap" id="grid">
        ${this.device?.buttons.map(
          (button) =>
            html`
              <mwc-button
                @click=${this._onClick}
                data-command=${button.command}
                icon=${this.config.show.icon && button.icon
                  ? button.icon
                  : nothing}
                outlined
              >
                ${this.config.show.label ? html`${button.label}` : nothing}
              </mwc-button>
            `
        )}
      </div>
    `;
  }

  static get styles() {
    return [
      baseStyle,
      css`
        #grid {
          grid-template-columns: repeat(auto-fit, 10rem);
          justify-content: center;
          padding: var(--padding);
        }
      `,
    ];
  }

  _onClick(e) {
    const command = e.target.dataset.command;

    command === "Power"
      ? this.hass.callService("switch", "toggle", {
          entity_id: this.config.switch,
        })
      : this.hass.callService("remote", "send_command", {
          entity_id: this.config.entity_id,
          command: e.target.dataset.command,
          device: this.device.id,
        });
  }
}
customElements.define("harmony-remote-card", HarmonyRemoteCard);
