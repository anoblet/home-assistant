import { LitElement, nothing } from "https://unpkg.com/lit?module";
import mergeWith from "https://unpkg.com/lodash-es@4.17.21/mergeWith.js";
import { SlotMixin } from "./SlotMixin.js";

export class BaseElement extends SlotMixin(LitElement) {
  _children = [];
  _defaultConfig = {};
  _requiredConfig = [];

  _helpers;

  static get properties() {
    return {
      hass: {},
      config: {},
      ready: false,
    };
  }

  /**
   * Methods to be completed before initial render
   */
  async _beforeRender() {
    // Set properties defined in the configuration style field on the element
    this._setStyle();

    // Render children into the light DOM
    this._renderChildren();

    // We are done
    this._beforeRenderComplete = true;
  }

  /**
   * Make sure the configuration has all of the required fields
   */
  _checkConfig(config) {
    this._requiredConfig.map((property) => {
      if (!(property in config))
        throw new Error(`You need to define ${property}`);
    });
  }

  /**
   * Set the style from the configuration on the element
   */
  _setStyle() {
    this.config.style?.map((property) => {
      for (const key in property) {
        this.style.setProperty(key, property[key]);
      }
    });
  }

  _createCard(config) {
    // Some cards don't allow extra fields
    const _config = { ...config };
    delete _config.slot;

    const el = this._helpers.createCardElement(_config);

    this._setSlot(el, config);

    el.hass = this.hass;

    return el;
  }

  /**
   *
   * @param {*} element
   * @param {*} config
   */
  _setSlot(element, config) {
    if (config.slot) element.setAttribute("slot", config.slot);
  }

  /**
   * Merge passed configuration with default configuration
   *
   * @param {*} config
   * @returns
   */
  mergeConfig(config) {
    return mergeWith(
      {},
      this._defaultConfig,
      config,
      (objectValue, sourceValue) =>
        sourceValue === null ? objectValue : undefined
    );
  }

  setConfig(config) {
    // Make sure we have the required fields
    this._checkConfig(config);

    // Merge the default and provided configuration
    this.config = this.mergeConfig(config);
  }

  async _renderChildren() {
    this._helpers = await window.loadCardHelpers();
    this.config.cards?.map(async (card) => {
      const child = this._createCard(card);
      this.appendChild(child);
      this._children.push(child);
    });
  }

  shouldUpdate() {
    if (!this._beforeRenderComplete) this._beforeRender();
    return true;
  }

  updated(changedProperties) {
    // Pass HASS object on to children
    if (changedProperties.has("hass")) {
      this._children?.map((card) => (card.hass = this.hass));
    }
  }
}
