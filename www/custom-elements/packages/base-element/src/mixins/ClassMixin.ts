import { LitElement } from "lit";
import { property } from "lit/decorators.js";

type Constructor<T = {}> = new (...args: any[]) => T;
type Mixable = Constructor<LitElement>;

export function ClassMixin<TBase extends Mixable>(Base: TBase) {
  class Mixin extends Base {
    @property() config;

    protected firstUpdated(
      _changedProperties: Map<string | number | symbol, unknown>
    ): void {
      super.firstUpdated(_changedProperties);

      this._setClass();
    }

    protected _setClass() {
      this.config?.class?.map((className) => {
        this.classList.add(className);
      });
    }
  }

  return Mixin;
}
