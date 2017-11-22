<template>
  <div>
    <div class="content-head">
      <div class="mui-container">
        <div class="grid">
          <div class="grid__col-xs-12 grid__col-lg-6">
            <h1 class="mui--text-title"><router-link :to="{ name: 'Channel', params: { channel: channel.name }}" class="mui--text-dark">{{ channel.title }}</router-link> <i class="material-icons mui--align-middle mui--text-dark mui--text-title">chevron_right</i> New Playlist</h1>
          </div>
        </div>
      </div>
    </div>
    <div class="mui-container">
      <div class="page-content">
        <div class="grid">
          <div class="grid__col-xs-12 grid__col-lg-6 form-wrapper">
            <Form v-if="showForm"></Form>
            <div v-if="loading" class="loader-wrapper">
              <i class="material-icons loader mui--text-display3 mui--text-white">sync</i>
            </div>
            <div v-for="error in errors">
              <p class="mui-form--error mui--text-body1">{{ error[0] }}</p>
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
  name: 'ImportPlaylist',
  data() {
    return {
      channel: {},
      showForm: false,
      path: this.$route.path,
      formTemplate: '',
      loading: false,
      errors: [],
    };
  },
  components: {
    Form: (resolve) => {
      resolve({
        template: vm.formTemplate,
        methods: {
          onFormSubmit(event) {
            event.preventDefault();
            vm.loading = true;
            const formdata = new FormData(document.getElementById('form'));
            axios.post(vm.path, formdata)
            .then((formResponse) => {
              vm.$router.push(formResponse.data.result.new_playlist_url);
            })
            .catch((e) => {
              vm.loading = false;
              vm.errors = e.response.data.errors;
            });
          },
        },
        mounted() {
          document.querySelectorAll('a.mui-btn')[0].addEventListener('click', (event) => {
            event.preventDefault();
            vm.$router.push({ name: 'Channel', params: { channel: vm.channel.name } });
          });
        },
      });
    },
  },
  created() {
    vm = this;
    axios.get(this.path)
    .then((response) => {
      this.channel = response.data.channel;
      this.formTemplate = Utils.getVueFormTemplate(response.data.form);
      this.showForm = true;
    })
    .catch((e) => {
      vm.errors.push(e);
    });
  },
};
</script>

<style scoped>
</style>
