const Utils = {
  getVueFormTemplate(form) {
    // Add onsubmit event handler for Vue to form
    const formTemplate = `${form.slice(0, form.search(/form/) + 4)} v-on:submit.prevent="onFormSubmit" ${form.slice(form.search(/form/) + 4)}`;
    // Replace script with script2 (https://github.com/taoeffect/vue-script2)
    return (formTemplate.replace(/\bscript\b/g, 'script2'));
  },
  showFormErrors(errors, vm) {
    window.Baseframe.Forms.showValidationErrors(errors);
    vm.$toasted.show('Please review the indicated issues', {
      theme: 'primary',
      position: 'top-right',
      icon: 'error',
      duration: 5000,
    });
  },
  showSuccessMessage(message, vm) {
    vm.$toasted.show(message, {
      theme: 'primary',
      position: 'top-right',
      icon: 'done',
      duration: 5000,
    });
  },
  handleCancelEvent(elementClass, cancelRoute, vm) {
    if (document.querySelectorAll(elementClass)[0]) {
      document.querySelectorAll(elementClass)[0].addEventListener('click', (event) => {
        event.preventDefault();
        vm.$router.push(cancelRoute);
      });
    }
  },
  getCsrfToken() {
    return document.head.querySelector('[name=csrf-token]').content;
  },
};

export default Utils;
