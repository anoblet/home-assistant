import { css, html, nothing } from "https://unpkg.com/lit?module";
import { classMap } from "https://unpkg.com/lit/directives/class-map.js?module";

import { BaseElement } from "../base-element/base-element.js";
import baseStyle from "../base-style.js";

class FanCard extends BaseElement {
  _defaultConfig = {
    show: {
      friendly_name: true,
    },
  };

  _requiredConfig = ["entity"];

  render() {
    const entity = this.hass.states[this.config.entity];
    return html`
      <div class="grid grid-gap" id="container">
        <div class="grid grid-gap padding" id="attributes">
          <label>Air Quality</label>
          <span class="capitalize">${entity.attributes.air_quality}</span>
          <div
            class="content full-row graph ${classMap({
              none: this._isSlotEmpty("quality_graph"),
            })}"
          >
            <slot name="quality_graph"></slot>
          </div>
          <label>Speed</label>
          <span class="capitalize">
            ${entity.state === "off"
              ? html`Off`
              : html`${entity.attributes.speed}`}
          </span>
          <div
            class="content full-row ${classMap({
              none: this._isSlotEmpty("speed_graph"),
            })}"
          >
            <slot name="speed_graph"></slot>
          </div>
          <label>Filter Life</label>
          <span class="capitilize">${entity.attributes.filter_life}%</span>
        </div>
        <hr />
        <buttons-card .config=${this.config} .hass=${this.hass}></buttons-card>
      </div>
    `;
  }

  static get styles() {
    return [
      baseStyle,
      css`
        :host {
          font-size: var(--state-font-size, 1rem);
        }

        #attributes {
          grid-template-columns: min-content 1fr;
        }

        #attributes > label,
        #attributes > span {
          white-space: nowrap;
        }

        #attributes > label::after {
          content: ":";
        }

        #friendly_name {
          font-size: var(--state-font-size, 2rem);
          line-height: 2rem;
        }

        .full-row {
          grid-column: 1/-1;
        }
      `,
    ];
  }
}
customElements.define("fan-card", FanCard);
