import { ChartType } from "chart.js";
import Chart from "chart.js/auto";
import "chartjs-adapter-date-fns";
import { css, html } from "lit";
import { customElement, query, state } from "lit/decorators.js";
import { BaseElement } from "../../base-element/src/index";
import baseStyle from "../../base-style/src/index";

const line: ChartType = "line";

@customElement("chart-js-card")
export default class ChartJSCard extends BaseElement {
  __chart;

  _defaultConfig = {
    chart: {
      options: {
        maintainAspectRatio: false,
      },
      type: "bar",
    },
    interval: 10000,
    style: {},
  };

  __data;
  __interval;

  @query("canvas") __canvas;
  @state() __history;

  static get styles() {
    return [
      baseStyle,
      css`
        canvas {
          height: 100% !important;
          width: 100% !important;
        }
      `,
    ];
  }

  render() {
    return html`<canvas></canvas>`;
  }

  protected async firstUpdated(
    _changedProperties: Map<string | number | symbol, unknown>
  ): Promise<void> {
    super.firstUpdated(_changedProperties);

    this.__data = await this.__getData();

    this.__registerChart();
    this.__registerInterval();
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();

    clearInterval(this.__interval);

    this.__chart.destroy();
  }

  get __entityIds() {
    return this.config.datasets.map((dataset) => dataset.entity_id).join(",");
  }

  private __registerChart() {
    this.config.chart.data = this.__formattedData;

    this.__chart = new Chart(this.__canvas, this.config.chart);
  }

  get __formattedData() {
    const datasets = [];

    this.__data.forEach((dataset, index) => {
      const _dataset = {
        ...{ data: [] },
        ...this.config.datasets[index].dataset,
      };

      dataset.forEach((point) => {
        let round = "";

        let lastChanged;

        switch (round) {
          case "hour":
            lastChanged = roundToNearestHour(
              new Date(point.last_changed)
            ).getTime();
            break;
          default:
            lastChanged = new Date(point.last_changed).getTime();
        }

        _dataset.data.push({
          x: new Date(point.last_changed).getTime(),
          y: Number(point.state),
        });
      });

      datasets.push(_dataset);
    });

    return { datasets };
  }

  __getData() {
    return this.hass.callApi(
      "get",
      `history/period?filter_entity_id=${this.__entityIds}&minimal_response&significant_changes_only`
    );
  }

  __registerInterval() {
    this.__interval = setInterval(async () => {
      this.__data = await this.__getData();
      this.__chart.data = this.__formattedData;
      this.__chart.update();
    }, this.config.interval);
  }
}

function roundToNearestHour(date) {
  date.setMinutes(date.getMinutes() + 30);
  date.setMinutes(0, 0, 0);

  return date;
}
