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
    console.log('showFormErrors', this);
    window.Baseframe.Forms.showValidationErrors(formId, errors);
    this.$snotify.error('Please review the indicated issues', {
      position: 'rightBottom',
      timeout: 5000,
    });
  },
  showSuccessMessage(message) {
    console.log('showFormErrors', this);
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
    console.log('handleFormSubmit', this);
    this.loading = true;
    const formdata = new FormData(document.getElementById(this.formId));
    axios.post(this.path, formdata)
    .then((formResponse) => {
      console.log('formResponse', formResponse);
      this.onSuccessFormSubmit(formResponse);
    })
    .catch((e) => {
      console.log('e', e);
      this.loading = false;
      this.onErrorFormSubmit(e);
    });
  },
  fetchJson() {
    console.log('fetchJson', this);
    console.log('this.path', this.path);
    console.log('this.onSuccessJsonFetch', this.onSuccessJsonFetch);
    axios.get(this.path)
    .then((response) => {
      this.onSuccessJsonFetch(response);
      console.log('done');
      this.$NProgress.done();
    })
    .catch((error) => {
      this.onErrorJsonFetch(error);
      this.$NProgress.done();
    });
  },
};

export default Utils;
