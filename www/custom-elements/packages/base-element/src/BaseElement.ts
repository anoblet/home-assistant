import { LitElement } from "lit";
import { property } from "lit/decorators.js";
import mergeWith from "lodash-es/mergeWith";
import { globalStyle } from "../../global-style/src/index";
import { applyStyle } from "../../utility/src/index";
import { ClassMixin } from "./mixins/ClassMixin";
import { SlotMixin } from "./mixins/SlotMixin";
import { StyleMixin } from "./mixins/StyleMixin";

declare global {
  interface Window {
    loadCardHelpers: any;
  }
}

export class BaseElement extends StyleMixin(ClassMixin(SlotMixin(LitElement))) {
  _beforeRenderComplete;
  _children = [];
  _defaultConfig = {};
  _requiredConfig = [];

  _helpers;

  @property() hass;
  @property() config;
  @property({ type: Boolean }) ready = false;

  async _applyGlobalStyle(el) {
    await el?.updateComplete;
    applyStyle(el, globalStyle);
  }

  /**
   * Methods to be completed before initial render
   */
  async _beforeRender() {
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

  get entity() {
    return this.hass.states[this.config.entity];
  }

  _createCard(config) {
    // Some cards don't allow extra fields
    const _config = { ...config };
    delete _config.slot;

    const el = this._helpers.createCardElement(_config);

    this._setSlot(el, config);

    el.hass = this.hass;

    // this._applyGlobalStyle(el);

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

    this.config?.cards?.map(async (card) => {
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
