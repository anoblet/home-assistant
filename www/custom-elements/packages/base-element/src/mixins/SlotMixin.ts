import { LitElement } from "lit";
import { property } from "lit/decorators.js";

type Constructor<T = {}> = new (...args: any[]) => T;
type Mixable = Constructor<LitElement>;

export function SlotMixin<TBase extends Mixable>(Base: TBase) {
  class Mixin extends Base {
    @property() _slots;

    constructor(...args) {
      super();
      this._slots = {};
    }

    protected firstUpdated(
      _changedProperties: Map<string | number | symbol, unknown>
    ): void {
      super.firstUpdated(_changedProperties);

      this._registerSlots();
    }

    _isSlotEmpty(slot) {
      return this._slots[slot]?.assignedElements().length === 0;
    }

    _registerSlots() {
      const slots = {};

      [...this.shadowRoot.querySelectorAll("slot")].map((slot) => {
        slots[slot.getAttribute("name")] = slot;

        slot.addEventListener("slotchange", () => this.requestUpdate());
      });

      this._slots = slots;
    }
  }

  return Mixin;
}
