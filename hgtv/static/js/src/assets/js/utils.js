const Utils = {
  getVueFormTemplate(form) {
    // Add onsubmit event handler for Vue to form
    const formTemplate = `${form.slice(0, form.search(/form/) + 4)} v-on:submit.prevent="onFormSubmit" ${form.slice(form.search(/form/) + 4)}`;
    // Replace script with script2 (https://github.com/taoeffect/vue-script2)
    return (formTemplate.replace(/\bscript\b/g, 'script2'));
  },
};

export default Utils;
