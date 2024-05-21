// SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
//
// SPDX-License-Identifier: MIT

import { LitElement, html } from "./lit-core.min.js";
import {
  format,
  formatDuration,
  intervalToDuration,
  parseISO,
} from "./date-fns.js";

export class Jobs extends LitElement {
  static properties = {
    _jobs: [],
  };

  constructor() {
    super();
    this._jobs = [];
    this._sse = null;
  }

  createRenderRoot() {
    return this;
  }

  connectedCallback() {
    super.connectedCallback();
    console.log("[Jobs] Connected");
    this._sse = new EventSource("/events/job");

    this._sse.addEventListener("job-list", (event) => {
      console.log("[Jobs] Received new job list:"); // , event.data);

      this._jobs = JSON.parse(event.data);
      console.log(this._jobs);
    });

    this._sse.addEventListener("job-started", this.jobStarted.bind(this));
    this._sse.addEventListener("job-progress", this.jobProgress.bind(this));
    this._sse.addEventListener("job-stopped", this.jobStopped.bind(this));

    this._sse.addEventListener("error", (err) => {
      this._sse.close();
    });
  }

  updated(changedProps) {
    const collapsibles = this.renderRoot.querySelectorAll(".collapsible");
    M.Collapsible.init(collapsibles, {});
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    console.log("[Jobs] Disconnected");
    if (this._sse) {
      console.log("Closing EventSource");
      this._sse.close();
    } else {
      console.log("EventSource unknown");
    }
  }

  jobStarted(event) {
    console.log("[Jobs] Job started");
    const jobEvent = JSON.parse(event.data);
    this._jobs = this._jobs.map((job) => {
      if (job.id === jobEvent.id) {
        return jobEvent;
      } else {
        return job;
      }
    });
  }

  jobStopped(event) {
    console.log("[Jobs] Job stopped");
    const jobEvent = JSON.parse(event.data);
    this._jobs = this._jobs.map((job) => {
      if (job.id === jobEvent.id) {
        return { ...job, finished_at: new Date().toISOString() };
      } else {
        return job;
      }
    });
  }

  jobProgress(event) {
    console.log("[Jobs] Received job progress");
    const progressEvent = JSON.parse(event.data);
    this._jobs = this._jobs.map((job) => {
      if (job.id === progressEvent.id) {
        return { ...job, progress: progressEvent.progress };
      } else {
        return job;
      }
    });
  }

  formatDate(isoDate) {
    const date = parseISO(isoDate);
    return format(date, "P ppp");
  }

  formatDuration(isoStart, isoEnd) {
    const start = parseISO(isoStart);
    const end = parseISO(isoEnd);
    return formatDuration(intervalToDuration({ start, end }));
  }

  jobStatus(job) {
    if (job.started_at) {
      let result = [];
      result.push(
        html`<small>Started at: ${this.formatDate(job.started_at)}</small>`,
      );
      if (job.finished_at) {
        result.push(
          html`<br /><small
              >Finished at: ${this.formatDate(job.finished_at)}
              (${this.formatDuration(job.finished_at, job.started_at)})</small
            >`,
        );
      }

      if (job.error) {
        result.push(
          html`<br /><small class="red-text"
              >Last run resulted in an error:
              <strong>${job.error_msg}</strong></small
            >`,
        );
      }
      return html`<div>${result}</div>`;
    } else {
      return html`<div><small>Waiting to start</small></div>`;
    }
  }

  jobProgressBar(job) {
    if (job.started_at && (!job.finished_at || job.error)) {
      if (job.progress) {
        return html`<div class="progress">
          <div class="determinate" style="width: ${job.progress}%"></div>
        </div>`;
      } else {
        return html`<div class="progress">
          <div class="indeterminate"></div>
        </div>`;
      }
    } else {
      return html``;
    }
  }

  jobAttributes(job) {
    let attributeRows = [];
    for (let attrId in job.attributes) {
      const attr = job.attributes[attrId];
      attributeRows.push(
        html` <tr>
          <td>${attr.displayName}</td>
          <td>${attr.values[0]}</td>
        </tr>`,
      );
    }
    return html`<ul class="collapsible expandable">
      <li>
        <div class="collapsible-header">
          <i class="material-icons">list_alt</i>Details
        </div>
        <div class="collapsible-body">
          <table class="responsive">
            <tbody>
              ${attributeRows}
            </tbody>
          </table>
        </div>
      </li>
    </ul>`;
  }

  removeFinishedJobButton(job) {
    return html`<a href="#" @click=${{ handleEvent: () => this.removeJob(job) }}
      >Remove</a
    >`;
  }

  renderJobList() {
    if (this._jobs.length > 0) {
      return html` ${this._jobs.map(
        (job) =>
          html` <div class="row" style="margin-top: 0.5rem">
            <div class="col s10 offset-s1">
              <div class="card">
                <div class="card-content">
                  <span class="card-title">${job.service_id}</span>
                  <small class="grey-text text-darken-2">${job.id}</small>
                  ${this.jobAttributes(job)}
                  <p>${this.jobStatus(job)}</p>
                  <p>${this.jobProgressBar(job)}</p>
                </div>
                <div class="card-action">
                  ${this.removeFinishedJobButton(job)}
                </div>
              </div>
            </div>
          </div>`,
      )}`;
    } else {
      return html`<div class="row" style="margin-top: 0.5rem">
        <div class="col s10 offset-s1"><p>No running jobs</p></div>
      </div>`;
    }
  }

  clearFinishedJobs() {
    fetch("/jobs/clear/finished", {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        this._jobs = this._jobs.filter((job) => job.id in data.deleted_jobs);
      })
      .catch((err) => console.error(`Error clearing finished jobs: ${err}`));
  }

  removeJob(job) {
    console.log(this._jobs);
    if (window.confirm("Are you sure?")) {
      fetch(`/jobs/${job.id}/delete`, {
        method: "POST",
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
        })
        .catch((err) => console.error(`Error removing job ${job.id}: ${err}`));
    }
  }

  render() {
    return html` <div>
      <div class="row">
        <div class="col s10 offset-s1">
          <h4>Running Jobs</h4>
        </div>
      </div>
      <div class="row">
        <div class="col s10 offset-s1">
          <button @click=${this.clearFinishedJobs} class="btn red waves-effect">
            Clear finished jobs
          </button>
        </div>
      </div>
      ${this.renderJobList()}
    </div>`;
  }
}

customElements.define("mercaido-jobs", Jobs);
