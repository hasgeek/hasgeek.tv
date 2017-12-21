<template>
  <div>
    <div class="content-head">
      <div class="mui-container">
        <div class="grid">
          <div class="grid__col-xs-12">
            <h1 class="mui--text-title"><router-link :to="{ name: 'Channel', params: { channel: channel.name }}" class="mui--text-dark">{{ channel.title }}</router-link> <i class="material-icons mui--align-middle mui--text-dark mui--text-title">chevron_right</i> New Video</h1>
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
  name: 'AddVideo',
  data() {
    return {
      channel: {},
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
            .then((formResponse) => {
              vm.$router.push(formResponse.data.result.new_video_edit_url);
            })
            .catch((e) => {
              vm.loading = false;
              Utils.showFormErrors(e.response.data.errors, vm);
            });
          },
        },
        mounted() {
          Utils.handleCancelEvent('a.mui-btn', { name: 'Channel', params: { channel: vm.channel.name } }, vm);
        },
      };
    },
  },
  created() {
    vm = this;
    axios.get(this.path)
    .then((response) => {
      this.channel = response.data.channel;
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
