import axios from 'axios';

const Utils = {
  getElementId(htmlString) {
    return htmlString.match(/id="(.*?)"/)[1];
  },
  getVueFormTemplate(htmlString) {
    // Add onsubmit event handler for Vue to form
    const formTemplate = `${htmlString.slice(0, htmlString.search(/form/) + 4)} v-on:submit.prevent="onFormSubmit" ${htmlString.slice(htmlString.search(/form/) + 4)}`;
    // Replace script with script2 (https://github.com/taoeffect/vue-script2)
    return (formTemplate.replace(/\bscript\b/g, 'script2'));
  },
  showFormErrors(errors, formId) {
    window.Baseframe.Forms.showValidationErrors(formId, errors);
    this.$snotify.error('Please review the indicated issues', {
      position: 'rightBottom',
      timeout: 5000,
    });
  },
  showSuccessMessage(message) {
    this.$snotify.success(message, {
      position: 'rightBottom',
      timeout: 5000,
    });
  },
  handleCancelEvent(elementClass, cancelRoute) {
    const vue = this;
    if (document.querySelector(elementClass)) {
      document.querySelector(elementClass).addEventListener('click', (event) => {
        event.preventDefault();
        vue.$router.push(cancelRoute);
      });
    }
  },
  getCsrfToken() {
    return document.head.querySelector('[name=csrf-token]').content;
  },
  handleFormSubmit() {
    this.loading = true;
    const formdata = new FormData(document.getElementById(this.formId));
    axios.post(this.$route.path, formdata)
    .then((formResponse) => {
      this.onSuccessFormSubmit(formResponse);
    })
    .catch((e) => {
      this.loading = false;
      this.onErrorFormSubmit(e);
    });
  },
  fetchJson() {
    axios.get(this.$route.path)
    .then((response) => {
      this.onSuccessJsonFetch(response);
      this.$NProgress.done();
    })
    .catch((error) => {
      this.onErrorJsonFetch(error);
      this.$NProgress.done();
    });
  },
  setPageTitle(...subTitles) {
    // Takes an array of titles and returns a concatenated string separated by " — "
    subTitles.push(window.hgtv.siteTitle);
    document.title = subTitles.join(' — ');
  },
};

export default Utils;
