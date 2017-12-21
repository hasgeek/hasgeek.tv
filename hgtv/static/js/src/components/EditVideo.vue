<template>
  <div>
    <div class="content-head">
      <div class="mui-container">
        <div class="grid">
          <div class="grid__col-xs-12">
            <h1 class="mui--text-title"><router-link :to="{ name: 'Video', params: { video: video.url }}" class="mui--text-dark">{{ video.title }}</router-link> <i class="material-icons mui--align-middle mui--text-dark mui--text-title">chevron_right</i> Edit video</h1>
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
              <i class="material-icons loader mui--text-display3 mui--text-white">sync</i>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Utils from '../assets/js/utils';

let vm = {};

export default {
  name: 'EditVideo',
  data() {
    return {
      video: {},
      path: this.$route.path,
      formTemplate: '',
      loading: false,
      errors: [],
    };
  },
  computed: {
    Form() {
      const template = this.formTemplate ? this.formTemplate : '<div class="mui--text-title"><i class="material-icons mui--text-title mui--align-middle">sync</i> Loading</div>';
      return {
        template,
        methods: {
          onFormSubmit() {
            vm.loading = true;
            const formdata = new FormData(document.getElementById('form'));
            axios.post(vm.path, formdata)
            .then(() => {
              vm.$router.push({ name: 'Video', params: { video: vm.video.url } });
            })
            .catch((e) => {
              vm.loading = false;
              Utils.showFormErrors(e.response.data.errors, vm);
            });
          },
        },
        mounted() {
          Utils.handleCancelEvent('a.mui-btn', { name: 'Video', params: { video: vm.video.url } }, vm);
        },
      };
    },
  },
  created() {
    vm = this;
    axios.get(this.path)
    .then((response) => {
      this.video = response.data.video;
      this.formTemplate = Utils.getVueFormTemplate(response.data.form);
    })
    .catch((e) => {
      vm.errors.push(e);
    });
  },
};
</script>

<style scoped>
</style>
