import { LitElement } from "lit";
import { property } from "lit/decorators.js";

type Constructor<T = {}> = new (...args: any[]) => T;
type Mixable = Constructor<LitElement>;

export function StyleMixin<TBase extends Mixable>(Base: TBase) {
  class Mixin extends Base {
    @property() config;

    protected firstUpdated(_changedProperties: Map<string | number | symbol, unknown>): void {
      super.firstUpdated(_changedProperties);
      
      this._setStyle();
    }

    /**
     * Set the style from the configuration on the element
     */
    _setStyle() {
      if (this.config?.style) {
        for (const key in this.config.style) {
          this.style.setProperty(key, this.config.style[key]);
        }
      }
    }
  }

  return Mixin;
}
