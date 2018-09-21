<template>
  <div>
    <div class="content-head">
      <div class="mui-container">
        <div class="grid">
          <div class="grid__col-xs-12">
            <h1 class="mui--text-title"><router-link :to="{ name: 'Channel', params: { channel: channel.name }}" class="mui--text-dark">{{ channel.title }}</router-link> <i class="material-icons mui--align-middle mui--text-dark mui--text-title">chevron_right</i> Edit channel</h1>
          </div>
        </div>
      </div>
    </div>
    <div class="mui-container">
      <div class="page-content">
        <div class="grid">
          <div class="grid__col-xs-12 form-wrapper">
            <component :is="Form"></component>
            <div v-if="loading" class="loader-wrapper">
              <i class="material-icons loader mui--text-display3 mui--text-white">refresh</i>
            </div>
          </div>
        </div>
      </div>
    </div>
    <DisplayError v-if="error" :error="error"></DisplayError>
  </div>
</template>

<script>
import Utils from '../assets/js/utils';

let vm = {};

export default {
  name: 'EditChannel',
  data() {
    return {
      currentView: 'Loader',
      channel: {},
      path: this.$route.path,
      formTemplate: '',
      formId: '',
      loading: false,
      errors: [],
    };
  },
  components: {
    DisplayError: () => import('./DisplayError.vue'),
  },
  methods: {
    onSuccessJsonFetch(response) {
      this.channel = response.data.channel;
      this.formTemplate = Utils.getVueFormTemplate(response.data.form);
      this.formId = Utils.getElementId(this.formTemplate);
    },
    onErrorJsonFetch(error) {
      this.error = error;
    },
    onSuccessFormSubmit(formResponse) {
      this.$router.push({ name: 'Channel', params: { channel: this.channel.name } });
      Utils.showSuccessMessage.bind(this, formResponse.data.doc)();
    },
    onErrorFormSubmit(e) {
      this.loading = false;
      Utils.showFormErrors.bind(this, e.response.data.errors, this.formId)();
    },
  },
  computed: {
    Form() {
      const template = this.formTemplate ? this.formTemplate : '<div class="loader-wrapper"><i class="material-icons loader mui--text-display3 mui--text-white">refresh</i></div>';
      return {
        template,
        methods: {
          onFormSubmit() {
            Utils.handleFormSubmit.bind(vm)();
          },
        },
        mounted() {
          Utils.handleCancelEvent.bind(vm, 'a.mui-btn', { name: 'Channel', params: { channel: vm.channel.name } })();
        },
      };
    },
  },
  beforeCreate() {
    this.$NProgress.configure({ showSpinner: false }).start();
    Utils.setPageTitle('Edit Channel');
  },
  created() {
    vm = this;
    Utils.fetchJson.bind(this)();
  },
};
</script>

<style scoped>
</style>
