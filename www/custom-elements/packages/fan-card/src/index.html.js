import { html } from "lit";
import { classMap } from "lit/directives/class-map.js";
import { buttons } from "./buttons.js";

export const template = function () {
  const entity = this.hass.states[this.config.entity];
  console.log(entity);
  return html`
    <div class="grid grid-gap" id="container">
      <div class="grid grid-gap padding" id="attributes">
        <label>Air Quality</label>
        <span class="capitalize">${entity.attributes.air_quality}</span>
        <div
          class="full-row relative ${classMap({
            empty: this._isSlotEmpty("quality_graph"),
          })}"
        >
          <slot name="quality_graph"></slot>
        </div>
        <label>Speed</label>
        <span class="capitalize">
          ${entity.state === "off"
            ? html`Off`
            : html`${this.__getSpeed() || entity.attributes.mode}`}
        </span>
        <div
          class="full-row ${classMap({
            epty: this._isSlotEmpty("speed_graph"),
          })}"
        >
          <slot name="speed_graph"></slot>
        </div>
        <label>Filter Life</label>
        <span class="capitilize">${entity.attributes.filter_life}%</span>
      </div>
      <hr />
      <div class="grid grid-gap" id="buttons">
        ${buttons.percentages.map(
          (percentage) => html`
            <mwc-button
              @click=${this._setPercentage}
              data-percentage="${percentage.value}"
              outlined
            >
              ${percentage.label}
            </mwc-button>
          `
        )}
        ${buttons.presetModes.map(
          (presetMode) => html`
            <mwc-button
              @click=${this._setPresetMode}
              data-preset-mode="${presetMode.value}"
              outlined
            >
              ${presetMode.label}
            </mwc-button>
          `
        )}
      </div>
    </div>
  `;
};
