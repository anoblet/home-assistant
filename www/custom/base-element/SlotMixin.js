export const SlotMixin = (superClass) =>
  class extends superClass {
    static get properties() {
      return { _slots: {} };
    }

    constructor() {
      super();
      this._slots = {};
    }

    firstUpdated() {
      super.firstUpdated();
      this._registerSlots();
    }

    _isSlotEmpty(slot) {
      return this._slots[slot]?.assignedElements().length === 0;
    }

    _registerSlots() {
      const slots = {};

      [...this.shadowRoot.querySelectorAll("slot")].map((slot) => {
        slots[slot.getAttribute("name")] = slot;
      });

      this._slots = slots;
    }

    _onSlotChange() {
      this.requestUpdate();
    }
  };
