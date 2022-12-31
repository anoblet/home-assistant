import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";
import { style } from "./index.css.js";
import { template } from "./index.html.js";

class FanCard extends BaseElement {
  _defaultConfig = {
    show: {
      friendly_name: true,
    },
  };

  _requiredConfig = ["entity"];

  static get styles() {
    return [baseStyle, style];
  }

  render = template.bind(this);

  __getSpeed() {
    const percentage = this.hass.states[this.config.entity].attributes.percentage;
    if (percentage) {
      switch(percentage) {
        case 33: {
          return "Low";
        }
        case 66: {
          return "Medium";
        }
        case 100: {
          return "High";
        }
      }
    }
  }

  _setPresetMode(e) {
    this.hass.callService("fan", "set_preset_mode", {
      entity_id: this.config.entity,
      preset_mode: e.target.dataset.presetMode,
    });
  }

  _setPercentage(e) {
    this.hass.callService("fan", "set_percentage", {
      entity_id: this.config.entity,
      percentage: e.target.dataset.percentage,
    })
  }
}
customElements.define("fan-card", FanCard);
